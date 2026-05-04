"""Lint and validate .env files for common issues."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from envault.crypto import decrypt
from envault.vault import VAULT_SUFFIX


@dataclass
class LintIssue:
    line_no: int
    line: str
    code: str
    message: str

    def __str__(self) -> str:
        return f"Line {self.line_no} [{self.code}]: {self.message!r} -> {self.line!r}"


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.issues) == 0

    def __str__(self) -> str:
        if self.ok:
            return "No issues found."
        return "\n".join(str(i) for i in self.issues)


def lint_env_text(text: str) -> LintResult:
    """Lint raw .env text and return a LintResult."""
    issues: List[LintIssue] = []
    seen_keys: dict[str, int] = {}

    for lineno, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            issues.append(LintIssue(lineno, raw_line, "E001", "Missing '=' separator"))
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if not key:
            issues.append(LintIssue(lineno, raw_line, "E002", "Empty key"))
            continue
        if " " in key:
            issues.append(LintIssue(lineno, raw_line, "E003", "Key contains whitespace"))
        if key in seen_keys:
            issues.append(
                LintIssue(lineno, raw_line, "W001",
                          f"Duplicate key '{key}' (first at line {seen_keys[key]})")
            )
        else:
            seen_keys[key] = lineno
        if not value:
            issues.append(LintIssue(lineno, raw_line, "W002", f"Empty value for key '{key}'"))

    return LintResult(issues=issues)


def lint_env_file(path: Path) -> LintResult:
    """Lint a plain .env file."""
    return lint_env_text(path.read_text(encoding="utf-8"))


def lint_vault_file(path: Path, password: str) -> LintResult:
    """Decrypt a vault file and lint its contents."""
    blob = path.read_text(encoding="utf-8").strip()
    plaintext = decrypt(blob, password)
    return lint_env_text(plaintext)
