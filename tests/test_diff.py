"""Tests for envault.diff module."""

import pytest

from envault.diff import DiffResult, diff_envs, format_diff, parse_env


ENV_A = """# comment
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=abc123
"""

ENV_B = """DB_HOST=localhost
DB_PORT=5433
API_KEY=newkey
"""


def test_parse_env_basic():
    result = parse_env("FOO=bar\nBAZ=qux\n")
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_parse_env_ignores_comments():
    result = parse_env("# comment\nFOO=bar")
    assert "# comment" not in result
    assert result["FOO"] == "bar"


def test_parse_env_ignores_blank_lines():
    result = parse_env("\n\nFOO=bar\n\n")
    assert list(result.keys()) == ["FOO"]


def test_parse_env_no_equals_skipped():
    result = parse_env("NODEQUALS\nFOO=bar")
    assert "NODEQUALS" not in result


def test_diff_detects_added():
    result = diff_envs(ENV_A, ENV_B)
    assert "API_KEY" in result.added


def test_diff_detects_removed():
    result = diff_envs(ENV_A, ENV_B)
    assert "SECRET_KEY" in result.removed


def test_diff_detects_changed():
    result = diff_envs(ENV_A, ENV_B)
    keys = [k for k, _, _ in result.changed]
    assert "DB_PORT" in keys


def test_diff_detects_unchanged():
    result = diff_envs(ENV_A, ENV_B)
    assert "DB_HOST" in result.unchanged


def test_diff_no_changes():
    result = diff_envs(ENV_A, ENV_A)
    assert not result.has_changes


def test_format_diff_masks_values():
    result = diff_envs(ENV_A, ENV_B)
    output = format_diff(result, mask_values=True)
    assert "newkey" not in output
    assert "***" in output


def test_format_diff_shows_values():
    result = diff_envs(ENV_A, ENV_B)
    output = format_diff(result, mask_values=False)
    assert "newkey" in output


def test_format_diff_no_changes_message():
    result = DiffResult()
    output = format_diff(result)
    assert "No changes" in output
