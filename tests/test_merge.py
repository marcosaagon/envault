"""Tests for envault.merge module."""

from __future__ import annotations

import pytest

from envault.merge import (
    ConflictStrategy,
    MergeConflict,
    MergeResult,
    merge_envs,
    parse_env,
    serialize_env,
)


# ---------------------------------------------------------------------------
# parse_env
# ---------------------------------------------------------------------------

def test_parse_env_basic():
    text = "FOO=bar\nBAZ=qux\n"
    result = parse_env(text)
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_parse_env_ignores_comments():
    text = "# comment\nFOO=bar\n"
    result = parse_env(text)
    assert "# comment" not in result
    assert result["FOO"] == "bar"


def test_parse_env_ignores_blank_lines():
    text = "\nFOO=bar\n\n"
    result = parse_env(text)
    assert result == {"FOO": "bar"}


def test_parse_env_no_equals_skipped():
    text = "NOEQUALS\nFOO=bar\n"
    result = parse_env(text)
    assert "NOEQUALS" not in result


# ---------------------------------------------------------------------------
# merge_envs — no conflicts
# ---------------------------------------------------------------------------

def test_merge_adds_new_keys_from_theirs():
    base = {"A": "1"}
    theirs = {"A": "1", "B": "2"}
    result = merge_envs(base, theirs)
    assert result.merged["B"] == "2"
    assert "B" in result.added


def test_merge_keeps_base_only_keys():
    base = {"A": "1", "B": "2"}
    theirs = {"A": "1"}
    result = merge_envs(base, theirs)
    assert "B" in result.merged
    assert "B" in result.removed


def test_merge_no_conflict_when_values_equal():
    base = {"A": "1"}
    theirs = {"A": "1"}
    result = merge_envs(base, theirs)
    assert not result.has_conflicts


# ---------------------------------------------------------------------------
# merge_envs — conflicts
# ---------------------------------------------------------------------------

def test_merge_conflict_detected():
    base = {"A": "old"}
    theirs = {"A": "new"}
    result = merge_envs(base, theirs, ConflictStrategy.OURS)
    assert result.has_conflicts
    assert result.conflicts[0].key == "A"
    assert result.conflicts[0].ours == "old"
    assert result.conflicts[0].theirs == "new"


def test_merge_strategy_ours_keeps_base_value():
    base = {"A": "old"}
    theirs = {"A": "new"}
    result = merge_envs(base, theirs, ConflictStrategy.OURS)
    assert result.merged["A"] == "old"


def test_merge_strategy_theirs_overwrites():
    base = {"A": "old"}
    theirs = {"A": "new"}
    result = merge_envs(base, theirs, ConflictStrategy.THEIRS)
    assert result.merged["A"] == "new"
    assert "A" in result.overwritten


# ---------------------------------------------------------------------------
# serialize_env
# ---------------------------------------------------------------------------

def test_serialize_env_round_trip():
    env = {"FOO": "bar", "BAZ": "qux"}
    text = serialize_env(env)
    parsed = parse_env(text)
    assert parsed == env


def test_serialize_env_sorted_keys():
    env = {"Z": "1", "A": "2"}
    lines = serialize_env(env).splitlines()
    assert lines[0].startswith("A=")
    assert lines[1].startswith("Z=")
