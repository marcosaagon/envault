"""Tests for the export CLI commands."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.export_cmd import export_group
from envault.crypto import encrypt

SAMPLE_ENV = "HOST=localhost\nPORT=5432\nTOKEN=secret\n"


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(SAMPLE_ENV)
    return p


@pytest.fixture
def vault_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env.vault"
    p.write_text(encrypt(SAMPLE_ENV, "pass"))
    return p


def test_export_env_json(runner: CliRunner, env_file: Path):
    result = runner.invoke(export_group, ["env", str(env_file), "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["HOST"] == "localhost"


def test_export_env_dotenv(runner: CliRunner, env_file: Path):
    result = runner.invoke(export_group, ["env", str(env_file), "--format", "dotenv"])
    assert result.exit_code == 0
    assert "HOST=localhost" in result.output


def test_export_env_toml(runner: CliRunner, env_file: Path):
    result = runner.invoke(export_group, ["env", str(env_file), "--format", "toml"])
    assert result.exit_code == 0
    assert 'HOST = "localhost"' in result.output


def test_export_env_to_output_file(runner: CliRunner, env_file: Path, tmp_path: Path):
    out = tmp_path / "out.json"
    result = runner.invoke(export_group, ["env", str(env_file), "--format", "json", "-o", str(out)])
    assert result.exit_code == 0
    assert out.exists()
    assert json.loads(out.read_text())["PORT"] == "5432"


def test_export_vault_json(runner: CliRunner, vault_file: Path):
    result = runner.invoke(
        export_group, ["vault", str(vault_file), "--format", "json", "--password", "pass"]
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["TOKEN"] == "secret"


def test_export_vault_wrong_password(runner: CliRunner, vault_file: Path):
    result = runner.invoke(
        export_group, ["vault", str(vault_file), "--password", "wrong"]
    )
    assert result.exit_code != 0
    assert "Error" in result.output


def test_import_cmd_roundtrip(runner: CliRunner, tmp_path: Path):
    source = tmp_path / "data.json"
    source.write_text(json.dumps({"KEY": "value", "OTHER": "data"}))
    vault = tmp_path / "new.vault"
    result = runner.invoke(
        export_group,
        ["import", str(source), str(vault), "--format", "json",
         "--password", "pw"],
        input="pw\npw\n",
    )
    assert result.exit_code == 0
    assert vault.exists()
    verify = runner.invoke(
        export_group, ["vault", str(vault), "--format", "json", "--password", "pw"]
    )
    assert json.loads(verify.output)["KEY"] == "value"


def test_export_env_missing_file(runner: CliRunner):
    result = runner.invoke(export_group, ["env", "/nonexistent/.env"])
    assert result.exit_code != 0
