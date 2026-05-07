"""Redact sensitive values from .env text or vault files."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from envault.vault import lock, unlock

DEFAULT_PLACEHOLDER = "***REDACTED***"

SENSITIVE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(secret|password|passwd|token|api[_-]?key|private[_-]?key|auth|credential)", re.IGNORECASE),
]


@dataclass
class RedactResult:
    original_keys: list[str] = field(default_factory=list)
    redacted_keys: list[str] = field(default_factory=list)
    output_text: str = ""

    @property
    def ok(self) -> bool:
        return len(self.redacted_keys) >= 0  # always valid

    def summary(self) -> str:
        if not self.redacted_keys:
            return "No sensitive keys detected."
        return f"Redacted {len(self.redacted_keys)} key(s): {', '.join(self.redacted_keys)}"


def _is_sensitive(key: str) -> bool:
    return any(p.search(key) for p in SENSITIVE_PATTERNS)


def redact_env_text(
    text: str,
    placeholder: str = DEFAULT_PLACEHOLDER,
    keys: list[str] | None = None,
) -> RedactResult:
    """Redact sensitive values in .env-formatted text.

    If *keys* is provided, only those keys are redacted regardless of name.
    Otherwise, keys matching SENSITIVE_PATTERNS are redacted automatically.
    """
    result = RedactResult()
    lines_out: list[str] = []

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            lines_out.append(line)
            continue

        key, _, value = stripped.partition("=")
        key = key.strip()
        result.original_keys.append(key)

        should_redact = (keys is not None and key in keys) or (
            keys is None and _is_sensitive(key)
        )

        if should_redact and value:
            lines_out.append(f"{key}={placeholder}")
            result.redacted_keys.append(key)
        else:
            lines_out.append(line)

    result.output_text = "\n".join(lines_out)
    if text.endswith("\n"):
        result.output_text += "\n"
    return result


def redact_env_file(
    env_path: Path,
    placeholder: str = DEFAULT_PLACEHOLDER,
    keys: list[str] | None = None,
) -> RedactResult:
    """Redact sensitive values in a plain .env file in-place."""
    text = env_path.read_text(encoding="utf-8")
    result = redact_env_text(text, placeholder=placeholder, keys=keys)
    env_path.write_text(result.output_text, encoding="utf-8")
    return result


def redact_vault(
    vault_path: Path,
    password: str,
    placeholder: str = DEFAULT_PLACEHOLDER,
    keys: list[str] | None = None,
) -> RedactResult:
    """Decrypt a vault, redact sensitive values, then re-encrypt in place."""
    text = unlock(vault_path, password)
    result = redact_env_text(text, placeholder=placeholder, keys=keys)
    lock(result.output_text, vault_path, password)
    return result
