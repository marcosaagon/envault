"""CLI entry point for envault."""

import click

from envault.vault import lock, unlock
from envault.audit import record_event


@click.group()
def cli():
    """envault — encrypt and manage your .env files."""


@cli.command("lock")
@click.argument("env_file", default=".env")
@click.argument("vault_file", default=".env.vault")
@click.option("--password", prompt=True, hide_input=True, help="Encryption password")
@click.option("--profile", default=None, help="Profile name for audit log")
def lock_cmd(env_file: str, vault_file: str, password: str, profile: str):
    """Encrypt ENV_FILE into VAULT_FILE."""
    try:
        lock(env_file, vault_file, password)
        record_event("lock", profile=profile, details=f"{env_file} -> {vault_file}")
        click.echo(f"Locked {env_file} -> {vault_file}")
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))


@cli.command("unlock")
@click.argument("vault_file", default=".env.vault")
@click.argument("env_file", default=".env")
@click.option("--password", prompt=True, hide_input=True, help="Decryption password")
@click.option("--profile", default=None, help="Profile name for audit log")
def unlock_cmd(vault_file: str, env_file: str, password: str, profile: str):
    """Decrypt VAULT_FILE into ENV_FILE."""
    try:
        unlock(vault_file, env_file, password)
        record_event("unlock", profile=profile, details=f"{vault_file} -> {env_file}")
        click.echo(f"Unlocked {vault_file} -> {env_file}")
    except (FileNotFoundError, ValueError) as exc:
        raise click.ClickException(str(exc))


@cli.command("log")
@click.option("--directory", default=".", help="Directory containing the audit log")
def log_cmd(directory: str):
    """Display the audit log for this vault."""
    from envault.audit import load_audit_log, format_log_entry

    entries = load_audit_log(directory)
    if not entries:
        click.echo("No audit log entries found.")
        return
    for entry in entries:
        click.echo(format_log_entry(entry))


if __name__ == "__main__":
    cli()
