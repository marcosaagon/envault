"""Tests for envault.env_inject."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.env_inject import build_injected_env, parse_env_text, run_with_vault
from envault.inject_cmd import inject_group
from envault.vault import lock


# ---------------------------------------------------------------------------
# parse_env_text
# ---------------------------------------------------------------------------

def test_parse_env_text_basic():
    text = "FOO=bar\nBAZ=qux\n"
    assert parse_env_text(text) == {"FOO": "bar", "BAZ": "qux"}


def test_parse_env_text_ignores_comments():
    text = "# comment\nFOO=bar\n"
    assert parse_env_text(text) == {"FOO": "bar"}


def test_parse_env_text_ignores_blank_lines():
    text = "\nFOO=bar\n\n"
    assert parse_env_text(text) == {"FOO": "bar"}


def test_parse_env_text_no_equals_skipped():
    text = "NOTAKEY\nFOO=bar\n"
    assert parse_env_text(text) == {"FOO": "bar"}


# ---------------------------------------------------------------------------
# build_injected_env
# ---------------------------------------------------------------------------

@pytest.fixture()
def vault_file(tmp_path: Path) -> Path:
    env = tmp_path / ".env"
    env.write_text("INJECT_KEY=hello\nANOTHER=world\n")
    vf = tmp_path / ".env.vault"
    lock(str(env), str(vf), "secret")
    return vf


def test_build_injected_env_contains_vault_keys(vault_file: Path):
    env = build_injected_env(str(vault_file), "secret")
    assert env["INJECT_KEY"] == "hello"
    assert env["ANOTHER"] == "world"


def test_build_injected_env_includes_os_env(vault_file: Path):
    env = build_injected_env(str(vault_file), "secret")
    # PATH should always be present in os.environ
    assert "PATH" in env


def test_build_injected_env_override_true(vault_file: Path, monkeypatch):
    monkeypatch.setenv("INJECT_KEY", "original")
    env = build_injected_env(str(vault_file), "secret", override=True)
    assert env["INJECT_KEY"] == "hello"


def test_build_injected_env_override_false(vault_file: Path, monkeypatch):
    monkeypatch.setenv("INJECT_KEY", "original")
    env = build_injected_env(str(vault_file), "secret", override=False)
    assert env["INJECT_KEY"] == "original"


def test_build_injected_env_wrong_password_raises(vault_file: Path):
    with pytest.raises(Exception):
        build_injected_env(str(vault_file), "wrong")


# ---------------------------------------------------------------------------
# inject run CLI
# ---------------------------------------------------------------------------

@pytest.fixture()
def runner():
    return CliRunner()


def test_inject_run_missing_vault(runner, tmp_path):
    result = runner.invoke(
        inject_group,
        ["run", "--vault", str(tmp_path / "missing.vault"), "--password", "x", "--", "echo", "hi"],
    )
    assert result.exit_code != 0


def test_inject_print_outputs_keys(runner, vault_file):
    result = runner.invoke(
        inject_group,
        ["print", "--vault", str(vault_file), "--password", "secret"],
    )
    assert result.exit_code == 0
    assert "INJECT_KEY=hello" in result.output
    assert "ANOTHER=world" in result.output


def test_inject_print_wrong_password(runner, vault_file):
    result = runner.invoke(
        inject_group,
        ["print", "--vault", str(vault_file), "--password", "bad"],
    )
    assert result.exit_code != 0
