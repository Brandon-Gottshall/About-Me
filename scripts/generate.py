#!/usr/bin/env python3
"""
LaTeX Generator for CV/Resume/Cover Letter
Reads YAML data files and generates LaTeX documents using templates.
"""

import os
import yaml
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template
import sys


def load_yaml(filepath):
    """Load and parse a YAML file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def escape_latex(text):
    """Escape special LaTeX characters, but preserve LaTeX commands."""
    if not text:
        return ""

    # Protect LaTeX commands first using a marker without special chars
    import re

    latex_commands = []

    def match_balanced_braces(s, start_pos):
        """Find the matching closing brace for an opening brace."""
        depth = 0
        pos = start_pos
        while pos < len(s):
            if s[pos] == "{":
                depth += 1
            elif s[pos] == "}":
                depth -= 1
                if depth == 0:
                    return pos
            pos += 1
        return -1

    # Find and protect all LaTeX commands like \command{...}
    result_parts = []
    pos = 0
    while pos < len(text):
        # Look for backslash followed by letters (LaTeX command)
        cmd_match = re.search(r"\\([a-zA-Z]+)\{", text[pos:])
        if not cmd_match:
            result_parts.append(text[pos:])
            break

        cmd_start = pos + cmd_match.start()
        cmd_name = cmd_match.group(1)
        brace_start = cmd_start + len(cmd_match.group(0)) - 1  # Position of {

        # Add text before the command
        result_parts.append(text[pos:cmd_start])

        # Find matching closing brace
        brace_end = match_balanced_braces(text, brace_start)
        if brace_end != -1:
            # Extract full command
            full_cmd = text[cmd_start : brace_end + 1]
            idx = len(latex_commands)
            latex_commands.append(full_cmd)
            # Use marker without underscores or special chars
            result_parts.append(f"LATEXCMDX{idx}X")
            pos = brace_end + 1
        else:
            # Malformed, just continue
            result_parts.append(text[cmd_start:])
            break

    text = "".join(result_parts)

    # Basic LaTeX escaping
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
    result = str(text)
    for char, replacement in replacements.items():
        result = result.replace(char, replacement)

    # Escape standalone backslashes (not part of protected commands or escape sequences)
    # Protect escape sequences first (like \&, \%, etc.)
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
    for i, esc in enumerate(escape_sequences):
        marker = f"ESCAPESEQX{i}X"
        protected_escapes.append((marker, esc))
        result = result.replace(esc, marker)

    # Now escape remaining standalone backslashes
    result = result.replace("\\", r"\textbackslash{}")

    # Restore protected escape sequences
    for marker, esc in protected_escapes:
        result = result.replace(marker, esc)

    # Restore protected LaTeX commands
    for idx, cmd in enumerate(latex_commands):
        result = result.replace(f"LATEXCMDX{idx}X", cmd)

    return result


def format_date_range(start_date, end_date):
    """Return a clean date range string without extra separators."""
    if start_date and end_date:
        return f"{start_date} - {end_date}"
    if start_date:
        return start_date
    if end_date:
        return end_date
    return ""


def format_cventry(entry, entry_type="experience"):
    """Format a single cventry for LaTeX."""
    if entry_type == "experience":
        title = escape_latex(entry.get("title", ""))
        organization = escape_latex(entry.get("organization", ""))
        location = escape_latex(entry.get("location", ""))
        if entry.get("date_range"):
            date_range = escape_latex(entry["date_range"])
        else:
            date_range = format_date_range(
                escape_latex(entry.get("start_date", "")),
                escape_latex(entry.get("end_date", "")),
            )

        items = ""
        if entry.get("items"):
            items = "{\n      \\begin{cvitems}\n"
            for item in entry["items"]:
                items += f"        \\item {{{escape_latex(item)}}}\n"
            items += "      \\end{cvitems}\n    }"
        else:
            items = "{}"

        return f"""%---------------------------------------------------------
  \\cventry
    {{{title}}} % Job title
    {{{organization}}} % Organization
    {{{location}}} % Location
    {{{date_range}}} % Date(s)
    {items}"""

    elif entry_type == "education":
        degree = escape_latex(entry.get("degree", ""))
        institution = escape_latex(entry.get("institution", ""))
        location = escape_latex(entry.get("location", ""))
        if entry.get("date_range"):
            date_range = escape_latex(entry["date_range"])
        else:
            date_range = format_date_range(
                escape_latex(entry.get("start_date", "")),
                escape_latex(entry.get("end_date", "")),
            )

        items = ""
        if entry.get("items"):
            items = "{\n      \\begin{cvitems}\n"
            for item in entry["items"]:
                items += f"        \\item {{{escape_latex(item)}}}\n"
            items += "      \\end{cvitems}\n    }"
        else:
            items = "{}"

        return f"""%---------------------------------------------------------
  \\cventry
    {{{degree}}} % Degree
    {{{institution}}} % Institution
    {{{location}}} % Location
    {{{date_range}}} % Date(s)
    {items}"""

    elif entry_type == "certification":
        name = escape_latex(entry.get("name", ""))
        organization = escape_latex(entry.get("organization", ""))
        if entry.get("date_range"):
            date_range = escape_latex(entry["date_range"])
        else:
            date_range = format_date_range(
                escape_latex(entry.get("start_date", "")),
                escape_latex(entry.get("end_date", "")),
            )
        location = escape_latex(entry.get("location", ""))

        items = ""
        if entry.get("items"):
            items = "{\n      \\begin{cvitems}\n"
            for item in entry["items"]:
                items += f"        \\item {{{escape_latex(item)}}}\n"
            items += "      \\end{cvitems}\n    }"
        else:
            items = "{}"

        return f"""%---------------------------------------------------------
    \\cventry
    {{{name}}} % Certification
    {{{organization}}} % Organization
    {{{location}}} % Location
    {{{date_range}}} % Date(s)
    {items}"""

    elif entry_type == "project":
        name = escape_latex(entry.get("name", ""))
        technologies = escape_latex(entry.get("technologies", ""))
        date = escape_latex(entry.get("date", ""))
        location = escape_latex(entry.get("location", ""))

        items = ""
        if entry.get("items"):
            items = "{\n      \\begin{cvitems}\n"
            for item in entry["items"]:
                items += f"        \\item {{{escape_latex(item)}}}\n"
            items += "      \\end{cvitems}\n    }"
        else:
            items = "{}"

        return f"""%---------------------------------------------------------
    \\cventry
    {{{name}}} % Project name
    {{{technologies}}} % Technologies used
    {{{date}}} % Date(s)
    {{{location}}} % Location
    {items}"""

    elif entry_type == "presentation":
        role = escape_latex(entry.get("role", ""))
        event = escape_latex(entry.get("event", ""))
        location = escape_latex(entry.get("location", ""))
        date = escape_latex(entry.get("date", ""))

        items = ""
        if entry.get("items"):
            items = "{\n      \\begin{cvitems}\n"
            for item in entry["items"]:
                items += f"        \\item {{{escape_latex(item)}}}\n"
            items += "      \\end{cvitems}\n    }"
        else:
            items = "{}"

        return f"""%---------------------------------------------------------
  \\cventry
    {{{role}}} % Role
    {{{event}}} % Event
    {{{location}}} % Location
    {{{date}}} % Date(s)
    {items}"""

    elif entry_type == "teaching":
        role = escape_latex(entry.get("role", ""))
        institution = escape_latex(entry.get("institution", ""))
        location = escape_latex(entry.get("location", ""))
        date = escape_latex(entry.get("date", ""))

        items = ""
        if entry.get("items"):
            items = "{\n      \\begin{cvitems}\n"
            for item in entry["items"]:
                items += f"        \\item {{{escape_latex(item)}}}\n"
            items += "      \\end{cvitems}\n    }"
        else:
            items = "{}"

        return f"""    \\cventry
    {{{role}}} % Role
    {{{institution}}} % Institution
    {{{location}}} % Location
    {{{date}}} % Date(s)
    {items}"""

    elif entry_type == "volunteer":
        position = escape_latex(entry.get("position", ""))
        organization = escape_latex(entry.get("organization", ""))
        location = escape_latex(entry.get("location", ""))
        date_range = escape_latex(entry.get("date_range", ""))

        items = ""
        if entry.get("items"):
            items = "{\n      \\begin{cvitems}\n"
            for item in entry["items"]:
                items += f"        \\item {{{escape_latex(item)}}}\n"
            items += "      \\end{cvitems}\n    }"
        else:
            items = "{}"

        return f"""    \\cventry
    {{{position}}} % Position
    {{{organization}}} % Organization
    {{{location}}} % Location
    {{{date_range}}} % Date(s)
    {items}"""

    return ""


def format_cvskill(category, items):
    """Format a cvskill entry."""
    category_escaped = escape_latex(category)
    if isinstance(items, (list, tuple)):
        formatted_items = "; ".join(
            escape_latex(item) for item in items if item
        )
        if formatted_items:
            items_escaped = "\\textemdash{} " + formatted_items
        else:
            items_escaped = ""
    else:
        items_escaped = escape_latex(items)
    return f"""%---------------------------------------------------------
  \\cvskill
    {{{category_escaped}}} % Category
    {{{items_escaped}}} % Skills"""


def format_language(language, proficiency):
    """Format a language entry."""
    lang_escaped = escape_latex(language)
    prof_escaped = escape_latex(proficiency)
    return f"""    \\cvskill
    {{{lang_escaped}}} % Language
    {{{prof_escaped}}} % Proficiency level"""


def format_leadership_entries(leadership_data):
    """Format leadership entries with category headers."""
    entries = []
    for category in leadership_data.get("categories", []):
        category_name = category.get("name", "")  # Don't escape in comments
        # Add category comment
        entries.append(
            f"%-------------------------------------------------------------------------------"
        )
        entries.append(f"%\t{category_name}")
        entries.append(
            f"%-------------------------------------------------------------------------------"
        )
        # Format each entry in the category
        for entry in category.get("entries", []):
            entries.append(format_cventry(entry, "experience"))
    return "\n".join(entries)


def load_variant_paragraph(variant_id, content_id, content_dir):
    """Load a paragraph from a variant-specific content file."""
    variant_content_path = (
        content_dir / "cover_letters" / "variants" / variant_id / "paragraphs.yaml"
    )
    if not variant_content_path.exists():
        raise FileNotFoundError(
            f"Variant paragraph file not found: {variant_content_path}"
        )

    variant_content = load_yaml(variant_content_path)
    paragraphs = variant_content.get("paragraphs", {})

    if content_id not in paragraphs:
        raise KeyError(f"Paragraph '{content_id}' not found in variant '{variant_id}'")

    return paragraphs[content_id]


def load_shared_paragraph(para_type, content_id, content_dir):
    """Load a paragraph from a shared content file."""
    shared_content_path = (
        content_dir / "cover_letters" / "paragraphs" / f"{para_type}.yaml"
    )
    if not shared_content_path.exists():
        raise FileNotFoundError(
            f"Shared paragraph file not found: {shared_content_path}"
        )

    shared_content = load_yaml(shared_content_path)
    paragraphs = shared_content.get("paragraphs", {})

    if content_id not in paragraphs:
        raise KeyError(
            f"Paragraph '{content_id}' not found in shared '{para_type}' paragraphs"
        )

    return paragraphs[content_id]


def load_cover_letter_variant(variant_id, config_dir, content_dir):
    """Load a specific cover letter variant configuration and paragraphs."""
    variant_config_path = config_dir / "cover_letters" / f"{variant_id}.yaml"
    if not variant_config_path.exists():
        raise FileNotFoundError(f"Variant config not found: {variant_config_path}")

    variant_config = load_yaml(variant_config_path)

    # Load paragraph content
    paragraphs = []
    for para_ref in variant_config.get("paragraphs", []):
        if para_ref.get("source") == "variant":
            para_content = load_variant_paragraph(
                variant_id, para_ref["content_id"], content_dir
            )
        else:  # shared
            para_content = load_shared_paragraph(
                para_ref["type"], para_ref["content_id"], content_dir
            )
        paragraphs.append(para_content)

    return variant_config, paragraphs


def format_cover_letter_body(paragraphs, substitutions=None):
    """Format paragraphs into LaTeX body with proper spacing."""
    if substitutions is None:
        substitutions = {}

    formatted_paragraphs = []
    for para in paragraphs:
        text = para.get("text", "")
        # Apply substitutions
        for key, value in substitutions.items():
            text = text.replace(f"[{key}]", value)

        # Escape LaTeX special characters (escape_latex now handles \textbf{} commands)
        escaped = escape_latex(text.strip())

        formatted_paragraphs.append(escaped)

    # Join with \letterskip for consistent rhythm (matches resume section spacing)
    return "\\letterskip\n\n".join(formatted_paragraphs)


def generate_sections(content_core_dir, content_optional_dir, config, doc_type):
    """Generate LaTeX sections based on config."""
    sections = []
    section_order = config[doc_type]["sections"]

    # Load core content files
    personal = load_yaml(content_core_dir / "personal.yaml")
    summary_data = load_yaml(content_core_dir / "summary.yaml")
    experience_data = load_yaml(content_core_dir / "experience.yaml")
    education_data = load_yaml(content_core_dir / "education.yaml")
    skills_data = load_yaml(content_core_dir / "skills.yaml")

    # Load optional content files (with fallback to empty)
    certifications_data = (
        load_yaml(content_optional_dir / "certifications.yaml")
        if (content_optional_dir / "certifications.yaml").exists()
        else {"entries": []}
    )
    projects_data = (
        load_yaml(content_optional_dir / "projects.yaml")
        if (content_optional_dir / "projects.yaml").exists()
        else {"entries": []}
    )
    languages_data = (
        load_yaml(content_optional_dir / "languages.yaml")
        if (content_optional_dir / "languages.yaml").exists()
        else {"entries": []}
    )
    publications_data = (
        load_yaml(content_optional_dir / "publications.yaml")
        if (content_optional_dir / "publications.yaml").exists()
        else {"entries": []}
    )
    presentations_data = (
        load_yaml(content_optional_dir / "presentations.yaml")
        if (content_optional_dir / "presentations.yaml").exists()
        else {"entries": []}
    )
    teaching_data = (
        load_yaml(content_optional_dir / "teaching.yaml")
        if (content_optional_dir / "teaching.yaml").exists()
        else {"entries": []}
    )
    volunteer_data = (
        load_yaml(content_optional_dir / "volunteer.yaml")
        if (content_optional_dir / "volunteer.yaml").exists()
        else {"entries": []}
    )

    # Template directory
    template_dir = Path(__file__).parent.parent / "templates" / "sections"
    # Use custom delimiters to avoid conflicts with LaTeX braces
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        variable_start_string="<<",
        variable_end_string=">>",
        block_start_string="<@",
        block_end_string="@>",
        comment_start_string="<#",
        comment_end_string="#>",
    )

    for section_name in section_order:
        if section_name == "summary":
            # Use different template title for leadership resume
            if doc_type == "leadership_resume":
                # Create a custom summary section with "Leadership Profile" title
                summary_text = (
                    summary_data.get("leadership_resume")
                    if summary_data.get("leadership_resume")
                    else summary_data["text"]
                )
                leadership_profile = f"""%-------------------------------------------------------------------------------
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
                sections.append(leadership_profile)
            else:
                template = env.get_template("summary.tex")
                sections.append(
                    template.render(summary_text=escape_latex(summary_data["text"]))
                )

        elif section_name == "experience":
            template = env.get_template("experience.tex")
            entries = "\n".join(
                [
                    format_cventry(entry, "experience")
                    for entry in experience_data["entries"]
                ]
            )
            sections.append(template.render(experience_entries=entries))

        elif section_name == "education":
            template = env.get_template("education.tex")
            entries = "\n".join(
                [
                    format_cventry(entry, "education")
                    for entry in education_data["entries"]
                ]
            )
            sections.append(template.render(education_entries=entries))

        elif section_name == "skills":
            # Use a narrative Skills & Strengths layout for leadership resume
            if doc_type == "leadership_resume" and skills_data.get("leadership_resume"):
                template = env.get_template("skills_leadership.tex")
                leadership_skills = skills_data["leadership_resume"]
                strengths = []
                for strength in leadership_skills.get("strengths", []):
                    category = escape_latex(strength.get("category", ""))
                    items = strength.get("items", [])
                    if isinstance(items, (list, tuple)):
                        items_text = ", ".join(
                            escape_latex(item) for item in items if item
                        )
                    else:
                        items_text = escape_latex(items)
                    strengths.append(
                        {
                            "category": category,
                            "items_text": items_text,
                        }
                    )
                certification_entries = "\n".join(
                    [
                        format_cvskill(cert["category"], cert["items"])
                        for cert in leadership_skills.get("certifications", [])
                    ]
                )
                sections.append(
                    template.render(
                        strengths=strengths,
                        certification_entries=certification_entries,
                    )
                )
            else:
                template = env.get_template("skills.tex")
                technical_skills = "\n".join(
                    [
                        format_cvskill(skill["category"], skill["items"])
                        for skill in skills_data["technical"]
                    ]
                )
                professional_skills = ""
                if skills_data.get("professional"):
                    professional_skills = "\n".join(
                        [
                            format_cvskill(skill["category"], skill["items"])
                            for skill in skills_data["professional"]
                        ]
                    )
                sections.append(
                    template.render(
                        technical_skills=technical_skills,
                        professional_skills=professional_skills,
                    )
                )

        elif section_name == "certifications":
            template = env.get_template("certifications.tex")
            entries = "\n".join(
                [
                    format_cventry(entry, "certification")
                    for entry in certifications_data["entries"]
                ]
            )
            sections.append(template.render(certification_entries=entries))

        elif section_name == "projects":
            template = env.get_template("projects.tex")
            entries_list = projects_data.get("entries", [])
            if entries_list:
                entries = "\n".join(
                    [format_cventry(entry, "project") for entry in entries_list]
                )
            else:
                entries = (
                    "% No projects entries found. Add entries to data/projects.yaml"
                )
            sections.append(template.render(project_entries=entries))

        elif section_name == "publications":
            template = env.get_template("publications.tex")
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
            template = env.get_template("presentations.tex")
            entries_list = presentations_data.get("entries", [])
            if entries_list:
                entries = "\n".join(
                    [format_cventry(entry, "presentation") for entry in entries_list]
                )
            else:
                entries = "% No presentations entries found. Add entries to data/presentations.yaml"
            sections.append(template.render(presentation_entries=entries))

        elif section_name == "teaching":
            template = env.get_template("teaching.tex")
            entries_list = teaching_data.get("entries", [])
            if entries_list:
                entries = "\n".join(
                    [format_cventry(entry, "teaching") for entry in entries_list]
                )
            else:
                entries = (
                    "% No teaching entries found. Add entries to data/teaching.yaml"
                )
            sections.append(template.render(teaching_entries=entries))

        elif section_name == "volunteer":
            template = env.get_template("volunteer.tex")
            entries_list = volunteer_data.get("entries", [])
            if entries_list:
                entries = "\n".join(
                    [format_cventry(entry, "volunteer") for entry in entries_list]
                )
            else:
                entries = (
                    "% No volunteer entries found. Add entries to data/volunteer.yaml"
                )
            sections.append(template.render(volunteer_entries=entries))

        elif section_name == "languages":
            template = env.get_template("languages.tex")
            entries = "\n".join(
                [
                    format_language(entry["language"], entry["proficiency"])
                    for entry in languages_data["entries"]
                ]
            )
            sections.append(template.render(language_entries=entries))

        elif section_name == "references":
            template = env.get_template("references.tex")
            sections.append(template.render())

        elif section_name == "leadership":
            template = env.get_template("leadership.tex")
            leadership_data = (
                load_yaml(content_optional_dir / "leadership.yaml")
                if (content_optional_dir / "leadership.yaml").exists()
                else {"categories": []}
            )
            leadership_entries = format_leadership_entries(leadership_data)
            sections.append(template.render(leadership_entries=leadership_entries))

    return "\n".join(sections)


