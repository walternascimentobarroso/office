# -*- coding: utf-8 -*-
"""Core utilities for Excel API"""

import json
from pathlib import Path
from typing import Dict, Any


def load_json_mapping(file_path: str) -> Dict[str, Any]:
    """Load JSON mapping file"""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Mapping file not found: {file_path}")

    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def sanitize_filename(name: str) -> str:
    """Sanitize filename for safe file output"""
    return "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()