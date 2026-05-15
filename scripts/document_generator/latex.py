"""LaTeX rendering for resumes, CVs, and cover letters."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from .content import (
    has_entries,
    has_leadership_entries,
    has_publication_entries,
    load_core_content,
    load_optional_content,
    load_yaml,
    project_root_from_content,
)
from .cover_letters import (
    format_cover_letter_body,
    latex_address,
    load_cover_letter_content,
)
from .entries import (
    format_cventry,
    format_cvskill,
    format_language,
    format_leadership_entries,
)
from .text import escape_latex


SECTION_RULE = "%" + "-" * 79


def template_environment(template_dir):
    """Create a Jinja environment that does not conflict with LaTeX braces."""
    return Environment(
        loader=FileSystemLoader(str(template_dir)),
        variable_start_string="<<",
        variable_end_string=">>",
        block_start_string="<@",
        block_end_string="@>",
        comment_start_string="<#",
        comment_end_string="#>",
    )


def render_latex_summary(env, summary_data, doc_type):
    """Render the summary section."""
    if doc_type == "leadership_resume":
        summary_text = (
            summary_data.get("leadership_resume")
            or summary_data["text"]
        )
        return f"""{SECTION_RULE}
%	SECTION TITLE
{SECTION_RULE}
\\cvsection{{Leadership Profile}}


{SECTION_RULE}
%	CONTENT
{SECTION_RULE}
\\begin{{cvparagraph}}
{escape_latex(summary_text)}
\\end{{cvparagraph}}
"""

    template = env.get_template("summary.tex")
    return template.render(summary_text=escape_latex(summary_data["text"]))


def render_latex_skills(env, skills_data, doc_type):
    """Render technical skills or leadership strengths."""
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


def generate_sections(content_core_dir, content_optional_dir, config, doc_type):
    """Generate LaTeX sections for one document."""
    core = load_core_content(Path(content_core_dir))
    optional = load_optional_content(Path(content_optional_dir))
    section_order = config[doc_type]["sections"]

    template_dir = (
        project_root_from_content(content_core_dir)
        / "templates"
        / "sections"
    )
    env = template_environment(template_dir)

    sections = []
    for section_name in section_order:
        if section_name == "summary":
            sections.append(render_latex_summary(env, core["summary"], doc_type))

        elif section_name == "experience":
            template = env.get_template("experience.tex")
            entries = "\n".join(
                format_cventry(entry, "experience")
                for entry in core["experience"]["entries"]
            )
            sections.append(template.render(experience_entries=entries))

        elif section_name == "education":
            template = env.get_template("education.tex")
            entries = "\n".join(
                format_cventry(entry, "education")
                for entry in core["education"]["entries"]
            )
            sections.append(template.render(education_entries=entries))

        elif section_name == "skills":
            sections.append(render_latex_skills(env, core["skills"], doc_type))

        elif section_name == "certifications":
            if not has_entries(optional["certifications"]):
                continue
            template = env.get_template("certifications.tex")
            entries = "\n".join(
                format_cventry(entry, "certification")
                for entry in optional["certifications"]["entries"]
            )
            sections.append(template.render(certification_entries=entries))

        elif section_name == "projects":
            if not has_entries(optional["projects"]):
                continue
            template = env.get_template("projects.tex")
            entries = "\n".join(
                format_cventry(entry, "project")
                for entry in optional["projects"]["entries"]
            )
            sections.append(template.render(project_entries=entries))

        elif section_name == "publications":
            if not has_publication_entries(optional["publications"]):
                continue
            template = env.get_template("publications.tex")
            sections.append(
                template.render(
                    journal_articles=optional["publications"].get(
                        "journal_articles",
                        [],
                    ),
                    conference_proceedings=optional["publications"].get(
                        "conference_proceedings",
                        [],
                    ),
                    preprints=optional["publications"].get("preprints", []),
                )
            )

        elif section_name == "presentations":
            if not has_entries(optional["presentations"]):
                continue
            template = env.get_template("presentations.tex")
            entries = "\n".join(
                format_cventry(entry, "presentation")
                for entry in optional["presentations"]["entries"]
            )
            sections.append(template.render(presentation_entries=entries))

        elif section_name == "teaching":
            if not has_entries(optional["teaching"]):
                continue
            template = env.get_template("teaching.tex")
            entries = "\n".join(
                format_cventry(entry, "teaching")
                for entry in optional["teaching"]["entries"]
            )
            sections.append(template.render(teaching_entries=entries))

        elif section_name == "volunteer":
            if not has_entries(optional["volunteer"]):
                continue
            template = env.get_template("volunteer.tex")
            entries = "\n".join(
                format_cventry(entry, "volunteer")
                for entry in optional["volunteer"]["entries"]
            )
            sections.append(template.render(volunteer_entries=entries))

        elif section_name == "languages":
            if not has_entries(optional["languages"]):
                continue
            template = env.get_template("languages.tex")
            entries = "\n".join(
                format_language(entry["language"], entry["proficiency"])
                for entry in optional["languages"]["entries"]
            )
            sections.append(template.render(language_entries=entries))

        elif section_name == "references":
            sections.append(env.get_template("references.tex").render())

        elif section_name == "leadership":
            if not has_leadership_entries(optional["leadership"]):
                continue
            template = env.get_template("leadership.tex")
            leadership_entries = format_leadership_entries(optional["leadership"])
            sections.append(template.render(leadership_entries=leadership_entries))

    return "\n".join(sections)


def boolean_setting(value):
    """Return the string expected by Awesome-CV boolean settings."""
    return "true" if value else "false"


def common_latex_context(personal, config_doc):
    """Build the template context shared by LaTeX documents."""
    settings = config_doc["settings"]
    return {
        "name": personal["name"],
        "position": personal["position"],
        "address": personal["address"],
        "contact": personal["contact"],
        "quote": personal["quote"],
        "font_size": settings["font_size"],
        "paper_size": settings["paper_size"],
        "margins": settings["margins"],
        "color": settings["color"],
        "section_color_highlight": boolean_setting(
            settings["section_color_highlight"]
        ),
        "header_alignment": settings.get("header_alignment", ""),
    }


def write_output(output_path, content):
    """Write one generated document."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    print(f"Generated: {output_path}")


