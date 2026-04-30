"""Merge two .env files or vaults, with conflict detection and resolution strategies."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class ConflictStrategy(str, Enum):
    OURS = "ours"
    THEIRS = "theirs"
    PROMPT = "prompt"


@dataclass
class MergeConflict:
    key: str
    ours: Optional[str]
    theirs: Optional[str]


@dataclass
class MergeResult:
    merged: Dict[str, str]
    conflicts: List[MergeConflict] = field(default_factory=list)
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    overwritten: List[str] = field(default_factory=list)

    @property
    def has_conflicts(self) -> bool:
        return len(self.conflicts) > 0


def parse_env(text: str) -> Dict[str, str]:
    """Parse .env text into a key/value dict, skipping comments and blanks."""
    result: Dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        result[key.strip()] = value.strip()
    return result


def merge_envs(
    base: Dict[str, str],
    theirs: Dict[str, str],
    strategy: ConflictStrategy = ConflictStrategy.OURS,
) -> MergeResult:
    """Merge two env dicts. Keys only in theirs are added; conflicts resolved by strategy."""
    merged = dict(base)
    conflicts: List[MergeConflict] = []
    added: List[str] = []
    removed: List[str] = []
    overwritten: List[str] = []

    all_keys = set(base) | set(theirs)

    for key in all_keys:
        in_base = key in base
        in_theirs = key in theirs

        if in_base and not in_theirs:
            # Key removed in theirs — keep ours (base)
            removed.append(key)
        elif not in_base and in_theirs:
            # New key from theirs
            merged[key] = theirs[key]
            added.append(key)
        elif base[key] != theirs[key]:
            # Conflict
            conflict = MergeConflict(key=key, ours=base[key], theirs=theirs[key])
            conflicts.append(conflict)
            if strategy == ConflictStrategy.THEIRS:
                merged[key] = theirs[key]
                overwritten.append(key)
            # OURS: keep base value (already in merged)

    return MergeResult(
        merged=merged,
        conflicts=conflicts,
        added=added,
        removed=removed,
        overwritten=overwritten,
    )


def serialize_env(env: Dict[str, str]) -> str:
    """Serialize a key/value dict back to .env format."""
    return "\n".join(f"{k}={v}" for k, v in sorted(env.items())) + "\n"
