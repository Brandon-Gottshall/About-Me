"""HTML rendering for resumes, CVs, and cover letters."""

from datetime import datetime
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
    read_text_if_exists,
)
from .cover_letters import (
    format_cover_letter_body_html,
    html_address,
    load_cover_letter_content,
)
from .entries import (
    format_cventry_html,
    format_cvskill_html,
    format_language_html,
)
from .text import escape_html, prepare_personal_html


def template_environment(template_dir):
    """Create a Jinja environment for HTML templates."""
    return Environment(
        loader=FileSystemLoader(str(template_dir)),
        variable_start_string="<<",
        variable_end_string=">>",
        block_start_string="<@",
        block_end_string="@>",
        comment_start_string="<#",
        comment_end_string="#>",
    )


def render_html_summary(env, summary_data, doc_type):
    """Render the HTML summary section."""
    template = env.get_template("summary.html")
    if doc_type == "leadership_resume":
        summary_text = summary_data.get("leadership_resume") or summary_data["text"]
        return template.render(
            summary_title_first="Leadership",
            summary_title_rest="Profile",
            summary_text=escape_html(summary_text),
        )

    return template.render(
        summary_title_first="Professional",
        summary_title_rest="Summary",
        summary_text=escape_html(summary_data["text"]),
    )


def render_html_skills(env, skills_data, doc_type):
    """Render technical skills or leadership strengths."""
    if doc_type == "leadership_resume" and skills_data.get("leadership_resume"):
        template = env.get_template("skills_leadership.html")
        leadership_skills = skills_data["leadership_resume"]
        strengths = []
        for strength in leadership_skills.get("strengths", []):
            items = strength.get("items", [])
            if isinstance(items, (list, tuple)):
                items_text = ", ".join(escape_html(item) for item in items if item)
            else:
                items_text = escape_html(items)
            strengths.append(
                {
                    "category": escape_html(strength.get("category", "")),
                    "items_text": items_text,
                }
            )

        certification_entries = "\n".join(
            format_cvskill_html(cert["category"], cert["items"])
            for cert in leadership_skills.get("certifications", [])
        )
        return template.render(
            strengths=strengths,
            certification_entries=certification_entries,
        )

    template = env.get_template("skills.html")
    technical_skills = "\n".join(
        format_cvskill_html(skill["category"], skill["items"])
        for skill in skills_data["technical"]
    )
    professional_skills = ""
    if skills_data.get("professional"):
        professional_skills = "\n".join(
            format_cvskill_html(skill["category"], skill["items"])
            for skill in skills_data["professional"]
        )

    return template.render(
        technical_skills=technical_skills,
        professional_skills=professional_skills,
    )


