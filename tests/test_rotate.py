"""Tests for envault.rotate — key rotation feature."""

import pytest
from pathlib import Path

from envault.vault import lock
from envault.rotate import rotate_vault_key, rotate_vault_key_for_dir
from envault.crypto import decrypt


OLD_PASSWORD = "old-secret-123"
NEW_PASSWORD = "new-secret-456"
SAMPLE_ENV = "DB_HOST=localhost\nDB_PORT=5432\nSECRET=abc\n"


@pytest.fixture()
def vault_file(tmp_path: Path) -> Path:
    env = tmp_path / ".env"
    env.write_text(SAMPLE_ENV, encoding="utf-8")
    vault = tmp_path / ".env.vault"
    lock(str(env), str(vault), OLD_PASSWORD)
    return vault


def test_rotate_vault_key_file_still_exists(vault_file: Path) -> None:
    rotate_vault_key(vault_file, OLD_PASSWORD, NEW_PASSWORD)
    assert vault_file.exists()


def test_rotate_vault_key_new_password_decrypts(vault_file: Path) -> None:
    rotate_vault_key(vault_file, OLD_PASSWORD, NEW_PASSWORD)
    blob = vault_file.read_text(encoding="utf-8").strip()
    recovered = decrypt(blob, NEW_PASSWORD)
    assert recovered == SAMPLE_ENV


def test_rotate_vault_key_old_password_no_longer_works(vault_file: Path) -> None:
    rotate_vault_key(vault_file, OLD_PASSWORD, NEW_PASSWORD)
    blob = vault_file.read_text(encoding="utf-8").strip()
    with pytest.raises(Exception):
        decrypt(blob, OLD_PASSWORD)


def test_rotate_vault_key_wrong_old_password_raises(vault_file: Path) -> None:
    with pytest.raises(ValueError, match="Key rotation failed"):
        rotate_vault_key(vault_file, "wrong-password", NEW_PASSWORD)


def test_rotate_vault_key_missing_file_raises(tmp_path: Path) -> None:
    missing = tmp_path / "ghost.vault"
    with pytest.raises(FileNotFoundError):
        rotate_vault_key(missing, OLD_PASSWORD, NEW_PASSWORD)


def test_rotate_vault_key_blob_changes(vault_file: Path) -> None:
    original_blob = vault_file.read_text(encoding="utf-8").strip()
    rotate_vault_key(vault_file, OLD_PASSWORD, NEW_PASSWORD)
    new_blob = vault_file.read_text(encoding="utf-8").strip()
    assert original_blob != new_blob


def test_rotate_vault_key_for_dir_returns_rotated_files(tmp_path: Path) -> None:
    for name in (".env", ".env.production"):
        env = tmp_path / name
        env.write_text(SAMPLE_ENV, encoding="utf-8")
        vault = tmp_path / (name + ".vault")
        lock(str(env), str(vault), OLD_PASSWORD)

    rotated = rotate_vault_key_for_dir(tmp_path, OLD_PASSWORD, NEW_PASSWORD)
    assert len(rotated) == 2
    for path in rotated:
        blob = path.read_text(encoding="utf-8").strip()
        assert decrypt(blob, NEW_PASSWORD) == SAMPLE_ENV


def test_rotate_vault_key_for_dir_empty_dir(tmp_path: Path) -> None:
    rotated = rotate_vault_key_for_dir(tmp_path, OLD_PASSWORD, NEW_PASSWORD)
    assert rotated == []
