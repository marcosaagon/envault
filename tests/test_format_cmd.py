"""Tests for envault.format_cmd CLI commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.format_cmd import format_group
from envault.vault import lock


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("ZEBRA=1\nAPPLE=2\n")
    return p


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / ".env.vault")
    lock(path, "ZEBRA=1\nAPPLE=2\n", "secret")
    return path


def test_format_env_no_changes(runner, env_file):
    result = runner.invoke(
        format_group, ["env", str(env_file)]
    )
    assert result.exit_code == 0
    assert "No changes" in result.output


def test_format_env_sort_keys(runner, env_file):
    result = runner.invoke(
        format_group, ["env", str(env_file), "--sort"]
    )
    assert result.exit_code == 0
    assert "Formatted" in result.output
    content = env_file.read_text()
    lines = [l for l in content.splitlines() if l]
    keys = [l.split("=")[0] for l in lines]
    assert keys == sorted(keys, key=str.lower)


def test_format_env_check_detects_unformatted(runner, env_file):
    result = runner.invoke(
        format_group, ["env", str(env_file), "--sort", "--check"]
    )
    assert result.exit_code == 1
    assert "Would reformat" in result.output


def test_format_env_check_passes_when_formatted(runner, tmp_path):
    p = tmp_path / ".env"
    p.write_text("APPLE=1\nZEBRA=2\n")
    result = runner.invoke(
        format_group, ["env", str(p), "--sort", "--check"]
    )
    assert result.exit_code == 0
    assert "Already formatted" in result.output


def test_format_env_missing_file(runner, tmp_path):
    result = runner.invoke(
        format_group, ["env", str(tmp_path / "missing.env")]
    )
    assert result.exit_code == 1
    assert "not found" in result.output


def test_format_vault_no_changes(runner, vault_file):
    result = runner.invoke(
        format_group,
        ["vault", vault_file, "--password", "secret"],
    )
    assert result.exit_code == 0
    assert "No changes" in result.output


def test_format_vault_sort_keys(runner, vault_file):
    result = runner.invoke(
        format_group,
        ["vault", vault_file, "--password", "secret", "--sort"],
    )
    assert result.exit_code == 0
    assert "Formatted vault" in result.output


def test_format_vault_wrong_password(runner, vault_file):
    result = runner.invoke(
        format_group,
        ["vault", vault_file, "--password", "wrong"],
    )
    assert result.exit_code == 1
    assert "Error" in result.output
