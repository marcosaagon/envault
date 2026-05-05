"""Validation helpers for .env files and vault contents."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

# Regex for a valid env key: starts with letter or underscore, alphanumeric/underscore only
_VALID_KEY_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')
# Warn on keys that look like they contain secrets but have short values
_SECRET_KEY_RE = re.compile(r'(SECRET|TOKEN|KEY|PASSWORD|PASS|PWD|API)', re.IGNORECASE)
_MIN_SECRET_LENGTH = 8


@dataclass
class ValidationIssue:
    line_number: int
    key: Optional[str]
    message: str
    severity: str  # 'error' | 'warning'

    def __str__(self) -> str:
        loc = f"line {self.line_number}" + (f" ({self.key})" if self.key else "")
        return f"[{self.severity.upper()}] {loc}: {self.message}"


@dataclass
class ValidationResult:
    issues: List[ValidationIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(i.severity == "error" for i in self.issues)

    @property
    def errors(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == "warning"]


def validate_env_text(text: str) -> ValidationResult:
    """Validate raw .env text, returning a ValidationResult with any issues."""
    result = ValidationResult()
    seen_keys: dict[str, int] = {}

    for lineno, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            result.issues.append(ValidationIssue(lineno, None, "Missing '=' separator", "error"))
            continue

        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()

        if not key:
            result.issues.append(ValidationIssue(lineno, None, "Empty key", "error"))
            continue

        if not _VALID_KEY_RE.match(key):
            result.issues.append(ValidationIssue(lineno, key, f"Invalid key name '{key}'", "error"))
            continue

        if key in seen_keys:
            result.issues.append(
                ValidationIssue(lineno, key, f"Duplicate key (first seen on line {seen_keys[key]})", "warning")
            )
        else:
            seen_keys[key] = lineno

        if _SECRET_KEY_RE.search(key) and len(value) < _MIN_SECRET_LENGTH:
            result.issues.append(
                ValidationIssue(lineno, key, f"Secret-like key has suspiciously short value (len={len(value)})", "warning")
            )

    return result
