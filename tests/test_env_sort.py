"""Tests for envault.env_sort module."""

import pytest
from pathlib import Path

from envault.env_sort import sort_env_text, sort_env_file, sort_vault, SortResult
from envault.crypto import encrypt


SAMPLE_ENV = """ZEBRA=1
APPLE=2
MANGO=3
"""

SORTED_ENV = """APPLE=2
MANGO=3
ZEBRA=1
"""

ENV_WITH_COMMENTS = """# top comment
ZEBRA=1
APPLE=2
# mid comment
MANGO=3
"""


def test_sort_env_text_basic():
    result = sort_env_text(SAMPLE_ENV)
    assert result.ok
    assert result.sorted_lines == ["APPLE=2", "MANGO=3", "ZEBRA=1", ""]


def test_sort_env_text_already_sorted():
    result = sort_env_text(SORTED_ENV)
    assert result.ok
    assert not result.changed


def test_sort_env_text_reverse():
    result = sort_env_text(SAMPLE_ENV, reverse=True)
    assert result.ok
    assert result.sorted_lines[0] == "ZEBRA=1"


def test_sort_env_text_preserves_comments():
    result = sort_env_text(ENV_WITH_COMMENTS)
    assert result.ok
    lines = result.sorted_lines
    assert "# top comment" in lines
    assert "# mid comment" in lines


def test_sort_env_text_keys_sorted_count():
    result = sort_env_text(SAMPLE_ENV)
    assert result.keys_sorted == 3


def test_sort_result_summary_changed():
    result = sort_env_text(SAMPLE_ENV)
    assert "Sorted" in result.summary()


def test_sort_result_summary_no_change():
    result = sort_env_text(SORTED_ENV)
    assert "Already sorted" in result.summary()


def test_sort_env_file_writes_sorted(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(SAMPLE_ENV)
    result = sort_env_file(env_file)
    assert result.ok
    assert result.changed
    content = env_file.read_text()
    assert content.startswith("APPLE")


def test_sort_env_file_dry_run_does_not_write(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(SAMPLE_ENV)
    result = sort_env_file(env_file, dry_run=True)
    assert result.ok
    assert result.changed
    content = env_file.read_text()
    assert content == SAMPLE_ENV


def test_sort_env_file_missing_returns_error(tmp_path):
    result = sort_env_file(tmp_path / "missing.env")
    assert not result.ok
    assert "not found" in result.error.lower()


def test_sort_vault_round_trip(tmp_path):
    vault_file = tmp_path / ".env.vault"
    password = "testpass"
    blob = encrypt(SAMPLE_ENV, password)
    vault_file.write_text(blob)
    result = sort_vault(vault_file, password)
    assert result.ok
    assert result.changed


def test_sort_vault_wrong_password_returns_error(tmp_path):
    vault_file = tmp_path / ".env.vault"
    blob = encrypt(SAMPLE_ENV, "correct")
    vault_file.write_text(blob)
    result = sort_vault(vault_file, "wrong")
    assert not result.ok
    assert result.error is not None


def test_sort_vault_missing_returns_error(tmp_path):
    result = sort_vault(tmp_path / "missing.vault", "pass")
    assert not result.ok
