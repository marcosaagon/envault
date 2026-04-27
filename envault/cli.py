"""CLI entry point for envault using Click."""

import click
from envault.vault import lock, unlock, DEFAULT_ENV_FILE, DEFAULT_VAULT_FILE


@click.group()
@click.version_option(version="0.1.0", prog_name="envault")
def cli():
    """envault — Encrypt and manage your .env files for safe Git sharing."""


@cli.command("lock")
@click.option("--env", default=DEFAULT_ENV_FILE, show_default=True, help="Path to the .env file to encrypt.")
@click.option("--vault", default=DEFAULT_VAULT_FILE, show_default=True, help="Output path for the encrypted vault file.")
@click.password_option("--password", prompt="Encryption password", help="Password used for encryption.")
def lock_cmd(env, vault, password):
    """Encrypt a .env file into an encrypted vault blob."""
    try:
        lock(env_path=env, vault_path=vault, password=password)
        click.secho(f"✔ Locked '{env}' → '{vault}'", fg="green")
    except (FileNotFoundError, ValueError) as exc:
        click.secho(f"✘ Error: {exc}", fg="red", err=True)
        raise SystemExit(1)


@cli.command("unlock")
@click.option("--vault", default=DEFAULT_VAULT_FILE, show_default=True, help="Path to the encrypted vault file.")
@click.option("--env", default=DEFAULT_ENV_FILE, show_default=True, help="Output path for the decrypted .env file.")
@click.option("--password", prompt="Decryption password", hide_input=True, help="Password used for decryption.")
def unlock_cmd(vault, env, password):
    """Decrypt a vault blob back into a .env file."""
    try:
        unlock(vault_path=vault, env_path=env, password=password)
        click.secho(f"✔ Unlocked '{vault}' → '{env}'", fg="green")
    except (FileNotFoundError, Exception) as exc:
        click.secho(f"✘ Error: {exc}", fg="red", err=True)
        raise SystemExit(1)


if __name__ == "__main__":
    cli()
