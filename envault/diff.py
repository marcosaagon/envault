"""Diff utilities for comparing .env vault snapshots."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class DiffResult:
    added: Dict[str, str] = field(default_factory=dict)
    removed: Dict[str, str] = field(default_factory=dict)
    changed: List[Tuple[str, str, str]] = field(default_factory=list)  # key, old, new
    unchanged: List[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.changed)


def parse_env(content: str) -> Dict[str, str]:
    """Parse .env file content into a key-value dictionary."""
    result: Dict[str, str] = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        result[key.strip()] = value.strip()
    return result


def diff_envs(old_content: str, new_content: str) -> DiffResult:
    """Compare two .env file contents and return a DiffResult."""
    old = parse_env(old_content)
    new = parse_env(new_content)

    result = DiffResult()

    all_keys = set(old) | set(new)
    for key in sorted(all_keys):
        if key in old and key not in new:
            result.removed[key] = old[key]
        elif key not in old and key in new:
            result.added[key] = new[key]
        elif old[key] != new[key]:
            result.changed.append((key, old[key], new[key]))
        else:
            result.unchanged.append(key)

    return result


def format_diff(result: DiffResult, mask_values: bool = True) -> str:
    """Format a DiffResult as a human-readable string."""
    lines: List[str] = []

    def _val(v: str) -> str:
        return "***" if mask_values else v

    for key, val in result.added.items():
        lines.append(f"+ {key}={_val(val)}")
    for key, val in result.removed.items():
        lines.append(f"- {key}={_val(val)}")
    for key, old, new in result.changed:
        lines.append(f"~ {key}: {_val(old)} -> {_val(new)}")

    if not lines:
        return "No changes detected."
    return "\n".join(lines)