def generate_document(
    doc_type, content_core_dir, content_optional_dir, config_dir, config, output_dir
):
    """Generate a LaTeX document."""
    # Load personal data
    personal = load_yaml(content_core_dir / "personal.yaml")
    config_doc = config[doc_type]
    project_root = (
        content_core_dir.parent.parent
    )  # content_core_dir is content/core, so parent.parent is project root

    # Load base template
    template_dir = Path(__file__).parent.parent / "templates"
    # Use custom delimiters to avoid conflicts with LaTeX braces
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        variable_start_string="<<",
        variable_end_string=">>",
        block_start_string="<@",
        block_end_string="@>",
        comment_start_string="<#",
        comment_end_string="#>",
    )

    if doc_type == "resume":
        template = env.get_template("base_resume.tex")
        sections = generate_sections(
            content_core_dir, content_optional_dir, config, "resume"
        )

        content = template.render(
            name=personal["name"],
            position=personal["position"],
            address=personal["address"],
            contact=personal["contact"],
            contact_line=personal.get("contact_line", {}).get("resume", ""),
            quote=personal["quote"],
            font_size=config_doc["settings"]["font_size"],
            paper_size=config_doc["settings"]["paper_size"],
            margins=config_doc["settings"]["margins"],
            color=config_doc["settings"]["color"],
            section_color_highlight=(
                "true" if config_doc["settings"]["section_color_highlight"] else "false"
            ),
            header_alignment=config_doc["settings"]["header_alignment"],
            sections=sections,
        )

        output_path = output_dir / "resume.tex"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Generated: {output_path}")

    elif doc_type == "cv":
        template = env.get_template("base_cv.tex")
        sections = generate_sections(
            content_core_dir, content_optional_dir, config, "cv"
        )

        content = template.render(
            name=personal["name"],
            position=personal["position"],
            address_cv=personal["address_cv"],
            contact=personal["contact"],
            quote=personal["quote"],
            font_size=config_doc["settings"]["font_size"],
            paper_size=config_doc["settings"]["paper_size"],
            margins=config_doc["settings"]["margins"],
            color=config_doc["settings"]["color"],
            section_color_highlight=(
                "true" if config_doc["settings"]["section_color_highlight"] else "false"
            ),
            header_alignment=config_doc["settings"].get("header_alignment", ""),
            sections=sections,
        )

        output_path = output_dir / "cv.tex"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Generated: {output_path}")

    elif doc_type == "cover_letter":
        template = env.get_template("base_cover_letter.tex")
        defaults = config_doc.get("defaults", {})

        # Determine variant (default to 'default' if not specified)
        variant_id = config_doc.get("variant", "default")

        # Try to load variant, fall back to old format if variant doesn't exist
        try:
            content_dir = project_root / "content"
            variant_config, paragraphs = load_cover_letter_variant(
                variant_id, config_dir, content_dir
            )

            # Format letter body from paragraphs
            substitutions = {
                "Position Name": variant_config.get("position_name", ""),
                "Company Name": variant_config.get("company_name", ""),
            }
            letter_body = format_cover_letter_body(paragraphs, substitutions)

            # Use variant config values
            recipient_name = variant_config.get(
                "recipient_name", defaults.get("recipient_name", "Hiring Manager")
            )
            company_name = variant_config.get(
                "company_name", defaults.get("company_name", "Company Name")
            )
            # Format address: replace newlines with \\ for LaTeX line breaks, strip trailing whitespace
            company_address_raw = variant_config.get(
                "company_address",
                defaults.get(
                    "company_address", "Company Address\nCity, State ZIP Code"
                ),
            )
            company_address = company_address_raw.strip().replace("\n", "\\\\")
            position_name = variant_config.get(
                "position_name", defaults.get("position_name", "[Position Name]")
            )
            letter_opening = variant_config.get(
                "letter_opening", defaults.get("letter_opening", "Dear Hiring Manager,")
            )
            letter_closing = variant_config.get(
                "letter_closing", defaults.get("letter_closing", "Sincerely,")
            )

        except (FileNotFoundError, KeyError) as e:
            # Fall back to old format for backward compatibility
            print(
                f"Warning: Variant '{variant_id}' not found, using legacy format: {e}"
            )
            cover_letter_data = (
                load_yaml(config_dir / "cover_letter.yaml")
                if (config_dir / "cover_letter.yaml").exists()
                else {}
            )
            letter_body = cover_letter_data.get("body", defaults.get("letter_body", ""))
            letter_body = escape_latex(letter_body)

            recipient_name = cover_letter_data.get(
                "recipient_name", defaults.get("recipient_name", "Hiring Manager")
            )
            company_name = cover_letter_data.get(
                "company_name", defaults.get("company_name", "Company Name")
            )
            company_address = cover_letter_data.get(
                "company_address",
                defaults.get(
                    "company_address", "Company Address\nCity, State ZIP Code"
                ),
            ).replace("\n", "\\\\")
            position_name = cover_letter_data.get(
                "position_name", defaults.get("position_name", "[Position Name]")
            )
            letter_opening = cover_letter_data.get(
                "letter_opening", defaults.get("letter_opening", "Dear Hiring Manager,")
            )
            letter_closing = cover_letter_data.get(
                "letter_closing", defaults.get("letter_closing", "Sincerely,")
            )

        # Use contact_line for academic_music variant (like leadership resume)
        contact_line = None
        if variant_id == "academic_music":
            contact_line = personal.get("contact_line", {}).get(
                "leadership_resume",
                personal.get("contact_line", {}).get("resume", ""),
            )

        content = template.render(
            name=personal["name"],
            position=personal["position"],
            address=personal["address"],
            contact=personal["contact"],
            contact_line=contact_line,
            font_size=config_doc["settings"]["font_size"],
            paper_size=config_doc["settings"]["paper_size"],
            margins=config_doc["settings"]["margins"],
            color=config_doc["settings"]["color"],
            section_color_highlight=(
                "true" if config_doc["settings"]["section_color_highlight"] else "false"
            ),
            header_alignment=config_doc["settings"]["header_alignment"],
            recipient_name=recipient_name,
            company_name=company_name,
            company_address=company_address,
            position_name=position_name,
            letter_opening=letter_opening,
            letter_closing=letter_closing,
            letter_body=letter_body,
            variant_id=variant_id,
        )

        output_path = output_dir / "coverletter.tex"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Generated: {output_path}")

    elif doc_type == "leadership_resume":
        template = env.get_template("base_resume.tex")
        sections = generate_sections(
            content_core_dir, content_optional_dir, config, "leadership_resume"
        )

        # Use leadership-focused position/quote if available, otherwise use resume defaults
        position_text = personal["position"].get(
            "leadership_resume", personal["position"].get("resume", "")
        )
        quote_text = personal["quote"].get(
            "leadership_resume", personal["quote"].get("resume", "")
        )

        content = template.render(
            name=personal["name"],
            position={"resume": position_text},  # Template expects 'resume' key
            address=personal["address"],
            contact=personal["contact"],
            contact_line=personal.get("contact_line", {}).get(
                "leadership_resume",
                personal.get("contact_line", {}).get("resume", ""),
            ),
            quote={"resume": quote_text},  # Template expects 'resume' key
            font_size=config_doc["settings"]["font_size"],
            paper_size=config_doc["settings"]["paper_size"],
            margins=config_doc["settings"]["margins"],
            color=config_doc["settings"]["color"],
            section_color_highlight=(
                "true" if config_doc["settings"]["section_color_highlight"] else "false"
            ),
            header_alignment=config_doc["settings"]["header_alignment"],
            sections=sections,
        )

        output_path = output_dir / "leadership_resume.tex"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Generated: {output_path}")


