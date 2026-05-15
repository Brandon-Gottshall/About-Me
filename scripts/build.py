#!/usr/bin/env python3
"""Generate documents and compile LaTeX outputs to PDF."""

import subprocess
import sys
from pathlib import Path


DOCUMENTS = {
    "resume": {
        "label": "Resume",
        "build_name": "resume",
        "tex": "resume.tex",
        "pdf": "resume.pdf",
    },
    "cv": {
        "label": "CV",
        "build_name": "CV",
        "tex": "cv.tex",
        "pdf": "cv.pdf",
    },
    "cover-letter": {
        "label": "Cover letter",
        "build_name": "cover letter",
        "tex": "coverletter.tex",
        "pdf": "coverletter.pdf",
    },
    "leadership-resume": {
        "label": "Leadership resume",
        "build_name": "leadership resume",
        "tex": "leadership_resume.tex",
        "pdf": "leadership_resume.pdf",
    },
}

DOCUMENT_ALIASES = {
    "cover_letter": "cover-letter",
    "leadership_resume": "leadership-resume",
}

DEFAULT_DOCUMENTS = ["resume", "cv", "cover-letter", "leadership-resume"]


def normalize_doc_type(doc_type):
    """Return the canonical build document name."""
    return DOCUMENT_ALIASES.get(doc_type, doc_type)


def run_command(cmd, cwd=None, check=True):
    """Run a command and return the completed process."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        if check:
            raise SystemExit(result.returncode)
    return result


def build_latex(tex_file, output_dir, num_passes=2):
    """Compile a LaTeX file to PDF."""
    tex_path = Path(tex_file)

    for pass_index in range(num_passes):
        result = run_command(
            [
                "xelatex",
                "-output-directory",
                str(output_dir),
                "-interaction=nonstopmode",
                "-halt-on-error",
                tex_path.name,
            ],
            cwd=str(tex_path.parent),
            check=(pass_index == num_passes - 1),
        )

        if result.returncode != 0:
            print(
                f"LaTeX compilation failed on pass {pass_index + 1}",
                file=sys.stderr,
            )
            return False

    return True


def run_generator(script_dir, project_root, generate_html, doc_args):
    """Run the YAML generator before building or publishing outputs."""
    if generate_html:
        print("Generating HTML files...")
        command = [sys.executable, str(script_dir / "generate.py"), "--html"]
    else:
        print("Generating LaTeX files...")
        command = [sys.executable, str(script_dir / "generate.py")]

    return run_command(command + doc_args, cwd=str(project_root))


def build_document(doc_type, generated_dir, output_dir):
    """Build one PDF document."""
    canonical_type = normalize_doc_type(doc_type)
    document = DOCUMENTS.get(canonical_type)
    if not document:
        print(f"Unknown document type: {doc_type}", file=sys.stderr)
        return False

    tex_file = generated_dir / document["tex"]
    pdf_file = output_dir / document["pdf"]

    if not tex_file.exists():
        print(f"Warning: {tex_file} not found. Run generator first.")
        return False

    print(f"\nBuilding {document['build_name']}...")
    if not build_latex(tex_file, output_dir):
        print(f"✗ {document['label']} build failed", file=sys.stderr)
        return False

    if not pdf_file.exists():
        print(
            f"✗ {document['label']} PDF not found at expected location",
            file=sys.stderr,
        )
        return False

    print(f"✓ {document['label']} built successfully: {pdf_file}")
    return True


def main():
    """Build requested PDF files, or generate requested HTML files."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    generated_dir = project_root / "generated"
    output_dir = project_root / "output"

    generate_html = "--html" in sys.argv or "-h" in sys.argv
    doc_args = [arg for arg in sys.argv[1:] if arg not in ("--html", "-h")]
    output_dir.mkdir(parents=True, exist_ok=True)

    generate_result = run_generator(script_dir, project_root, generate_html, doc_args)
    if generate_result.returncode != 0:
        print("Generator failed!", file=sys.stderr)
        raise SystemExit(1)

    if generate_html:
        print("\n✓ HTML files generated successfully")
        return

    requested_docs = doc_args or DEFAULT_DOCUMENTS
    failures = [
        doc_type
        for doc_type in requested_docs
        if not build_document(doc_type, generated_dir, output_dir)
    ]

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
