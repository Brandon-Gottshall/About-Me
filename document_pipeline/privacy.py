"""Privacy checks for public repository surfaces."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from document_pipeline.validate import load_yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_TEXT_ROOTS = ["README.md", "docs", "content", "config", "templates", "scripts"]
UNEXPECTED_PATTERNS = {
    "old personal gmail": re.compile(r"blgottshall@gmail\.com", re.IGNORECASE),
    "old phone number": re.compile(r"229[- ]234[- ]7471|\+1 229-234-7471"),
    "generic twitter placeholder": re.compile(r"twitter\.com/yourhandle", re.IGNORECASE),
    "generic website placeholder": re.compile(r"yourwebsite\.com", re.IGNORECASE),
}


@dataclass(frozen=True)
class Finding:
    path: Path
    label: str
    line: int | None = None

    def render(self) -> str:
        rel_path = self.path.relative_to(PROJECT_ROOT)
        suffix = f":{self.line}" if self.line else ""
        return f"{rel_path}{suffix}: {self.label}"


def iter_public_text_files() -> list[Path]:
    files: list[Path] = []
    for root in PUBLIC_TEXT_ROOTS:
        path = PROJECT_ROOT / root
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(
                item
                for item in path.rglob("*")
                if item.is_file() and item.suffix.lower() in {".md", ".yaml", ".tex", ".py", ".json"}
            )
    return sorted(files)


def scan_text_files() -> list[Finding]:
    findings: list[Finding] = []
    for path in iter_public_text_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for index, line in enumerate(text.splitlines(), start=1):
            for label, pattern in UNEXPECTED_PATTERNS.items():
                if pattern.search(line):
                    findings.append(Finding(path, label, index))
    return findings


def scan_pdf_locations() -> list[Finding]:
    findings: list[Finding] = []
    for path in PROJECT_ROOT.glob("*.pdf"):
        findings.append(Finding(path, "PDF outside output/ is not an official tracked output"))
    return findings


def scan_pdf_text() -> list[Finding]:
    if not shutil.which("pdftotext"):
        return []
    findings: list[Finding] = []
    for path in sorted((PROJECT_ROOT / "output").glob("*.pdf")):
        try:
            result = subprocess.run(
                ["pdftotext", str(path), "-"],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError:
            findings.append(Finding(path, "could not extract PDF text"))
            continue
        for label, pattern in UNEXPECTED_PATTERNS.items():
            if pattern.search(result.stdout):
                findings.append(Finding(path, label))
    return findings


def expected_public_contact_summary() -> list[str]:
    personal = load_yaml(PROJECT_ROOT / "content" / "core" / "personal.yaml")
    contact = personal["contact"]
    return [
        personal["address"],
        contact["mobile"],
        contact["email"],
        contact["homepage"],
        f"github.com/{contact['github']}",
        f"linkedin.com/in/{contact['linkedin']}",
    ]


def main() -> None:
    findings = scan_text_files() + scan_pdf_locations() + scan_pdf_text()
    if findings:
        for finding in findings:
            print(finding.render(), file=sys.stderr)
        sys.exit(1)
    print("Privacy scan passed.")
    print("Expected public contact surfaces:")
    for item in expected_public_contact_summary():
        print(f"- {item}")


if __name__ == "__main__":
    main()
