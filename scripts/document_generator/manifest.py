"""Public document manifest generation."""

import json
from datetime import datetime, timezone
from pathlib import Path


PUBLIC_DOCUMENTS = [
    {
        "type": "resume",
        "title": "Resume",
        "summary": "Concise professional resume for software engineering roles.",
        "pdf": "resume.pdf",
        "html": "resume.html",
    },
    {
        "type": "cv",
        "title": "CV",
        "summary": "Expanded curriculum vitae with education and credentials.",
        "pdf": "cv.pdf",
        "html": "cv.html",
    },
]


def current_utc_timestamp():
    """Return an ISO-8601 timestamp for generated artifacts."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def document_manifest(generated_at=None):
    """Return the public document manifest payload."""
    return {
        "version": 1,
        "generatedAt": generated_at or current_utc_timestamp(),
        "documents": PUBLIC_DOCUMENTS,
    }


def write_document_manifest(output_dir, generated_at=None):
    """Write the public document manifest into the output directory."""
    output_path = Path(output_dir) / "documents.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(document_manifest(generated_at), indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Generated: {output_path}")
    return output_path
