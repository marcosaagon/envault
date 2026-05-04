"""High-level lock/unlock operations for .env vault files."""
from __future__ import annotations

from pathlib import Path

from envault.crypto import encrypt, decrypt

VAULT_SUFFIX = ".vault"


def lock(env_path: Path, vault_path: Path, password: str) -> None:
    """Encrypt *env_path* and write the ciphertext blob to *vault_path*."""
    plaintext = env_path.read_text(encoding="utf-8")
    blob = encrypt(plaintext, password)
    vault_path.write_text(blob, encoding="utf-8")


def unlock(vault_path: Path, env_path: Path, password: str) -> None:
    """Decrypt *vault_path* and write the plaintext to *env_path*."""
    blob = vault_path.read_text(encoding="utf-8").strip()
    plaintext = decrypt(blob, password)
    env_path.write_text(plaintext, encoding="utf-8")
