from __future__ import annotations

import re
from pathlib import Path

SAFE_NAME_PATTERN = re.compile(r"[^a-zA-Z0-9._-]+")


def sanitize_name(value: str) -> str:
    cleaned = SAFE_NAME_PATTERN.sub("_", value).strip("_")
    return cleaned or "dataset"


def ensure_path_within(base: Path, target: Path) -> Path:
    resolved_base = base.resolve()
    resolved_target = target.resolve()
    if resolved_base not in resolved_target.parents and resolved_target != resolved_base:
        raise ValueError("Invalid path outside project scope")
    return resolved_target
