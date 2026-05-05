"""Rename keys in .env files and encrypted vaults."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from envault.crypto import decrypt, encrypt


@dataclass
class RenameResult:
    old_key: str
    new_key: str
    renamed: bool
    message: str = ""

    @property
    def ok(self) -> bool:
        return self.renamed


def rename_key_in_text(env_text: str, old_key: str, new_key: str) -> tuple[str, RenameResult]:
    """Rename a key in raw .env text. Returns updated text and result."""
    lines = env_text.splitlines(keepends=True)
    found = False
    output_lines = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#") or "=" not in stripped:
            output_lines.append(line)
            continue

        key, _, rest = stripped.partition("=")
        key = key.strip()

        if key == old_key:
            if found:
                # duplicate — rename all occurrences
                pass
            found = True
            # preserve original line ending
            ending = line[len(line.rstrip("\n\r")):]  
            output_lines.append(f"{new_key}={rest}{ending}")
        else:
            output_lines.append(line)

    if not found:
        result = RenameResult(
            old_key=old_key,
            new_key=new_key,
            renamed=False,
            message=f"Key '{old_key}' not found.",
        )
        return env_text, result

    result = RenameResult(
        old_key=old_key,
        new_key=new_key,
        renamed=True,
        message=f"Renamed '{old_key}' -> '{new_key}'.",
    )
    return "".join(output_lines), result


def rename_key_in_env_file(path: str, old_key: str, new_key: str) -> RenameResult:
    """Rename a key directly in a plaintext .env file."""
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()

    updated, result = rename_key_in_text(text, old_key, new_key)

    if result.renamed:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(updated)

    return result


def rename_key_in_vault(vault_path: str, password: str, old_key: str, new_key: str) -> RenameResult:
    """Rename a key inside an encrypted vault file."""
    with open(vault_path, "r", encoding="utf-8") as fh:
        blob = fh.read().strip()

    plaintext = decrypt(blob, password)
    updated, result = rename_key_in_text(plaintext, old_key, new_key)

    if result.renamed:
        new_blob = encrypt(updated, password)
        with open(vault_path, "w", encoding="utf-8") as fh:
            fh.write(new_blob)

    return result
