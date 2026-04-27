"""Unit tests for envault.crypto — encrypt/decrypt round-trips and error cases."""

import pytest
from cryptography.exceptions import InvalidTag
from envault.crypto import encrypt, decrypt


PASSWORD = "super-secret-passphrase"
PLAINTEXT = "DB_HOST=localhost\nDB_PORT=5432\nAPI_KEY=abc123\n"


def test_encrypt_returns_string():
    blob = encrypt(PLAINTEXT, PASSWORD)
    assert isinstance(blob, str)
    assert len(blob) > 0


def test_encrypt_produces_different_blobs():
    """Each call should produce a unique ciphertext due to random salt and nonce."""
    blob1 = encrypt(PLAINTEXT, PASSWORD)
    blob2 = encrypt(PLAINTEXT, PASSWORD)
    assert blob1 != blob2


def test_decrypt_round_trip():
    blob = encrypt(PLAINTEXT, PASSWORD)
    recovered = decrypt(blob, PASSWORD)
    assert recovered == PLAINTEXT


def test_decrypt_wrong_password_raises():
    blob = encrypt(PLAINTEXT, PASSWORD)
    with pytest.raises(InvalidTag):
        decrypt(blob, "wrong-password")


def test_encrypt_empty_string():
    blob = encrypt("", PASSWORD)
    recovered = decrypt(blob, PASSWORD)
    assert recovered == ""


def test_decrypt_corrupted_blob_raises():
    blob = encrypt(PLAINTEXT, PASSWORD)
    corrupted = blob[:-4] + "XXXX"
    with pytest.raises(Exception):
        decrypt(corrupted, PASSWORD)


def test_unicode_plaintext_round_trip():
    unicode_text = "SECRET=こんにちは\nMOTTO=café\n"
    blob = encrypt(unicode_text, PASSWORD)
    recovered = decrypt(blob, PASSWORD)
    assert recovered == unicode_text
