"""Content loading and document names for the generator."""

from dataclasses import dataclass
from pathlib import Path

import yaml


DEFAULT_DOCUMENTS = ["resume", "cv", "cover_letter", "leadership_resume"]

DOCUMENT_ALIASES = {
    "resume": "resume",
    "cv": "cv",
    "cover-letter": "cover_letter",
    "cover_letter": "cover_letter",
    "leadership-resume": "leadership_resume",
    "leadership_resume": "leadership_resume",
}

OPTIONAL_SECTION_DEFAULTS = {
    "certifications": {"entries": []},
    "projects": {"entries": []},
    "languages": {"entries": []},
    "publications": {"entries": []},
    "presentations": {"entries": []},
    "teaching": {"entries": []},
    "volunteer": {"entries": []},
    "leadership": {"categories": []},
}


@dataclass(frozen=True)
class ProjectPaths:
    """All repo paths the generator needs."""

    root: Path
    content_core_dir: Path
    content_optional_dir: Path
    config_dir: Path
    generated_dir: Path
    output_dir: Path
    template_dir: Path

    @classmethod
    def from_root(cls, root):
        root = Path(root).resolve()
        return cls(
            root=root,
            content_core_dir=root / "content" / "core",
            content_optional_dir=root / "content" / "optional",
            config_dir=root / "config",
            generated_dir=root / "generated",
            output_dir=root / "output",
            template_dir=root / "templates",
        )


def normalize_document_type(name):
    """Return the config key for a CLI document name."""
    return DOCUMENT_ALIASES.get(name, name)


def project_root_from_content(content_core_dir):
    """Return the repo root from a content/core path."""
    return Path(content_core_dir).resolve().parents[1]


def load_yaml(filepath):
    """Load one YAML file as a dictionary or list."""
    with open(filepath, "r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def load_optional_yaml(filepath, default):
    """Load a YAML file when it exists; otherwise return a copy of default."""
    filepath = Path(filepath)
    if filepath.exists():
        return load_yaml(filepath)
    return dict(default)


def load_core_content(content_core_dir):
    """Load the required content files once."""
    return {
        "personal": load_yaml(content_core_dir / "personal.yaml"),
        "summary": load_yaml(content_core_dir / "summary.yaml"),
        "experience": load_yaml(content_core_dir / "experience.yaml"),
        "education": load_yaml(content_core_dir / "education.yaml"),
        "skills": load_yaml(content_core_dir / "skills.yaml"),
    }


def load_optional_content(content_optional_dir):
    """Load optional content files with empty fallbacks."""
    return {
        name: load_optional_yaml(
            content_optional_dir / f"{name}.yaml",
            default,
        )
        for name, default in OPTIONAL_SECTION_DEFAULTS.items()
    }


def has_entries(data, key="entries"):
    """Return whether a section has publishable entries."""
    return bool(data.get(key))


def has_publication_entries(publications_data):
    """Return whether publication data has at least one publication group."""
    publication_keys = ("journal_articles", "conference_proceedings", "preprints")
    return any(publications_data.get(key) for key in publication_keys)


def has_leadership_entries(leadership_data):
    """Return whether leadership data has at least one entry."""
    return any(
        category.get("entries")
        for category in leadership_data.get("categories", [])
    )


def read_text_if_exists(filepath):
    """Return text from a file, or an empty string when it is absent."""
    filepath = Path(filepath)
    if not filepath.exists():
        return ""
    return filepath.read_text(encoding="utf-8")
