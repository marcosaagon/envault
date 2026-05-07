"""Pin specific keys in a vault so they are protected from overwrite during merge/import."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


def _pins_path(vault_path: Path) -> Path:
    """Return the path to the pins file for a given vault."""
    return vault_path.with_suffix(".pins.json")


def load_pins(vault_path: Path) -> list[str]:
    """Load pinned keys for a vault. Returns empty list if no pins file exists."""
    path = _pins_path(vault_path)
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("pinned", [])


def save_pins(vault_path: Path, pins: list[str]) -> None:
    """Save pinned keys for a vault."""
    path = _pins_path(vault_path)
    with path.open("w", encoding="utf-8") as f:
        json.dump({"pinned": sorted(set(pins))}, f, indent=2)


def pin_key(vault_path: Path, key: str) -> bool:
    """Pin a key. Returns True if newly pinned, False if already pinned."""
    pins = load_pins(vault_path)
    if key in pins:
        return False
    pins.append(key)
    save_pins(vault_path, pins)
    return True


def unpin_key(vault_path: Path, key: str) -> bool:
    """Unpin a key. Returns True if removed, False if it was not pinned."""
    pins = load_pins(vault_path)
    if key not in pins:
        return False
    pins = [p for p in pins if p != key]
    save_pins(vault_path, pins)
    return True


def is_pinned(vault_path: Path, key: str) -> bool:
    """Return True if the given key is pinned."""
    return key in load_pins(vault_path)


def filter_pinned(vault_path: Path, keys: list[str]) -> list[str]:
    """Return only the keys from the provided list that are pinned."""
    pins = set(load_pins(vault_path))
    return [k for k in keys if k in pins]