def main():
    """Main entry point."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    content_core_dir = project_root / "content" / "core"
    content_optional_dir = project_root / "content" / "optional"
    config_dir = project_root / "config"
    output_dir = project_root / "generated"

    # Check if content directories exist
    if not content_core_dir.exists():
        print(
            f"Error: Content directory not found at {content_core_dir}", file=sys.stderr
        )
        sys.exit(1)

    # Load config
    config_path = config_dir / "documents.yaml"
    if not config_path.exists():
        print(f"Error: Config file not found at {config_path}", file=sys.stderr)
        sys.exit(1)

    config = load_yaml(config_path)

    # Generate documents
    if len(sys.argv) > 1:
        doc_types = sys.argv[1:]
    else:
        doc_types = ["resume", "cv", "cover_letter", "leadership_resume"]

    # Map command-line names to config keys
    doc_type_map = {
        "resume": "resume",
        "cv": "cv",
        "cover-letter": "cover_letter",
        "cover_letter": "cover_letter",
        "leadership-resume": "leadership_resume",
        "leadership_resume": "leadership_resume",
    }

    for doc_type_arg in doc_types:
        doc_type = doc_type_map.get(doc_type_arg, doc_type_arg)
        if doc_type in config:
            generate_document(
                doc_type,
                content_core_dir,
                content_optional_dir,
                config_dir,
                config,
                output_dir,
            )
        else:
            print(f"Unknown document type: {doc_type_arg}")


if __name__ == "__main__":
    main()
