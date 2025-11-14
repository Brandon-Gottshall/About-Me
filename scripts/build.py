#!/usr/bin/env python3
"""
Build automation script for LaTeX documents.
Runs generator and compiles LaTeX documents to PDF.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, cwd=None, check=True):
    """Run a shell command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        if check:
            sys.exit(result.returncode)
    return result


def build_latex(tex_file, output_dir, num_passes=2):
    """Build a LaTeX file to PDF."""
    tex_path = Path(tex_file)
    tex_dir = tex_path.parent

    # Change to generated directory for compilation (so relative paths work)
    for i in range(num_passes):
        result = run_command(
            [
                "xelatex",
                "-output-directory",
                str(output_dir),
                "-interaction=nonstopmode",
                "-halt-on-error",
                tex_path.name,
            ],
            cwd=str(tex_dir),
            check=(i == num_passes - 1),  # Only fail on last pass
        )

        if result.returncode != 0:
            print(f"LaTeX compilation failed on pass {i+1}", file=sys.stderr)
            return False

    return True


def main():
    """Main entry point."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    generated_dir = project_root / "generated"
    output_dir = project_root / "output"

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Run generator first
    print("Generating LaTeX files...")
    generate_result = run_command(
        [sys.executable, str(script_dir / "generate.py")] + sys.argv[1:],
        cwd=str(project_root),
    )

    if generate_result.returncode != 0:
        print("Generator failed!", file=sys.stderr)
        sys.exit(1)

    # Determine which documents to build
    if len(sys.argv) > 1:
        doc_types = sys.argv[1:]
    else:
        doc_types = ["resume", "cv", "cover-letter"]

    # Build each document
    for doc_type in doc_types:
        if doc_type == "resume":
            tex_file = generated_dir / "resume.tex"
            if tex_file.exists():
                print(f"\nBuilding resume...")
                if build_latex(tex_file, output_dir):
                    print(f"✓ Resume built successfully: {output_dir / 'resume.pdf'}")
                else:
                    print(f"✗ Resume build failed", file=sys.stderr)
            else:
                print(f"Warning: {tex_file} not found. Run generator first.")

        elif doc_type == "cv":
            tex_file = generated_dir / "cv.tex"
            if tex_file.exists():
                print(f"\nBuilding CV...")
                if build_latex(tex_file, output_dir):
                    print(f"✓ CV built successfully: {output_dir / 'cv.pdf'}")
                else:
                    print(f"✗ CV build failed", file=sys.stderr)
            else:
                print(f"Warning: {tex_file} not found. Run generator first.")

        elif doc_type == "cover-letter":
            tex_file = generated_dir / "coverletter.tex"
            if tex_file.exists():
                print(f"\nBuilding cover letter...")
                if build_latex(tex_file, output_dir):
                    cover_letter_pdf = output_dir / "coverletter.pdf"
                    if cover_letter_pdf.exists():
                        print(f"✓ Cover letter built successfully: {cover_letter_pdf}")
                    else:
                        print(
                            f"✗ Cover letter PDF not found at expected location",
                            file=sys.stderr,
                        )
                else:
                    print(f"✗ Cover letter build failed", file=sys.stderr)
            else:
                print(f"Warning: {tex_file} not found. Run generator first.")

        elif doc_type in ["leadership-resume", "leadership_resume"]:
            tex_file = generated_dir / "leadership_resume.tex"
            if tex_file.exists():
                print(f"\nBuilding leadership resume...")
                if build_latex(tex_file, output_dir):
                    leadership_pdf = output_dir / "leadership_resume.pdf"
                    if leadership_pdf.exists():
                        print(
                            f"✓ Leadership resume built successfully: {leadership_pdf}"
                        )
                    else:
                        print(
                            f"✗ Leadership resume PDF not found at expected location",
                            file=sys.stderr,
                        )
                else:
                    print(f"✗ Leadership resume build failed", file=sys.stderr)
            else:
                print(f"Warning: {tex_file} not found. Run generator first.")

        else:
            print(f"Unknown document type: {doc_type}", file=sys.stderr)


if __name__ == "__main__":
    main()
