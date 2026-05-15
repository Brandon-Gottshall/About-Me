"""Cover-letter variant loading and body formatting."""

from dataclasses import dataclass

from .content import load_yaml
from .text import escape_html, escape_latex, format_inline_html


@dataclass(frozen=True)
class CoverLetterContent:
    recipient_name: str
    company_name: str
    company_address: str
    position_name: str
    letter_opening: str
    letter_closing: str
    paragraphs: list
    substitutions: dict


def load_variant_paragraph(variant_id, content_id, content_dir):
    """Load a paragraph from one cover-letter variant."""
    paragraph_path = (
        content_dir / "cover_letters" / "variants" / variant_id / "paragraphs.yaml"
    )
    if not paragraph_path.exists():
        raise FileNotFoundError(f"Variant paragraph file not found: {paragraph_path}")

    paragraphs = load_yaml(paragraph_path).get("paragraphs", {})
    if content_id not in paragraphs:
        raise KeyError(f"Paragraph '{content_id}' not found in variant '{variant_id}'")
    return paragraphs[content_id]


def load_shared_paragraph(para_type, content_id, content_dir):
    """Load a paragraph from shared cover-letter content."""
    paragraph_path = content_dir / "cover_letters" / "paragraphs" / f"{para_type}.yaml"
    if not paragraph_path.exists():
        raise FileNotFoundError(f"Shared paragraph file not found: {paragraph_path}")

    paragraphs = load_yaml(paragraph_path).get("paragraphs", {})
    if content_id not in paragraphs:
        raise KeyError(
            f"Paragraph '{content_id}' not found in shared '{para_type}' paragraphs"
        )
    return paragraphs[content_id]


def load_cover_letter_variant(variant_id, config_dir, content_dir):
    """Load a cover-letter variant config and its paragraphs."""
    variant_config_path = config_dir / "cover_letters" / f"{variant_id}.yaml"
    if not variant_config_path.exists():
        raise FileNotFoundError(f"Variant config not found: {variant_config_path}")

    variant_config = load_yaml(variant_config_path)
    paragraphs = []
    for paragraph_ref in variant_config.get("paragraphs", []):
        if paragraph_ref.get("source") == "variant":
            paragraph = load_variant_paragraph(
                variant_id,
                paragraph_ref["content_id"],
                content_dir,
            )
        else:
            paragraph = load_shared_paragraph(
                paragraph_ref["type"],
                paragraph_ref["content_id"],
                content_dir,
            )
        paragraphs.append(paragraph)

    return variant_config, paragraphs


def load_cover_letter_content(variant_id, config_dir, content_dir, defaults):
    """Load the active cover-letter content with a legacy fallback."""
    try:
        variant_config, paragraphs = load_cover_letter_variant(
            variant_id,
            config_dir,
            content_dir,
        )
        source = variant_config
        substitutions = {
            "Position Name": variant_config.get("position_name", ""),
            "Company Name": variant_config.get("company_name", ""),
        }
    except (FileNotFoundError, KeyError) as error:
        print(
            f"Warning: Variant '{variant_id}' not found, "
            f"using legacy format: {error}"
        )
        legacy_path = config_dir / "cover_letter.yaml"
        source = load_yaml(legacy_path) if legacy_path.exists() else {}
        paragraphs = [
            {
                "text": source.get("body", defaults.get("letter_body", "")),
            }
        ]
        substitutions = {}

    return CoverLetterContent(
        recipient_name=source.get(
            "recipient_name",
            defaults.get("recipient_name", "Hiring Manager"),
        ),
        company_name=source.get(
            "company_name",
            defaults.get("company_name", "Organization"),
        ),
        company_address=source.get(
            "company_address",
            defaults.get("company_address", "Company Address\nCity, State ZIP Code"),
        ),
        position_name=source.get(
            "position_name",
            defaults.get("position_name", "Role"),
        ),
        letter_opening=source.get(
            "letter_opening",
            defaults.get("letter_opening", "Dear Hiring Manager,"),
        ),
        letter_closing=source.get(
            "letter_closing",
            defaults.get("letter_closing", "Sincerely,"),
        ),
        paragraphs=paragraphs,
        substitutions=substitutions,
    )


def apply_substitutions(text, substitutions):
    """Replace bracketed tokens in cover-letter paragraphs."""
    for key, value in substitutions.items():
        text = text.replace(f"[{key}]", str(value))
    return text


def format_cover_letter_body(paragraphs, substitutions=None):
    """Format cover-letter paragraphs for LaTeX."""
    substitutions = substitutions or {}
    formatted_paragraphs = []
    for paragraph in paragraphs:
        text = apply_substitutions(paragraph.get("text", ""), substitutions)
        formatted_paragraphs.append(escape_latex(text.strip()))
    return "\\letterskip\n\n".join(formatted_paragraphs)


def format_cover_letter_body_html(paragraphs, substitutions=None):
    """Format cover-letter paragraphs for HTML."""
    substitutions = substitutions or {}
    formatted_paragraphs = []
    for paragraph in paragraphs:
        text = apply_substitutions(paragraph.get("text", ""), substitutions)
        formatted_paragraphs.append(f"<p>{format_inline_html(text.strip())}</p>")
    return "\n".join(formatted_paragraphs)


def latex_address(address):
    """Escape an address and keep its line breaks for LaTeX."""
    lines = [escape_latex(line.strip()) for line in str(address).strip().splitlines()]
    return "\\\\".join(line for line in lines if line)


def html_address(address):
    """Escape an address for HTML."""
    return escape_html(str(address).strip())
