"""Tests for envault profile management."""

import json
import pytest
from pathlib import Path

from envault.profiles import (
    add_profile,
    get_profile,
    list_profiles,
    load_profiles,
    remove_profile,
    save_profiles,
    PROFILES_CONFIG_FILE,
)


@pytest.fixture
def tmp_dir(tmp_path):
    return str(tmp_path)


def test_load_profiles_returns_empty_when_no_file(tmp_dir):
    result = load_profiles(tmp_dir)
    assert result == {}


def test_save_and_load_profiles_roundtrip(tmp_dir):
    data = {"dev": {"env_file": ".env", "vault_file": ".env.vault"}}
    save_profiles(data, tmp_dir)
    loaded = load_profiles(tmp_dir)
    assert loaded == data


def test_save_creates_json_file(tmp_dir):
    save_profiles({"x": {}}, tmp_dir)
    config_file = Path(tmp_dir) / PROFILES_CONFIG_FILE
    assert config_file.exists()
    with open(config_file) as f:
        content = json.load(f)
    assert "x" in content


def test_add_profile_stores_entry(tmp_dir):
    add_profile("prod", ".env.prod", ".env.prod.vault", tmp_dir)
    profiles = load_profiles(tmp_dir)
    assert "prod" in profiles
    assert profiles["prod"]["env_file"] == ".env.prod"
    assert profiles["prod"]["vault_file"] == ".env.prod.vault"


def test_add_multiple_profiles(tmp_dir):
    add_profile("dev", ".env", ".env.vault", tmp_dir)
    add_profile("staging", ".env.staging", ".env.staging.vault", tmp_dir)
    assert set(list_profiles(tmp_dir)) == {"dev", "staging"}


def test_get_profile_returns_correct_data(tmp_dir):
    add_profile("dev", ".env", ".env.vault", tmp_dir)
    profile = get_profile("dev", tmp_dir)
    assert profile["env_file"] == ".env"
    assert profile["vault_file"] == ".env.vault"


def test_get_profile_raises_for_missing(tmp_dir):
    with pytest.raises(KeyError, match="not found"):
        get_profile("nonexistent", tmp_dir)


def test_remove_profile_deletes_entry(tmp_dir):
    add_profile("temp", ".env", ".env.vault", tmp_dir)
    remove_profile("temp", tmp_dir)
    assert "temp" not in list_profiles(tmp_dir)


def test_remove_profile_raises_for_missing(tmp_dir):
    with pytest.raises(KeyError):
        remove_profile("ghost", tmp_dir)


def test_list_profiles_returns_sorted(tmp_dir):
    add_profile("zebra", ".env", ".env.vault", tmp_dir)
    add_profile("alpha", ".env", ".env.vault", tmp_dir)
    add_profile("middle", ".env", ".env.vault", tmp_dir)
    assert list_profiles(tmp_dir) == ["alpha", "middle", "zebra"]
