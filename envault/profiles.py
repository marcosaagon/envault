"""Profile management for envault — supports named env profiles (e.g. dev, prod)."""

import json
import os
from pathlib import Path

DEFAULT_PROFILE = "default"
PROFILES_CONFIG_FILE = ".envault_profiles.json"


def _config_path(base_dir: str = ".") -> Path:
    return Path(base_dir) / PROFILES_CONFIG_FILE


def load_profiles(base_dir: str = ".") -> dict:
    """Load profiles config from disk. Returns empty dict if not found."""
    path = _config_path(base_dir)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def save_profiles(profiles: dict, base_dir: str = ".") -> None:
    """Persist profiles config to disk."""
    path = _config_path(base_dir)
    with open(path, "w") as f:
        json.dump(profiles, f, indent=2)


def add_profile(name: str, env_file: str, vault_file: str, base_dir: str = ".") -> None:
    """Register a new named profile mapping env_file <-> vault_file."""
    profiles = load_profiles(base_dir)
    profiles[name] = {
        "env_file": env_file,
        "vault_file": vault_file,
    }
    save_profiles(profiles, base_dir)


def get_profile(name: str, base_dir: str = ".") -> dict:
    """Retrieve a profile by name. Raises KeyError if not found."""
    profiles = load_profiles(base_dir)
    if name not in profiles:
        raise KeyError(f"Profile '{name}' not found. Available: {list(profiles.keys())}")
    return profiles[name]


def remove_profile(name: str, base_dir: str = ".") -> None:
    """Remove a profile by name. Raises KeyError if not found."""
    profiles = load_profiles(base_dir)
    if name not in profiles:
        raise KeyError(f"Profile '{name}' does not exist.")
    del profiles[name]
    save_profiles(profiles, base_dir)


def list_profiles(base_dir: str = ".") -> list:
    """Return sorted list of profile names."""
    return sorted(load_profiles(base_dir).keys())
