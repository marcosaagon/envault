"""Tests for envault.watch module."""

import time
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from envault.watch import EnvWatcher, _file_hash


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("KEY=value\n")
    return f


def test_file_hash_returns_string(env_file):
    result = _file_hash(env_file)
    assert isinstance(result, str)
    assert len(result) == 32


def test_file_hash_missing_file(tmp_path):
    assert _file_hash(tmp_path / "missing.env") is None


def test_file_hash_changes_on_content_change(env_file):
    h1 = _file_hash(env_file)
    env_file.write_text("KEY=other\n")
    h2 = _file_hash(env_file)
    assert h1 != h2


def test_watcher_starts_and_stops(env_file):
    callback = MagicMock()
    watcher = EnvWatcher(env_file, callback, poll_interval=0.1)
    watcher.start()
    assert watcher.is_running
    watcher.stop()
    assert not watcher.is_running


def test_watcher_calls_callback_on_change(env_file):
    called_paths = []

    def cb(path):
        called_paths.append(path)

    watcher = EnvWatcher(env_file, cb, poll_interval=0.05)
    watcher.start()
    time.sleep(0.05)
    env_file.write_text("KEY=changed\n")
    time.sleep(0.3)
    watcher.stop()
    assert len(called_paths) >= 1
    assert called_paths[0] == env_file


def test_watcher_no_callback_if_no_change(env_file):
    callback = MagicMock()
    watcher = EnvWatcher(env_file, callback, poll_interval=0.05)
    watcher.start()
    time.sleep(0.3)
    watcher.stop()
    callback.assert_not_called()


def test_watcher_start_twice_is_safe(env_file):
    callback = MagicMock()
    watcher = EnvWatcher(env_file, callback, poll_interval=0.1)
    watcher.start()
    watcher.start()  # should not raise
    watcher.stop()


def test_watcher_callback_exception_does_not_crash(env_file):
    def bad_cb(path):
        raise RuntimeError("oops")

    watcher = EnvWatcher(env_file, bad_cb, poll_interval=0.05)
    watcher.start()
    env_file.write_text("KEY=boom\n")
    time.sleep(0.3)
    watcher.stop()  # should not propagate exception
