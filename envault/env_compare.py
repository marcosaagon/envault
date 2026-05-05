"""Compare two .env files or vaults and report differences."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class CompareResult:
    only_in_left: List[str] = field(default_factory=list)
    only_in_right: List[str] = field(default_factory=list)
    value_changed: List[Tuple[str, str, str]] = field(default_factory=list)  # (key, left_val, right_val)
    identical: List[str] = field(default_factory=list)

    @property
    def has_differences(self) -> bool:
        return bool(self.only_in_left or self.only_in_right or self.value_changed)

    def summary(self) -> str:
        parts = []
        if self.only_in_left:
            parts.append(f"{len(self.only_in_left)} only in left")
        if self.only_in_right:
            parts.append(f"{len(self.only_in_right)} only in right")
        if self.value_changed:
            parts.append(f"{len(self.value_changed)} value(s) changed")
        if not parts:
            return "Files are identical."
        return ", ".join(parts) + "."


def parse_env_text(text: str) -> Dict[str, str]:
    """Parse .env text into a key-value dict, ignoring comments and blanks."""
    result = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        key = key.strip()
        value = value.strip()
        if key:
            result[key] = value
    return result


def compare_envs(left: Dict[str, str], right: Dict[str, str]) -> CompareResult:
    """Compare two parsed env dicts and return a CompareResult."""
    result = CompareResult()
    all_keys = set(left) | set(right)
    for key in sorted(all_keys):
        in_left = key in left
        in_right = key in right
        if in_left and not in_right:
            result.only_in_left.append(key)
        elif in_right and not in_left:
            result.only_in_right.append(key)
        elif left[key] != right[key]:
            result.value_changed.append((key, left[key], right[key]))
        else:
            result.identical.append(key)
    return result


def compare_env_texts(left_text: str, right_text: str) -> CompareResult:
    """Compare two raw .env strings."""
    return compare_envs(parse_env_text(left_text), parse_env_text(right_text))


def format_compare_result(result: CompareResult, mask_values: bool = False) -> str:
    """Format a CompareResult into a human-readable string."""
    lines = []
    for key in result.only_in_left:
        lines.append(f"< {key}")
    for key in result.only_in_right:
        lines.append(f"> {key}")
    for key, lval, rval in result.value_changed:
        if mask_values:
            lines.append(f"~ {key}: [hidden] -> [hidden]")
        else:
            lines.append(f"~ {key}: {lval!r} -> {rval!r}")
    if not lines:
        return "(no differences)"
    return "\n".join(lines)
