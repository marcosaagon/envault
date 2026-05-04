"""Tests for envault.lint module."""
from __future__ import annotations

import pytest
from pathlib import Path

from envault.lint import lint_env_text, lint_env_file, lint_vault_file, LintResult
from envault.vault import lock


# ── helpers ──────────────────────────────────────────────────────────────────

GOOD_ENV = "DB_HOST=localhost\nDB_PORT=5432\nSECRET_KEY=abc123\n"


# ── lint_env_text ─────────────────────────────────────────────────────────────

def test_lint_clean_env_returns_no_issues():
    result = lint_env_text(GOOD_ENV)
    assert result.ok


def test_lint_missing_equals_is_error():
    result = lint_env_text("BADLINE\n")
    codes = [i.code for i in result.issues]
    assert "E001" in codes


def test_lint_empty_key_is_error():
    result = lint_env_text("=value\n")
    codes = [i.code for i in result.issues]
    assert "E002" in codes


def test_lint_key_with_space_is_error():
    result = lint_env_text("MY KEY=value\n")
    codes = [i.code for i in result.issues]
    assert "E003" in codes


def test_lint_duplicate_key_is_warning():
    result = lint_env_text("FOO=1\nFOO=2\n")
    codes = [i.code for i in result.issues]
    assert "W001" in codes


def test_lint_empty_value_is_warning():
    result = lint_env_text("EMPTY_KEY=\n")
    codes = [i.code for i in result.issues]
    assert "W002" in codes


def test_lint_ignores_comments_and_blank_lines():
    text = "# comment\n\nFOO=bar\n"
    result = lint_env_text(text)
    assert result.ok


def test_lint_result_str_ok():
    result = lint_env_text(GOOD_ENV)
    assert str(result) == "No issues found."


def test_lint_result_str_issues():
    result = lint_env_text("BADLINE\n")
    assert "E001" in str(result)


# ── lint_env_file ─────────────────────────────────────────────────────────────

def test_lint_env_file(tmp_path: Path):
    env = tmp_path / ".env"
    env.write_text(GOOD_ENV)
    result = lint_env_file(env)
    assert result.ok


def test_lint_env_file_with_issues(tmp_path: Path):
    env = tmp_path / ".env"
    env.write_text("BADLINE\n")
    result = lint_env_file(env)
    assert not result.ok


# ── lint_vault_file ───────────────────────────────────────────────────────────

def test_lint_vault_file_clean(tmp_path: Path):
    env = tmp_path / ".env"
    vault = tmp_path / ".env.vault"
    env.write_text(GOOD_ENV)
    lock(env, vault, "secret")
    result = lint_vault_file(vault, "secret")
    assert result.ok


def test_lint_vault_file_wrong_password_raises(tmp_path: Path):
    env = tmp_path / ".env"
    vault = tmp_path / ".env.vault"
    env.write_text(GOOD_ENV)
    lock(env, vault, "secret")
    with pytest.raises(Exception):
        lint_vault_file(vault, "wrong")
