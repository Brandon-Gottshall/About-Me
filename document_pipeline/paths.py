"""Repository path helpers for the document pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectPaths:
    """Resolved paths used by generator, build, export, and validation code."""

    root: Path

    @classmethod
    def from_root(cls, root: Path | str | None = None) -> "ProjectPaths":
        if root is None:
            root_path = Path(__file__).resolve().parents[1]
        else:
            root_path = Path(root)
        return cls(root=root_path.resolve())

    @property
    def content_dir(self) -> Path:
        return self.root / "content"

    @property
    def content_core_dir(self) -> Path:
        return self.content_dir / "core"

    @property
    def content_optional_dir(self) -> Path:
        return self.content_dir / "optional"

    @property
    def config_dir(self) -> Path:
        return self.root / "config"

    @property
    def generated_dir(self) -> Path:
        return self.root / "generated"

    @property
    def output_dir(self) -> Path:
        return self.root / "output"

    @property
    def templates_dir(self) -> Path:
        return self.root / "templates"

    @property
    def section_templates_dir(self) -> Path:
        return self.templates_dir / "sections"

    @property
    def exports_dir(self) -> Path:
        return self.root / "exports"
