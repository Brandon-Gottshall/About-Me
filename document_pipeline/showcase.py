"""Render first-page PDF preview images for showcase and portfolio use."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from document_pipeline.export import DOCUMENTS, PROJECT_ROOT


def render_previews(project_root: Path = PROJECT_ROOT) -> list[Path]:
    if not shutil.which("pdftoppm"):
        raise RuntimeError("pdftoppm is required to render showcase previews.")

    rendered: list[Path] = []
    for document in DOCUMENTS:
        pdf_path = project_root / document["path"]
        preview_path = project_root / document["preview"]
        preview_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_prefix = preview_path.with_suffix("")
        subprocess.run(
            [
                "pdftoppm",
                "-png",
                "-f",
                "1",
                "-l",
                "1",
                str(pdf_path),
                str(tmp_prefix),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        generated = tmp_prefix.with_name(f"{tmp_prefix.name}-1").with_suffix(".png")
        generated.replace(preview_path)
        rendered.append(preview_path)
    return rendered


def main() -> None:
    try:
        rendered = render_previews()
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
    for path in rendered:
        print(f"Rendered preview: {path}")


if __name__ == "__main__":
    main()
