"""Vault operations: lock (encrypt) and unlock (decrypt) .env files."""

import os
from pathlib import Path
from envault.crypto import encrypt, decrypt

DEFAULT_ENV_FILE = ".env"
DEFAULT_VAULT_FILE = ".env.vault"


def lock(env_path: str = DEFAULT_ENV_FILE, vault_path: str = DEFAULT_VAULT_FILE, password: str = "") -> None:
    """
    Encrypt the contents of an .env file and write the encrypted blob to a vault file.

    Args:
        env_path: Path to the plaintext .env file.
        vault_path: Destination path for the encrypted vault file.
        password: Encryption password.
    """
    env_file = Path(env_path)
    if not env_file.exists():
        raise FileNotFoundError(f"Environment file not found: {env_path}")

    plaintext = env_file.read_text(encoding="utf-8")
    if not plaintext.strip():
        raise ValueError(f"Environment file is empty: {env_path}")

    blob = encrypt(plaintext, password)
    Path(vault_path).write_text(blob, encoding="utf-8")


def unlock(vault_path: str = DEFAULT_VAULT_FILE, env_path: str = DEFAULT_ENV_FILE, password: str = "") -> None:
    """
    Decrypt a vault file and write the plaintext to an .env file.

    Args:
        vault_path: Path to the encrypted vault file.
        env_path: Destination path for the decrypted .env file.
        password: Decryption password.
    """
    vault_file = Path(vault_path)
    if not vault_file.exists():
        raise FileNotFoundError(f"Vault file not found: {vault_path}")

    blob = vault_file.read_text(encoding="utf-8").strip()
    plaintext = decrypt(blob, password)
    Path(env_path).write_text(plaintext, encoding="utf-8")
