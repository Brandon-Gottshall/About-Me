"""Static portfolio export for the document pipeline."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPORT_DIR = PROJECT_ROOT / "exports"


DOCUMENTS = [
    {
        "id": "resume",
        "label": "Resume",
        "kind": "resume",
        "path": "output/resume.pdf",
        "preview": "docs/showcase/resume-page-1.png",
    },
    {
        "id": "cv",
        "label": "CV",
        "kind": "cv",
        "path": "output/cv.pdf",
        "preview": "docs/showcase/cv-page-1.png",
    },
    {
        "id": "leadership_resume",
        "label": "Leadership Resume",
        "kind": "resume",
        "path": "output/leadership_resume.pdf",
        "preview": "docs/showcase/leadership-resume-page-1.png",
    },
    {
        "id": "coverletter",
        "label": "Cover Letter",
        "kind": "cover_letter",
        "path": "output/coverletter.pdf",
        "preview": "docs/showcase/coverletter-page-1.png",
    },
]


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def pdf_page_count(path: Path) -> int | None:
    if not path.exists():
        return None
    try:
        result = subprocess.run(
            ["pdfinfo", str(path)],
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    for line in result.stdout.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":", 1)[1].strip())
    return None


def clean_portfolio_text(value: Any) -> Any:
    if isinstance(value, str):
        return (
            value.replace(r"\&", "&")
            .replace("~", " ")
            .replace(r"\textbullet{}", "•")
        )
    if isinstance(value, list):
        return [clean_portfolio_text(item) for item in value]
    if isinstance(value, dict):
        return {key: clean_portfolio_text(item) for key, item in value.items()}
    return value


def build_profile_export(project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    personal = load_yaml(project_root / "content" / "core" / "personal.yaml")
    summary = load_yaml(project_root / "content" / "core" / "summary.yaml")
    skills = load_yaml(project_root / "content" / "core" / "skills.yaml")
    config = load_yaml(project_root / "config" / "documents.yaml")

    documents = []
    for document in DOCUMENTS:
        pdf_path = project_root / document["path"]
        documents.append(
            {
                **document,
                "publicPath": document["path"],
                "previewPath": document["preview"],
                "pages": pdf_page_count(pdf_path),
                "exists": pdf_path.exists(),
            }
        )

    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "source": {
            "repository": "https://github.com/Brandon-Gottshall/About-Me",
            "contentRoot": "content",
            "configRoot": "config",
        },
        "profile": {
            "name": f"{personal['name']['first']} {personal['name']['last']}",
            "position": clean_portfolio_text(personal["position"]),
            "summary": clean_portfolio_text(summary),
            "contact": {
                "homepage": personal["contact"]["homepage"],
                "github": personal["contact"]["github"],
                "linkedin": personal["contact"]["linkedin"],
            },
            "skills": {
                "technical": skills.get("technical", []),
                "professional": skills.get("professional", []),
            },
        },
        "documents": documents,
        "documentConfig": {
            key: value.get("sections", [])
            for key, value in config.items()
            if isinstance(value, dict) and "sections" in value
        },
    }


def write_export(project_root: Path = PROJECT_ROOT) -> Path:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    export_path = EXPORT_DIR / "profile.json"
    payload = build_profile_export(project_root)
    with export_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    return export_path


def main() -> None:
    export_path = write_export()
    print(f"Exported portfolio data: {export_path}")


if __name__ == "__main__":
    main()
