"""Tests for envault.filter_cmd CLI commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.filter_cmd import filter_group
from envault.vault import lock


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text(
        "DB_HOST=localhost\nDB_PORT=5432\nAWS_KEY=secret\nAPP_NAME=myapp\n"
    )
    return str(p)


@pytest.fixture()
def vault_file(tmp_path, env_file):
    vf = str(tmp_path / ".env.vault")
    lock(env_file, vf, "testpass")
    return vf


def test_filter_env_prefix(runner, env_file):
    result = runner.invoke(filter_group, ["env", env_file, "--prefix", "DB_"])
    assert result.exit_code == 0
    assert "DB_HOST" in result.output
    assert "AWS_KEY" not in result.output


def test_filter_env_suffix(runner, env_file):
    result = runner.invoke(filter_group, ["env", env_file, "--suffix", "_KEY"])
    assert result.exit_code == 0
    assert "AWS_KEY" in result.output
    assert "DB_HOST" not in result.output


def test_filter_env_pattern(runner, env_file):
    result = runner.invoke(filter_group, ["env", env_file, "--pattern", "APP_*"])
    assert result.exit_code == 0
    assert "APP_NAME" in result.output


def test_filter_env_invert(runner, env_file):
    result = runner.invoke(filter_group, ["env", env_file, "--prefix", "DB_", "--invert"])
    assert result.exit_code == 0
    assert "AWS_KEY" in result.output
    assert "DB_HOST" not in result.output


def test_filter_env_no_match_exits_nonzero(runner, env_file):
    result = runner.invoke(filter_group, ["env", env_file, "--prefix", "NOPE_"])
    assert result.exit_code != 0


def test_filter_vault_prefix(runner, vault_file):
    result = runner.invoke(
        filter_group,
        ["vault", vault_file, "--password", "testpass", "--prefix", "DB_"],
    )
    assert result.exit_code == 0
    assert "DB_HOST" in result.output
    assert "AWS_KEY" not in result.output


def test_filter_vault_wrong_password(runner, vault_file):
    result = runner.invoke(
        filter_group,
        ["vault", vault_file, "--password", "wrongpass", "--prefix", "DB_"],
    )
    assert result.exit_code != 0
