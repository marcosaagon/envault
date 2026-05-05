"""Tag management for vault entries — group and filter env vars by tag."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

_TAGS_FILENAME = ".envault_tags.json"


def _tags_path(directory: str = ".") -> Path:
    return Path(directory) / _TAGS_FILENAME


def load_tags(directory: str = ".") -> Dict[str, List[str]]:
    """Load tag mappings {key: [tag, ...]} from the tags file."""
    path = _tags_path(directory)
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_tags(tags: Dict[str, List[str]], directory: str = ".") -> None:
    """Persist tag mappings to disk."""
    path = _tags_path(directory)
    with path.open("w", encoding="utf-8") as f:
        json.dump(tags, f, indent=2)


def add_tag(key: str, tag: str, directory: str = ".") -> None:
    """Add a tag to an env key."""
    tags = load_tags(directory)
    existing = tags.get(key, [])
    if tag not in existing:
        existing.append(tag)
    tags[key] = existing
    save_tags(tags, directory)


def remove_tag(key: str, tag: str, directory: str = ".") -> None:
    """Remove a tag from an env key."""
    tags = load_tags(directory)
    existing = tags.get(key, [])
    tags[key] = [t for t in existing if t != tag]
    if not tags[key]:
        del tags[key]
    save_tags(tags, directory)


def keys_for_tag(tag: str, directory: str = ".") -> List[str]:
    """Return all env keys that have the given tag."""
    tags = load_tags(directory)
    return [key for key, key_tags in tags.items() if tag in key_tags]


def tags_for_key(key: str, directory: str = ".") -> List[str]:
    """Return all tags assigned to a specific env key."""
    tags = load_tags(directory)
    return tags.get(key, [])


def all_tags(directory: str = ".") -> List[str]:
    """Return a sorted list of all unique tags in use."""
    tags = load_tags(directory)
    unique: set = set()
    for key_tags in tags.values():
        unique.update(key_tags)
    return sorted(unique)
