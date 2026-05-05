"""Backup and restore vault files with timestamped copies."""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional


def _backup_dir(vault_path: str) -> Path:
    """Return the backup directory for a given vault file."""
    vault = Path(vault_path).resolve()
    return vault.parent / ".envault_backups" / vault.stem


def create_backup(vault_path: str) -> str:
    """Create a timestamped backup of a vault file. Returns the backup path."""
    vault = Path(vault_path)
    if not vault.exists():
        raise FileNotFoundError(f"Vault file not found: {vault_path}")

    backup_dir = _backup_dir(vault_path)
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    backup_name = f"{vault.stem}_{timestamp}{vault.suffix}"
    backup_path = backup_dir / backup_name

    shutil.copy2(vault_path, backup_path)
    return str(backup_path)


def list_backups(vault_path: str) -> List[dict]:
    """List all backups for a vault file, newest first."""
    backup_dir = _backup_dir(vault_path)
    if not backup_dir.exists():
        return []

    vault = Path(vault_path)
    entries = []
    for f in sorted(backup_dir.iterdir(), reverse=True):
        if f.is_file() and f.suffix == vault.suffix:
            stat = f.stat()
            entries.append({
                "name": f.name,
                "path": str(f),
                "size": stat.st_size,
                "created": datetime.utcfromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S UTC"),
            })
    return entries


def restore_backup(backup_path: str, vault_path: str) -> None:
    """Restore a vault file from a backup, overwriting the current vault."""
    src = Path(backup_path)
    if not src.exists():
        raise FileNotFoundError(f"Backup file not found: {backup_path}")
    shutil.copy2(backup_path, vault_path)


def delete_backup(backup_path: str) -> None:
    """Delete a single backup file."""
    p = Path(backup_path)
    if not p.exists():
        raise FileNotFoundError(f"Backup not found: {backup_path}")
    p.unlink()


def purge_backups(vault_path: str) -> int:
    """Delete all backups for a vault file. Returns the number deleted."""
    backup_dir = _backup_dir(vault_path)
    if not backup_dir.exists():
        return 0
    count = 0
    for f in backup_dir.iterdir():
        if f.is_file():
            f.unlink()
            count += 1
    return count
