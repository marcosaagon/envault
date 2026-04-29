"""Tests for envault.audit module."""

import json
import pytest
from pathlib import Path

from envault.audit import (
    load_audit_log,
    save_audit_log,
    record_event,
    clear_audit_log,
    format_log_entry,
    DEFAULT_AUDIT_FILE,
)


@pytest.fixture
def tmp_dir(tmp_path):
    return str(tmp_path)


def test_load_audit_log_returns_empty_when_no_file(tmp_dir):
    result = load_audit_log(tmp_dir)
    assert result == []


def test_save_and_load_roundtrip(tmp_dir):
    entries = [{"action": "lock", "profile": "dev"}]
    save_audit_log(entries, tmp_dir)
    loaded = load_audit_log(tmp_dir)
    assert loaded == entries


def test_save_creates_json_file(tmp_dir):
    save_audit_log([{"action": "unlock"}], tmp_dir)
    audit_file = Path(tmp_dir) / DEFAULT_AUDIT_FILE
    assert audit_file.exists()
    with open(audit_file) as f:
        data = json.load(f)
    assert len(data) == 1


def test_record_event_appends_entry(tmp_dir):
    record_event("lock", profile="prod", directory=tmp_dir)
    entries = load_audit_log(tmp_dir)
    assert len(entries) == 1
    assert entries[0]["action"] == "lock"
    assert entries[0]["profile"] == "prod"


def test_record_event_accumulates(tmp_dir):
    record_event("lock", directory=tmp_dir)
    record_event("unlock", directory=tmp_dir)
    record_event("export", directory=tmp_dir)
    entries = load_audit_log(tmp_dir)
    assert len(entries) == 3
    actions = [e["action"] for e in entries]
    assert actions == ["lock", "unlock", "export"]


def test_record_event_includes_timestamp(tmp_dir):
    entry = record_event("lock", directory=tmp_dir)
    assert "timestamp" in entry
    assert "T" in entry["timestamp"]  # ISO format check


def test_record_event_includes_user(tmp_dir):
    entry = record_event("lock", directory=tmp_dir)
    assert "user" in entry
    assert isinstance(entry["user"], str)


def test_clear_audit_log(tmp_dir):
    record_event("lock", directory=tmp_dir)
    record_event("unlock", directory=tmp_dir)
    clear_audit_log(tmp_dir)
    entries = load_audit_log(tmp_dir)
    assert entries == []


def test_format_log_entry_contains_action():
    entry = {
        "timestamp": "2024-01-01T00:00:00+00:00",
        "action": "lock",
        "profile": "staging",
        "user": "alice",
        "details": "via CLI",
    }
    line = format_log_entry(entry)
    assert "LOCK" in line
    assert "staging" in line
    assert "alice" in line
    assert "via CLI" in line


def test_format_log_entry_no_details():
    entry = {
        "timestamp": "2024-01-01T00:00:00+00:00",
        "action": "unlock",
        "profile": None,
        "user": "bob",
        "details": None,
    }
    line = format_log_entry(entry)
    assert "UNLOCK" in line
    assert "default" in line
