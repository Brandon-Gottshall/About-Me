"""YAML validation for the document pipeline."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = PROJECT_ROOT / "schemas"


@dataclass(frozen=True)
class ValidationIssue:
    path: Path
    message: str

    def render(self, project_root: Path) -> str:
        rel_path = self.path.relative_to(project_root)
        return f"{rel_path}: {self.message}"


SCHEMA_MAP = {
    "config/cover_letter.yaml": "config/legacy-cover-letter.schema.json",
    "config/documents.yaml": "config/documents.schema.json",
    "content/core/education.yaml": "content/core/education.schema.json",
    "content/core/experience.yaml": "content/core/experience.schema.json",
    "content/core/personal.yaml": "content/core/personal.schema.json",
    "content/core/skills.yaml": "content/core/skills.schema.json",
    "content/core/summary.yaml": "content/core/summary.schema.json",
    "content/optional/certifications.yaml": "content/optional/certifications.schema.json",
    "content/optional/languages.yaml": "content/optional/languages.schema.json",
    "content/optional/leadership.yaml": "content/optional/leadership.schema.json",
    "content/optional/presentations.yaml": "content/optional/entry-list.schema.json",
    "content/optional/projects.yaml": "content/optional/entry-list.schema.json",
    "content/optional/publications.yaml": "content/optional/publications.schema.json",
    "content/optional/teaching.yaml": "content/optional/entry-list.schema.json",
    "content/optional/volunteer.yaml": "content/optional/entry-list.schema.json",
}


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_schema(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def schema_path_for(yaml_path: Path, project_root: Path) -> Path:
    rel_path = yaml_path.relative_to(project_root).as_posix()
    if rel_path in SCHEMA_MAP:
        return SCHEMA_DIR / SCHEMA_MAP[rel_path]
    if rel_path.startswith("config/cover_letters/"):
        return SCHEMA_DIR / "config/cover-letter-variant.schema.json"
    if rel_path.startswith("content/cover_letters/variants/"):
        return SCHEMA_DIR / "content/cover-letter-paragraphs.schema.json"
    return SCHEMA_DIR / "yaml-object.schema.json"


def iter_yaml_files(project_root: Path) -> list[Path]:
    roots = [project_root / "content", project_root / "config"]
    files: list[Path] = []
    for root in roots:
        files.extend(sorted(root.rglob("*.yaml")))
    return files


def validate_file(path: Path, project_root: Path = PROJECT_ROOT) -> list[ValidationIssue]:
    data = load_yaml(path)
    schema_path = schema_path_for(path, project_root)
    schema = load_schema(schema_path)
    validator = Draft202012Validator(schema)
    issues = []
    for error in sorted(validator.iter_errors(data), key=lambda item: list(item.path)):
        location = "/".join(str(part) for part in error.path)
        prefix = f"{location}: " if location else ""
        issues.append(ValidationIssue(path, f"{prefix}{error.message}"))
    return issues


def validate_project(project_root: Path = PROJECT_ROOT) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for yaml_path in iter_yaml_files(project_root):
        try:
            issues.extend(validate_file(yaml_path, project_root))
        except Exception as exc:  # pragma: no cover - surfaced through CLI
            issues.append(ValidationIssue(yaml_path, str(exc)))
    return issues


def main() -> None:
    project_root = PROJECT_ROOT
    issues = validate_project(project_root)
    if issues:
        for issue in issues:
            print(issue.render(project_root), file=sys.stderr)
        sys.exit(1)
    print("Validated YAML content and configuration.")


if __name__ == "__main__":
    main()
