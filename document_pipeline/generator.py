"""Compatibility module for generating LaTeX documents.

The implementation lives in smaller modules:
- `models` loads typed project data
- `sections` renders configured document sections
- `renderer` renders full LaTeX documents
- `latex` owns escaping and formatting helpers
"""

from __future__ import annotations

import sys

from document_pipeline.latex import (
    escape_latex,
    format_cover_letter_body,
    format_cventry,
    format_cvskill,
    format_date_range,
    format_language,
    format_leadership_entries,
)
from document_pipeline.renderer import generate_documents

__all__ = [
    "escape_latex",
    "format_cover_letter_body",
    "format_cventry",
    "format_cvskill",
    "format_date_range",
    "format_language",
    "format_leadership_entries",
    "generate_documents",
    "main",
]


def main(argv: list[str] | None = None) -> None:
    generate_documents(requested=argv if argv is not None else sys.argv[1:])


if __name__ == "__main__":
    main()
