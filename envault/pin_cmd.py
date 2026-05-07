"""CLI commands for managing pinned keys in a vault."""

from __future__ import annotations

from pathlib import Path

import click

from envault.env_pin import load_pins, pin_key, unpin_key, is_pinned


@click.group("pin")
def pin_group() -> None:
    """Manage pinned (write-protected) keys in a vault."""


@pin_group.command("add")
@click.argument("vault", type=click.Path(exists=True))
@click.argument("key")
def pin_add_cmd(vault: str, key: str) -> None:
    """Pin KEY in VAULT to protect it from overwrites."""
    vault_path = Path(vault)
    added = pin_key(vault_path, key)
    if added:
        click.echo(f"Pinned '{key}' in {vault_path.name}.")
    else:
        click.echo(f"'{key}' is already pinned in {vault_path.name}.")


@pin_group.command("remove")
@click.argument("vault", type=click.Path(exists=True))
@click.argument("key")
def pin_remove_cmd(vault: str, key: str) -> None:
    """Unpin KEY in VAULT."""
    vault_path = Path(vault)
    removed = unpin_key(vault_path, key)
    if removed:
        click.echo(f"Unpinned '{key}' from {vault_path.name}.")
    else:
        click.echo(f"'{key}' was not pinned in {vault_path.name}.")


@pin_group.command("list")
@click.argument("vault", type=click.Path(exists=True))
def pin_list_cmd(vault: str) -> None:
    """List all pinned keys in VAULT."""
    vault_path = Path(vault)
    pins = load_pins(vault_path)
    if not pins:
        click.echo("No pinned keys.")
    else:
        click.echo(f"Pinned keys in {vault_path.name}:")
        for key in pins:
            click.echo(f"  - {key}")


@pin_group.command("check")
@click.argument("vault", type=click.Path(exists=True))
@click.argument("key")
def pin_check_cmd(vault: str, key: str) -> None:
    """Check whether KEY is pinned in VAULT."""
    vault_path = Path(vault)
    if is_pinned(vault_path, key):
        click.echo(f"'{key}' is pinned.")
    else:
        click.echo(f"'{key}' is not pinned.")
