"""Tests for envault.search module."""

from __future__ import annotations

from pathlib import Path

import pytest

from envault.search import (
    SearchResult,
    format_results,
    search_env_text,
    search_vault,
)
from envault.vault import lock


ENV_TEXT = """
# This is a comment
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=supersecret
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
EMPTY_VALUE=
"""


# ---------------------------------------------------------------------------
# search_env_text
# ---------------------------------------------------------------------------

def test_search_env_text_finds_key_substring():
    results = search_env_text(ENV_TEXT, "DB", source="test")
    keys = [r.key for r in results]
    assert "DB_HOST" in keys
    assert "DB_PORT" in keys


def test_search_env_text_finds_value_substring():
    results = search_env_text(ENV_TEXT, "localhost", source="test")
    assert len(results) == 1
    assert results[0].key == "DB_HOST"


def test_search_env_text_case_insensitive():
    results = search_env_text(ENV_TEXT, "secret", source="test")
    keys = [r.key for r in results]
    assert "SECRET_KEY" in keys


def test_search_env_text_no_match_returns_empty():
    results = search_env_text(ENV_TEXT, "NONEXISTENT_XYZ", source="test")
    assert results == []


def test_search_env_text_ignores_comments():
    results = search_env_text(ENV_TEXT, "comment", source="test")
    assert results == []


def test_search_env_text_regex_pattern():
    # Match keys that start with AWS or SECRET
    results = search_env_text(ENV_TEXT, r"^(AWS|SECRET)", source="test")
    keys = [r.key for r in results]
    assert "AWS_ACCESS_KEY_ID" in keys
    assert "SECRET_KEY" in keys
    assert "DB_HOST" not in keys


def test_search_env_text_result_has_source():
    results = search_env_text(ENV_TEXT, "DB_HOST", source="my_vault")
    assert all(r.source == "my_vault" for r in results)


# ---------------------------------------------------------------------------
# search_vault (integration with vault lock/unlock)
# ---------------------------------------------------------------------------

@pytest.fixture()
def vault_file(tmp_path: Path):
    env = tmp_path / ".env"
    env.write_text(ENV_TEXT)
    vault = tmp_path / ".env.vault"
    lock(env, vault, password="testpass")
    return vault


def test_search_vault_finds_key(vault_file: Path):
    results = search_vault(vault_file, "testpass", "DB_HOST")
    assert any(r.key == "DB_HOST" for r in results)


def test_search_vault_keys_only_skips_value_match(vault_file: Path):
    # "localhost" only appears in the value of DB_HOST
    results = search_vault(vault_file, "testpass", "localhost", keys_only=True)
    assert results == []


def test_search_vault_keys_only_matches_key(vault_file: Path):
    results = search_vault(vault_file, "testpass", "SECRET", keys_only=True)
    assert any(r.key == "SECRET_KEY" for r in results)


# ---------------------------------------------------------------------------
# format_results
# ---------------------------------------------------------------------------

def test_format_results_no_matches():
    assert format_results([]) == "No matches found."


def test_format_results_shows_key_value():
    r = SearchResult(key="FOO", value="bar", source="vault")
    output = format_results([r])
    assert "FOO=bar" in output
    assert "[vault]" in output


def test_format_results_hides_values():
    r = SearchResult(key="FOO", value="bar", source="vault")
    output = format_results([r], show_values=False)
    assert "bar" not in output
    assert "FOO" in output