def generate_html_sections(content_core_dir, content_optional_dir, config, doc_type):
    """Generate HTML sections for one document."""
    core = load_core_content(Path(content_core_dir))
    optional = load_optional_content(Path(content_optional_dir))
    section_order = config[doc_type]["sections"]

    template_dir = (
        project_root_from_content(content_core_dir) / "templates" / "html" / "sections"
    )
    env = template_environment(template_dir)

    sections = []
    for section_name in section_order:
        if section_name == "summary":
            sections.append(render_html_summary(env, core["summary"], doc_type))

        elif section_name == "experience":
            template = env.get_template("experience.html")
            entries = "\n".join(
                format_cventry_html(entry, "experience")
                for entry in core["experience"]["entries"]
            )
            sections.append(template.render(experience_entries=entries))

        elif section_name == "education":
            template = env.get_template("education.html")
            entries = "\n".join(
                format_cventry_html(entry, "education")
                for entry in core["education"]["entries"]
            )
            sections.append(template.render(education_entries=entries))

        elif section_name == "skills":
            sections.append(render_html_skills(env, core["skills"], doc_type))

        elif section_name == "certifications":
            if not has_entries(optional["certifications"]):
                continue
            template = env.get_template("certifications.html")
            entries = "\n".join(
                format_cventry_html(entry, "certification")
                for entry in optional["certifications"]["entries"]
            )
            sections.append(template.render(certification_entries=entries))

        elif section_name == "projects":
            if not has_entries(optional["projects"]):
                continue
            template = env.get_template("projects.html")
            entries = "\n".join(
                format_cventry_html(entry, "project")
                for entry in optional["projects"]["entries"]
            )
            sections.append(template.render(project_entries=entries))

        elif section_name == "publications":
            if not has_publication_entries(optional["publications"]):
                continue
            template = env.get_template("publications.html")
            sections.append(
                template.render(
                    journal_articles=[
                        escape_html(article)
                        for article in optional["publications"].get(
                            "journal_articles",
                            [],
                        )
                    ],
                    conference_proceedings=[
                        escape_html(proceeding)
                        for proceeding in optional["publications"].get(
                            "conference_proceedings",
                            [],
                        )
                    ],
                    preprints=[
                        escape_html(preprint)
                        for preprint in optional["publications"].get("preprints", [])
                    ],
                )
            )

        elif section_name == "presentations":
            if not has_entries(optional["presentations"]):
                continue
            template = env.get_template("presentations.html")
            entries = "\n".join(
                format_cventry_html(entry, "presentation")
                for entry in optional["presentations"]["entries"]
            )
            sections.append(template.render(presentation_entries=entries))

        elif section_name == "teaching":
            if not has_entries(optional["teaching"]):
                continue
            template = env.get_template("teaching.html")
            entries = "\n".join(
                format_cventry_html(entry, "teaching")
                for entry in optional["teaching"]["entries"]
            )
            sections.append(template.render(teaching_entries=entries))

        elif section_name == "volunteer":
            if not has_entries(optional["volunteer"]):
                continue
            template = env.get_template("volunteer.html")
            entries = "\n".join(
                format_cventry_html(entry, "volunteer")
                for entry in optional["volunteer"]["entries"]
            )
            sections.append(template.render(volunteer_entries=entries))

        elif section_name == "languages":
            if not has_entries(optional["languages"]):
                continue
            template = env.get_template("languages.html")
            entries = "\n".join(
                format_language_html(entry["language"], entry["proficiency"])
                for entry in optional["languages"]["entries"]
            )
            sections.append(template.render(language_entries=entries))

        elif section_name == "references":
            sections.append(env.get_template("references.html").render())

        elif section_name == "leadership":
            if not has_leadership_entries(optional["leadership"]):
                continue
            template = env.get_template("leadership.html")
            entries = "\n".join(
                format_cventry_html(entry, "experience")
                for category in optional["leadership"].get("categories", [])
                for entry in category.get("entries", [])
            )
            sections.append(template.render(leadership_entries=entries))

    return "\n".join(sections)


