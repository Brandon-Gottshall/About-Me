"""Section rendering for resume and CV style documents."""

from __future__ import annotations

from typing import Any

from document_pipeline.io import latex_environment
from document_pipeline.latex import (
    escape_latex,
    format_cventry,
    format_cvskill,
    format_language,
    format_leadership_entries,
)
from document_pipeline.models import ProjectData


def render_leadership_profile(summary_data: dict[str, Any]) -> str:
    summary_text = summary_data.get("leadership_resume") or summary_data["text"]
    return f"""%-------------------------------------------------------------------------------
%	SECTION TITLE
%-------------------------------------------------------------------------------
\\cvsection{{Leadership Profile}}


%-------------------------------------------------------------------------------
%	CONTENT
%-------------------------------------------------------------------------------
\\begin{{cvparagraph}}
{escape_latex(summary_text)}
\\end{{cvparagraph}}
"""


def render_skills_section(data: ProjectData, doc_type: str, env) -> str:
    skills_data = data.core["skills"]
    if doc_type == "leadership_resume" and skills_data.get("leadership_resume"):
        template = env.get_template("skills_leadership.tex")
        leadership_skills = skills_data["leadership_resume"]
        strengths = []
        for strength in leadership_skills.get("strengths", []):
            items = strength.get("items", [])
            if isinstance(items, (list, tuple)):
                items_text = ", ".join(escape_latex(item) for item in items if item)
            else:
                items_text = escape_latex(items)
            strengths.append(
                {
                    "category": escape_latex(strength.get("category", "")),
                    "items_text": items_text,
                }
            )
        certification_entries = "\n".join(
            format_cvskill(cert["category"], cert["items"])
            for cert in leadership_skills.get("certifications", [])
        )
        return template.render(
            strengths=strengths,
            certification_entries=certification_entries,
        )

    template = env.get_template("skills.tex")
    technical_skills = "\n".join(
        format_cvskill(skill["category"], skill["items"])
        for skill in skills_data["technical"]
    )
    professional_skills = ""
    if skills_data.get("professional"):
        professional_skills = "\n".join(
            format_cvskill(skill["category"], skill["items"])
            for skill in skills_data["professional"]
        )
    return template.render(
        technical_skills=technical_skills,
        professional_skills=professional_skills,
    )


def render_optional_entries(
    data: ProjectData,
    env,
    section_name: str,
    template_name: str,
    entry_type: str,
    template_var: str,
    empty_comment: str,
) -> str:
    template = env.get_template(template_name)
    entries_list = data.optional_content(section_name, {"entries": []}).get("entries", [])
    if entries_list:
        entries = "\n".join(format_cventry(entry, entry_type) for entry in entries_list)
    else:
        entries = empty_comment
    return template.render(**{template_var: entries})


def generate_sections(data: ProjectData, doc_type: str) -> str:
    """Generate LaTeX sections based on document configuration."""
    env = latex_environment(data.paths.section_templates_dir)
    sections: list[str] = []
    section_order = data.document(doc_type).sections

    for section_name in section_order:
        if section_name == "summary":
            if doc_type == "leadership_resume":
                sections.append(render_leadership_profile(data.core["summary"]))
            else:
                template = env.get_template("summary.tex")
                summary_data = data.core["summary"]
                summary_text = summary_data.get(doc_type) or summary_data["text"]
                sections.append(
                    template.render(summary_text=escape_latex(summary_text))
                )

        elif section_name == "experience":
            template = env.get_template("experience.tex")
            entries = "\n".join(
                format_cventry(entry, "experience")
                for entry in data.core["experience"]["entries"]
            )
            sections.append(template.render(experience_entries=entries))

        elif section_name == "education":
            template = env.get_template("education.tex")
            entries = "\n".join(
                format_cventry(entry, "education")
                for entry in data.core["education"]["entries"]
            )
            sections.append(template.render(education_entries=entries))

        elif section_name == "skills":
            sections.append(render_skills_section(data, doc_type, env))

        elif section_name == "certifications":
            template = env.get_template("certifications.tex")
            entries = "\n".join(
                format_cventry(entry, "certification")
                for entry in data.optional_content("certifications", {"entries": []})[
                    "entries"
                ]
            )
            sections.append(template.render(certification_entries=entries))

        elif section_name == "projects":
            sections.append(
                render_optional_entries(
                    data,
                    env,
                    "projects",
                    "projects.tex",
                    "project",
                    "project_entries",
                    "% No projects entries found. Add entries to content/optional/projects.yaml",
                )
            )

        elif section_name == "publications":
            template = env.get_template("publications.tex")
            publications_data = data.optional_content("publications", {})
            sections.append(
                template.render(
                    journal_articles=publications_data.get("journal_articles", []),
                    conference_proceedings=publications_data.get(
                        "conference_proceedings", []
                    ),
                    preprints=publications_data.get("preprints", []),
                )
            )

        elif section_name == "presentations":
            sections.append(
                render_optional_entries(
                    data,
                    env,
                    "presentations",
                    "presentations.tex",
                    "presentation",
                    "presentation_entries",
                    "% No presentations entries found. Add entries to content/optional/presentations.yaml",
                )
            )

        elif section_name == "teaching":
            sections.append(
                render_optional_entries(
                    data,
                    env,
                    "teaching",
                    "teaching.tex",
                    "teaching",
                    "teaching_entries",
                    "% No teaching entries found. Add entries to content/optional/teaching.yaml",
                )
            )

        elif section_name == "volunteer":
            sections.append(
                render_optional_entries(
                    data,
                    env,
                    "volunteer",
                    "volunteer.tex",
                    "volunteer",
                    "volunteer_entries",
                    "% No volunteer entries found. Add entries to content/optional/volunteer.yaml",
                )
            )

        elif section_name == "languages":
            template = env.get_template("languages.tex")
            entries = "\n".join(
                format_language(entry["language"], entry["proficiency"])
                for entry in data.optional_content("languages", {"entries": []})[
                    "entries"
                ]
            )
            sections.append(template.render(language_entries=entries))

        elif section_name == "references":
            sections.append(env.get_template("references.tex").render())

        elif section_name == "leadership":
            template = env.get_template("leadership.tex")
            leadership_data = data.optional_content("leadership", {"categories": []})
            sections.append(
                template.render(
                    leadership_entries=format_leadership_entries(leadership_data)
                )
            )

    return "\n".join(sections)
