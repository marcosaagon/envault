"""Health check module for .env files and vaults."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from envault.validate import validate_env_text
from envault.lint import lint_env_text
from envault.vault import unlock


@dataclass
class HealthReport:
    path: str
    validation_errors: List[str] = field(default_factory=list)
    lint_warnings: List[str] = field(default_factory=list)
    missing_keys: List[str] = field(default_factory=list)

    @property
    def healthy(self) -> bool:
        return not self.validation_errors and not self.missing_keys

    def summary(self) -> str:
        lines = [f"Health report for: {self.path}"]
        if self.healthy:
            lines.append("  Status: OK")
        else:
            lines.append("  Status: UNHEALTHY")
        if self.validation_errors:
            lines.append(f"  Validation errors ({len(self.validation_errors)}):")
            for e in self.validation_errors:
                lines.append(f"    - {e}")
        if self.lint_warnings:
            lines.append(f"  Lint warnings ({len(self.lint_warnings)}):")
            for w in self.lint_warnings:
                lines.append(f"    - {w}")
        if self.missing_keys:
            lines.append(f"  Missing required keys ({len(self.missing_keys)}):")
            for k in self.missing_keys:
                lines.append(f"    - {k}")
        return "\n".join(lines)


def check_env_text(text: str, path: str = "<text>", required_keys: List[str] | None = None) -> HealthReport:
    report = HealthReport(path=path)
    val_result = validate_env_text(text)
    report.validation_errors = [str(i) for i in val_result.issues]
    lint_result = lint_env_text(text)
    report.lint_warnings = [str(i) for i in lint_result.issues]
    if required_keys:
        present = set()
        for line in text.splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key = line.split("=", 1)[0].strip()
                present.add(key)
        report.missing_keys = [k for k in required_keys if k not in present]
    return report


def check_env_file(env_path: Path, required_keys: List[str] | None = None) -> HealthReport:
    text = env_path.read_text(encoding="utf-8")
    return check_env_text(text, path=str(env_path), required_keys=required_keys)


def check_vault_file(vault_path: Path, password: str, required_keys: List[str] | None = None) -> HealthReport:
    text = unlock(vault_path, password)
    return check_env_text(text, path=str(vault_path), required_keys=required_keys)