def write_output(output_path, content):
    """Write one generated HTML document."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    clean_content = "\n".join(line.rstrip() for line in content.splitlines())
    output_path.write_text(f"{clean_content}\n", encoding="utf-8")
    print(f"Generated: {output_path}")


def read_document_css(template_dir, document_css):
    """Return shared document CSS plus document-specific overrides."""
    css_parts = [
        read_text_if_exists(Path(template_dir) / "document.css"),
        read_text_if_exists(Path(template_dir) / document_css),
    ]
    return "\n".join(css for css in css_parts if css)


def generate_html_resume(
    doc_type,
    env,
    personal,
    config_doc,
    sections,
    css,
    output_dir,
):
    """Generate a resume-shaped HTML document."""
    if doc_type == "leadership_resume":
        position_text = personal["position"].get(
            "leadership_resume",
            personal["position"].get("resume", ""),
        )
        quote_text = personal["quote"].get(
            "leadership_resume",
            personal["quote"].get("resume", ""),
        )
        contact_line = personal.get("contact_line", {}).get(
            "leadership_resume",
            personal.get("contact_line", {}).get("resume", ""),
        )
        document_title = "Leadership Resume"
        output_name = "leadership_resume.html"
    else:
        position_text = personal["position"].get("resume", "")
        quote_text = personal["quote"].get("resume", "")
        contact_line = personal.get("contact_line", {}).get("resume", "")
        document_title = "Resume"
        output_name = "resume.html"

    content = env.get_template("base_resume.html").render(
        name=personal["name"],
        position={"resume": position_text},
        address=personal["address"],
        contact=personal["contact"],
        contact_line=contact_line,
        quote={"resume": quote_text},
        header_alignment=config_doc["settings"]["header_alignment"],
        document_title=document_title,
        sections=sections,
        css_content=css,
    )
    write_output(Path(output_dir) / output_name, content)


def generate_html_cv(env, personal, config_doc, sections, css, output_dir):
    """Generate the HTML CV."""
    content = env.get_template("base_cv.html").render(
        name=personal["name"],
        position=personal["position"],
        address_cv=personal["address_cv"],
        contact=personal["contact"],
        quote=personal["quote"],
        header_alignment=config_doc["settings"].get("header_alignment", ""),
        sections=sections,
        css_content=css,
    )
    write_output(Path(output_dir) / "cv.html", content)


def generate_html_cover_letter(
    env,
    personal,
    config_doc,
    config_dir,
    content_dir,
    css,
    output_dir,
):
    """Generate the HTML cover letter."""
    defaults = config_doc.get("defaults", {})
    variant_id = config_doc.get("variant", "default")
    letter = load_cover_letter_content(variant_id, config_dir, content_dir, defaults)

    contact_line = None
    position = personal["position"]
    if variant_id == "academic_music":
        contact_line = personal.get("contact_line", {}).get(
            "leadership_resume",
            personal.get("contact_line", {}).get("resume", ""),
        )
        position = {
            **personal["position"],
            "resume": personal["position"].get(
                "leadership_resume",
                personal["position"].get("resume", ""),
            ),
        }

    content = env.get_template("base_cover_letter.html").render(
        name=personal["name"],
        position=position,
        address=personal["address"],
        contact=personal["contact"],
        contact_line=contact_line,
        header_alignment=config_doc["settings"]["header_alignment"],
        recipient_name=escape_html(letter.recipient_name),
        company_name=escape_html(letter.company_name),
        company_address=html_address(letter.company_address),
        position_name=escape_html(letter.position_name),
        letter_opening=escape_html(letter.letter_opening),
        letter_closing=escape_html(letter.letter_closing),
        letter_body=format_cover_letter_body_html(
            letter.paragraphs,
            letter.substitutions,
        ),
        date=datetime.now().strftime("%B %d, %Y"),
        css_content=css,
    )
    write_output(Path(output_dir) / "coverletter.html", content)


def generate_html_document(
    doc_type,
    content_core_dir,
    content_optional_dir,
    config_dir,
    config,
    output_dir,
):
    """Generate one HTML document."""
    content_core_dir = Path(content_core_dir)
    content_optional_dir = Path(content_optional_dir)
    config_dir = Path(config_dir)
    output_dir = Path(output_dir)

    personal = prepare_personal_html(load_yaml(content_core_dir / "personal.yaml"))
    config_doc = config[doc_type]
    project_root = project_root_from_content(content_core_dir)
    template_dir = project_root / "templates" / "html"
    env = template_environment(template_dir)

    if doc_type in ("resume", "leadership_resume"):
        sections = generate_html_sections(
            content_core_dir,
            content_optional_dir,
            config,
            doc_type,
        )
        css = read_document_css(template_dir, "resume.css")
        generate_html_resume(
            doc_type,
            env,
            personal,
            config_doc,
            sections,
            css,
            output_dir,
        )
    elif doc_type == "cv":
        sections = generate_html_sections(
            content_core_dir,
            content_optional_dir,
            config,
            "cv",
        )
        css = read_document_css(template_dir, "cv.css")
        generate_html_cv(env, personal, config_doc, sections, css, output_dir)
    elif doc_type == "cover_letter":
        css = read_document_css(template_dir, "coverletter.css")
        generate_html_cover_letter(
            env,
            personal,
            config_doc,
            config_dir,
            project_root / "content",
            css,
            output_dir,
        )
