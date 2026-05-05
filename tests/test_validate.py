"""Tests for envault.validate module."""

import pytest
from envault.validate import validate_env_text, ValidationResult, ValidationIssue


def test_clean_env_returns_no_issues():
    text = "DB_HOST=localhost\nDB_PORT=5432\nAPP_NAME=myapp\n"
    result = validate_env_text(text)
    assert result.ok
    assert result.issues == []


def test_missing_equals_is_error():
    result = validate_env_text("BADLINE\n")
    assert not result.ok
    assert any("Missing '='" in i.message for i in result.errors)


def test_empty_key_is_error():
    result = validate_env_text("=somevalue\n")
    assert not result.ok
    assert any("Empty key" in i.message for i in result.errors)


def test_invalid_key_name_is_error():
    result = validate_env_text("1INVALID=value\n")
    assert not result.ok
    assert any("Invalid key name" in i.message for i in result.errors)


def test_key_with_space_is_error():
    result = validate_env_text("MY KEY=value\n")
    assert not result.ok
    assert any("Invalid key name" in i.message for i in result.errors)


def test_duplicate_key_is_warning():
    text = "FOO=bar\nFOO=baz\n"
    result = validate_env_text(text)
    assert result.ok  # duplicate is only a warning
    assert any("Duplicate key" in i.message for i in result.warnings)


def test_short_secret_value_is_warning():
    result = validate_env_text("API_SECRET=abc\n")
    assert result.ok
    assert any("suspiciously short" in i.message for i in result.warnings)


def test_adequate_secret_value_no_warning():
    result = validate_env_text("API_SECRET=averylongsecretvalue\n")
    assert result.ok
    assert result.warnings == []


def test_comments_and_blank_lines_ignored():
    text = "# This is a comment\n\nDB=localhost\n"
    result = validate_env_text(text)
    assert result.ok
    assert result.issues == []


def test_line_number_reported_correctly():
    text = "GOOD=value\nBADLINE\nALSOGOOD=ok\n"
    result = validate_env_text(text)
    errors = result.errors
    assert len(errors) == 1
    assert errors[0].line_number == 2


def test_validation_issue_str_includes_severity_and_line():
    issue = ValidationIssue(line_number=3, key="MY_KEY", message="Some problem", severity="error")
    s = str(issue)
    assert "ERROR" in s
    assert "line 3" in s
    assert "MY_KEY" in s
    assert "Some problem" in s


def test_errors_and_warnings_properties():
    text = "BADLINE\nAPI_TOKEN=x\nFOO=bar\nFOO=baz\n"
    result = validate_env_text(text)
    assert len(result.errors) >= 1
    assert len(result.warnings) >= 1
