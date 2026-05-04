"""CLI commands for linting .env and vault files."""
from __future__ import annotations

from pathlib import Path

import click

from envault.lint import lint_env_file, lint_vault_file


@click.group(name="lint")
def lint_group() -> None:
    """Lint .env files for common issues."""


@lint_group.command(name="env")
@click.argument("env_file", default=".env", metavar="ENV_FILE")
def lint_env_cmd(env_file: str) -> None:
    """Lint a plain .env file."""
    path = Path(env_file)
    if not path.exists():
        click.echo(f"Error: file not found: {env_file}", err=True)
        raise SystemExit(1)
    result = lint_env_file(path)
    if result.ok:
        click.echo(click.style(f"✔ {env_file}: no issues found.", fg="green"))
    else:
        for issue in result.issues:
            color = "red" if issue.code.startswith("E") else "yellow"
            click.echo(click.style(str(issue), fg=color))
        raise SystemExit(1)


@lint_group.command(name="vault")
@click.argument("vault_file", default=".env.vault", metavar="VAULT_FILE")
@click.option("--password", "-p", prompt=True, hide_input=True, help="Vault password.")
def lint_vault_cmd(vault_file: str, password: str) -> None:
    """Decrypt a vault file and lint its contents."""
    path = Path(vault_file)
    if not path.exists():
        click.echo(f"Error: file not found: {vault_file}", err=True)
        raise SystemExit(1)
    try:
        result = lint_vault_file(path, password)
    except Exception as exc:
        click.echo(f"Error decrypting vault: {exc}", err=True)
        raise SystemExit(1)
    if result.ok:
        click.echo(click.style(f"✔ {vault_file}: no issues found.", fg="green"))
    else:
        for issue in result.issues:
            color = "red" if issue.code.startswith("E") else "yellow"
            click.echo(click.style(str(issue), fg=color))
        raise SystemExit(1)
