"""Template support: generate a .env.template from an existing .env or vault."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from envault.vault import unlock

_PLACEHOLDER = "<CHANGE_ME>"


def parse_env_lines(text: str) -> list[tuple[str, str]]:
    """Return (raw_line, key) pairs preserving comments and blanks."""
    result = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            result.append((line, ""))
            continue
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=", stripped)
        if match:
            result.append((line, match.group(1)))
        else:
            result.append((line, ""))
    return result


def generate_template(
    source_text: str,
    mask_values: bool = True,
    placeholder: str = _PLACEHOLDER,
) -> str:
    """Return a template string with values replaced by *placeholder*."""
    lines = []
    for raw_line, key in parse_env_lines(source_text):
        if key and mask_values:
            lines.append(f"{key}={placeholder}")
        else:
            lines.append(raw_line)
    return "\n".join(lines)


def template_from_env_file(
    env_path: Path,
    output_path: Optional[Path] = None,
    placeholder: str = _PLACEHOLDER,
) -> str:
    """Read *env_path*, strip values, optionally write to *output_path*."""
    text = env_path.read_text(encoding="utf-8")
    result = generate_template(text, placeholder=placeholder)
    if output_path is not None:
        output_path.write_text(result, encoding="utf-8")
    return result


def template_from_vault(
    vault_path: Path,
    password: str,
    output_path: Optional[Path] = None,
    placeholder: str = _PLACEHOLDER,
) -> str:
    """Decrypt *vault_path* and produce a template without secret values."""
    plaintext = unlock(vault_path, password)
    result = generate_template(plaintext, placeholder=placeholder)
    if output_path is not None:
        output_path.write_text(result, encoding="utf-8")
    return result
