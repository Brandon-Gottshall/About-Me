#!/usr/bin/env python3
"""Validate YAML content and configuration."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from document_pipeline.validate import main


if __name__ == "__main__":
    main()
