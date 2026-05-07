"""Format and normalize .env file content."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class FormatResult:
    original: str
    formatted: str
    changes: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return True

    @property
    def changed(self) -> bool:
        return self.original != self.formatted

    def summary(self) -> str:
        if not self.changed:
            return "Already formatted."
        return f"Applied {len(self.changes)} formatting change(s)."


def format_env_text(
    text: str,
    *,
    quote_values: bool = False,
    remove_trailing_spaces: bool = True,
    ensure_newline: bool = True,
    sort_keys: bool = False,
) -> FormatResult:
    """Normalize .env text content according to formatting options."""
    changes: List[str] = []
    lines = text.splitlines()
    output_lines: List[str] = []

    kv_lines: List[str] = []
    other_lines: List[str] = []

    for line in lines:
        stripped = line.rstrip() if remove_trailing_spaces else line
        if remove_trailing_spaces and stripped != line:
            changes.append(f"Removed trailing whitespace: {line!r}")
            line = stripped

        if "=" in line and not line.lstrip().startswith("#"):
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            if quote_values and value and not (value.startswith('"') and value.endswith('"')):
                new_line = f'{key}="{value}"'
                if new_line != line:
                    changes.append(f"Quoted value for key: {key}")
                line = new_line
            kv_lines.append(line)
        else:
            other_lines.append(line)

    if sort_keys:
        original_kv = list(kv_lines)
        kv_lines = sorted(kv_lines, key=lambda l: l.split("=")[0].lower())
        if kv_lines != original_kv:
            changes.append("Sorted keys alphabetically.")
        output_lines = other_lines + kv_lines
    else:
        output_lines = lines if not remove_trailing_spaces else [
            l.rstrip() for l in lines
        ]
        # rebuild properly
        output_lines = []
        kv_iter = iter(kv_lines)
        other_iter = iter(other_lines)
        for orig in lines:
            stripped_orig = orig.rstrip()
            if "=" in stripped_orig and not stripped_orig.lstrip().startswith("#"):
                output_lines.append(next(kv_iter))
            else:
                output_lines.append(next(other_iter))

    formatted = "\n".join(output_lines)
    if ensure_newline and formatted and not formatted.endswith("\n"):
        formatted += "\n"
        changes.append("Added trailing newline.")

    return FormatResult(original=text, formatted=formatted, changes=changes)


def format_env_file(path: str, **kwargs) -> FormatResult:
    """Read, format, and write back a .env file."""
    with open(path, "r") as f:
        text = f.read()
    result = format_env_text(text, **kwargs)
    if result.changed:
        with open(path, "w") as f:
            f.write(result.formatted)
    return result
