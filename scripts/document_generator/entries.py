"""Resume and CV entry formatting."""

from dataclasses import dataclass

from .text import escape_html, escape_latex, format_date_range


@dataclass(frozen=True)
class EntryFields:
    first: str
    second: str
    location: str
    date: str
    first_comment: str
    second_comment: str
    location_comment: str = "Location"
    date_comment: str = "Date(s)"
    indent: str = "  "


LATEX_ENTRY_FIELDS = {
    "experience": EntryFields(
        "title",
        "organization",
        "location",
        "range",
        "Job title",
        "Organization",
    ),
    "education": EntryFields(
        "degree",
        "institution",
        "location",
        "range",
        "Degree",
        "Institution",
    ),
    "certification": EntryFields(
        "name",
        "organization",
        "location",
        "range",
        "Certification",
        "Organization",
        indent="    ",
    ),
    "project": EntryFields(
        "name",
        "technologies",
        "date",
        "location",
        "Project name",
        "Technologies used",
        "Date(s)",
        "Location",
    ),
    "presentation": EntryFields(
        "role",
        "event",
        "location",
        "date",
        "Role",
        "Event",
    ),
    "teaching": EntryFields(
        "role",
        "institution",
        "location",
        "date",
        "Role",
        "Institution",
        indent="    ",
    ),
    "volunteer": EntryFields(
        "position",
        "organization",
        "location",
        "date_range",
        "Position",
        "Organization",
        indent="    ",
    ),
}

HTML_ENTRY_FIELDS = {
    "experience": EntryFields(
        "title",
        "organization",
        "location",
        "range",
        "Title",
        "Organization",
    ),
    "education": EntryFields(
        "degree",
        "institution",
        "location",
        "range",
        "Degree",
        "Institution",
    ),
    "certification": EntryFields(
        "name",
        "organization",
        "location",
        "range",
        "Certification",
        "Organization",
    ),
    "project": EntryFields(
        "name",
        "technologies",
        "location",
        "date",
        "Project",
        "Technologies",
    ),
    "presentation": EntryFields(
        "role",
        "event",
        "location",
        "date",
        "Role",
        "Event",
    ),
    "teaching": EntryFields(
        "role",
        "institution",
        "location",
        "date",
        "Role",
        "Institution",
    ),
    "volunteer": EntryFields(
        "position",
        "organization",
        "location",
        "date_range",
        "Position",
        "Organization",
    ),
}

COMMENT_RULE = "%" + "-" * 79


def _entry_date(entry, date_key, escape):
    if date_key == "range":
        if entry.get("date_range"):
            return escape(entry["date_range"])
        return format_date_range(
            escape(entry.get("start_date", "")),
            escape(entry.get("end_date", "")),
        )
    return escape(entry.get(date_key, ""))


def _latex_item_block(items):
    if not items:
        return "{}"

    lines = ["{", "      \\begin{cvitems}"]
    for item in items:
        lines.append(f"        \\item {{{escape_latex(item)}}}")
    lines.extend(["      \\end{cvitems}", "    }"])
    return "\n".join(lines)


def format_cventry(entry, entry_type="experience"):
    """Format one entry for an Awesome-CV LaTeX section."""
    fields = LATEX_ENTRY_FIELDS.get(entry_type)
    if not fields:
        return ""

    first = escape_latex(entry.get(fields.first, ""))
    second = escape_latex(entry.get(fields.second, ""))
    location = escape_latex(entry.get(fields.location, ""))
    date = _entry_date(entry, fields.date, escape_latex)
    item_block = _latex_item_block(entry.get("items", []))

    return f"""%---------------------------------------------------------
{fields.indent}\\cventry
    {{{first}}} % {fields.first_comment}
    {{{second}}} % {fields.second_comment}
    {{{location}}} % {fields.location_comment}
    {{{date}}} % {fields.date_comment}
    {item_block}"""


def format_cvskill(category, items):
    """Format one skill row for LaTeX."""
    category_escaped = escape_latex(category)
    if isinstance(items, (list, tuple)):
        item_text = "; ".join(escape_latex(item) for item in items if item)
        items_escaped = "\\textemdash{} " + item_text if item_text else ""
    else:
        items_escaped = escape_latex(items)

    return f"""%---------------------------------------------------------
  \\cvskill
    {{{category_escaped}}} % Category
    {{{items_escaped}}} % Skills"""


def format_language(language, proficiency):
    """Format one language row for LaTeX."""
    return f"""    \\cvskill
    {{{escape_latex(language)}}} % Language
    {{{escape_latex(proficiency)}}} % Proficiency level"""


def format_leadership_entries(leadership_data):
    """Format leadership entries with category comments."""
    entries = []
    for category in leadership_data.get("categories", []):
        category_name = category.get("name", "")
        entries.append(COMMENT_RULE)
        entries.append(f"%\t{category_name}")
        entries.append(COMMENT_RULE)
        for entry in category.get("entries", []):
            entries.append(format_cventry(entry, "experience"))
    return "\n".join(entries)


def _html_items(items):
    if not items:
        return ""

    lines = ['<ul class="cvitems">']
    for item in items:
        lines.append(f"      <li>{escape_html(item)}</li>")
    lines.append("    </ul>")
    return "\n".join(lines)


def format_cventry_html(entry, entry_type="experience"):
    """Format one entry for an HTML section."""
    fields = HTML_ENTRY_FIELDS.get(entry_type)
    if not fields:
        return ""

    first = escape_html(entry.get(fields.first, ""))
    second = escape_html(entry.get(fields.second, ""))
    location = escape_html(entry.get(fields.location, ""))
    date = _entry_date(entry, fields.date, escape_html)
    items_html = _html_items(entry.get("items", []))

    return f"""    <div class="cventry">
      <div class="cventry-header">
        <span class="cventry-title">{first}</span>
        <span class="cventry-org">{second}</span>
      </div>
      <div class="cventry-meta">
        <span class="cventry-location">{location}</span>
        <span class="cventry-date">{date}</span>
      </div>
{items_html}
    </div>"""


def format_cvskill_html(category, items):
    """Format one skill row for HTML."""
    category_escaped = escape_html(category)
    if isinstance(items, (list, tuple)):
        items_escaped = ", ".join(escape_html(item) for item in items if item)
    else:
        items_escaped = escape_html(items)

    return f"""    <div class="cvskill">
      <span class="cvskill-category">{category_escaped}</span>
      <span class="cvskill-items">{items_escaped}</span>
    </div>"""


def format_language_html(language, proficiency):
    """Format one language row for HTML."""
    return f"""    <div class="cvskill">
      <span class="cvskill-category">{escape_html(language)}</span>
      <span class="cvskill-items">{escape_html(proficiency)}</span>
    </div>"""
