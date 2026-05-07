"""Strip comments and blank lines from .env files or vault contents."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from envault.crypto import decrypt, encrypt


@dataclass
class StripResult:
    original_lines: int = 0
    stripped_lines: int = 0
    removed_comments: int = 0
    removed_blanks: int = 0
    output: str = ""

    @property
    def ok(self) -> bool:
        return True

    @property
    def summary(self) -> str:
        removed = self.original_lines - self.stripped_lines
        return (
            f"Stripped {removed} line(s): "
            f"{self.removed_comments} comment(s), "
            f"{self.removed_blanks} blank(s)."
        )


def strip_env_text(
    text: str,
    remove_comments: bool = True,
    remove_blanks: bool = True,
) -> StripResult:
    """Strip comments and/or blank lines from env text."""
    lines = text.splitlines()
    original_lines = len(lines)
    removed_comments = 0
    removed_blanks = 0
    kept: list[str] = []

    for line in lines:
        stripped = line.strip()
        if remove_comments and stripped.startswith("#"):
            removed_comments += 1
            continue
        if remove_blanks and stripped == "":
            removed_blanks += 1
            continue
        kept.append(line)

    output = "\n".join(kept)
    if output and not output.endswith("\n"):
        output += "\n"

    return StripResult(
        original_lines=original_lines,
        stripped_lines=len(kept),
        removed_comments=removed_comments,
        removed_blanks=removed_blanks,
        output=output,
    )


def strip_env_file(
    path: Path,
    remove_comments: bool = True,
    remove_blanks: bool = True,
) -> StripResult:
    """Strip comments and blank lines from a .env file in place."""
    text = path.read_text(encoding="utf-8")
    result = strip_env_text(text, remove_comments=remove_comments, remove_blanks=remove_blanks)
    path.write_text(result.output, encoding="utf-8")
    return result


def strip_vault(
    vault_path: Path,
    password: str,
    remove_comments: bool = True,
    remove_blanks: bool = True,
) -> StripResult:
    """Decrypt a vault, strip its contents, and re-encrypt in place."""
    ciphertext = vault_path.read_text(encoding="utf-8")
    plaintext = decrypt(ciphertext, password)
    result = strip_env_text(plaintext, remove_comments=remove_comments, remove_blanks=remove_blanks)
    new_ciphertext = encrypt(result.output, password)
    vault_path.write_text(new_ciphertext, encoding="utf-8")
    return result
