"""Tests for envault.snapshot module."""

import json
from pathlib import Path

import pytest

from envault.snapshot import (
    delete_snapshot,
    list_snapshots,
    load_snapshot,
    purge_snapshots,
    save_snapshot,
)


@pytest.fixture
def vault_file(tmp_path: Path) -> Path:
    vf = tmp_path / ".env.vault"
    vf.write_text("encrypted_blob_content")
    return vf


def test_save_snapshot_creates_file(vault_file: Path):
    snap = save_snapshot(vault_file, "blob123")
    assert snap.exists()


def test_save_snapshot_content(vault_file: Path):
    snap = save_snapshot(vault_file, "blob_data", label="v1")
    data = json.loads(snap.read_text())
    assert data["blob"] == "blob_data"
    assert data["label"] == "v1"
    assert "timestamp" in data


def test_list_snapshots_empty(vault_file: Path):
    assert list_snapshots(vault_file) == []


def test_list_snapshots_returns_entries(vault_file: Path):
    save_snapshot(vault_file, "blob1")
    save_snapshot(vault_file, "blob2")
    snaps = list_snapshots(vault_file)
    assert len(snaps) == 2


def test_list_snapshots_newest_first(vault_file: Path):
    s1 = save_snapshot(vault_file, "old")
    s2 = save_snapshot(vault_file, "new")
    snaps = list_snapshots(vault_file)
    timestamps = [s["timestamp"] for s in snaps]
    assert timestamps == sorted(timestamps, reverse=True)


def test_load_snapshot_returns_blob(vault_file: Path):
    snap = save_snapshot(vault_file, "my_blob")
    assert load_snapshot(snap) == "my_blob"


def test_delete_snapshot(vault_file: Path):
    snap = save_snapshot(vault_file, "blob")
    assert snap.exists()
    delete_snapshot(snap)
    assert not snap.exists()


def test_purge_snapshots_keeps_n(vault_file: Path):
    for i in range(8):
        save_snapshot(vault_file, f"blob{i}")
    removed = purge_snapshots(vault_file, keep=3)
    assert removed == 5
    assert len(list_snapshots(vault_file)) == 3


def test_purge_snapshots_no_excess(vault_file: Path):
    save_snapshot(vault_file, "blob")
    removed = purge_snapshots(vault_file, keep=5)
    assert removed == 0
