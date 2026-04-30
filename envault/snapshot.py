"""Snapshot management for tracking vault history."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import List, Optional

SNAPSHOT_DIR = ".envault_snapshots"


def _snapshot_dir(vault_path: Path) -> Path:
    return vault_path.parent / SNAPSHOT_DIR


def save_snapshot(vault_path: Path, encrypted_content: str, label: Optional[str] = None) -> Path:
    """Save a snapshot of the current vault file."""
    snap_dir = _snapshot_dir(vault_path)
    snap_dir.mkdir(parents=True, exist_ok=True)

    ts = int(time.time())
    name = f"{vault_path.stem}_{ts}.snap"
    snap_file = snap_dir / name

    payload = {
        "timestamp": ts,
        "label": label or "",
        "source": vault_path.name,
        "blob": encrypted_content,
    }
    snap_file.write_text(json.dumps(payload, indent=2))
    return snap_file


def list_snapshots(vault_path: Path) -> List[dict]:
    """Return metadata for all snapshots of a vault file, newest first."""
    snap_dir = _snapshot_dir(vault_path)
    if not snap_dir.exists():
        return []

    entries = []
    for f in sorted(snap_dir.glob(f"{vault_path.stem}_*.snap"), reverse=True):
        try:
            data = json.loads(f.read_text())
            data["path"] = str(f)
            entries.append(data)
        except (json.JSONDecodeError, KeyError):
            continue
    return entries


def load_snapshot(snap_path: Path) -> str:
    """Load the encrypted blob from a snapshot file."""
    data = json.loads(snap_path.read_text())
    return data["blob"]


def delete_snapshot(snap_path: Path) -> None:
    """Delete a specific snapshot file."""
    snap_path.unlink(missing_ok=True)


def purge_snapshots(vault_path: Path, keep: int = 5) -> int:
    """Remove old snapshots, keeping only the most recent `keep` entries."""
    snaps = list_snapshots(vault_path)
    to_delete = snaps[keep:]
    for entry in to_delete:
        Path(entry["path"]).unlink(missing_ok=True)
    return len(to_delete)
