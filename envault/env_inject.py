"""Inject decrypted .env variables into a subprocess environment."""

from __future__ import annotations

import os
import subprocess
from typing import Dict, List, Optional

from envault.vault import unlock


def parse_env_text(text: str) -> Dict[str, str]:
    """Parse KEY=VALUE lines from env text, ignoring comments and blanks."""
    result: Dict[str, str] = {}
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


def build_injected_env(
    vault_path: str,
    password: str,
    override: bool = True,
) -> Dict[str, str]:
    """Return a copy of os.environ with vault variables injected.

    Args:
        vault_path: Path to the encrypted vault file.
        password: Password to decrypt the vault.
        override: If True, vault values overwrite existing env vars.

    Returns:
        A dict suitable for use as subprocess env.
    """
    plaintext = unlock(vault_path, password)
    vault_vars = parse_env_text(plaintext)

    env = os.environ.copy()
    for key, value in vault_vars.items():
        if override or key not in env:
            env[key] = value
    return env


def run_with_vault(
    command: List[str],
    vault_path: str,
    password: str,
    override: bool = True,
    extra_env: Optional[Dict[str, str]] = None,
) -> subprocess.CompletedProcess:
    """Run a subprocess with decrypted vault variables injected into env.

    Args:
        command: Command and arguments to execute.
        vault_path: Path to the encrypted vault file.
        password: Password to decrypt the vault.
        override: If True, vault values overwrite existing env vars.
        extra_env: Additional variables to inject (applied last).

    Returns:
        CompletedProcess instance.
    """
    env = build_injected_env(vault_path, password, override=override)
    if extra_env:
        env.update(extra_env)
    return subprocess.run(command, env=env)  # noqa: S603
