"""Small text helpers shared by LaTeX and HTML output."""

import html as html_lib
import re


def format_date_range(start_date, end_date):
    """Return a clean date range string without extra separators."""
    if start_date and end_date:
        return f"{start_date} - {end_date}"
    if start_date:
        return start_date
    if end_date:
        return end_date
    return ""


def escape_latex(text):
    """Escape LaTeX special characters while preserving LaTeX commands."""
    if not text:
        return ""

    text = str(text)
    commands = []

    def find_matching_brace(source, opening_position):
        depth = 0
        for position in range(opening_position, len(source)):
            if source[position] == "{":
                depth += 1
            elif source[position] == "}":
                depth -= 1
                if depth == 0:
                    return position
        return -1

    protected_parts = []
    position = 0
    while position < len(text):
        command_match = re.search(r"\\([a-zA-Z]+)\{", text[position:])
        if not command_match:
            protected_parts.append(text[position:])
            break

        command_start = position + command_match.start()
        brace_start = command_start + len(command_match.group(0)) - 1

        protected_parts.append(text[position:command_start])
        brace_end = find_matching_brace(text, brace_start)

        if brace_end == -1:
            protected_parts.append(text[command_start:])
            break

        marker = f"LATEXCMDX{len(commands)}X"
        commands.append(text[command_start : brace_end + 1])
        protected_parts.append(marker)
        position = brace_end + 1

    escaped = "".join(protected_parts)
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

    for character, replacement in replacements.items():
        escaped = escaped.replace(character, replacement)

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
    protected_escapes = []
    for index, sequence in enumerate(escape_sequences):
        marker = f"ESCAPESEQX{index}X"
        protected_escapes.append((marker, sequence))
        escaped = escaped.replace(sequence, marker)

    escaped = escaped.replace("\\", r"\textbackslash{}")

    for marker, sequence in protected_escapes:
        escaped = escaped.replace(marker, sequence)

    for index, command in enumerate(commands):
        escaped = escaped.replace(f"LATEXCMDX{index}X", command)

    return escaped


def format_inline_html(text):
    """Convert supported LaTeX inline commands to safe HTML."""
    if not text:
        return ""

    result = str(text)
    entity_markers = {
        r"\textbullet{}": "HTMLENTITYBULLET",
        r"\textbullet": "HTMLENTITYBULLET",
        r"\textemdash{}": "HTMLENTITYMDASH",
        r"\textemdash": "HTMLENTITYMDASH",
    }

    for latex_command, marker in entity_markers.items():
        result = result.replace(latex_command, marker)

    result = result.replace(r"\&", "&")
    result = re.sub(r"\\textbf\{([^{}]+)\}", r"<strong>\1</strong>", result)
    result = html_lib.escape(result)
    result = result.replace("HTMLENTITYBULLET", "&bull;")
    result = result.replace("HTMLENTITYMDASH", "&mdash;")
    result = result.replace("&lt;strong&gt;", "<strong>")
    result = result.replace("&lt;/strong&gt;", "</strong>")
    return result


def escape_html(text):
    """Escape text for HTML output."""
    return format_inline_html(text)


def prepare_personal_html(personal):
    """Escape personal metadata before passing it into HTML templates."""
    return {
        "name": {
            key: format_inline_html(value)
            for key, value in personal.get("name", {}).items()
        },
        "position": {
            key: format_inline_html(value)
            for key, value in personal.get("position", {}).items()
        },
        "address": format_inline_html(personal.get("address", "")),
        "address_cv": format_inline_html(personal.get("address_cv", "")),
        "contact": {
            key: format_inline_html(value)
            for key, value in personal.get("contact", {}).items()
        },
        "contact_line": {
            key: format_inline_html(value)
            for key, value in personal.get("contact_line", {}).items()
        },
        "quote": {
            key: format_inline_html(value)
            for key, value in personal.get("quote", {}).items()
        },
    }
