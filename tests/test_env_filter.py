"""Tests for envault.env_filter."""

from __future__ import annotations

import pytest

from envault.env_filter import filter_env_text, parse_env_text

SAMPLE = """\
# database config
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mydb
AWS_ACCESS_KEY=abc123
AWS_SECRET_KEY=secret
APP_NAME=myapp
APP_ENV=production
"""


def test_parse_env_text_basic():
    result = parse_env_text("KEY=value\nOTHER=123")
    assert result == {"KEY": "value", "OTHER": "123"}


def test_parse_env_text_ignores_comments():
    result = parse_env_text("# comment\nKEY=value")
    assert "KEY" in result
    assert len(result) == 1


def test_parse_env_text_ignores_blank_lines():
    result = parse_env_text("\n\nKEY=value\n\n")
    assert result == {"KEY": "value"}


def test_parse_env_text_no_equals_skipped():
    result = parse_env_text("NOEQUALS\nKEY=value")
    assert "NOEQUALS" not in result
    assert "KEY" in result


def test_filter_by_prefix():
    result = filter_env_text(SAMPLE, prefix="DB_")
    assert set(result.matched_keys) == {"DB_HOST", "DB_PORT", "DB_NAME"}


def test_filter_by_suffix():
    result = filter_env_text(SAMPLE, suffix="_KEY")
    assert set(result.matched_keys) == {"AWS_ACCESS_KEY", "AWS_SECRET_KEY"}


def test_filter_by_glob_pattern():
    result = filter_env_text(SAMPLE, pattern="APP_*")
    assert set(result.matched_keys) == {"APP_NAME", "APP_ENV"}


def test_filter_by_regex():
    result = filter_env_text(SAMPLE, regex=r"^AWS_")
    assert set(result.matched_keys) == {"AWS_ACCESS_KEY", "AWS_SECRET_KEY"}


def test_filter_invert():
    result = filter_env_text(SAMPLE, prefix="DB_", invert=True)
    assert "DB_HOST" not in result.matched_keys
    assert "AWS_ACCESS_KEY" in result.matched_keys


def test_filter_no_criteria_matches_all():
    result = filter_env_text(SAMPLE)
    assert result.total_keys == 7
    assert len(result.matched_keys) == 7


def test_filter_result_summary():
    result = filter_env_text(SAMPLE, prefix="DB_")
    assert "3" in result.summary()
    assert "7" in result.summary()


def test_filter_result_ok_false_when_no_match():
    result = filter_env_text(SAMPLE, prefix="NONEXISTENT_")
    assert not result.ok
    assert result.matched_keys == []


def test_filtered_text_excludes_unmatched_keys():
    result = filter_env_text(SAMPLE, prefix="DB_")
    assert "DB_HOST=localhost" in result.filtered_text
    assert "AWS_ACCESS_KEY" not in result.filtered_text


def test_filtered_text_preserves_comments():
    result = filter_env_text(SAMPLE, prefix="DB_")
    assert "# database config" in result.filtered_text
