"""Copy (clone) keys from one env/vault source to another, with optional key filtering."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from envault.crypto import decrypt, encrypt


@dataclass
class CopyResult:
    copied: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    overwritten: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return bool(self.copied or self.overwritten)

    def summary(self) -> str:
        parts = []
        if self.copied:
            parts.append(f"{len(self.copied)} copied")
        if self.overwritten:
            parts.append(f"{len(self.overwritten)} overwritten")
        if self.skipped:
            parts.append(f"{len(self.skipped)} skipped")
        return ", ".join(parts) if parts else "nothing changed"


def parse_env_text(text: str) -> dict[str, str]:
    """Parse .env text into a key->value dict, ignoring comments and blanks."""
    result: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        key = key.strip()
        if key:
            result[key] = value.strip()
    return result


def copy_keys(
    source_text: str,
    dest_text: str,
    keys: Optional[list[str]] = None,
    overwrite: bool = False,
) -> tuple[str, CopyResult]:
    """Copy keys from source env text into dest env text.

    Args:
        source_text: The source .env content.
        dest_text: The destination .env content.
        keys: Optional list of specific keys to copy; copies all if None.
        overwrite: If True, overwrite existing keys in dest.

    Returns:
        Tuple of (new dest text, CopyResult).
    """
    src = parse_env_text(source_text)
    dst = parse_env_text(dest_text)
    result = CopyResult()

    candidates = keys if keys is not None else list(src.keys())

    lines = [l for l in dest_text.splitlines() if l.strip()]
    added_lines: list[str] = []

    for key in candidates:
        if key not in src:
            result.skipped.append(key)
            continue
        if key in dst:
            if not overwrite:
                result.skipped.append(key)
                continue
            # Replace existing line
            lines = [
                f"{key}={src[key]}" if l.strip().startswith(f"{key}=") else l
                for l in lines
            ]
            result.overwritten.append(key)
        else:
            added_lines.append(f"{key}={src[key]}")
            result.copied.append(key)

    all_lines = lines + added_lines
    new_text = "\n".join(all_lines) + ("\n" if all_lines else "")
    return new_text, result


def copy_keys_between_vaults(
    src_vault: Path,
    src_password: str,
    dst_vault: Path,
    dst_password: str,
    keys: Optional[list[str]] = None,
    overwrite: bool = False,
) -> CopyResult:
    """Copy keys from one encrypted vault to another."""
    src_text = decrypt(src_vault.read_text(), src_password)
    dst_text = decrypt(dst_vault.read_text(), dst_password)

    new_dst_text, result = copy_keys(src_text, dst_text, keys=keys, overwrite=overwrite)

    dst_vault.write_text(encrypt(new_dst_text, dst_password))
    return result
