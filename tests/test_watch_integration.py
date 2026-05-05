"""Integration tests: watcher triggers vault.lock on file change."""

import time
from pathlib import Path

import pytest

from envault.watch import EnvWatcher
from envault.vault import lock, unlock


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("API_KEY=initial\n")
    return f


@pytest.fixture
def vault_file(tmp_path):
    return tmp_path / ".env.vault"


def test_watcher_triggers_lock_and_vault_readable(env_file, vault_file):
    password = "watchpass"
    locked_events = []

    def on_change(path: Path):
        lock(path, vault_file, password)
        locked_events.append(True)

    watcher = EnvWatcher(env_file, on_change, poll_interval=0.05)
    watcher.start()

    env_file.write_text("API_KEY=updated\n")
    time.sleep(0.4)
    watcher.stop()

    assert len(locked_events) >= 1
    assert vault_file.exists()

    recovered = unlock(vault_file, password)
    assert "API_KEY=updated" in recovered


def test_watcher_multiple_changes_all_locked(env_file, vault_file):
    password = "multipass"
    values_seen = []

    def on_change(path: Path):
        lock(path, vault_file, password)
        values_seen.append(path.read_text())

    watcher = EnvWatcher(env_file, on_change, poll_interval=0.05)
    watcher.start()

    for i in range(3):
        env_file.write_text(f"COUNTER={i}\n")
        time.sleep(0.2)

    watcher.stop()

    assert len(values_seen) >= 2
    last = unlock(vault_file, password)
    assert "COUNTER=" in last
