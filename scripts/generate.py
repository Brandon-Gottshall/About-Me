#!/usr/bin/env python3
"""Compatibility wrapper for the document generator package."""

from document_generator import (  # noqa: F401
    DEFAULT_DOCUMENTS,
    DOCUMENT_ALIASES,
    ProjectPaths,
    PUBLIC_DOCUMENTS,
    current_utc_timestamp,
    document_manifest,
    escape_html,
    escape_latex,
    format_cover_letter_body,
    format_cover_letter_body_html,
    format_cventry,
    format_cventry_html,
    format_cvskill,
    format_cvskill_html,
    format_date_range,
    format_inline_html,
    format_language,
    format_language_html,
    format_leadership_entries,
    generate_document,
    generate_html_document,
    generate_html_sections,
    generate_sections,
    has_entries,
    has_leadership_entries,
    has_publication_entries,
    load_core_content,
    load_cover_letter_content,
    load_cover_letter_variant,
    load_optional_content,
    load_optional_yaml,
    load_shared_paragraph,
    load_variant_paragraph,
    load_yaml,
    main,
    normalize_document_type,
    prepare_personal_html,
    write_document_manifest,
)


if __name__ == "__main__":
    main()
