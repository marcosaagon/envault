"""Tests for envault.env_strip."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.env_strip import strip_env_text, strip_env_file, strip_vault, StripResult
from envault.vault import lock


SAMPLE_ENV = """# This is a comment
DB_HOST=localhost

DB_PORT=5432
# Another comment
SECRET_KEY=abc123

"""


def test_strip_removes_comments():
    result = strip_env_text(SAMPLE_ENV, remove_comments=True, remove_blanks=False)
    assert "# This is a comment" not in result.output
    assert "# Another comment" not in result.output
    assert result.removed_comments == 2


def test_strip_removes_blank_lines():
    result = strip_env_text(SAMPLE_ENV, remove_comments=False, remove_blanks=True)
    lines = [l for l in result.output.splitlines() if l.strip() == ""]
    assert lines == []
    assert result.removed_blanks >= 1


def test_strip_preserves_key_value_pairs():
    result = strip_env_text(SAMPLE_ENV)
    assert "DB_HOST=localhost" in result.output
    assert "DB_PORT=5432" in result.output
    assert "SECRET_KEY=abc123" in result.output


def test_strip_both_comments_and_blanks():
    result = strip_env_text(SAMPLE_ENV, remove_comments=True, remove_blanks=True)
    assert result.removed_comments == 2
    assert result.removed_blanks >= 1
    assert "#" not in result.output
    for line in result.output.splitlines():
        assert line.strip() != ""


def test_strip_no_removal():
    result = strip_env_text(SAMPLE_ENV, remove_comments=False, remove_blanks=False)
    assert result.removed_comments == 0
    assert result.removed_blanks == 0
    assert result.original_lines == result.stripped_lines


def test_strip_result_summary_contains_counts():
    result = strip_env_text(SAMPLE_ENV)
    summary = result.summary
    assert "comment" in summary
    assert "blank" in summary


def test_strip_result_ok_is_true():
    result = strip_env_text(SAMPLE_ENV)
    assert result.ok is True


def test_strip_empty_string():
    result = strip_env_text("")
    assert result.output == "" or result.output == "\n"
    assert result.removed_comments == 0
    assert result.removed_blanks == 0


def test_strip_env_file(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text(SAMPLE_ENV, encoding="utf-8")
    result = strip_env_file(env_file)
    content = env_file.read_text(encoding="utf-8")
    assert "#" not in content
    assert result.removed_comments == 2


def test_strip_vault_round_trip(tmp_path: Path):
    env_file = tmp_path / ".env"
    vault_file = tmp_path / ".env.vault"
    env_file.write_text(SAMPLE_ENV, encoding="utf-8")
    lock(env_file, vault_file, "testpass")

    result = strip_vault(vault_file, "testpass")
    assert result.removed_comments == 2

    from envault.vault import unlock
    out_file = tmp_path / ".env.out"
    unlock(vault_file, out_file, "testpass")
    content = out_file.read_text(encoding="utf-8")
    assert "DB_HOST=localhost" in content
    assert "#" not in content
