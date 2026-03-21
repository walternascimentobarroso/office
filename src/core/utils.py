# -*- coding: utf-8 -*-
"""Core utilities for Excel API."""

import json
from pathlib import Path
from typing import Any, Dict

from src.core.exceptions import MappingError


def load_json_mapping(file_path: str) -> Dict[str, Any]:
    """Load JSON mapping file."""

    path = Path(file_path)
    if not path.exists():
        raise MappingError(f"Mapping file not found: {file_path}")

    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise MappingError(f"Invalid JSON in mapping file {file_path}: {e}") from e


def sanitize_filename(name: str) -> str:
    """Sanitize filename for safe file output."""

    return "".join(c for c in name if c.isalnum() or c in (" ", "-", "_")).rstrip()
