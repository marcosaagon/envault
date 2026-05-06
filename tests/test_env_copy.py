"""Tests for envault.env_copy."""

from pathlib import Path

import pytest

from envault.crypto import encrypt
from envault.env_copy import (
    CopyResult,
    copy_keys,
    copy_keys_between_vaults,
    parse_env_text,
)


# ---------------------------------------------------------------------------
# parse_env_text
# ---------------------------------------------------------------------------

def test_parse_env_text_basic():
    text = "FOO=bar\nBAZ=qux\n"
    assert parse_env_text(text) == {"FOO": "bar", "BAZ": "qux"}


def test_parse_env_text_ignores_comments():
    text = "# comment\nFOO=bar\n"
    assert parse_env_text(text) == {"FOO": "bar"}


def test_parse_env_text_ignores_blank_lines():
    text = "\nFOO=bar\n\n"
    assert parse_env_text(text) == {"FOO": "bar"}


def test_parse_env_text_no_equals_skipped():
    text = "NOEQUALS\nFOO=bar\n"
    assert parse_env_text(text) == {"FOO": "bar"}


# ---------------------------------------------------------------------------
# copy_keys
# ---------------------------------------------------------------------------

def test_copy_keys_adds_new_key():
    src = "FOO=bar\nNEW=value\n"
    dst = "FOO=bar\n"
    new_text, result = copy_keys(src, dst, keys=["NEW"])
    assert "NEW=value" in new_text
    assert "NEW" in result.copied
    assert result.ok


def test_copy_keys_skips_existing_without_overwrite():
    src = "FOO=new_val\n"
    dst = "FOO=old_val\n"
    new_text, result = copy_keys(src, dst, keys=["FOO"], overwrite=False)
    assert "FOO=old_val" in new_text
    assert "FOO" in result.skipped
    assert not result.overwritten


def test_copy_keys_overwrites_when_flag_set():
    src = "FOO=new_val\n"
    dst = "FOO=old_val\n"
    new_text, result = copy_keys(src, dst, keys=["FOO"], overwrite=True)
    assert "FOO=new_val" in new_text
    assert "FOO" in result.overwritten


def test_copy_keys_skips_missing_source_key():
    src = "FOO=bar\n"
    dst = "BAZ=qux\n"
    _, result = copy_keys(src, dst, keys=["MISSING"])
    assert "MISSING" in result.skipped
    assert not result.copied


def test_copy_all_keys_when_no_filter():
    src = "A=1\nB=2\n"
    dst = ""
    new_text, result = copy_keys(src, dst)
    assert "A=1" in new_text
    assert "B=2" in new_text
    assert len(result.copied) == 2


def test_copy_result_summary_mixed():
    result = CopyResult(copied=["A"], overwritten=["B"], skipped=["C"])
    summary = result.summary()
    assert "copied" in summary
    assert "overwritten" in summary
    assert "skipped" in summary


def test_copy_result_summary_nothing_changed():
    result = CopyResult()
    assert result.summary() == "nothing changed"
    assert not result.ok


# ---------------------------------------------------------------------------
# copy_keys_between_vaults
# ---------------------------------------------------------------------------

@pytest.fixture
def src_vault(tmp_path: Path) -> Path:
    p = tmp_path / "src.vault"
    p.write_text(encrypt("SHARED=hello\nSRC_ONLY=world\n", "src-pass"))
    return p


@pytest.fixture
def dst_vault(tmp_path: Path) -> Path:
    p = tmp_path / "dst.vault"
    p.write_text(encrypt("EXISTING=keep\n", "dst-pass"))
    return p


def test_copy_between_vaults_adds_key(src_vault, dst_vault):
    from envault.crypto import decrypt

    result = copy_keys_between_vaults(
        src_vault, "src-pass", dst_vault, "dst-pass", keys=["SHARED"]
    )
    decrypted = decrypt(dst_vault.read_text(), "dst-pass")
    assert "SHARED=hello" in decrypted
    assert "SHARED" in result.copied


def test_copy_between_vaults_preserves_existing(src_vault, dst_vault):
    from envault.crypto import decrypt

    copy_keys_between_vaults(
        src_vault, "src-pass", dst_vault, "dst-pass", keys=["SHARED"]
    )
    decrypted = decrypt(dst_vault.read_text(), "dst-pass")
    assert "EXISTING=keep" in decrypted
