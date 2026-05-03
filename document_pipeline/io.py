"""Small IO helpers shared across the document pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def latex_environment(template_dir: Path) -> Environment:
    return Environment(
        loader=FileSystemLoader(str(template_dir)),
        variable_start_string="<<",
        variable_end_string=">>",
        block_start_string="<@",
        block_end_string="@>",
        comment_start_string="<#",
        comment_end_string="#>",
    )
