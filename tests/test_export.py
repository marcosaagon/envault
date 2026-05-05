"""Tests for envault.export module."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.export import (
    export_env_file,
    export_vault_file,
    import_to_vault,
    parse_env_text,
    to_dotenv,
    to_json,
    to_toml,
    _parse_toml,
)
from envault.crypto import encrypt


SAMPLE_ENV = "DB_HOST=localhost\nDB_PORT=5432\nSECRET=abc123\n"


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


def test_parse_env_text_basic():
    data = parse_env_text(SAMPLE_ENV)
    assert data["DB_HOST"] == "localhost"
    assert data["DB_PORT"] == "5432"
    assert data["SECRET"] == "abc123"


def test_parse_env_text_ignores_comments():
    data = parse_env_text("# comment\nKEY=val\n")
    assert "# comment" not in data
    assert data["KEY"] == "val"


def test_parse_env_text_ignores_blank_lines():
    data = parse_env_text("\n\nKEY=val\n")
    assert len(data) == 1


def test_to_dotenv_roundtrip():
    data = {"A": "1", "B": "2"}
    result = to_dotenv(data)
    assert "A=1" in result
    assert "B=2" in result


def test_to_json_is_valid_json():
    data = {"KEY": "value"}
    result = to_json(data)
    parsed = json.loads(result)
    assert parsed == data


def test_to_toml_and_parse_roundtrip():
    data = {"HOST": "localhost", "PORT": "5432"}
    toml_str = to_toml(data)
    parsed = _parse_toml(toml_str)
    assert parsed == data


def test_export_env_file_json(env_file: Path):
    result = export_env_file(env_file, "json")
    parsed = json.loads(result)
    assert parsed["DB_HOST"] == "localhost"


def test_export_env_file_dotenv(env_file: Path):
    result = export_env_file(env_file, "dotenv")
    assert "DB_HOST=localhost" in result


def test_export_env_file_toml(env_file: Path):
    result = export_env_file(env_file, "toml")
    assert 'DB_HOST = "localhost"' in result


def test_export_vault_file_json(vault_file: Path):
    result = export_vault_file(vault_file, "pass", "json")
    parsed = json.loads(result)
    assert parsed["SECRET"] == "abc123"


def test_export_vault_wrong_password_raises(vault_file: Path):
    with pytest.raises(Exception):
        export_vault_file(vault_file, "wrong", "json")


def test_import_to_vault_roundtrip(tmp_path: Path):
    data = json.dumps({"FOO": "bar", "BAZ": "qux"})
    vault = tmp_path / "out.vault"
    import_to_vault(data, "json", vault, "secret")
    assert vault.exists()
    recovered = export_vault_file(vault, "secret", "json")
    assert json.loads(recovered)["FOO"] == "bar"


def test_import_to_vault_from_dotenv(tmp_path: Path):
    dotenv = "X=1\nY=2\n"
    vault = tmp_path / "out.vault"
    import_to_vault(dotenv, "dotenv", vault, "pw")
    result = export_vault_file(vault, "pw", "json")
    assert json.loads(result)["X"] == "1"
