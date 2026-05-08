"""Export and import env/vault data in multiple formats (JSON, TOML, dotenv)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Literal

from envault.crypto import decrypt, encrypt

ExportFormat = Literal["json", "dotenv", "toml"]


def parse_env_text(text: str) -> Dict[str, str]:
    """Parse .env text into a key/value dict."""
    result: Dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        result[key.strip()] = value.strip()
    return result


def to_dotenv(data: Dict[str, str]) -> str:
    """Serialize a dict to .env format."""
    return "\n".join(f"{k}={v}" for k, v in data.items()) + "\n"


def to_json(data: Dict[str, str]) -> str:
    """Serialize a dict to JSON format."""
    return json.dumps(data, indent=2) + "\n"


def to_toml(data: Dict[str, str]) -> str:
    """Serialize a dict to a minimal TOML format."""
    lines = []
    for k, v in data.items():
        escaped = v.replace('"', '\\"')
        lines.append(f'{k} = "{escaped}"')
    return "\n".join(lines) + "\n"


def export_env_file(env_path: Path, fmt: ExportFormat) -> str:
    """Read a plaintext .env file and return it in the requested format."""
    text = env_path.read_text(encoding="utf-8")
    data = parse_env_text(text)
    return _serialize(data, fmt)


def export_vault_file(vault_path: Path, password: str, fmt: ExportFormat) -> str:
    """Decrypt a vault file and return its contents in the requested format."""
    ciphertext = vault_path.read_text(encoding="utf-8")
    plaintext = decrypt(ciphertext, password)
    data = parse_env_text(plaintext)
    return _serialize(data, fmt)


def import_to_vault(source: str, fmt: ExportFormat, vault_path: Path, password: str) -> None:
    """Parse exported data and write it as an encrypted vault file."""
    data = _deserialize(source, fmt)
    plaintext = to_dotenv(data)
    ciphertext = encrypt(plaintext, password)
    vault_path.write_text(ciphertext, encoding="utf-8")


def _serialize(data: Dict[str, str], fmt: ExportFormat) -> str:
    if fmt == "json":
        return to_json(data)
    if fmt == "toml":
        return to_toml(data)
    return to_dotenv(data)


def _deserialize(source: str, fmt: ExportFormat) -> Dict[str, str]:
    if fmt == "json":
        return json.loads(source)
    if fmt == "toml":
        return _parse_toml(source)
    return parse_env_text(source)


def _parse_toml(text: str) -> Dict[str, str]:
    """Minimal TOML key=\"value\" parser (no sections)."""
    result: Dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, rest = stripped.partition("=")
        value = rest.strip()
        # Strip surrounding double quotes and unescape internal quotes
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1].replace('\\"', '"')
        result[key.strip()] = value
    return result
