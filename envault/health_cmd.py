"""CLI commands for env/vault health checks."""
from __future__ import annotations

from pathlib import Path

import click

from envault.env_health import check_env_file, check_vault_file


@click.group("health")
def health_group():
    """Health check commands for .env files and vaults."""


@health_group.command("env")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.option("--require", "-r", multiple=True, metavar="KEY", help="Required key(s) that must be present.")
@click.option("--strict", is_flag=True, help="Exit non-zero on lint warnings too.")
def health_env_cmd(env_file: Path, require: tuple, strict: bool):
    """Check health of a plaintext .env file."""
    required = list(require) if require else None
    report = check_env_file(env_file, required_keys=required)
    click.echo(report.summary())
    if not report.healthy or (strict and report.lint_warnings):
        raise SystemExit(1)


@health_group.command("vault")
@click.argument("vault_file", type=click.Path(exists=True, path_type=Path))
@click.option("--password", "-p", prompt=True, hide_input=True, help="Vault password.")
@click.option("--require", "-r", multiple=True, metavar="KEY", help="Required key(s) that must be present.")
@click.option("--strict", is_flag=True, help="Exit non-zero on lint warnings too.")
def health_vault_cmd(vault_file: Path, password: str, require: tuple, strict: bool):
    """Check health of an encrypted vault file."""
    required = list(require) if require else None
    try:
        report = check_vault_file(vault_file, password, required_keys=required)
    except Exception as exc:
        raise click.ClickException(f"Failed to unlock vault: {exc}") from exc
    click.echo(report.summary())
    if not report.healthy or (strict and report.lint_warnings):
        raise SystemExit(1)
