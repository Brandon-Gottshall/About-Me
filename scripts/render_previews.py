#!/usr/bin/env python3
"""Render showcase preview images from official PDFs."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from document_pipeline.showcase import main


if __name__ == "__main__":
    main()