def generate_resume(doc_type, env, personal, config_doc, sections, output_dir):
    """Generate a resume-shaped LaTeX document."""
    context = common_latex_context(personal, config_doc)
    if doc_type == "leadership_resume":
        position_text = personal["position"].get(
            "leadership_resume",
            personal["position"].get("resume", ""),
        )
        quote_text = personal["quote"].get(
            "leadership_resume",
            personal["quote"].get("resume", ""),
        )
        context["position"] = {"resume": position_text}
        context["quote"] = {"resume": quote_text}
        context["contact_line"] = personal.get("contact_line", {}).get(
            "leadership_resume",
            personal.get("contact_line", {}).get("resume", ""),
        )
        output_name = "leadership_resume.tex"
    else:
        context["contact_line"] = personal.get("contact_line", {}).get("resume", "")
        output_name = "resume.tex"

    context["sections"] = sections
    content = env.get_template("base_resume.tex").render(**context)
    write_output(Path(output_dir) / output_name, content)


def generate_cv(env, personal, config_doc, sections, output_dir):
    """Generate a CV LaTeX document."""
    context = common_latex_context(personal, config_doc)
    context.update(
        {
            "address_cv": personal["address_cv"],
            "sections": sections,
        }
    )
    content = env.get_template("base_cv.tex").render(**context)
    write_output(Path(output_dir) / "cv.tex", content)


def generate_cover_letter(
    env,
    personal,
    config_doc,
    config_dir,
    content_dir,
    output_dir,
):
    """Generate a cover-letter LaTeX document."""
    defaults = config_doc.get("defaults", {})
    variant_id = config_doc.get("variant", "default")
    letter = load_cover_letter_content(variant_id, config_dir, content_dir, defaults)
    context = common_latex_context(personal, config_doc)

    contact_line = None
    if variant_id == "academic_music":
        contact_line = personal.get("contact_line", {}).get(
            "leadership_resume",
            personal.get("contact_line", {}).get("resume", ""),
        )

    context.update(
        {
            "contact_line": contact_line,
            "recipient_name": escape_latex(letter.recipient_name),
            "company_name": escape_latex(letter.company_name),
            "company_address": latex_address(letter.company_address),
            "position_name": escape_latex(letter.position_name),
            "letter_opening": escape_latex(letter.letter_opening),
            "letter_closing": escape_latex(letter.letter_closing),
            "letter_body": format_cover_letter_body(
                letter.paragraphs,
                letter.substitutions,
            ),
            "variant_id": variant_id,
        }
    )

    content = env.get_template("base_cover_letter.tex").render(**context)
    write_output(Path(output_dir) / "coverletter.tex", content)


def generate_document(
    doc_type,
    content_core_dir,
    content_optional_dir,
    config_dir,
    config,
    output_dir,
):
    """Generate one LaTeX document."""
    content_core_dir = Path(content_core_dir)
    content_optional_dir = Path(content_optional_dir)
    config_dir = Path(config_dir)
    output_dir = Path(output_dir)

    personal = load_yaml(content_core_dir / "personal.yaml")
    config_doc = config[doc_type]
    project_root = project_root_from_content(content_core_dir)
    env = template_environment(project_root / "templates")

    if doc_type in ("resume", "leadership_resume"):
        sections = generate_sections(
            content_core_dir,
            content_optional_dir,
            config,
            doc_type,
        )
        generate_resume(doc_type, env, personal, config_doc, sections, output_dir)
    elif doc_type == "cv":
        sections = generate_sections(
            content_core_dir,
            content_optional_dir,
            config,
            "cv",
        )
        generate_cv(env, personal, config_doc, sections, output_dir)
    elif doc_type == "cover_letter":
        generate_cover_letter(
            env,
            personal,
            config_doc,
            config_dir,
            project_root / "content",
            output_dir,
        )
