"""envault.env_set — Set, update, or delete keys in .env files and vaults.

Provides utilities to programmatically set or remove individual keys
within plaintext .env files or encrypted vault files.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from envault.vault import lock, unlock


@dataclass
class SetResult:
    """Result of a set/delete operation on an env source."""

    key: str
    action: str  # 'set', 'updated', 'deleted', 'noop'
    previous_value: Optional[str] = None
    new_value: Optional[str] = None
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.action != "noop" or not self.warnings

    def summary(self) -> str:
        if self.action == "set":
            return f"Set '{self.key}' (new key)"
        if self.action == "updated":
            return f"Updated '{self.key}'"
        if self.action == "deleted":
            return f"Deleted '{self.key}'"
        return f"No change for '{self.key}'"


def set_key_in_text(text: str, key: str, value: str) -> tuple[str, SetResult]:
    """Set or update a key=value pair in env text.

    Preserves existing comments, blank lines, and key ordering.
    If the key already exists it is updated in-place; otherwise it is
    appended at the end of the file.

    Args:
        text: Raw .env file contents.
        key: The key name to set.
        value: The value to assign.

    Returns:
        A tuple of (updated_text, SetResult).
    """
    lines = text.splitlines(keepends=True)
    updated_lines: list[str] = []
    found = False
    previous_value: Optional[str] = None

    for line in lines:
        stripped = line.rstrip("\n").rstrip("\r")
        # Skip comments and blank lines unchanged
        if stripped.startswith("#") or not stripped.strip():
            updated_lines.append(line)
            continue
        if "=" in stripped:
            k, _, v = stripped.partition("=")
            if k.strip() == key:
                previous_value = v
                new_line = f"{key}={value}\n"
                updated_lines.append(new_line)
                found = True
                continue
        updated_lines.append(line)

    if found:
        result = SetResult(
            key=key,
            action="updated",
            previous_value=previous_value,
            new_value=value,
        )
    else:
        # Ensure file ends with newline before appending
        if updated_lines and not updated_lines[-1].endswith("\n"):
            updated_lines[-1] += "\n"
        updated_lines.append(f"{key}={value}\n")
        result = SetResult(key=key, action="set", previous_value=None, new_value=value)

    return "".join(updated_lines), result


def delete_key_in_text(text: str, key: str) -> tuple[str, SetResult]:
    """Remove a key from env text.

    Args:
        text: Raw .env file contents.
        key: The key name to delete.

    Returns:
        A tuple of (updated_text, SetResult).
    """
    lines = text.splitlines(keepends=True)
    updated_lines: list[str] = []
    found = False
    previous_value: Optional[str] = None

    for line in lines:
        stripped = line.rstrip("\n").rstrip("\r")
        if stripped.startswith("#") or not stripped.strip():
            updated_lines.append(line)
            continue
        if "=" in stripped:
            k, _, v = stripped.partition("=")
            if k.strip() == key:
                previous_value = v
                found = True
                continue  # drop the line
        updated_lines.append(line)

    action = "deleted" if found else "noop"
    warnings = [] if found else [f"Key '{key}' not found; nothing deleted."]
    result = SetResult(
        key=key,
        action=action,
        previous_value=previous_value,
        new_value=None,
        warnings=warnings,
    )
    return "".join(updated_lines), result


def set_key_in_env_file(env_path: Path, key: str, value: str) -> SetResult:
    """Set or update a key in a plaintext .env file on disk."""
    text = env_path.read_text(encoding="utf-8") if env_path.exists() else ""
    new_text, result = set_key_in_text(text, key, value)
    env_path.write_text(new_text, encoding="utf-8")
    return result


def delete_key_in_env_file(env_path: Path, key: str) -> SetResult:
    """Delete a key from a plaintext .env file on disk."""
    if not env_path.exists():
        return SetResult(key=key, action="noop", warnings=[f"{env_path} does not exist."])
    text = env_path.read_text(encoding="utf-8")
    new_text, result = delete_key_in_text(text, key)
    env_path.write_text(new_text, encoding="utf-8")
    return result


def set_key_in_vault(vault_path: Path, key: str, value: str, password: str) -> SetResult:
    """Set or update a key inside an encrypted vault file."""
    text = unlock(str(vault_path), password)
    new_text, result = set_key_in_text(text, key, value)
    lock(new_text, str(vault_path), password)
    return result


def delete_key_in_vault(vault_path: Path, key: str, password: str) -> SetResult:
    """Delete a key from an encrypted vault file."""
    text = unlock(str(vault_path), password)
    new_text, result = delete_key_in_text(text, key)
    lock(new_text, str(vault_path), password)
    return result
