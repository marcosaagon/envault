"""Tests for envault.env_compare module."""

import pytest
from envault.env_compare import (
    CompareResult,
    compare_env_texts,
    compare_envs,
    format_compare_result,
    parse_env_text,
)


def test_parse_env_text_basic():
    text = "FOO=bar\nBAZ=qux\n"
    result = parse_env_text(text)
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_parse_env_text_ignores_comments():
    text = "# comment\nFOO=bar\n"
    result = parse_env_text(text)
    assert "FOO" in result
    assert len(result) == 1


def test_parse_env_text_ignores_blank_lines():
    text = "\n\nFOO=bar\n\n"
    result = parse_env_text(text)
    assert result == {"FOO": "bar"}


def test_parse_env_text_no_equals_skipped():
    text = "NOEQUALS\nFOO=bar\n"
    result = parse_env_text(text)
    assert "NOEQUALS" not in result


def test_compare_envs_identical():
    env = {"A": "1", "B": "2"}
    result = compare_envs(env, env.copy())
    assert not result.has_differences
    assert result.identical == ["A", "B"]


def test_compare_envs_only_in_left():
    left = {"A": "1", "B": "2"}
    right = {"A": "1"}
    result = compare_envs(left, right)
    assert result.only_in_left == ["B"]
    assert result.has_differences


def test_compare_envs_only_in_right():
    left = {"A": "1"}
    right = {"A": "1", "C": "3"}
    result = compare_envs(left, right)
    assert result.only_in_right == ["C"]
    assert result.has_differences


def test_compare_envs_value_changed():
    left = {"A": "old"}
    right = {"A": "new"}
    result = compare_envs(left, right)
    assert len(result.value_changed) == 1
    key, lval, rval = result.value_changed[0]
    assert key == "A"
    assert lval == "old"
    assert rval == "new"


def test_compare_env_texts_roundtrip():
    left = "FOO=1\nBAR=2\n"
    right = "FOO=1\nBAR=changed\nNEW=3\n"
    result = compare_env_texts(left, right)
    assert result.has_differences
    assert "BAR" in [k for k, _, _ in result.value_changed]
    assert "NEW" in result.only_in_right


def test_format_compare_result_no_diff():
    result = CompareResult(identical=["A"])
    output = format_compare_result(result)
    assert "no differences" in output


def test_format_compare_result_shows_changes():
    result = CompareResult(
        only_in_left=["OLD"],
        only_in_right=["NEW"],
        value_changed=[("X", "a", "b")],
    )
    output = format_compare_result(result)
    assert "< OLD" in output
    assert "> NEW" in output
    assert "~ X" in output


def test_format_compare_result_mask_values():
    result = CompareResult(value_changed=[("SECRET", "real", "other")])
    output = format_compare_result(result, mask_values=True)
    assert "real" not in output
    assert "[hidden]" in output


def test_summary_identical():
    result = CompareResult(identical=["A", "B"])
    assert result.summary() == "Files are identical."


def test_summary_with_differences():
    result = CompareResult(only_in_left=["A"], value_changed=[("B", "x", "y")])
    summary = result.summary()
    assert "only in left" in summary
    assert "value(s) changed" in summary
