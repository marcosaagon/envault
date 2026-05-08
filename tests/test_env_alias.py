"""Tests for envault.env_alias."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.env_alias import (
    add_alias,
    list_aliases,
    load_aliases,
    remove_alias,
    resolve_alias,
    save_aliases,
)


@pytest.fixture()
def vault_file(tmp_path: Path) -> Path:
    vf = tmp_path / ".env.vault"
    vf.write_text("encrypted-blob")
    return vf


def test_load_aliases_returns_empty_when_no_file(vault_file: Path) -> None:
    result = load_aliases(vault_file)
    assert result == {}


def test_save_and_load_roundtrip(vault_file: Path) -> None:
    data = {"db": "DATABASE_URL", "secret": "SECRET_KEY"}
    save_aliases(vault_file, data)
    loaded = load_aliases(vault_file)
    assert loaded == data


def test_save_creates_json_file(vault_file: Path) -> None:
    save_aliases(vault_file, {"x": "MY_KEY"})
    alias_file = vault_file.parent / ".envault_aliases.json"
    assert alias_file.exists()
    raw = json.loads(alias_file.read_text())
    assert raw == {"x": "MY_KEY"}


def test_add_alias_returns_true_when_new(vault_file: Path) -> None:
    assert add_alias(vault_file, "db", "DATABASE_URL") is True


def test_add_alias_returns_false_when_updated(vault_file: Path) -> None:
    add_alias(vault_file, "db", "DATABASE_URL")
    assert add_alias(vault_file, "db", "DB_URL") is False


def test_add_alias_persists_mapping(vault_file: Path) -> None:
    add_alias(vault_file, "token", "API_TOKEN")
    aliases = load_aliases(vault_file)
    assert aliases["token"] == "API_TOKEN"


def test_remove_alias_returns_true_when_existed(vault_file: Path) -> None:
    add_alias(vault_file, "db", "DATABASE_URL")
    assert remove_alias(vault_file, "db") is True


def test_remove_alias_returns_false_when_missing(vault_file: Path) -> None:
    assert remove_alias(vault_file, "nonexistent") is False


def test_remove_alias_deletes_entry(vault_file: Path) -> None:
    add_alias(vault_file, "db", "DATABASE_URL")
    remove_alias(vault_file, "db")
    assert "db" not in load_aliases(vault_file)


def test_resolve_alias_returns_key(vault_file: Path) -> None:
    add_alias(vault_file, "s", "SECRET_KEY")
    assert resolve_alias(vault_file, "s") == "SECRET_KEY"


def test_resolve_alias_returns_none_for_unknown(vault_file: Path) -> None:
    assert resolve_alias(vault_file, "unknown") is None


def test_list_aliases_returns_all(vault_file: Path) -> None:
    add_alias(vault_file, "a", "AAA")
    add_alias(vault_file, "b", "BBB")
    result = list_aliases(vault_file)
    assert result == {"a": "AAA", "b": "BBB"}
