"""CLI commands for vault backup and restore."""

import click
from envault.backup import (
    create_backup,
    list_backups,
    restore_backup,
    delete_backup,
    purge_backups,
)


@click.group(name="backup")
def backup_group():
    """Backup and restore vault files."""


@backup_group.command(name="create")
@click.argument("vault", default=".env.vault")
def backup_create_cmd(vault: str):
    """Create a timestamped backup of a vault file."""
    try:
        path = create_backup(vault)
        click.echo(f"Backup created: {path}")
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@backup_group.command(name="list")
@click.argument("vault", default=".env.vault")
def backup_list_cmd(vault: str):
    """List all backups for a vault file."""
    entries = list_backups(vault)
    if not entries:
        click.echo("No backups found.")
        return
    click.echo(f"{'Name':<40} {'Size':>8}  Created")
    click.echo("-" * 72)
    for e in entries:
        click.echo(f"{e['name']:<40} {e['size']:>8}  {e['created']}")


@backup_group.command(name="restore")
@click.argument("backup_path")
@click.argument("vault", default=".env.vault")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt.")
def backup_restore_cmd(backup_path: str, vault: str, yes: bool):
    """Restore a vault file from a backup."""
    if not yes:
        click.confirm(f"Overwrite '{vault}' with '{backup_path}'?", abort=True)
    try:
        restore_backup(backup_path, vault)
        click.echo(f"Restored '{vault}' from '{backup_path}'.")
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@backup_group.command(name="delete")
@click.argument("backup_path")
def backup_delete_cmd(backup_path: str):
    """Delete a single backup file."""
    try:
        delete_backup(backup_path)
        click.echo(f"Deleted backup: {backup_path}")
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@backup_group.command(name="purge")
@click.argument("vault", default=".env.vault")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt.")
def backup_purge_cmd(vault: str, yes: bool):
    """Delete all backups for a vault file."""
    if not yes:
        click.confirm(f"Delete ALL backups for '{vault}'?", abort=True)
    count = purge_backups(vault)
    click.echo(f"Deleted {count} backup(s).")
