"""LaTeX formatting helpers for Brandon's document templates."""

from __future__ import annotations

import re
from typing import Any


def escape_latex(text: Any) -> str:
    """Escape special LaTeX characters while preserving explicit commands."""
    if not text:
        return ""

    text = str(text)
    latex_commands: list[str] = []

    def match_balanced_braces(source: str, start_pos: int) -> int:
        depth = 0
        pos = start_pos
        while pos < len(source):
            if source[pos] == "{":
                depth += 1
            elif source[pos] == "}":
                depth -= 1
                if depth == 0:
                    return pos
            pos += 1
        return -1

    result_parts: list[str] = []
    pos = 0
    while pos < len(text):
        command_match = re.search(r"\\([a-zA-Z]+)\{", text[pos:])
        if not command_match:
            result_parts.append(text[pos:])
            break

        command_start = pos + command_match.start()
        brace_start = command_start + len(command_match.group(0)) - 1
        result_parts.append(text[pos:command_start])

        brace_end = match_balanced_braces(text, brace_start)
        if brace_end != -1:
            marker = f"LATEXCMDX{len(latex_commands)}X"
            latex_commands.append(text[command_start : brace_end + 1])
            result_parts.append(marker)
            pos = brace_end + 1
        else:
            result_parts.append(text[command_start:])
            break

    result = "".join(result_parts)
    replacements = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "^": r"\textasciicircum{}",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
    }
    for char, replacement in replacements.items():
        result = result.replace(char, replacement)

    escape_sequences = [
        r"\&",
        r"\%",
        r"\$",
        r"\#",
        r"\_",
        r"\{",
        r"\}",
        r"\textasciicircum{}",
        r"\textasciitilde{}",
    ]
    protected_escapes: list[tuple[str, str]] = []
    for index, sequence in enumerate(escape_sequences):
        marker = f"ESCAPESEQX{index}X"
        protected_escapes.append((marker, sequence))
        result = result.replace(sequence, marker)

    result = result.replace("\\", r"\textbackslash{}")

    for marker, sequence in protected_escapes:
        result = result.replace(marker, sequence)
    for index, command in enumerate(latex_commands):
        result = result.replace(f"LATEXCMDX{index}X", command)

    return result


def format_date_range(start_date: str, end_date: str) -> str:
    if start_date and end_date:
        return f"{start_date} - {end_date}"
    if start_date:
        return start_date
    if end_date:
        return end_date
    return ""


def entry_date(entry: dict[str, Any]) -> str:
    if entry.get("date_range"):
        return escape_latex(entry["date_range"])
    return format_date_range(
        escape_latex(entry.get("start_date", "")),
        escape_latex(entry.get("end_date", "")),
    )


def cvitems(items: list[str] | None) -> str:
    if not items:
        return "{}"
    body = "{\n      \\begin{cvitems}\n"
    for item in items:
        body += f"        \\item {{{escape_latex(item)}}}\n"
    body += "      \\end{cvitems}\n    }"
    return body


def format_cventry(entry: dict[str, Any], entry_type: str = "experience") -> str:
    fields_by_type = {
        "experience": ("title", "organization", "location", "__date_range__"),
        "education": ("degree", "institution", "location", "__date_range__"),
        "certification": ("name", "organization", "location", "__date_range__"),
        "project": ("name", "technologies", "date", "location"),
        "presentation": ("role", "event", "location", "date"),
        "teaching": ("role", "institution", "location", "date"),
        "volunteer": ("position", "organization", "location", "date_range"),
    }
    comment_labels = {
        "experience": ("Job title", "Organization", "Location", "Date(s)"),
        "education": ("Degree", "Institution", "Location", "Date(s)"),
        "certification": ("Certification", "Organization", "Location", "Date(s)"),
        "project": ("Project name", "Technologies used", "Date(s)", "Location"),
        "presentation": ("Role", "Event", "Location", "Date(s)"),
        "teaching": ("Role", "Institution", "Location", "Date(s)"),
        "volunteer": ("Position", "Organization", "Location", "Date(s)"),
    }
    if entry_type not in fields_by_type:
        return ""

    values = []
    for field in fields_by_type[entry_type]:
        if field == "__date_range__":
            values.append(entry_date(entry))
        elif field == "date_range":
            values.append(escape_latex(entry.get("date_range", "")))
        else:
            values.append(escape_latex(entry.get(field, "")))

    indent = "    " if entry_type in {"certification", "project", "teaching", "volunteer"} else "  "
    labels = comment_labels[entry_type]
    return f"""%---------------------------------------------------------
{indent}\\cventry
    {{{values[0]}}} % {labels[0]}
    {{{values[1]}}} % {labels[1]}
    {{{values[2]}}} % {labels[2]}
    {{{values[3]}}} % {labels[3]}
    {cvitems(entry.get("items"))}"""


def format_cvskill(category: str, items: Any) -> str:
    category_escaped = escape_latex(category)
    if isinstance(items, (list, tuple)):
        formatted_items = "; ".join(escape_latex(item) for item in items if item)
        items_escaped = "\\textemdash{} " + formatted_items if formatted_items else ""
    else:
        items_escaped = escape_latex(items)
    return f"""%---------------------------------------------------------
  \\cvskill
    {{{category_escaped}}} % Category
    {{{items_escaped}}} % Skills"""


def format_language(language: str, proficiency: str) -> str:
    return f"""    \\cvskill
    {{{escape_latex(language)}}} % Language
    {{{escape_latex(proficiency)}}} % Proficiency level"""


def format_leadership_entries(leadership_data: dict[str, Any]) -> str:
    entries: list[str] = []
    for category in leadership_data.get("categories", []):
        category_name = category.get("name", "")
        entries.append("%-------------------------------------------------------------------------------")
        entries.append(f"%\t{category_name}")
        entries.append("%-------------------------------------------------------------------------------")
        for entry in category.get("entries", []):
            entries.append(format_cventry(entry, "experience"))
    return "\n".join(entries)


def format_cover_letter_body(
    paragraphs: list[dict[str, Any]], substitutions: dict[str, str] | None = None
) -> str:
    substitutions = substitutions or {}
    formatted_paragraphs = []
    for paragraph in paragraphs:
        text = paragraph.get("text", "")
        for key, value in substitutions.items():
            text = text.replace(f"[{key}]", value)
        formatted_paragraphs.append(escape_latex(text.strip()))
    return "\\letterskip\n\n".join(formatted_paragraphs)
