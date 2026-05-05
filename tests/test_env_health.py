"""Tests for envault.env_health module."""
from pathlib import Path

import pytest

from envault.env_health import check_env_text, check_env_file, check_vault_file, HealthReport
from envault.vault import lock


VALID_ENV = "DB_HOST=localhost\nDB_PORT=5432\nSECRET_KEY=abc123\n"
INVALID_ENV = "NOEQUALSSIGN\nDB_HOST=localhost\n"
DUPLICATE_ENV = "FOO=bar\nFOO=baz\n"


def test_health_report_healthy_when_no_issues():
    report = HealthReport(path="test")
    assert report.healthy is True


def test_health_report_unhealthy_on_validation_errors():
    report = HealthReport(path="test", validation_errors=["some error"])
    assert report.healthy is False


def test_health_report_unhealthy_on_missing_keys():
    report = HealthReport(path="test", missing_keys=["SECRET_KEY"])
    assert report.healthy is False


def test_check_env_text_valid_returns_healthy():
    report = check_env_text(VALID_ENV, path="test.env")
    assert report.healthy is True
    assert report.validation_errors == []


def test_check_env_text_invalid_has_errors():
    report = check_env_text(INVALID_ENV, path="test.env")
    assert len(report.validation_errors) > 0


def test_check_env_text_required_keys_all_present():
    report = check_env_text(VALID_ENV, required_keys=["DB_HOST", "DB_PORT"])
    assert report.missing_keys == []
    assert report.healthy is True


def test_check_env_text_required_keys_missing():
    report = check_env_text(VALID_ENV, required_keys=["DB_HOST", "MISSING_KEY"])
    assert "MISSING_KEY" in report.missing_keys
    assert report.healthy is False


def test_check_env_text_duplicate_key_produces_lint_warning():
    report = check_env_text(DUPLICATE_ENV)
    assert len(report.lint_warnings) > 0


def test_check_env_file_reads_and_checks(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(VALID_ENV, encoding="utf-8")
    report = check_env_file(env_file)
    assert report.healthy is True
    assert report.path == str(env_file)


def test_check_env_file_missing_required_key(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(VALID_ENV, encoding="utf-8")
    report = check_env_file(env_file, required_keys=["NOT_THERE"])
    assert "NOT_THERE" in report.missing_keys


def test_check_vault_file_valid(tmp_path):
    vault_file = tmp_path / ".env.vault"
    lock(Path(tmp_path / ".env"), VALID_ENV, "password123", vault_file)
    report = check_vault_file(vault_file, "password123")
    assert report.healthy is True


def test_check_vault_file_required_key_missing(tmp_path):
    vault_file = tmp_path / ".env.vault"
    lock(Path(tmp_path / ".env"), VALID_ENV, "password123", vault_file)
    report = check_vault_file(vault_file, "password123", required_keys=["GHOST_KEY"])
    assert "GHOST_KEY" in report.missing_keys


def test_summary_contains_path():
    report = HealthReport(path="myfile.env", validation_errors=["bad line"])
    summary = report.summary()
    assert "myfile.env" in summary
    assert "bad line" in summary
    assert "UNHEALTHY" in summary


def test_summary_ok_when_healthy():
    report = HealthReport(path="myfile.env")
    summary = report.summary()
    assert "OK" in summary
