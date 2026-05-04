"""Tests for envault.lint_cmd CLI commands."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.lint_cmd import lint_group
from envault.vault import lock

GOOD_ENV = "DB_HOST=localhost\nDB_PORT=5432\n"
BAD_ENV = "MISSING_EQUALS\nDUP=1\nDUP=2\n"


@pytest.fixture()
def runner():
    return CliRunner()


# ── lint env ──────────────────────────────────────────────────────────────────

def test_lint_env_ok(runner: CliRunner, tmp_path: Path):
    env = tmp_path / ".env"
    env.write_text(GOOD_ENV)
    result = runner.invoke(lint_group, ["env", str(env)])
    assert result.exit_code == 0
    assert "no issues" in result.output


def test_lint_env_issues_exits_nonzero(runner: CliRunner, tmp_path: Path):
    env = tmp_path / ".env"
    env.write_text(BAD_ENV)
    result = runner.invoke(lint_group, ["env", str(env)])
    assert result.exit_code != 0
    assert "E001" in result.output or "W001" in result.output


def test_lint_env_missing_file(runner: CliRunner, tmp_path: Path):
    result = runner.invoke(lint_group, ["env", str(tmp_path / "nope.env")])
    assert result.exit_code != 0
    assert "not found" in result.output


# ── lint vault ────────────────────────────────────────────────────────────────

def test_lint_vault_ok(runner: CliRunner, tmp_path: Path):
    env = tmp_path / ".env"
    vault = tmp_path / ".env.vault"
    env.write_text(GOOD_ENV)
    lock(env, vault, "pass")
    result = runner.invoke(lint_group, ["vault", str(vault), "--password", "pass"])
    assert result.exit_code == 0
    assert "no issues" in result.output


def test_lint_vault_wrong_password(runner: CliRunner, tmp_path: Path):
    env = tmp_path / ".env"
    vault = tmp_path / ".env.vault"
    env.write_text(GOOD_ENV)
    lock(env, vault, "pass")
    result = runner.invoke(lint_group, ["vault", str(vault), "--password", "wrong"])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_lint_vault_missing_file(runner: CliRunner, tmp_path: Path):
    result = runner.invoke(
        lint_group, ["vault", str(tmp_path / "nope.vault"), "--password", "x"]
    )
    assert result.exit_code != 0
    assert "not found" in result.output
