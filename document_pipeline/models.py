"""Typed models for core document configuration and profile data."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from document_pipeline.io import load_yaml
from document_pipeline.paths import ProjectPaths


class FlexibleModel(BaseModel):
    model_config = ConfigDict(extra="allow")


class Margins(FlexibleModel):
    left: str
    top: str
    right: str
    bottom: str
    footskip: str


class DocumentSettings(FlexibleModel):
    paper_size: str
    font_size: str
    margins: Margins
    color: str
    section_color_highlight: bool
    header_alignment: str = ""


class CoverLetterDefaults(FlexibleModel):
    recipient_name: str = "Hiring Manager"
    company_name: str = "Company Name"
    company_address: str = "Company Address\nCity, State ZIP Code"
    position_name: str = "[Position Name]"
    letter_opening: str = "Dear Hiring Manager,"
    letter_closing: str = "Sincerely,"
    letter_body: str = ""


class DocumentSpec(FlexibleModel):
    sections: list[str] = Field(default_factory=list)
    settings: DocumentSettings


class CoverLetterSpec(FlexibleModel):
    variant: str = "default"
    settings: DocumentSettings
    defaults: CoverLetterDefaults = Field(default_factory=CoverLetterDefaults)


class DocumentsConfig(FlexibleModel):
    resume: DocumentSpec
    cv: DocumentSpec
    cover_letter: CoverLetterSpec
    leadership_resume: DocumentSpec

    def for_type(self, doc_type: str) -> DocumentSpec | CoverLetterSpec:
        return getattr(self, doc_type)


class Name(FlexibleModel):
    first: str
    last: str


class Contact(FlexibleModel):
    mobile: str = ""
    email: str = ""
    homepage: str = ""
    homepage2: str = ""
    github: str = ""
    linkedin: str = ""


class PersonalProfile(FlexibleModel):
    name: Name
    position: dict[str, str]
    address: str
    address_cv: str
    contact: Contact
    contact_line: dict[str, str] = Field(default_factory=dict)
    quote: dict[str, str]


@dataclass(frozen=True)
class ProjectData:
    """Loaded YAML content with typed high-level models and raw section data."""

    paths: ProjectPaths
    documents: DocumentsConfig
    identity: dict[str, Any]
    personal: PersonalProfile
    core: dict[str, Any]
    optional: dict[str, dict[str, Any]]

    @classmethod
    def load(cls, root: Path | str | None = None) -> "ProjectData":
        paths = ProjectPaths.from_root(root)
        documents_raw = load_yaml(paths.config_dir / "documents.yaml")
        identity_raw = load_yaml(paths.config_dir / "identity.yaml")
        personal_raw = load_yaml(paths.content_core_dir / "personal.yaml")
        core = {
            "personal": personal_raw,
            "summary": load_yaml(paths.content_core_dir / "summary.yaml"),
            "experience": load_yaml(paths.content_core_dir / "experience.yaml"),
            "education": load_yaml(paths.content_core_dir / "education.yaml"),
            "skills": load_yaml(paths.content_core_dir / "skills.yaml"),
        }
        optional: dict[str, dict[str, Any]] = {}
        if paths.content_optional_dir.exists():
            for yaml_path in sorted(paths.content_optional_dir.glob("*.yaml")):
                optional[yaml_path.stem] = load_yaml(yaml_path) or {}
        return cls(
            paths=paths,
            documents=DocumentsConfig.model_validate(documents_raw),
            identity=identity_raw,
            personal=PersonalProfile.model_validate(personal_raw),
            core=core,
            optional=optional,
        )

    def document(self, doc_type: str) -> DocumentSpec | CoverLetterSpec:
        return self.documents.for_type(doc_type)

    def optional_content(
        self, name: str, default: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        return self.optional.get(name, default or {})
