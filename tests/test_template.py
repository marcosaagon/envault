"""Tests for envault.template."""
from __future__ import annotations

from pathlib import Path

import pytest

from envault.template import (
    generate_template,
    parse_env_lines,
    template_from_env_file,
    template_from_vault,
)
from envault.vault import lock


SAMPLE_ENV = """# database config
DB_HOST=localhost
DB_PORT=5432
DB_PASS=supersecret

APP_KEY=abc123
"""


def test_parse_env_lines_identifies_keys():
    pairs = parse_env_lines(SAMPLE_ENV)
    keys = [k for _, k in pairs if k]
    assert keys == ["DB_HOST", "DB_PORT", "DB_PASS", "APP_KEY"]


def test_parse_env_lines_preserves_comments():
    pairs = parse_env_lines(SAMPLE_ENV)
    raw_lines = [r for r, k in pairs if not k]
    assert any("# database config" in r for r in raw_lines)


def test_generate_template_masks_values():
    result = generate_template(SAMPLE_ENV)
    assert "supersecret" not in result
    assert "abc123" not in result
    assert "DB_HOST=<CHANGE_ME>" in result


def test_generate_template_custom_placeholder():
    result = generate_template(SAMPLE_ENV, placeholder="FILL_IN")
    assert "DB_PASS=FILL_IN" in result


def test_generate_template_preserves_comments():
    result = generate_template(SAMPLE_ENV)
    assert "# database config" in result


def test_generate_template_no_mask():
    result = generate_template(SAMPLE_ENV, mask_values=False)
    assert "supersecret" in result


def test_template_from_env_file(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text(SAMPLE_ENV, encoding="utf-8")
    result = template_from_env_file(env_file)
    assert "supersecret" not in result
    assert "DB_HOST=<CHANGE_ME>" in result


def test_template_from_env_file_writes_output(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text(SAMPLE_ENV, encoding="utf-8")
    out_file = tmp_path / ".env.template"
    template_from_env_file(env_file, output_path=out_file)
    assert out_file.exists()
    assert "<CHANGE_ME>" in out_file.read_text(encoding="utf-8")


def test_template_from_vault(tmp_path: Path):
    vault_file = tmp_path / ".env.vault"
    password = "vaultpass"
    lock(tmp_path / ".env", vault_file, password, env_content=SAMPLE_ENV)
    result = template_from_vault(vault_file, password)
    assert "supersecret" not in result
    assert "APP_KEY=<CHANGE_ME>" in result


def test_template_from_vault_writes_output(tmp_path: Path):
    vault_file = tmp_path / ".env.vault"
    password = "vaultpass"
    lock(tmp_path / ".env", vault_file, password, env_content=SAMPLE_ENV)
    out_file = tmp_path / ".env.template"
    template_from_vault(vault_file, password, output_path=out_file)
    assert out_file.exists()
