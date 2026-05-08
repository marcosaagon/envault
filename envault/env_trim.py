"""Trim leading/trailing whitespace from env variable values."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple

from envault.vault import lock, unlock


@dataclass
class TrimResult:
    trimmed_keys: List[str] = field(default_factory=list)
    output_text: str = ""

    @property
    def ok(self) -> bool:
        return True

    @property
    def changed(self) -> bool:
        return len(self.trimmed_keys) > 0

    @property
    def summary(self) -> str:
        if not self.changed:
            return "No values needed trimming."
        keys = ", ".join(self.trimmed_keys)
        return f"Trimmed {len(self.trimmed_keys)} key(s): {keys}"


def trim_env_text(text: str) -> TrimResult:
    """Trim whitespace from values in env text. Returns a TrimResult."""
    lines: List[str] = []
    trimmed_keys: List[str] = []

    for line in text.splitlines(keepends=True):
        stripped = line.rstrip("\n")
        if stripped.lstrip().startswith("#") or "=" not in stripped:
            lines.append(line)
            continue

        key, _, value = stripped.partition("=")
        trimmed_value = value.strip()
        if trimmed_value != value:
            trimmed_keys.append(key.strip())
        lines.append(f"{key}={trimmed_value}\n")

    return TrimResult(trimmed_keys=trimmed_keys, output_text="".join(lines))


def trim_env_file(path: Path) -> TrimResult:
    """Trim whitespace from values in a .env file in-place."""
    text = path.read_text()
    result = trim_env_text(text)
    if result.changed:
        path.write_text(result.output_text)
    return result


def trim_vault(vault_path: Path, password: str) -> TrimResult:
    """Decrypt a vault, trim values, and re-encrypt in-place."""
    text = unlock(vault_path, password)
    result = trim_env_text(text)
    if result.changed:
        lock(result.output_text, vault_path, password)
    return result
