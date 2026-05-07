"""Tests for envault.env_pin module."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.env_pin import (
    load_pins,
    save_pins,
    pin_key,
    unpin_key,
    is_pinned,
    filter_pinned,
    _pins_path,
)


@pytest.fixture
def vault_file(tmp_path: Path) -> Path:
    v = tmp_path / "test.vault"
    v.write_text("encrypted_blob")
    return v


def test_load_pins_returns_empty_when_no_file(vault_file: Path) -> None:
    assert load_pins(vault_file) == []


def test_save_and_load_pins_roundtrip(vault_file: Path) -> None:
    save_pins(vault_file, ["DB_PASSWORD", "API_KEY"])
    result = load_pins(vault_file)
    assert "DB_PASSWORD" in result
    assert "API_KEY" in result


def test_save_creates_json_file(vault_file: Path) -> None:
    save_pins(vault_file, ["SECRET"])
    pins_path = _pins_path(vault_file)
    assert pins_path.exists()
    data = json.loads(pins_path.read_text())
    assert "pinned" in data


def test_pin_key_returns_true_when_newly_pinned(vault_file: Path) -> None:
    assert pin_key(vault_file, "TOKEN") is True


def test_pin_key_returns_false_when_already_pinned(vault_file: Path) -> None:
    pin_key(vault_file, "TOKEN")
    assert pin_key(vault_file, "TOKEN") is False


def test_pin_key_persists(vault_file: Path) -> None:
    pin_key(vault_file, "MY_KEY")
    assert "MY_KEY" in load_pins(vault_file)


def test_unpin_key_returns_true_when_removed(vault_file: Path) -> None:
    pin_key(vault_file, "REMOVE_ME")
    assert unpin_key(vault_file, "REMOVE_ME") is True


def test_unpin_key_returns_false_when_not_pinned(vault_file: Path) -> None:
    assert unpin_key(vault_file, "GHOST") is False


def test_unpin_key_removes_from_list(vault_file: Path) -> None:
    pin_key(vault_file, "GONE")
    unpin_key(vault_file, "GONE")
    assert "GONE" not in load_pins(vault_file)


def test_is_pinned_true(vault_file: Path) -> None:
    pin_key(vault_file, "X")
    assert is_pinned(vault_file, "X") is True


def test_is_pinned_false(vault_file: Path) -> None:
    assert is_pinned(vault_file, "NOPE") is False


def test_filter_pinned_returns_only_pinned(vault_file: Path) -> None:
    pin_key(vault_file, "A")
    pin_key(vault_file, "C")
    result = filter_pinned(vault_file, ["A", "B", "C", "D"])
    assert result == ["A", "C"]


def test_save_pins_deduplicates(vault_file: Path) -> None:
    save_pins(vault_file, ["DUP", "DUP", "OTHER"])
    pins = load_pins(vault_file)
    assert pins.count("DUP") == 1
