"""Document rendering orchestration for the YAML-driven LaTeX pipeline."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from document_pipeline.io import latex_environment, load_yaml, write_text
from document_pipeline.latex import escape_latex, format_cover_letter_body
from document_pipeline.models import CoverLetterSpec, DocumentSpec, ProjectData
from document_pipeline.paths import ProjectPaths
from document_pipeline.sections import generate_sections
from document_pipeline.validate import validate_project


DOCUMENT_TYPE_MAP = {
    "resume": "resume",
    "cv": "cv",
    "cover-letter": "cover_letter",
    "cover_letter": "cover_letter",
    "leadership-resume": "leadership_resume",
    "leadership_resume": "leadership_resume",
}

DEFAULT_DOCUMENTS = ["resume", "cv", "cover_letter", "leadership_resume"]


def normalize_doc_type(doc_type: str) -> str:
    return DOCUMENT_TYPE_MAP.get(doc_type, doc_type)


def output_name_for(doc_type: str) -> str:
    return {
        "resume": "resume.tex",
        "cv": "cv.tex",
        "cover_letter": "coverletter.tex",
        "leadership_resume": "leadership_resume.tex",
    }[doc_type]


def settings_context(spec: DocumentSpec | CoverLetterSpec) -> dict[str, Any]:
    settings = spec.settings
    return {
        "font_size": settings.font_size,
        "paper_size": settings.paper_size,
        "margins": settings.margins,
        "color": settings.color,
        "section_color_highlight": (
            "true" if settings.section_color_highlight else "false"
        ),
        "header_alignment": settings.header_alignment,
    }


class DocumentRenderer:
    def __init__(self, data: ProjectData):
        self.data = data
        self.env = latex_environment(data.paths.templates_dir)

    @property
    def personal(self) -> dict[str, Any]:
        return self.data.core["personal"]

    def render(self, doc_type: str) -> Path:
        normalized_type = normalize_doc_type(doc_type)
        if normalized_type not in DEFAULT_DOCUMENTS:
            raise KeyError(f"Unknown document type: {doc_type}")

        if normalized_type == "cover_letter":
            content = self.render_cover_letter()
        else:
            content = self.render_profile_document(normalized_type)

        output_path = self.data.paths.generated_dir / output_name_for(normalized_type)
        write_text(output_path, content)
        print(f"Generated: {output_path}")
        return output_path

    def render_profile_document(self, doc_type: str) -> str:
        personal = self.personal
        spec = self.data.document(doc_type)
        sections = generate_sections(self.data, doc_type)

        if doc_type == "cv":
            template = self.env.get_template("base_cv.tex")
            return template.render(
                name=personal["name"],
                position=personal["position"],
                address_cv=personal["address_cv"],
                contact=personal["contact"],
                quote=personal["quote"],
                sections=sections,
                **settings_context(spec),
            )

        template = self.env.get_template("base_resume.tex")
        if doc_type == "leadership_resume":
            position_text = personal["position"].get(
                "leadership_resume", personal["position"].get("resume", "")
            )
            quote_text = personal["quote"].get(
                "leadership_resume", personal["quote"].get("resume", "")
            )
            return template.render(
                name=personal["name"],
                position={"resume": position_text},
                address=personal["address"],
                contact=personal["contact"],
                contact_line=personal.get("contact_line", {}).get(
                    "leadership_resume",
                    personal.get("contact_line", {}).get("resume", ""),
                ),
                quote={"resume": quote_text},
                sections=sections,
                **settings_context(spec),
            )

        return template.render(
            name=personal["name"],
            position=personal["position"],
            address=personal["address"],
            contact=personal["contact"],
            contact_line=personal.get("contact_line", {}).get("resume", ""),
            quote=personal["quote"],
            sections=sections,
            **settings_context(spec),
        )

    def render_cover_letter(self) -> str:
        personal = self.personal
        spec = self.data.document("cover_letter")
        if not isinstance(spec, CoverLetterSpec):
            raise TypeError("cover_letter document config must be a CoverLetterSpec")
        defaults = spec.defaults
        variant_id = spec.variant

        try:
            variant_config, paragraphs = self.load_cover_letter_variant(variant_id)
            substitutions = {
                "Position Name": variant_config.get("position_name", ""),
                "Company Name": variant_config.get("company_name", ""),
            }
            letter_body = format_cover_letter_body(paragraphs, substitutions)
            recipient_name = variant_config.get(
                "recipient_name", defaults.recipient_name
            )
            company_name = variant_config.get("company_name", defaults.company_name)
            company_address_raw = variant_config.get(
                "company_address", defaults.company_address
            )
            position_name = variant_config.get("position_name", defaults.position_name)
            letter_opening = variant_config.get(
                "letter_opening", defaults.letter_opening
            )
            letter_closing = variant_config.get(
                "letter_closing", defaults.letter_closing
            )
        except (FileNotFoundError, KeyError) as exc:
            print(
                f"Warning: Variant '{variant_id}' not found, using legacy format: {exc}"
            )
            legacy_data = self.load_legacy_cover_letter()
            letter_body = escape_latex(
                legacy_data.get("body", defaults.letter_body)
            )
            recipient_name = legacy_data.get(
                "recipient_name", defaults.recipient_name
            )
            company_name = legacy_data.get("company_name", defaults.company_name)
            company_address_raw = legacy_data.get(
                "company_address", defaults.company_address
            )
            position_name = legacy_data.get("position_name", defaults.position_name)
            letter_opening = legacy_data.get(
                "letter_opening", defaults.letter_opening
            )
            letter_closing = legacy_data.get(
                "letter_closing", defaults.letter_closing
            )

        contact_line = None
        if variant_id == "academic_music":
            contact_line = personal.get("contact_line", {}).get(
                "leadership_resume",
                personal.get("contact_line", {}).get("resume", ""),
            )

        template = self.env.get_template("base_cover_letter.tex")
        return template.render(
            name=personal["name"],
            position=personal["position"],
            address=personal["address"],
            contact=personal["contact"],
            contact_line=contact_line,
            recipient_name=recipient_name,
            company_name=company_name,
            company_address=company_address_raw.strip().replace("\n", "\\\\"),
            position_name=position_name,
            letter_opening=letter_opening,
            letter_closing=letter_closing,
            letter_body=letter_body,
            variant_id=variant_id,
            **settings_context(spec),
        )

    def load_cover_letter_variant(
        self, variant_id: str
    ) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        variant_config_path = self.data.paths.config_dir / "cover_letters" / f"{variant_id}.yaml"
        if not variant_config_path.exists():
            raise FileNotFoundError(f"Variant config not found: {variant_config_path}")

        variant_config = load_yaml(variant_config_path)
        paragraphs = []
        for paragraph_ref in variant_config.get("paragraphs", []):
            if paragraph_ref.get("source") == "variant":
                paragraphs.append(
                    self.load_variant_paragraph(variant_id, paragraph_ref["content_id"])
                )
            else:
                paragraphs.append(
                    self.load_shared_paragraph(
                        paragraph_ref["type"], paragraph_ref["content_id"]
                    )
                )
        return variant_config, paragraphs

    def load_variant_paragraph(self, variant_id: str, content_id: str) -> dict[str, Any]:
        variant_content_path = (
            self.data.paths.content_dir
            / "cover_letters"
            / "variants"
            / variant_id
            / "paragraphs.yaml"
        )
        if not variant_content_path.exists():
            raise FileNotFoundError(
                f"Variant paragraph file not found: {variant_content_path}"
            )
        paragraphs = load_yaml(variant_content_path).get("paragraphs", {})
        if content_id not in paragraphs:
            raise KeyError(
                f"Paragraph '{content_id}' not found in variant '{variant_id}'"
            )
        return paragraphs[content_id]

    def load_shared_paragraph(self, paragraph_type: str, content_id: str) -> dict[str, Any]:
        shared_content_path = (
            self.data.paths.content_dir
            / "cover_letters"
            / "paragraphs"
            / f"{paragraph_type}.yaml"
        )
        if not shared_content_path.exists():
            raise FileNotFoundError(
                f"Shared paragraph file not found: {shared_content_path}"
            )
        paragraphs = load_yaml(shared_content_path).get("paragraphs", {})
        if content_id not in paragraphs:
            raise KeyError(
                f"Paragraph '{content_id}' not found in shared '{paragraph_type}' paragraphs"
            )
        return paragraphs[content_id]

    def load_legacy_cover_letter(self) -> dict[str, Any]:
        legacy_path = self.data.paths.config_dir / "cover_letter.yaml"
        if not legacy_path.exists():
            return {}
        return load_yaml(legacy_path) or {}


def generate_documents(
    project_root: Path | str | None = None, requested: list[str] | None = None
) -> list[Path]:
    paths = ProjectPaths.from_root(project_root)
    validation_issues = validate_project(paths.root)
    if validation_issues:
        for issue in validation_issues:
            print(issue.render(paths.root), file=sys.stderr)
        raise SystemExit(1)

    try:
        data = ProjectData.load(paths.root)
    except ValidationError as exc:
        print(exc, file=sys.stderr)
        raise SystemExit(1) from exc

    doc_types = requested or DEFAULT_DOCUMENTS
    renderer = DocumentRenderer(data)
    output_paths: list[Path] = []
    for doc_type_arg in doc_types:
        normalized_type = normalize_doc_type(doc_type_arg)
        if normalized_type not in DEFAULT_DOCUMENTS:
            print(f"Unknown document type: {doc_type_arg}", file=sys.stderr)
            raise SystemExit(1)
        output_paths.append(renderer.render(normalized_type))
    return output_paths


def main(argv: list[str] | None = None) -> None:
    generate_documents(requested=argv if argv is not None else sys.argv[1:])


if __name__ == "__main__":
    main()
