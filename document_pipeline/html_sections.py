"""HTML section renderers for resume, CV, and leadership-resume documents.

Each function here mirrors a branch of :mod:`document_pipeline.sections`
but emits semantic HTML instead of LaTeX. The result of
:func:`generate_html_sections` is a list of HTML strings — one per
configured section — that the renderer drops inside the document
``<main>`` element.
"""

from __future__ import annotations

from typing import Any, Iterable

from document_pipeline.html import (
    entry_date,
    format_date_range,
    html_escape_text,
    normalize_latex_text,
    skill_items_text,
)
from document_pipeline.models import ProjectData


SECTION_TITLES = {
    "summary": "Summary",
    "leadership_profile": "Leadership Profile",
    "experience": "Experience",
    "education": "Education",
    "skills": "Skills",
    "certifications": "Certifications",
    "projects": "Projects",
    "publications": "Publications",
    "presentations": "Presentations",
    "teaching": "Teaching",
    "volunteer": "Volunteer",
    "languages": "Languages",
    "references": "References",
    "leadership": "Leadership",
}


def _section(slug: str, title: str, body: str) -> str:
    return (
        f'    <section class="rg-section rg-section--{slug}" '
        f'aria-labelledby="section-{slug}-title">\n'
        f'      <h2 id="section-{slug}-title">{html_escape_text(title)}</h2>\n'
        f"{body}\n"
        f"    </section>"
    )


def _paragraph_block(text: Any) -> str:
    paragraphs = [p.strip() for p in normalize_latex_text(text).split("\n\n") if p.strip()]
    if not paragraphs:
        return '      <p class="rg-empty">No content available.</p>'
    return "\n".join(
        f'      <p>{html_escape_text(paragraph)}</p>' for paragraph in paragraphs
    )


def _format_entry(entry: dict[str, Any], entry_type: str) -> str:
    headline_field, org_field = _entry_headline_fields(entry_type)
    headline = html_escape_text(entry.get(headline_field, ""))
    organization = html_escape_text(entry.get(org_field, ""))
    location = html_escape_text(entry.get("location", ""))

    if entry_type in {"project", "presentation", "teaching"} and entry.get("date"):
        date_text = normalize_latex_text(entry.get("date", "")).strip()
    elif entry_type == "volunteer" and entry.get("date_range"):
        date_text = normalize_latex_text(entry.get("date_range", "")).strip()
    else:
        date_text = entry_date(entry)
    date_text = html_escape_text(date_text)

    meta_parts: list[str] = []
    if location:
        meta_parts.append(f'<span class="rg-entry__location">{location}</span>')
    if date_text:
        meta_parts.append(f'<time class="rg-entry__date">{date_text}</time>')
    meta_html = (
        "        <p class=\"rg-entry__meta\">"
        + " <span aria-hidden=\"true\">·</span> ".join(meta_parts)
        + "</p>\n"
        if meta_parts
        else ""
    )

    items = entry.get("items") or []
    items_html = ""
    if items:
        items_html = (
            "        <ul class=\"rg-entry__items\">\n"
            + "\n".join(
                f"          <li>{html_escape_text(item)}</li>" for item in items
            )
            + "\n        </ul>\n"
        )

    organization_html = (
        f'        <p class="rg-entry__organization">{organization}</p>\n'
        if organization
        else ""
    )

    return (
        '      <article class="rg-entry">\n'
        '        <header class="rg-entry__header">\n'
        f'          <h3 class="rg-entry__headline">{headline}</h3>\n'
        f"{organization_html}{meta_html.rstrip()}\n"
        "        </header>\n"
        f"{items_html}"
        "      </article>"
    )


def _entry_headline_fields(entry_type: str) -> tuple[str, str]:
    by_type = {
        "experience": ("title", "organization"),
        "education": ("degree", "institution"),
        "certification": ("name", "organization"),
        "project": ("name", "technologies"),
        "presentation": ("role", "event"),
        "teaching": ("role", "institution"),
        "volunteer": ("position", "organization"),
    }
    return by_type[entry_type]


def _render_entry_list(entries: Iterable[dict[str, Any]], entry_type: str) -> str:
    rendered = [_format_entry(entry, entry_type) for entry in entries]
    return "\n".join(rendered) if rendered else '      <p class="rg-empty">No entries.</p>'


def _render_summary(data: ProjectData, doc_type: str) -> str:
    summary_data = data.core["summary"]
    if doc_type == "leadership_resume":
        text = summary_data.get("leadership_resume") or summary_data["text"]
        body = _paragraph_block(text)
        return _section("summary", SECTION_TITLES["leadership_profile"], body)
    return _section("summary", SECTION_TITLES["summary"], _paragraph_block(summary_data["text"]))


def _render_experience(data: ProjectData) -> str:
    entries = data.core["experience"].get("entries", [])
    body = _render_entry_list(entries, "experience")
    return _section("experience", SECTION_TITLES["experience"], body)


def _render_education(data: ProjectData) -> str:
    entries = data.core["education"].get("entries", [])
    body = _render_entry_list(entries, "education")
    return _section("education", SECTION_TITLES["education"], body)


