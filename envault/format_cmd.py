"""CLI commands for formatting .env files and vaults."""

from __future__ import annotations

import click

from envault.env_format import format_env_file, format_env_text
from envault.vault import unlock


@click.group("format")
def format_group() -> None:
    """Format and normalize .env files."""


@format_group.command("env")
@click.argument("env_file", default=".env")
@click.option("--quote", is_flag=True, default=False, help="Quote all values.")
@click.option("--sort", is_flag=True, default=False, help="Sort keys alphabetically.")
@click.option("--check", is_flag=True, default=False, help="Check only, do not write.")
def format_env_cmd(env_file: str, quote: bool, sort: bool, check: bool) -> None:
    """Format a .env file in place."""
    try:
        if check:
            with open(env_file, "r") as f:
                text = f.read()
            result = format_env_text(text, quote_values=quote, sort_keys=sort)
            if result.changed:
                click.echo(f"Would reformat: {env_file}")
                for change in result.changes:
                    click.echo(f"  - {change}")
                raise SystemExit(1)
            else:
                click.echo(f"Already formatted: {env_file}")
        else:
            result = format_env_file(env_file, quote_values=quote, sort_keys=sort)
            if result.changed:
                click.echo(f"Formatted: {env_file}")
                for change in result.changes:
                    click.echo(f"  - {change}")
            else:
                click.echo(f"No changes needed: {env_file}")
    except FileNotFoundError:
        click.echo(f"Error: file not found: {env_file}", err=True)
        raise SystemExit(1)


@format_group.command("vault")
@click.argument("vault_file", default=".env.vault")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--quote", is_flag=True, default=False, help="Quote all values.")
@click.option("--sort", is_flag=True, default=False, help="Sort keys alphabetically.")
@click.option("--check", is_flag=True, default=False, help="Check only, do not write.")
def format_vault_cmd(
    vault_file: str, password: str, quote: bool, sort: bool, check: bool
) -> None:
    """Decrypt a vault, format its content, and re-encrypt."""
    from envault.vault import lock

    try:
        text = unlock(vault_file, password)
    except Exception as exc:
        click.echo(f"Error decrypting vault: {exc}", err=True)
        raise SystemExit(1)

    result = format_env_text(text, quote_values=quote, sort_keys=sort)

    if check:
        if result.changed:
            click.echo(f"Would reformat vault: {vault_file}")
            for change in result.changes:
                click.echo(f"  - {change}")
            raise SystemExit(1)
        else:
            click.echo(f"Vault already formatted: {vault_file}")
        return

    if result.changed:
        lock(vault_file, result.formatted, password)
        click.echo(f"Formatted vault: {vault_file}")
        for change in result.changes:
            click.echo(f"  - {change}")
    else:
        click.echo(f"No changes needed: {vault_file}")
