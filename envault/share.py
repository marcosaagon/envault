"""Share module for envault.

Handles exporting and importing encrypted vault blobs for team sharing
via Git-friendly base64-encoded files or stdout.
"""

import base64
import json
import os
from pathlib import Path
from typing import Optional

from envault.crypto import encrypt, decrypt

# Default filename for shared encrypted blobs
DEFAULT_SHARE_FILE = ".env.shared"


def export_vault(
    vault_path: str,
    password: str,
    output_path: Optional[str] = None,
    profile: Optional[str] = None,
) -> str:
    """Export an encrypted vault as a shareable blob.

    Reads the raw encrypted vault bytes, wraps them in a JSON envelope
    with optional metadata, and writes to a file or returns as a string.

    Args:
        vault_path: Path to the existing .env.vault file.
        password: Password used to re-encrypt the export blob.
        output_path: Destination file path. If None, returns the blob string.
        profile: Optional profile name to embed in the envelope metadata.

    Returns:
        The base64-encoded encrypted blob string.

    Raises:
        FileNotFoundError: If the vault file does not exist.
    """
    vault_file = Path(vault_path)
    if not vault_file.exists():
        raise FileNotFoundError(f"Vault file not found: {vault_path}")

    # Read the raw vault content (already encrypted)
    raw_vault = vault_file.read_text(encoding="utf-8").strip()

    # Wrap in an envelope so we can attach metadata
    envelope = json.dumps(
        {
            "version": 1,
            "profile": profile or "default",
            "vault": raw_vault,
        }
    )

    # Encrypt the envelope with the provided password
    blob = encrypt(envelope, password)

    if output_path:
        Path(output_path).write_text(blob, encoding="utf-8")

    return blob


def import_vault(
    blob_source: str,
    password: str,
    output_path: str,
    is_file: bool = True,
) -> str:
    """Import a shared encrypted blob and write it as a vault file.

    Decrypts the blob, validates the envelope structure, and writes the
    inner vault content to the specified output path.

    Args:
        blob_source: Either a file path (if is_file=True) or a raw blob string.
        password: Password to decrypt the blob.
        output_path: Destination path for the recovered vault file.
        is_file: If True, read the blob from a file; otherwise treat as raw string.

    Returns:
        The profile name embedded in the envelope.

    Raises:
        FileNotFoundError: If is_file=True and the blob file does not exist.
        ValueError: If the blob cannot be decrypted or has an invalid envelope.
    """
    if is_file:
        blob_path = Path(blob_source)
        if not blob_path.exists():
            raise FileNotFoundError(f"Shared blob file not found: {blob_source}")
        blob = blob_path.read_text(encoding="utf-8").strip()
    else:
        blob = blob_source.strip()

    # Decrypt and parse the envelope
    try:
        envelope_json = decrypt(blob, password)
    except Exception as exc:
        raise ValueError(f"Failed to decrypt shared blob: {exc}") from exc

    try:
        envelope = json.loads(envelope_json)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid envelope format in shared blob: {exc}") from exc

    required_keys = {"version", "profile", "vault"}
    if not required_keys.issubset(envelope.keys()):
        raise ValueError(
            f"Envelope missing required keys. Expected {required_keys}, "
            f"got {set(envelope.keys())}"
        )

    # Write the inner vault content to the output path
    Path(output_path).write_text(envelope["vault"], encoding="utf-8")

    return envelope["profile"]
