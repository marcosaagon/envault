"""Sort keys in .env files or vaults alphabetically or by custom order."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from envault.crypto import decrypt, encrypt


@dataclass
class SortResult:
    success: bool
    original_lines: List[str] = field(default_factory=list)
    sorted_lines: List[str] = field(default_factory=list)
    keys_sorted: int = 0
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.success

    @property
    def changed(self) -> bool:
        return self.original_lines != self.sorted_lines

    def summary(self) -> str:
        if not self.success:
            return f"Sort failed: {self.error}"
        if not self.changed:
            return "Already sorted — no changes made."
        return f"Sorted {self.keys_sorted} key(s) alphabetically."


def sort_env_text(text: str, reverse: bool = False) -> SortResult:
    """Sort key=value lines in env text, preserving comments and blanks in place."""
    original_lines = text.splitlines()
    blocks: List[List[str]] = []
    current_block: List[str] = []

    for line in original_lines:
        stripped = line.strip()
        if stripped.startswith("#") or stripped == "":
            if current_block:
                blocks.append(current_block)
                current_block = []
            blocks.append([line])
        else:
            current_block.append(line)

    if current_block:
        blocks.append(current_block)

    sorted_blocks = []
    keys_sorted = 0
    for block in blocks:
        if len(block) == 1 and (block[0].strip().startswith("#") or block[0].strip() == ""):
            sorted_blocks.append(block)
        else:
            sorted_block = sorted(block, key=lambda l: l.split("=", 1)[0].strip().lower(), reverse=reverse)
            keys_sorted += len(sorted_block)
            sorted_blocks.append(sorted_block)

    sorted_lines = [line for block in sorted_blocks for line in block]
    return SortResult(
        success=True,
        original_lines=original_lines,
        sorted_lines=sorted_lines,
        keys_sorted=keys_sorted,
    )


def sort_env_file(env_path: Path, reverse: bool = False, dry_run: bool = False) -> SortResult:
    """Sort an .env file in-place (unless dry_run)."""
    if not env_path.exists():
        return SortResult(success=False, error=f"File not found: {env_path}")
    text = env_path.read_text()
    result = sort_env_text(text, reverse=reverse)
    if result.ok and result.changed and not dry_run:
        env_path.write_text("\n".join(result.sorted_lines) + "\n")
    return result


def sort_vault(vault_path: Path, password: str, reverse: bool = False, dry_run: bool = False) -> SortResult:
    """Sort keys inside an encrypted vault file."""
    if not vault_path.exists():
        return SortResult(success=False, error=f"Vault not found: {vault_path}")
    try:
        blob = vault_path.read_text().strip()
        plaintext = decrypt(blob, password)
        result = sort_env_text(plaintext, reverse=reverse)
        if result.ok and result.changed and not dry_run:
            new_text = "\n".join(result.sorted_lines) + "\n"
            new_blob = encrypt(new_text, password)
            vault_path.write_text(new_blob)
        return result
    except Exception as exc:
        return SortResult(success=False, error=str(exc))
