"""Audit log for vault operations — tracks lock/unlock/share events."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DEFAULT_AUDIT_FILE = ".envault_audit.json"


def _audit_path(directory: str = ".") -> Path:
    return Path(directory) / DEFAULT_AUDIT_FILE


def load_audit_log(directory: str = ".") -> list:
    """Load the audit log from disk. Returns empty list if not found."""
    path = _audit_path(directory)
    if not path.exists():
        return []
    with open(path, "r") as f:
        return json.load(f)


def save_audit_log(entries: list, directory: str = ".") -> None:
    """Persist the audit log to disk."""
    path = _audit_path(directory)
    with open(path, "w") as f:
        json.dump(entries, f, indent=2)


def record_event(
    action: str,
    profile: Optional[str] = None,
    details: Optional[str] = None,
    directory: str = ".",
) -> dict:
    """Append a new event to the audit log and return the entry."""
    entries = load_audit_log(directory)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "profile": profile,
        "details": details,
        "user": os.environ.get("USER") or os.environ.get("USERNAME") or "unknown",
    }
    entries.append(entry)
    save_audit_log(entries, directory)
    return entry


def clear_audit_log(directory: str = ".") -> None:
    """Remove all audit log entries."""
    save_audit_log([], directory)


def format_log_entry(entry: dict) -> str:
    """Return a human-readable string for a single log entry."""
    ts = entry.get("timestamp", "unknown")
    action = entry.get("action", "unknown")
    profile = entry.get("profile") or "default"
    user = entry.get("user", "unknown")
    details = entry.get("details", "")
    line = f"[{ts}] {action.upper():10s} profile={profile} user={user}"
    if details:
        line += f" | {details}"
    return line
