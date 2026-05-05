"""Tests for envault.env_rename."""

import pytest

from envault.env_rename import (
    rename_key_in_env_file,
    rename_key_in_text,
    rename_key_in_vault,
)
from envault.vault import lock


# ---------------------------------------------------------------------------
# rename_key_in_text
# ---------------------------------------------------------------------------

ENV_TEXT = "DB_HOST=localhost\nDB_PORT=5432\nSECRET=abc123\n"


def test_rename_existing_key_succeeds():
    updated, result = rename_key_in_text(ENV_TEXT, "DB_HOST", "DATABASE_HOST")
    assert result.renamed is True
    assert "DATABASE_HOST=localhost" in updated
    assert "DB_HOST" not in updated


def test_rename_preserves_other_keys():
    updated, result = rename_key_in_text(ENV_TEXT, "DB_PORT", "DATABASE_PORT")
    assert "DB_HOST=localhost" in updated
    assert "SECRET=abc123" in updated


def test_rename_missing_key_returns_false():
    _, result = rename_key_in_text(ENV_TEXT, "MISSING_KEY", "NEW_KEY")
    assert result.renamed is False
    assert "MISSING_KEY" in result.message or "not found" in result.message


def test_rename_missing_key_text_unchanged():
    updated, _ = rename_key_in_text(ENV_TEXT, "MISSING_KEY", "NEW_KEY")
    assert updated == ENV_TEXT


def test_rename_ignores_comments():
    text = "# DB_HOST=old\nDB_HOST=real\n"
    updated, result = rename_key_in_text(text, "DB_HOST", "DATABASE_HOST")
    assert result.renamed is True
    assert "# DB_HOST=old" in updated  # comment untouched
    assert "DATABASE_HOST=real" in updated


def test_rename_key_with_empty_value():
    text = "EMPTY=\n"
    updated, result = rename_key_in_text(text, "EMPTY", "BLANK")
    assert result.renamed is True
    assert "BLANK=" in updated


# ---------------------------------------------------------------------------
# rename_key_in_env_file
# ---------------------------------------------------------------------------


def test_rename_in_env_file(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("API_KEY=secret\nDEBUG=true\n")

    result = rename_key_in_env_file(str(env_file), "API_KEY", "SERVICE_API_KEY")

    assert result.renamed is True
    content = env_file.read_text()
    assert "SERVICE_API_KEY=secret" in content
    assert "API_KEY" not in content


def test_rename_in_env_file_missing_key_does_not_modify(tmp_path):
    env_file = tmp_path / ".env"
    original = "API_KEY=secret\n"
    env_file.write_text(original)

    result = rename_key_in_env_file(str(env_file), "NONEXISTENT", "NEW")

    assert result.renamed is False
    assert env_file.read_text() == original


# ---------------------------------------------------------------------------
# rename_key_in_vault
# ---------------------------------------------------------------------------


@pytest.fixture()
def vault_file(tmp_path):
    env = tmp_path / ".env"
    vault = tmp_path / ".env.vault"
    env.write_text("DB_URL=postgres://localhost/mydb\nSECRET=hunter2\n")
    lock(str(env), str(vault), "testpass")
    return vault


def test_rename_in_vault_succeeds(vault_file):
    result = rename_key_in_vault(str(vault_file), "testpass", "DB_URL", "DATABASE_URL")
    assert result.renamed is True


def test_rename_in_vault_new_key_decryptable(vault_file):
    from envault.vault import unlock

    rename_key_in_vault(str(vault_file), "testpass", "DB_URL", "DATABASE_URL")
    plaintext = unlock(str(vault_file), "testpass")
    assert "DATABASE_URL=postgres://localhost/mydb" in plaintext
    assert "DB_URL" not in plaintext


def test_rename_in_vault_wrong_password_raises(vault_file):
    with pytest.raises(Exception):
        rename_key_in_vault(str(vault_file), "wrongpass", "DB_URL", "DATABASE_URL")


def test_rename_in_vault_missing_key(vault_file):
    result = rename_key_in_vault(str(vault_file), "testpass", "NONEXISTENT", "NEW")
    assert result.renamed is False
