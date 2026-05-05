"""Tests for envault.tags_cmd CLI commands."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.tags_cmd import tags_group


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def tmp_dir(tmp_path: Path) -> str:
    return str(tmp_path)


def test_add_tag_outputs_confirmation(runner: CliRunner, tmp_dir: str) -> None:
    result = runner.invoke(tags_group, ["add", "DB_HOST", "db", "--dir", tmp_dir])
    assert result.exit_code == 0
    assert "Tagged 'DB_HOST' with 'db'" in result.output


def test_remove_tag_outputs_confirmation(runner: CliRunner, tmp_dir: str) -> None:
    runner.invoke(tags_group, ["add", "DB_HOST", "db", "--dir", tmp_dir])
    result = runner.invoke(tags_group, ["remove", "DB_HOST", "db", "--dir", tmp_dir])
    assert result.exit_code == 0
    assert "Removed tag 'db' from 'DB_HOST'" in result.output


def test_list_all_tags(runner: CliRunner, tmp_dir: str) -> None:
    runner.invoke(tags_group, ["add", "DB_HOST", "db", "--dir", tmp_dir])
    runner.invoke(tags_group, ["add", "API_KEY", "secrets", "--dir", tmp_dir])
    result = runner.invoke(tags_group, ["list", "--dir", tmp_dir])
    assert result.exit_code == 0
    assert "db" in result.output
    assert "secrets" in result.output


def test_list_tags_for_key(runner: CliRunner, tmp_dir: str) -> None:
    runner.invoke(tags_group, ["add", "API_KEY", "secrets", "--dir", tmp_dir])
    result = runner.invoke(tags_group, ["list", "--key", "API_KEY", "--dir", tmp_dir])
    assert result.exit_code == 0
    assert "secrets" in result.output


def test_list_keys_for_tag(runner: CliRunner, tmp_dir: str) -> None:
    runner.invoke(tags_group, ["add", "DB_HOST", "db", "--dir", tmp_dir])
    runner.invoke(tags_group, ["add", "DB_PASS", "db", "--dir", tmp_dir])
    result = runner.invoke(tags_group, ["list", "--tag", "db", "--dir", tmp_dir])
    assert result.exit_code == 0
    assert "DB_HOST" in result.output
    assert "DB_PASS" in result.output


def test_list_no_tags_message(runner: CliRunner, tmp_dir: str) -> None:
    result = runner.invoke(tags_group, ["list", "--dir", tmp_dir])
    assert result.exit_code == 0
    assert "No tags defined" in result.output


def test_list_key_no_tags_message(runner: CliRunner, tmp_dir: str) -> None:
    result = runner.invoke(tags_group, ["list", "--key", "MISSING", "--dir", tmp_dir])
    assert result.exit_code == 0
    assert "No tags found" in result.output


def test_list_tag_no_keys_message(runner: CliRunner, tmp_dir: str) -> None:
    result = runner.invoke(tags_group, ["list", "--tag", "ghost", "--dir", tmp_dir])
    assert result.exit_code == 0
    assert "No keys found" in result.output
