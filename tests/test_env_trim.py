"""Tests for envault.env_trim module."""

from pathlib import Path

import pytest

from envault.env_trim import TrimResult, trim_env_text, trim_env_file, trim_vault
from envault.vault import lock, unlock


# ---------------------------------------------------------------------------
# trim_env_text
# ---------------------------------------------------------------------------

def test_trim_env_text_no_whitespace_unchanged():
    text = "KEY=value\nOTHER=hello\n"
    result = trim_env_text(text)
    assert not result.changed
    assert result.trimmed_keys == []


def test_trim_env_text_strips_leading_space_in_value():
    text = "KEY=  value\n"
    result = trim_env_text(text)
    assert result.changed
    assert "KEY" in result.trimmed_keys
    assert "KEY=value\n" in result.output_text


def test_trim_env_text_strips_trailing_space_in_value():
    text = "KEY=value   \n"
    result = trim_env_text(text)
    assert result.changed
    assert "KEY" in result.trimmed_keys
    assert "KEY=value\n" in result.output_text


def test_trim_env_text_strips_both_sides():
    text = "MY_VAR=  hello world  \n"
    result = trim_env_text(text)
    assert result.changed
    assert result.output_text == "MY_VAR=hello world\n"


def test_trim_env_text_preserves_comments():
    text = "# comment\nKEY=value\n"
    result = trim_env_text(text)
    assert "# comment\n" in result.output_text


def test_trim_env_text_skips_lines_without_equals():
    text = "NOEQUALS\nKEY=val\n"
    result = trim_env_text(text)
    assert "NOEQUALS\n" in result.output_text


def test_trim_env_text_summary_no_changes():
    result = trim_env_text("KEY=value\n")
    assert result.summary == "No values needed trimming."


def test_trim_env_text_summary_with_changes():
    result = trim_env_text("A=  1  \nB=  2  \n")
    assert "2 key(s)" in result.summary


def test_trim_env_text_ok_always_true():
    result = trim_env_text("")
    assert result.ok is True


# ---------------------------------------------------------------------------
# trim_env_file
# ---------------------------------------------------------------------------

def test_trim_env_file_writes_trimmed_content(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=  hello  \n")
    result = trim_env_file(env_file)
    assert result.changed
    assert env_file.read_text() == "KEY=hello\n"


def test_trim_env_file_no_change_leaves_file_intact(tmp_path):
    env_file = tmp_path / ".env"
    original = "KEY=hello\n"
    env_file.write_text(original)
    result = trim_env_file(env_file)
    assert not result.changed
    assert env_file.read_text() == original


# ---------------------------------------------------------------------------
# trim_vault
# ---------------------------------------------------------------------------

@pytest.fixture
def vault_file(tmp_path):
    path = tmp_path / "test.vault"
    lock("KEY=  secret  \nOTHER=clean\n", path, "password123")
    return path


def test_trim_vault_changes_applied(vault_file):
    result = trim_vault(vault_file, "password123")
    assert result.changed
    decrypted = unlock(vault_file, "password123")
    assert "KEY=secret\n" in decrypted


def test_trim_vault_clean_vault_no_changes(tmp_path):
    path = tmp_path / "clean.vault"
    lock("KEY=clean\n", path, "pass")
    result = trim_vault(path, "pass")
    assert not result.changed
