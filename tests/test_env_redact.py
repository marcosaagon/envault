"""Tests for envault.env_redact."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.env_redact import (
    RedactResult,
    redact_env_text,
    redact_env_file,
    redact_vault,
    DEFAULT_PLACEHOLDER,
)
from envault.vault import unlock


SAMPLE_ENV = """APP_NAME=myapp
API_KEY=supersecret
DATABASE_PASSWORD=hunter2
DEBUG=true
SECRET_TOKEN=abc123
"""


def test_redact_env_text_detects_sensitive_keys():
    result = redact_env_text(SAMPLE_ENV)
    assert "API_KEY" in result.redacted_keys
    assert "DATABASE_PASSWORD" in result.redacted_keys
    assert "SECRET_TOKEN" in result.redacted_keys


def test_redact_env_text_leaves_non_sensitive_keys():
    result = redact_env_text(SAMPLE_ENV)
    assert "APP_NAME" not in result.redacted_keys
    assert "DEBUG" not in result.redacted_keys


def test_redact_env_text_replaces_values_with_placeholder():
    result = redact_env_text(SAMPLE_ENV)
    for line in result.output_text.splitlines():
        if line.startswith("API_KEY="):
            assert line == f"API_KEY={DEFAULT_PLACEHOLDER}"
        if line.startswith("DATABASE_PASSWORD="):
            assert line == f"DATABASE_PASSWORD={DEFAULT_PLACEHOLDER}"


def test_redact_env_text_custom_placeholder():
    result = redact_env_text(SAMPLE_ENV, placeholder="<hidden>")
    assert "<hidden>" in result.output_text
    assert "supersecret" not in result.output_text


def test_redact_env_text_explicit_keys_only():
    result = redact_env_text(SAMPLE_ENV, keys=["APP_NAME"])
    assert "APP_NAME" in result.redacted_keys
    # API_KEY should NOT be redacted because explicit list given
    assert "API_KEY" not in result.redacted_keys


def test_redact_env_text_preserves_comments():
    text = "# comment\nSECRET=value\n"
    result = redact_env_text(text)
    assert "# comment" in result.output_text


def test_redact_env_text_preserves_blank_lines():
    text = "APP=x\n\nSECRET=y\n"
    result = redact_env_text(text)
    assert "\n\n" in result.output_text


def test_redact_result_summary_no_redactions():
    result = redact_env_text("APP=hello\n")
    assert result.summary() == "No sensitive keys detected."


def test_redact_result_summary_with_redactions():
    result = redact_env_text("SECRET=abc\n")
    assert "1 key(s)" in result.summary()
    assert "SECRET" in result.summary()


def test_redact_env_file_modifies_file(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text("API_KEY=secret\nAPP=hello\n")
    result = redact_env_file(env_file)
    content = env_file.read_text()
    assert DEFAULT_PLACEHOLDER in content
    assert "secret" not in content
    assert "APP=hello" in content
    assert "API_KEY" in result.redacted_keys


@pytest.fixture
def vault_file(tmp_path: Path) -> Path:
    from envault.vault import lock
    path = tmp_path / "test.vault"
    lock(SAMPLE_ENV, path, "testpass")
    return path


def test_redact_vault_re_encrypts(vault_file: Path):
    result = redact_vault(vault_file, password="testpass")
    assert "API_KEY" in result.redacted_keys


def test_redact_vault_plaintext_no_longer_contains_secret(vault_file: Path):
    redact_vault(vault_file, password="testpass")
    decrypted = unlock(vault_file, "testpass")
    assert "supersecret" not in decrypted
    assert DEFAULT_PLACEHOLDER in decrypted


def test_redact_vault_non_sensitive_values_preserved(vault_file: Path):
    redact_vault(vault_file, password="testpass")
    decrypted = unlock(vault_file, "testpass")
    assert "APP_NAME=myapp" in decrypted
    assert "DEBUG=true" in decrypted
