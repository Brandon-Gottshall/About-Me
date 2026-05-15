"""HTML formatting helpers for the document pipeline.

These mirror the LaTeX helpers in `document_pipeline.latex`, but emit
plain text suitable for HTML escaping. Source YAML occasionally carries
LaTeX artefacts (``\\&``, ``\\textbullet{}``, ``~`` non-breaking spaces);
those are normalised back to plain text before HTML escaping so the
published HTML never leaks LaTeX commands.
"""

from __future__ import annotations

import html
import re
from typing import Any


_LATEX_INLINE_COMMANDS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\\textbullet\{\}"), "•"),
    (re.compile(r"\\textemdash\{\}"), "—"),
    (re.compile(r"\\textendash\{\}"), "–"),
    (re.compile(r"\\textasciitilde\{\}"), "~"),
    (re.compile(r"\\textasciicircum\{\}"), "^"),
    (re.compile(r"\\ldots\{\}|\\ldots"), "…"),
    (re.compile(r"\\letterskip\b"), "\n\n"),
)


def normalize_latex_text(value: Any) -> str:
    """Convert YAML text that may contain LaTeX artefacts into plain text.

    The result is *not* HTML escaped; pass it through ``html_escape_text``
    for direct use in markup.
    """

    if value is None:
        return ""
    text = str(value)

    for pattern, replacement in _LATEX_INLINE_COMMANDS:
        text = pattern.sub(replacement, text)

    # Unwrap explicit escapes (`\&`, `\%`, `\$`, `\#`, `\_`, `\{`, `\}`).
    text = re.sub(r"\\([&%$#_{}])", r"\1", text)

    # `~` is LaTeX's non-breaking space; map to U+00A0 so tokens like
    # "Marine Corps" stay together without re-introducing tildes.
    text = text.replace("~", " ")

    return text


def html_escape_text(value: Any) -> str:
    """Normalise LaTeX-flavoured input and escape it for HTML use."""

    return html.escape(normalize_latex_text(value), quote=True)


def format_date_range(start_date: Any, end_date: Any) -> str:
    start = normalize_latex_text(start_date).strip()
    end = normalize_latex_text(end_date).strip()
    if start and end:
        return f"{start} – {end}"
    return start or end


def entry_date(entry: dict[str, Any]) -> str:
    if entry.get("date_range"):
        return normalize_latex_text(entry["date_range"]).strip()
    return format_date_range(entry.get("start_date", ""), entry.get("end_date", ""))


def skill_items_text(items: Any) -> str:
    if items is None:
        return ""
    if isinstance(items, (list, tuple)):
        return ", ".join(
            normalize_latex_text(item).strip()
            for item in items
            if item not in (None, "")
        )
    return normalize_latex_text(items).strip()
