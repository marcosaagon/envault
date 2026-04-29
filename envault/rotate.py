"""Key rotation support for envault vaults."""

import json
from pathlib import Path
from typing import Optional

from envault.crypto import encrypt, decrypt
from envault.audit import record_event


def rotate_vault_key(
    vault_path: str | Path,
    old_password: str,
    new_password: str,
    profile: Optional[str] = None,
) -> None:
    """Re-encrypt an existing vault file with a new password.

    Decrypts the vault using *old_password*, then immediately re-encrypts
    the plaintext with *new_password* and writes the result back to the
    same file.  An audit event is recorded on success.

    Args:
        vault_path: Path to the ``.vault`` file.
        old_password: Current encryption password.
        new_password: Replacement encryption password.
        profile: Optional profile name to associate with the audit event.

    Raises:
        FileNotFoundError: If *vault_path* does not exist.
        ValueError: If *old_password* is incorrect (decryption fails).
    """
    vault_path = Path(vault_path)

    if not vault_path.exists():
        raise FileNotFoundError(f"Vault file not found: {vault_path}")

    encrypted_blob = vault_path.read_text(encoding="utf-8").strip()

    try:
        plaintext = decrypt(encrypted_blob, old_password)
    except Exception as exc:
        raise ValueError("Key rotation failed: could not decrypt vault with the provided old password.") from exc

    new_blob = encrypt(plaintext, new_password)
    vault_path.write_text(new_blob + "\n", encoding="utf-8")

    record_event(
        action="rotate",
        target=str(vault_path),
        profile=profile,
        details={"status": "success"},
    )


def rotate_vault_key_for_dir(
    directory: str | Path,
    old_password: str,
    new_password: str,
    profile: Optional[str] = None,
) -> list[Path]:
    """Rotate the encryption key for every ``.vault`` file in *directory*.

    Returns:
        List of vault ``Path`` objects that were successfully rotated.
    """
    directory = Path(directory)
    rotated: list[Path] = []

    for vault_file in sorted(directory.glob("*.vault")):
        rotate_vault_key(vault_file, old_password, new_password, profile=profile)
        rotated.append(vault_file)

    return rotated
