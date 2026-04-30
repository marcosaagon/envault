"""Search and filter keys across .env vault files."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from envault.vault import unlock


@dataclass
class SearchResult:
    key: str
    value: str
    source: str  # file path or profile name


def search_env_text(env_text: str, pattern: str, source: str) -> List[SearchResult]:
    """Search parsed env text for keys or values matching *pattern*.

    Matching is case-insensitive substring search unless the pattern looks like
    a regex (contains special chars), in which case it is compiled as one.
    """
    results: List[SearchResult] = []
    try:
        regex = re.compile(pattern, re.IGNORECASE)
    except re.error:
        regex = re.compile(re.escape(pattern), re.IGNORECASE)

    for line in env_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        key = key.strip()
        value = value.strip()
        if regex.search(key) or regex.search(value):
            results.append(SearchResult(key=key, value=value, source=source))
    return results


def search_vault(
    vault_path: Path,
    password: str,
    pattern: str,
    keys_only: bool = False,
) -> List[SearchResult]:
    """Decrypt *vault_path* and search its contents for *pattern*.

    Args:
        vault_path: Path to the encrypted vault file.
        password: Password used to decrypt the vault.
        pattern: Substring or regex pattern to match against keys (and values
                 unless *keys_only* is True).
        keys_only: When True only key names are searched, not values.

    Returns:
        List of :class:`SearchResult` instances for each matching entry.
    """
    plaintext = unlock(vault_path, password)
    source = str(vault_path)

    if keys_only:
        # Temporarily blank values so the shared helper won't match them
        sanitised_lines = []
        for line in plaintext.splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and "=" in stripped:
                key, _, _ = stripped.partition("=")
                sanitised_lines.append(f"{key.strip()}=")
            else:
                sanitised_lines.append(line)
        plaintext = "\n".join(sanitised_lines)

    return search_env_text(plaintext, pattern, source)


def format_results(results: List[SearchResult], show_values: bool = True) -> str:
    """Format search results as a human-readable string."""
    if not results:
        return "No matches found."
    lines = []
    for r in results:
        if show_values:
            lines.append(f"[{r.source}] {r.key}={r.value}")
        else:
            lines.append(f"[{r.source}] {r.key}")
    return "\n".join(lines)
