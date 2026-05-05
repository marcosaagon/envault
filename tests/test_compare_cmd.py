"""Tests for envault compare CLI commands."""

import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.compare_cmd import compare_group
from envault.vault import lock


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def env_file_left(tmp_path):
    f = tmp_path / ".env.left"
    f.write_text("FOO=bar\nBAZ=qux\n")
    return f


@pytest.fixture
def env_file_right(tmp_path):
    f = tmp_path / ".env.right"
    f.write_text("FOO=bar\nBAZ=changed\nNEW=val\n")
    return f


def test_compare_env_identical(runner, tmp_path):
    f = tmp_path / ".env"
    f.write_text("FOO=bar\n")
    result = runner.invoke(compare_group, ["env", str(f), str(f)])
    assert result.exit_code == 0
    assert "identical" in result.output.lower()


def test_compare_env_differences(runner, env_file_left, env_file_right):
    result = runner.invoke(
        compare_group, ["env", str(env_file_left), str(env_file_right)]
    )
    assert result.exit_code == 1
    assert "BAZ" in result.output
    assert "NEW" in result.output


def test_compare_env_mask_hides_values(runner, env_file_left, env_file_right):
    result = runner.invoke(
        compare_group, ["env", "--mask", str(env_file_left), str(env_file_right)]
    )
    assert "[hidden]" in result.output
    assert "changed" not in result.output


def test_compare_env_missing_file(runner, tmp_path):
    real = tmp_path / ".env"
    real.write_text("FOO=bar\n")
    result = runner.invoke(compare_group, ["env", str(real), str(tmp_path / "missing")])
    assert result.exit_code != 0


def test_compare_vault_identical(runner, tmp_path):
    password = "testpass"
    content = "FOO=bar\nBAZ=qux\n"
    vault_a = tmp_path / "a.vault"
    vault_b = tmp_path / "b.vault"
    env_a = tmp_path / ".env.a"
    env_b = tmp_path / ".env.b"
    env_a.write_text(content)
    env_b.write_text(content)
    lock(env_a, vault_a, password)
    lock(env_b, vault_b, password)
    result = runner.invoke(
        compare_group,
        ["vault", str(vault_a), str(vault_b), "--password", password],
    )
    assert result.exit_code == 0
    assert "identical" in result.output.lower()


def test_compare_vault_wrong_password(runner, tmp_path):
    password = "correct"
    env_a = tmp_path / ".env.a"
    vault_a = tmp_path / "a.vault"
    env_a.write_text("FOO=bar\n")
    lock(env_a, vault_a, password)
    result = runner.invoke(
        compare_group,
        ["vault", str(vault_a), str(vault_a), "--password", "wrong"],
    )
    assert result.exit_code != 0