def _render_skill_table(rows: Iterable[dict[str, Any]], heading: str | None) -> str:
    rendered_rows: list[str] = []
    for row in rows:
        category = html_escape_text(row.get("category", ""))
        items_text = html_escape_text(skill_items_text(row.get("items")))
        rendered_rows.append(
            '        <li class="rg-skill">\n'
            f'          <span class="rg-skill__category">{category}</span>\n'
            f'          <span class="rg-skill__items">{items_text}</span>\n'
            "        </li>"
        )
    body_rows = "\n".join(rendered_rows) if rendered_rows else '        <li class="rg-empty">No skills listed.</li>'
    heading_html = (
        f'      <h3 class="rg-skill-group__heading">{html_escape_text(heading)}</h3>\n'
        if heading
        else ""
    )
    return (
        '      <div class="rg-skill-group">\n'
        f"{heading_html}"
        '        <ul class="rg-skill-list">\n'
        f"{body_rows}\n"
        "        </ul>\n"
        "      </div>"
    )


def _render_skills(data: ProjectData, doc_type: str) -> str:
    skills_data = data.core["skills"]
    if doc_type == "leadership_resume" and skills_data.get("leadership_resume"):
        leadership = skills_data["leadership_resume"]
        strengths = leadership.get("strengths", [])
        certifications = leadership.get("certifications", [])
        body_parts = [
            _render_skill_table(strengths, "Strengths"),
            _render_skill_table(certifications, "Certifications"),
        ]
        return _section("skills", SECTION_TITLES["skills"], "\n".join(body_parts))

    technical = skills_data.get("technical", [])
    professional = skills_data.get("professional", [])
    body_parts = [_render_skill_table(technical, "Technical")]
    if professional:
        body_parts.append(_render_skill_table(professional, "Professional"))
    return _section("skills", SECTION_TITLES["skills"], "\n".join(body_parts))


def _render_optional_entries(
    data: ProjectData, key: str, entry_type: str, slug: str
) -> str:
    entries = data.optional_content(key, {"entries": []}).get("entries", [])
    body = _render_entry_list(entries, entry_type)
    return _section(slug, SECTION_TITLES[slug], body)


def _render_certifications(data: ProjectData) -> str:
    return _render_optional_entries(data, "certifications", "certification", "certifications")


def _render_languages(data: ProjectData) -> str:
    entries = data.optional_content("languages", {"entries": []}).get("entries", [])
    if not entries:
        body = '      <p class="rg-empty">No languages listed.</p>'
    else:
        items: list[str] = []
        for entry in entries:
            language = html_escape_text(entry.get("language", ""))
            proficiency = html_escape_text(entry.get("proficiency", ""))
            items.append(
                '        <li class="rg-language">\n'
                f'          <span class="rg-language__name">{language}</span>\n'
                f'          <span class="rg-language__level">{proficiency}</span>\n'
                "        </li>"
            )
        body = (
            '      <ul class="rg-language-list">\n'
            + "\n".join(items)
            + "\n      </ul>"
        )
    return _section("languages", SECTION_TITLES["languages"], body)


def _render_references(_: ProjectData) -> str:
    body = (
        '      <p class="rg-references">References available upon request.</p>'
    )
    return _section("references", SECTION_TITLES["references"], body)


def _render_leadership(data: ProjectData) -> str:
    leadership_data = data.optional_content("leadership", {"categories": []})
    categories = leadership_data.get("categories", [])
    if not categories:
        body = '      <p class="rg-empty">No leadership entries.</p>'
    else:
        rendered_categories: list[str] = []
        for category in categories:
            name = html_escape_text(category.get("name", ""))
            entries_html = _render_entry_list(category.get("entries", []), "experience")
            rendered_categories.append(
                '      <div class="rg-leadership-group">\n'
                f'        <h3 class="rg-leadership-group__heading">{name}</h3>\n'
                f"{entries_html}\n"
                "      </div>"
            )
        body = "\n".join(rendered_categories)
    return _section("leadership", SECTION_TITLES["leadership"], body)


SECTION_RENDERERS = {
    "summary": _render_summary,
    "experience": lambda data, doc_type: _render_experience(data),
    "education": lambda data, doc_type: _render_education(data),
    "skills": _render_skills,
    "certifications": lambda data, doc_type: _render_certifications(data),
    "languages": lambda data, doc_type: _render_languages(data),
    "references": lambda data, doc_type: _render_references(data),
    "leadership": lambda data, doc_type: _render_leadership(data),
    "projects": lambda data, doc_type: _render_optional_entries(
        data, "projects", "project", "projects"
    ),
    "publications": lambda data, doc_type: _render_optional_entries(
        data, "publications", "experience", "publications"
    ),
    "presentations": lambda data, doc_type: _render_optional_entries(
        data, "presentations", "presentation", "presentations"
    ),
    "teaching": lambda data, doc_type: _render_optional_entries(
        data, "teaching", "teaching", "teaching"
    ),
    "volunteer": lambda data, doc_type: _render_optional_entries(
        data, "volunteer", "volunteer", "volunteer"
    ),
}


def generate_html_sections(data: ProjectData, doc_type: str) -> str:
    """Render every configured section for ``doc_type`` as HTML."""

    section_names = data.document(doc_type).sections
    rendered: list[str] = []
    for name in section_names:
        renderer = SECTION_RENDERERS.get(name)
        if renderer is None:
            continue
        rendered.append(renderer(data, doc_type))
    return "\n".join(rendered)
