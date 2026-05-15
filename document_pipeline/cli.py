"""Module CLI for document pipeline commands."""

from __future__ import annotations

import argparse
from collections.abc import Callable

from document_pipeline import builder, export, privacy, showcase, validate
from document_pipeline.html_renderer import render_html_documents
from document_pipeline.renderer import generate_documents


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="document-pipeline",
        description="Validate, generate, build, and export Brandon's official documents.",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    generate_parser = subcommands.add_parser("generate", help="Generate LaTeX files.")
    generate_parser.add_argument("documents", nargs="*")

    build_parser_ = subcommands.add_parser("build", help="Build PDFs with XeLaTeX.")
    build_parser_.add_argument("documents", nargs="*")

    html_parser = subcommands.add_parser(
        "html", help="Render the public HTML document set into output/."
    )
    html_parser.add_argument("documents", nargs="*")

    subcommands.add_parser("validate", help="Validate YAML content and config.")
    subcommands.add_parser(
        "export",
        help="Write exports/profile.json and output/documents.json.",
    )
    subcommands.add_parser("showcase", help="Render showcase preview images.")
    subcommands.add_parser("privacy-scan", help="Scan public surfaces for private data.")
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    handlers: dict[str, Callable[[], None]] = {
        "validate": validate.main,
        "export": export.main,
        "showcase": showcase.main,
        "privacy-scan": privacy.main,
    }

    if args.command == "generate":
        generate_documents(requested=args.documents)
        return
    if args.command == "build":
        builder.main(args.documents)
        return
    if args.command == "html":
        render_html_documents(requested=args.documents or None)
        return

    handlers[args.command]()


if __name__ == "__main__":
    main()
