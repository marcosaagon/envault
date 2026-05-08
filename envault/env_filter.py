"""Filter keys from .env text or vault by prefix, suffix, or pattern."""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class FilterResult:
    matched_keys: List[str] = field(default_factory=list)
    filtered_text: str = ""
    total_keys: int = 0

    @property
    def ok(self) -> bool:
        return len(self.matched_keys) > 0

    def summary(self) -> str:
        return (
            f"Matched {len(self.matched_keys)} of {self.total_keys} keys."
        )


def parse_env_text(text: str) -> dict[str, str]:
    """Parse .env text into a key-value dict, ignoring comments and blanks."""
    result: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        result[key.strip()] = value.strip()
    return result


def filter_env_text(
    text: str,
    *,
    prefix: Optional[str] = None,
    suffix: Optional[str] = None,
    pattern: Optional[str] = None,
    regex: Optional[str] = None,
    invert: bool = False,
) -> FilterResult:
    """Return only lines whose keys match the given filter criteria."""
    all_keys = parse_env_text(text)
    total = len(all_keys)
    output_lines: list[str] = []
    matched: list[str] = []

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            output_lines.append(line)
            continue

        key = stripped.partition("=")[0].strip()
        keep = _matches(key, prefix=prefix, suffix=suffix, pattern=pattern, regex=regex)
        if invert:
            keep = not keep

        if keep:
            output_lines.append(line)
            matched.append(key)

    return FilterResult(
        matched_keys=matched,
        filtered_text="\n".join(output_lines),
        total_keys=total,
    )


def _matches(
    key: str,
    *,
    prefix: Optional[str],
    suffix: Optional[str],
    pattern: Optional[str],
    regex: Optional[str],
) -> bool:
    if prefix is not None and not key.startswith(prefix):
        return False
    if suffix is not None and not key.endswith(suffix):
        return False
    if pattern is not None and not fnmatch.fnmatch(key, pattern):
        return False
    if regex is not None and not re.search(regex, key):
        return False
    return True
