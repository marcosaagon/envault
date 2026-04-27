"""Integration tests for envault.vault — lock/unlock file operations."""

import pytest
from pathlib import Path
from envault.vault import lock, unlock


PASSWORD = "test-password-123"
ENV_CONTENT = "APP_ENV=production\nSECRET_KEY=s3cr3t\nDEBUG=false\n"


@pytest.fixture()
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text(ENV_CONTENT, encoding="utf-8")
    return f


@pytest.fixture()
def vault_file(tmp_path):
    return tmp_path / ".env.vault"


def test_lock_creates_vault_file(env_file, vault_file):
    lock(env_path=str(env_file), vault_path=str(vault_file), password=PASSWORD)
    assert vault_file.exists()


def test_lock_vault_content_differs_from_plaintext(env_file, vault_file):
    lock(env_path=str(env_file), vault_path=str(vault_file), password=PASSWORD)
    blob = vault_file.read_text(encoding="utf-8")
    assert blob != ENV_CONTENT
    assert "SECRET_KEY" not in blob


def test_unlock_recovers_original_content(env_file, vault_file, tmp_path):
    lock(env_path=str(env_file), vault_path=str(vault_file), password=PASSWORD)
    output_env = tmp_path / ".env.recovered"
    unlock(vault_path=str(vault_file), env_path=str(output_env), password=PASSWORD)
    assert output_env.read_text(encoding="utf-8") == ENV_CONTENT


def test_lock_raises_if_env_missing(tmp_path, vault_file):
    with pytest.raises(FileNotFoundError):
        lock(env_path=str(tmp_path / "nonexistent.env"), vault_path=str(vault_file), password=PASSWORD)


def test_lock_raises_if_env_empty(tmp_path, vault_file):
    empty_env = tmp_path / ".env"
    empty_env.write_text("", encoding="utf-8")
    with pytest.raises(ValueError):
        lock(env_path=str(empty_env), vault_path=str(vault_file), password=PASSWORD)


def test_unlock_raises_if_vault_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        unlock(vault_path=str(tmp_path / "nonexistent.vault"), env_path=str(tmp_path / ".env"), password=PASSWORD)


def test_unlock_raises_on_wrong_password(env_file, vault_file, tmp_path):
    lock(env_path=str(env_file), vault_path=str(vault_file), password=PASSWORD)
    output_env = tmp_path / ".env.out"
    with pytest.raises(Exception):
        unlock(vault_path=str(vault_file), env_path=str(output_env), password="wrong-password")
