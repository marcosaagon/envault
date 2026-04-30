"""CLI commands for diff and snapshot features."""

from __future__ import annotations

from pathlib import Path

import click

from envault.crypto import decrypt
from envault.diff import diff_envs, format_diff
from envault.snapshot import (
    delete_snapshot,
    list_snapshots,
    load_snapshot,
    purge_snapshots,
    save_snapshot,
)
from envault.vault import DEFAULT_VAULT_FILE


@click.group()
def diff_group() -> None:
    """Diff and snapshot commands."""


@diff_group.command("diff")
@click.option("--vault", default=DEFAULT_VAULT_FILE, show_default=True)
@click.option("--snapshot", required=True, help="Path to snapshot file to compare against.")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--show-values", is_flag=True, default=False)
def diff_cmd(vault: str, snapshot: str, password: str, show_values: bool) -> None:
    """Diff current vault against a snapshot."""
    vault_path = Path(vault)
    if not vault_path.exists():
        raise click.ClickException(f"Vault file not found: {vault}")

    snap_path = Path(snapshot)
    if not snap_path.exists():
        raise click.ClickException(f"Snapshot not found: {snapshot}")

    current_blob = vault_path.read_text().strip()
    snap_blob = load_snapshot(snap_path)

    try:
        current_plain = decrypt(current_blob, password)
        snap_plain = decrypt(snap_blob, password)
    except Exception as exc:
        raise click.ClickException(f"Decryption failed: {exc}") from exc

    result = diff_envs(snap_plain, current_plain)
    click.echo(format_diff(result, mask_values=not show_values))


@diff_group.command("snapshot")
@click.option("--vault", default=DEFAULT_VAULT_FILE, show_default=True)
@click.option("--label", default="", help="Optional label for the snapshot.")
def snapshot_cmd(vault: str, label: str) -> None:
    """Save a snapshot of the current vault."""
    vault_path = Path(vault)
    if not vault_path.exists():
        raise click.ClickException(f"Vault file not found: {vault}")

    blob = vault_path.read_text().strip()
    snap_file = save_snapshot(vault_path, blob, label=label or None)
    click.echo(f"Snapshot saved: {snap_file}")


@diff_group.command("snapshots")
@click.option("--vault", default=DEFAULT_VAULT_FILE, show_default=True)
def list_cmd(vault: str) -> None:
    """List available snapshots for a vault."""
    vault_path = Path(vault)
    snaps = list_snapshots(vault_path)
    if not snaps:
        click.echo("No snapshots found.")
        return
    for s in snaps:
        label = f" [{s['label']}]" if s.get("label") else ""
        click.echo(f"{s['timestamp']}  {s['path']}{label}")


@diff_group.command("purge")
@click.option("--vault", default=DEFAULT_VAULT_FILE, show_default=True)
@click.option("--keep", default=5, show_default=True)
def purge_cmd(vault: str, keep: int) -> None:
    """Purge old snapshots, keeping the N most recent."""
    vault_path = Path(vault)
    removed = purge_snapshots(vault_path, keep=keep)
    click.echo(f"Removed {removed} snapshot(s).")
