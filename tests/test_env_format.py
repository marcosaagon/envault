"""Tests for envault.env_format."""

from __future__ import annotations

import pytest

from envault.env_format import FormatResult, format_env_text, format_env_file


# ---------------------------------------------------------------------------
# format_env_text
# ---------------------------------------------------------------------------

def test_format_no_changes_returns_same_text():
    text = "KEY=value\nOTHER=thing\n"
    result = format_env_text(text)
    assert not result.changed
    assert result.formatted == text


def test_format_adds_trailing_newline():
    text = "KEY=value"
    result = format_env_text(text, ensure_newline=True)
    assert result.formatted.endswith("\n")
    assert result.changed
    assert any("newline" in c.lower() for c in result.changes)


def test_format_no_trailing_newline_when_disabled():
    text = "KEY=value"
    result = format_env_text(text, ensure_newline=False)
    assert not result.formatted.endswith("\n")


def test_format_removes_trailing_spaces():
    text = "KEY=value   \nOTHER=thing\n"
    result = format_env_text(text, remove_trailing_spaces=True)
    assert "   " not in result.formatted
    assert result.changed


def test_format_quotes_values():
    text = "KEY=hello\n"
    result = format_env_text(text, quote_values=True)
    assert 'KEY="hello"' in result.formatted
    assert result.changed


def test_format_does_not_double_quote():
    text = 'KEY="already_quoted"\n'
    result = format_env_text(text, quote_values=True)
    assert result.formatted.count('"') == 2


def test_format_sort_keys():
    text = "ZEBRA=1\nAPPLE=2\nMIDDLE=3\n"
    result = format_env_text(text, sort_keys=True)
    lines = [l for l in result.formatted.splitlines() if l]
    keys = [l.split("=")[0] for l in lines]
    assert keys == sorted(keys, key=str.lower)
    assert result.changed


def test_format_sort_already_sorted_no_change_flag():
    text = "APPLE=1\nZEBRA=2\n"
    result = format_env_text(text, sort_keys=True, ensure_newline=False)
    assert not result.changed


def test_format_preserves_comments():
    text = "# comment\nKEY=value\n"
    result = format_env_text(text)
    assert "# comment" in result.formatted


def test_format_result_summary_changed():
    text = "KEY=value"
    result = format_env_text(text, ensure_newline=True)
    assert "change" in result.summary().lower()


def test_format_result_summary_unchanged():
    text = "KEY=value\n"
    result = format_env_text(text)
    assert "already" in result.summary().lower()


def test_format_result_ok_always_true():
    text = "KEY=value\n"
    result = format_env_text(text)
    assert result.ok is True


# ---------------------------------------------------------------------------
# format_env_file
# ---------------------------------------------------------------------------

def test_format_env_file_writes_back(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=value")
    result = format_env_file(str(env_file), ensure_newline=True)
    assert result.changed
    assert env_file.read_text().endswith("\n")


def test_format_env_file_no_write_when_unchanged(tmp_path):
    """Ensure format_env_file does not rewrite the file when nothing changed."""
    env_file = tmp_path / ".env"
    original_content = "KEY=value\n"
    env_file.write_text(original_content)
    mtime_before = env_file.stat().st_mtime

    result = format_env_file(str(env_file))

    assert not result.changed
    assert env_file.stat().st_mtime == mtime_before


def test_format_env_file_missing_raises(tmp_path):
    """Ensure format_env_file raises FileNotFoundError for missing files."""
    missing = tmp_path / "nonexistent.env"
    with pytest.raises(FileNotFoundError):
        format_env_file(str(missing))
