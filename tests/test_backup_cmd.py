"""Tests for envault/backup_cmd.py"""

import pytest
from click.testing import CliRunner
from pathlib import Path
from envault.backup_cmd import backup_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path):
    vf = tmp_path / ".env.vault"
    vf.write_text("ENCRYPTED_BLOB")
    return str(vf)


def test_backup_create_success(runner, vault_file):
    result = runner.invoke(backup_group, ["create", vault_file])
    assert result.exit_code == 0
    assert "Backup created" in result.output


def test_backup_create_missing_vault(runner, tmp_path):
    result = runner.invoke(backup_group, ["create", str(tmp_path / "missing.vault")])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_backup_list_empty(runner, vault_file):
    result = runner.invoke(backup_group, ["list", vault_file])
    assert result.exit_code == 0
    assert "No backups found" in result.output


def test_backup_list_shows_entries(runner, vault_file):
    runner.invoke(backup_group, ["create", vault_file])
    result = runner.invoke(backup_group, ["list", vault_file])
    assert result.exit_code == 0
    assert ".vault" in result.output


def test_backup_restore_with_yes_flag(runner, vault_file):
    create_result = runner.invoke(backup_group, ["create", vault_file])
    backup_path = create_result.output.split("Backup created: ")[1].strip()
    Path(vault_file).write_text("CHANGED")
    result = runner.invoke(backup_group, ["restore", backup_path, vault_file, "--yes"])
    assert result.exit_code == 0
    assert "Restored" in result.output
    assert Path(vault_file).read_text() == "ENCRYPTED_BLOB"


def test_backup_restore_missing_backup(runner, vault_file):
    result = runner.invoke(
        backup_group, ["restore", "/no/such/backup.vault", vault_file, "--yes"]
    )
    assert result.exit_code == 1
    assert "Error" in result.output


def test_backup_delete_success(runner, vault_file):
    create_result = runner.invoke(backup_group, ["create", vault_file])
    backup_path = create_result.output.split("Backup created: ")[1].strip()
    result = runner.invoke(backup_group, ["delete", backup_path])
    assert result.exit_code == 0
    assert "Deleted backup" in result.output


def test_backup_purge_with_yes_flag(runner, vault_file):
    runner.invoke(backup_group, ["create", vault_file])
    runner.invoke(backup_group, ["create", vault_file])
    result = runner.invoke(backup_group, ["purge", vault_file, "--yes"])
    assert result.exit_code == 0
    assert "2 backup(s)" in result.output
