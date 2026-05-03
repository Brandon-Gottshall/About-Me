#!/usr/bin/env python3
"""Create a private custom-generation archive run skeleton."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator


REPO_ROOT = Path(__file__).resolve().parents[3]
ARCHIVE_SCHEMA = REPO_ROOT / "schemas" / "archive" / "custom-generation-run.schema.json"


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return re.sub(r"-{2,}", "-", slug) or "custom-generation"


def git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        return "unknown"
    return result.stdout.strip()


def copy_optional_file(source: str | None, destination: Path, run_root: Path) -> list[str]:
    if not source:
        return []
    source_path = Path(source).expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, destination)
    return [str(destination.relative_to(run_root))]


def validate_manifest(manifest: dict) -> None:
    schema = json.loads(ARCHIVE_SCHEMA.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(manifest), key=lambda item: list(item.path))
    if errors:
        for error in errors:
            print(error.message, file=sys.stderr)
        sys.exit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company", required=True)
    parser.add_argument("--role", required=True)
    parser.add_argument("--source-url", default="")
    parser.add_argument("--run-id", default="")
    parser.add_argument("--job-description", default="")
    parser.add_argument("--source-notes", default="")
    parser.add_argument(
        "--tool",
        default="",
        help="Agent that produced the run (e.g. codex, claude). Falls back to ARCHIVE_AGENT_TOOL env, then 'codex'.",
    )
    parser.add_argument(
        "--plugin",
        default="document-generator",
        help="Plugin or skill name recorded in the manifest.",
    )
    return parser.parse_args()


def main() -> None:
    archive_root_env = os.environ.get("CUSTOM_GENERATION_ARCHIVE_ROOT")
    if not archive_root_env:
        print(
            "Set CUSTOM_GENERATION_ARCHIVE_ROOT to the private companion repo before archiving.",
            file=sys.stderr,
        )
        sys.exit(2)

    args = parse_args()
    archive_root = Path(archive_root_env).expanduser().resolve()
    now = datetime.now(timezone.utc)
    run_id = args.run_id or f"{now:%Y-%m-%d}-{slugify(args.company)}-{slugify(args.role)}"
    run_root = archive_root / "runs" / f"{now:%Y}" / run_id
    agent_tool = args.tool or os.environ.get("ARCHIVE_AGENT_TOOL", "") or "codex"

    input_paths = []
    input_paths.extend(
        copy_optional_file(args.job_description, run_root / "input" / "job-description.md", run_root)
    )
    input_paths.extend(
        copy_optional_file(args.source_notes, run_root / "input" / "source-notes.md", run_root)
    )

    for directory in ["prompts", "selected-facts", "drafts", "artifacts/generated-tex", "verification"]:
        (run_root / directory).mkdir(parents=True, exist_ok=True)

    manifest = {
        "runId": run_id,
        "createdAt": now.isoformat(),
        "sourceRepository": {
            "url": "https://github.com/Brandon-Gottshall/About-Me",
            "commit": git_commit(),
        },
        "target": {
            "company": args.company,
            "role": args.role,
            "sourceUrl": args.source_url,
        },
        "agent": {
            "tool": agent_tool,
            "plugin": args.plugin,
        },
        "inputs": input_paths,
        "prompts": [],
        "selectedFacts": [],
        "artifacts": [],
        "verification": {
            "validation": "pending",
            "build": "pending",
            "privacy": "pending",
        },
        "publication": "private",
    }

    validate_manifest(manifest)
    manifest_path = run_root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Created private archive run: {run_root}")


if __name__ == "__main__":
    main()
