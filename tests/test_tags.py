"""Tests for envault.tags module."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.tags import (
    _TAGS_FILENAME,
    add_tag,
    all_tags,
    keys_for_tag,
    load_tags,
    remove_tag,
    save_tags,
    tags_for_key,
)


@pytest.fixture
def tmp_dir(tmp_path: Path) -> str:
    return str(tmp_path)


def test_load_tags_returns_empty_when_no_file(tmp_dir: str) -> None:
    assert load_tags(tmp_dir) == {}


def test_save_and_load_roundtrip(tmp_dir: str) -> None:
    data = {"DB_HOST": ["db", "prod"], "API_KEY": ["secrets"]}
    save_tags(data, tmp_dir)
    assert load_tags(tmp_dir) == data


def test_save_creates_json_file(tmp_dir: str) -> None:
    save_tags({"FOO": ["bar"]}, tmp_dir)
    tags_file = Path(tmp_dir) / _TAGS_FILENAME
    assert tags_file.exists()
    raw = json.loads(tags_file.read_text())
    assert raw == {"FOO": ["bar"]}


def test_add_tag_stores_entry(tmp_dir: str) -> None:
    add_tag("MY_KEY", "production", tmp_dir)
    assert "production" in load_tags(tmp_dir)["MY_KEY"]


def test_add_tag_no_duplicates(tmp_dir: str) -> None:
    add_tag("MY_KEY", "production", tmp_dir)
    add_tag("MY_KEY", "production", tmp_dir)
    assert load_tags(tmp_dir)["MY_KEY"].count("production") == 1


def test_add_multiple_tags(tmp_dir: str) -> None:
    add_tag("MY_KEY", "production", tmp_dir)
    add_tag("MY_KEY", "secrets", tmp_dir)
    assert set(load_tags(tmp_dir)["MY_KEY"]) == {"production", "secrets"}


def test_remove_tag(tmp_dir: str) -> None:
    add_tag("MY_KEY", "production", tmp_dir)
    add_tag("MY_KEY", "secrets", tmp_dir)
    remove_tag("MY_KEY", "production", tmp_dir)
    assert load_tags(tmp_dir)["MY_KEY"] == ["secrets"]


def test_remove_last_tag_removes_key(tmp_dir: str) -> None:
    add_tag("MY_KEY", "production", tmp_dir)
    remove_tag("MY_KEY", "production", tmp_dir)
    assert "MY_KEY" not in load_tags(tmp_dir)


def test_keys_for_tag(tmp_dir: str) -> None:
    add_tag("DB_HOST", "db", tmp_dir)
    add_tag("DB_PASS", "db", tmp_dir)
    add_tag("API_KEY", "secrets", tmp_dir)
    result = keys_for_tag("db", tmp_dir)
    assert set(result) == {"DB_HOST", "DB_PASS"}


def test_tags_for_key(tmp_dir: str) -> None:
    add_tag("API_KEY", "secrets", tmp_dir)
    add_tag("API_KEY", "prod", tmp_dir)
    assert set(tags_for_key("API_KEY", tmp_dir)) == {"secrets", "prod"}


def test_tags_for_key_missing_returns_empty(tmp_dir: str) -> None:
    assert tags_for_key("NONEXISTENT", tmp_dir) == []


def test_all_tags_sorted(tmp_dir: str) -> None:
    add_tag("X", "zebra", tmp_dir)
    add_tag("Y", "alpha", tmp_dir)
    add_tag("Z", "alpha", tmp_dir)
    assert all_tags(tmp_dir) == ["alpha", "zebra"]


def test_all_tags_empty_when_no_tags(tmp_dir: str) -> None:
    assert all_tags(tmp_dir) == []
