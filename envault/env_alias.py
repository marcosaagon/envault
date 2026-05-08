"""Alias management: map short names to vault keys."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional


def _aliases_path(vault_path: Path) -> Path:
    return vault_path.parent / ".envault_aliases.json"


def load_aliases(vault_path: Path) -> Dict[str, str]:
    """Load alias→key mappings from disk. Returns empty dict if none exist."""
    path = _aliases_path(vault_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_aliases(vault_path: Path, aliases: Dict[str, str]) -> None:
    """Persist alias mappings to disk."""
    path = _aliases_path(vault_path)
    path.write_text(json.dumps(aliases, indent=2))


def add_alias(vault_path: Path, alias: str, key: str) -> bool:
    """Register *alias* as a short name for *key*. Returns True if newly added."""
    aliases = load_aliases(vault_path)
    is_new = alias not in aliases
    aliases[alias] = key
    save_aliases(vault_path, aliases)
    return is_new


def remove_alias(vault_path: Path, alias: str) -> bool:
    """Remove *alias*. Returns True if it existed."""
    aliases = load_aliases(vault_path)
    if alias not in aliases:
        return False
    del aliases[alias]
    save_aliases(vault_path, aliases)
    return True


def resolve_alias(vault_path: Path, alias: str) -> Optional[str]:
    """Return the key name for *alias*, or None if unknown."""
    return load_aliases(vault_path).get(alias)


def list_aliases(vault_path: Path) -> Dict[str, str]:
    """Return all alias→key mappings."""
    return load_aliases(vault_path)
