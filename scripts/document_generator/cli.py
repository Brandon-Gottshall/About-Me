"""Command-line entrypoint for document generation."""

import sys
from pathlib import Path

from .content import DEFAULT_DOCUMENTS, ProjectPaths, load_yaml, normalize_document_type
from .html import generate_html_document
from .latex import generate_document
from .manifest import write_document_manifest


def project_paths():
    """Return paths for the repo that owns this package."""
    return ProjectPaths.from_root(Path(__file__).resolve().parents[2])


def main(argv=None):
    """Generate requested documents."""
    args = list(sys.argv[1:] if argv is None else argv)
    paths = project_paths()

    generate_html = "--html" in args or "-h" in args
    args = [arg for arg in args if arg not in ("--html", "-h")]
    output_dir = paths.output_dir if generate_html else paths.generated_dir

    if not paths.content_core_dir.exists():
        print(
            f"Error: Content directory not found at {paths.content_core_dir}",
            file=sys.stderr,
        )
        raise SystemExit(1)

    config_path = paths.config_dir / "documents.yaml"
    if not config_path.exists():
        print(f"Error: Config file not found at {config_path}", file=sys.stderr)
        raise SystemExit(1)

    config = load_yaml(config_path)
    document_args = args or DEFAULT_DOCUMENTS

    for document_arg in document_args:
        doc_type = normalize_document_type(document_arg)
        if doc_type not in config:
            print(f"Unknown document type: {document_arg}")
            continue

        if generate_html:
            generate_html_document(
                doc_type,
                paths.content_core_dir,
                paths.content_optional_dir,
                paths.config_dir,
                config,
                output_dir,
            )
        else:
            generate_document(
                doc_type,
                paths.content_core_dir,
                paths.content_optional_dir,
                paths.config_dir,
                config,
                output_dir,
            )

    if generate_html:
        write_document_manifest(output_dir)
