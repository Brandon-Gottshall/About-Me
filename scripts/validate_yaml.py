#!/usr/bin/env python3
"""Validate generator YAML files."""

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def yaml_files():
    """Return all content and config YAML files."""
    paths = list((ROOT / "config").glob("**/*.yaml"))
    paths += list((ROOT / "content").glob("**/*.yaml"))
    return sorted(paths)


def main():
    """Load every YAML file and report the total checked."""
    paths = yaml_files()
    for path in paths:
        with path.open(encoding="utf-8") as handle:
            yaml.safe_load(handle)
    print(f"YAML validation: {len(paths)} files OK")


if __name__ == "__main__":
    main()
