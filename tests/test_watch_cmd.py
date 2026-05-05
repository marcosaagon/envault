"""Tests for envault.watch_cmd CLI commands."""

from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from envault.watch_cmd import watch_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("SECRET=abc\n")
    return f


def test_watch_start_missing_env_file(runner, tmp_path):
    with runner.isolated_filesystem():
        result = runner.invoke(
            watch_group,
            ["start", "nonexistent.env", "--password", "pw"],
        )
    assert result.exit_code != 0
    assert "not found" in result.output.lower() or "Error" in result.output


def test_watch_start_exits_on_keyboard_interrupt(runner, env_file):
    """Simulate Ctrl+C stopping the watcher gracefully."""
    import time as _time

    real_sleep = _time.sleep

    call_count = 0

    def fake_sleep(n):
        nonlocal call_count
        call_count += 1
        if call_count >= 2:
            raise KeyboardInterrupt
        real_sleep(0.01)

    with patch("envault.watch_cmd.EnvWatcher") as MockWatcher, \
         patch("time.sleep", side_effect=fake_sleep):
        mock_instance = MagicMock()
        MockWatcher.return_value = mock_instance

        result = runner.invoke(
            watch_group,
            ["start", str(env_file), "--vault", str(env_file.parent / ".env.vault"),
             "--password", "secret", "--interval", "0.1"],
        )

    assert result.exit_code == 0
    assert "stopped" in result.output.lower()
    mock_instance.start.assert_called_once()
    mock_instance.stop.assert_called_once()
