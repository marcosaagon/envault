"""Tests for envault/backup.py"""

import os
import pytest
from pathlib import Path
from envault.backup import (
    create_backup,
    list_backups,
    restore_backup,
    delete_backup,
    purge_backups,
    _backup_dir,
)


@pytest.fixture
def vault_file(tmp_path):
    vf = tmp_path / ".env.vault"
    vf.write_text("ENCRYPTED_CONTENT_HERE")
    return str(vf)


def test_create_backup_creates_file(vault_file):
    backup_path = create_backup(vault_file)
    assert os.path.exists(backup_path)


def test_create_backup_content_matches(vault_file):
    backup_path = create_backup(vault_file)
    original = Path(vault_file).read_text()
    backup = Path(backup_path).read_text()
    assert original == backup


def test_create_backup_missing_vault_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        create_backup(str(tmp_path / "nonexistent.vault"))


def test_list_backups_empty_when_none(vault_file):
    assert list_backups(vault_file) == []


def test_list_backups_returns_entries(vault_file):
    create_backup(vault_file)
    create_backup(vault_file)
    entries = list_backups(vault_file)
    assert len(entries) == 2


def test_list_backups_entry_has_required_keys(vault_file):
    create_backup(vault_file)
    entries = list_backups(vault_file)
    assert len(entries) == 1
    entry = entries[0]
    assert "name" in entry
    assert "path" in entry
    assert "size" in entry
    assert "created" in entry


def test_list_backups_newest_first(vault_file):
    p1 = create_backup(vault_file)
    import time; time.sleep(0.05)
    p2 = create_backup(vault_file)
    entries = list_backups(vault_file)
    assert entries[0]["path"] == p2
    assert entries[1]["path"] == p1


def test_restore_backup_overwrites_vault(vault_file):
    backup_path = create_backup(vault_file)
    Path(vault_file).write_text("CHANGED")
    restore_backup(backup_path, vault_file)
    assert Path(vault_file).read_text() == "ENCRYPTED_CONTENT_HERE"


def test_restore_backup_missing_raises(vault_file):
    with pytest.raises(FileNotFoundError):
        restore_backup("/no/such/backup.vault", vault_file)


def test_delete_backup_removes_file(vault_file):
    backup_path = create_backup(vault_file)
    delete_backup(backup_path)
    assert not os.path.exists(backup_path)


def test_delete_backup_missing_raises(vault_file):
    with pytest.raises(FileNotFoundError):
        delete_backup("/no/such/backup.vault")


def test_purge_backups_removes_all(vault_file):
    create_backup(vault_file)
    create_backup(vault_file)
    count = purge_backups(vault_file)
    assert count == 2
    assert list_backups(vault_file) == []


def test_purge_backups_no_backups_returns_zero(vault_file):
    assert purge_backups(vault_file) == 0
