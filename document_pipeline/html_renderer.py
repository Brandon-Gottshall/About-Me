"""Orchestrate HTML rendering for the public document set.

Mirrors :class:`document_pipeline.renderer.DocumentRenderer` but emits
self-contained HTML files into ``output/`` for resume, CV, and
leadership-resume documents. Cover letters stay PDF-only because they
ship per-recipient and are not part of the public manifest.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape
from pydantic import ValidationError

from document_pipeline.html import html_escape_text, normalize_latex_text
from document_pipeline.html_sections import generate_html_sections
from document_pipeline.io import write_text
from document_pipeline.models import ProjectData
from document_pipeline.paths import ProjectPaths
from document_pipeline.renderer import normalize_doc_type
from document_pipeline.validate import validate_project


HTML_DOCUMENT_TYPES = ("resume", "cv", "leadership_resume")

DOCUMENT_DESCRIPTIONS = {
    "resume": (
        "Resume",
        "Concise software engineering resume.",
        "resume.pdf",
    ),
    "cv": (
        "Curriculum Vitae",
        "Expanded curriculum vitae covering experience, education, and skills.",
        "cv.pdf",
    ),
    "leadership_resume": (
        "Leadership Resume",
        "Leadership-focused resume covering ensemble, military, and technical leadership.",
        "leadership_resume.pdf",
    ),
}

HTML_OUTPUT_NAMES = {
    "resume": "resume.html",
    "cv": "cv.html",
    "leadership_resume": "leadership_resume.html",
}

SOURCE_REPO = "https://github.com/Brandon-Gottshall/About-Me"
DEFAULT_DOCUMENTS_BASE_URL = "https://brandon-gottshall.github.io/About-Me"


def html_environment(template_dir: Path) -> Environment:
    return Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(default=False),
        trim_blocks=False,
        lstrip_blocks=False,
    )


def _contact_items(personal: dict[str, Any]) -> list[dict[str, str]]:
    contact = personal.get("contact", {}) or {}
    items: list[dict[str, str]] = []

    homepage = contact.get("homepage")
    if homepage:
        items.append({"label": homepage, "href": f"https://{homepage}"})

    email = contact.get("email")
    if email:
        items.append({"label": email, "href": f"mailto:{email}"})

    mobile = contact.get("mobile")
    if mobile:
        dialable = "".join(character for character in mobile if character.isdigit() or character == "+")
        items.append({"label": mobile, "href": f"tel:{dialable}"})

    github = contact.get("github")
    if github:
        items.append(
            {"label": f"github.com/{github}", "href": f"https://github.com/{github}"}
        )

    linkedin = contact.get("linkedin")
    if linkedin:
        items.append(
            {
                "label": f"linkedin.com/in/{linkedin}",
                "href": f"https://www.linkedin.com/in/{linkedin}",
            }
        )

    return items


def _full_name(personal: dict[str, Any]) -> str:
    name = personal.get("name", {}) or {}
    parts = [str(name.get("first", "")).strip(), str(name.get("last", "")).strip()]
    return " ".join(p for p in parts if p)


def _position_for(personal: dict[str, Any], doc_type: str) -> str:
    positions = personal.get("position", {}) or {}
    value = positions.get(doc_type)
    if not value:
        value = positions.get("resume", "")
    return normalize_latex_text(value).strip()


def _quote_for(personal: dict[str, Any], doc_type: str) -> str:
    quotes = personal.get("quote", {}) or {}
    value = quotes.get(doc_type)
    if not value:
        return ""
    return normalize_latex_text(value).strip().strip('"').strip("“").strip("”")


def _styles(template_dir: Path) -> str:
    return (template_dir / "styles.css").read_text(encoding="utf-8")


class HtmlDocumentRenderer:
    def __init__(self, data: ProjectData):
        self.data = data
        self.template_dir = data.paths.templates_dir / "html"
        self.env = html_environment(self.template_dir)
        self._styles_cache: str | None = None

    @property
    def styles(self) -> str:
        if self._styles_cache is None:
            self._styles_cache = _styles(self.template_dir)
        return self._styles_cache

    def render(self, doc_type: str) -> Path:
        normalized_type = normalize_doc_type(doc_type)
        if normalized_type not in HTML_DOCUMENT_TYPES:
            raise KeyError(f"Unsupported HTML document type: {doc_type}")

        personal = self.data.core["personal"]
        title_label, description, pdf_filename = DOCUMENT_DESCRIPTIONS[normalized_type]
        full_name = _full_name(personal)
        position = _position_for(personal, normalized_type)
        quote = _quote_for(personal, normalized_type)
        contact_items = _contact_items(personal)
        sections_html = generate_html_sections(self.data, normalized_type)
        identity = self.data.identity
        record = identity["records"][normalized_type]
        canonical_url = f"{DEFAULT_DOCUMENTS_BASE_URL}/{HTML_OUTPUT_NAMES[normalized_type]}"

        page_title = f"{full_name} — {title_label}".strip(" —")
        template = self.env.get_template("base.html.jinja")
        rendered = template.render(
            page_title=page_title,
            description=description,
            canonical_url=canonical_url,
            doc_slug=normalized_type.replace("_", "-"),
            full_name=full_name,
            position=position,
            contact_items=contact_items,
            quote=quote,
            sections_html=sections_html,
            identity=identity,
            record=record,
            generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            source_repo=SOURCE_REPO,
            pdf_filename=pdf_filename,
            styles=self.styles,
        )

        output_path = self.data.paths.output_dir / HTML_OUTPUT_NAMES[normalized_type]
        write_text(output_path, rendered)
        print(f"Generated: {output_path}")
        return output_path


def render_html_documents(
    project_root: Path | str | None = None,
    requested: list[str] | None = None,
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

    requested_types = requested or list(HTML_DOCUMENT_TYPES)
    renderer = HtmlDocumentRenderer(data)
    output_paths: list[Path] = []
    for doc_type_arg in requested_types:
        normalized_type = normalize_doc_type(doc_type_arg)
        if normalized_type not in HTML_DOCUMENT_TYPES:
            print(f"Skipping unsupported HTML type: {doc_type_arg}", file=sys.stderr)
            continue
        output_paths.append(renderer.render(normalized_type))
    return output_paths


def main(argv: list[str] | None = None) -> None:
    render_html_documents(requested=argv if argv is not None else sys.argv[1:])


if __name__ == "__main__":
    main()
