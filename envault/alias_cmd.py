"""CLI commands for managing vault key aliases."""

from __future__ import annotations

from pathlib import Path

import click

from envault.env_alias import add_alias, list_aliases, remove_alias, resolve_alias


@click.group("alias")
def alias_group() -> None:
    """Manage short-name aliases for vault keys."""


@alias_group.command("add")
@click.argument("alias")
@click.argument("key")
@click.option("--vault", default=".env.vault", show_default=True, help="Vault file path.")
def add_alias_cmd(alias: str, key: str, vault: str) -> None:
    """Map ALIAS to KEY inside VAULT."""
    vault_path = Path(vault)
    if not vault_path.exists():
        click.echo(f"Error: vault file '{vault}' not found.", err=True)
        raise SystemExit(1)
    is_new = add_alias(vault_path, alias, key)
    verb = "Added" if is_new else "Updated"
    click.echo(f"{verb} alias '{alias}' -> '{key}'.")


@alias_group.command("remove")
@click.argument("alias")
@click.option("--vault", default=".env.vault", show_default=True, help="Vault file path.")
def remove_alias_cmd(alias: str, vault: str) -> None:
    """Remove ALIAS from VAULT."""
    vault_path = Path(vault)
    if not vault_path.exists():
        click.echo(f"Error: vault file '{vault}' not found.", err=True)
        raise SystemExit(1)
    removed = remove_alias(vault_path, alias)
    if removed:
        click.echo(f"Removed alias '{alias}'.")
    else:
        click.echo(f"Alias '{alias}' not found.", err=True)
        raise SystemExit(1)


@alias_group.command("list")
@click.option("--vault", default=".env.vault", show_default=True, help="Vault file path.")
def list_aliases_cmd(vault: str) -> None:
    """List all aliases defined for VAULT."""
    vault_path = Path(vault)
    aliases = list_aliases(vault_path)
    if not aliases:
        click.echo("No aliases defined.")
        return
    for alias, key in sorted(aliases.items()):
        click.echo(f"{alias} -> {key}")


@alias_group.command("resolve")
@click.argument("alias")
@click.option("--vault", default=".env.vault", show_default=True, help="Vault file path.")
def resolve_alias_cmd(alias: str, vault: str) -> None:
    """Print the key name that ALIAS maps to."""
    vault_path = Path(vault)
    key = resolve_alias(vault_path, alias)
    if key is None:
        click.echo(f"Alias '{alias}' not found.", err=True)
        raise SystemExit(1)
    click.echo(key)
