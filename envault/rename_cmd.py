"""CLI commands for renaming keys in .env files and vaults."""

import click

from envault.env_rename import rename_key_in_env_file, rename_key_in_vault


@click.group(name="rename")
def rename_group() -> None:
    """Rename a key in a .env file or encrypted vault."""


@rename_group.command(name="env")
@click.argument("path", default=".env")
@click.argument("old_key")
@click.argument("new_key")
def rename_env_cmd(path: str, old_key: str, new_key: str) -> None:
    """Rename OLD_KEY to NEW_KEY in a plaintext .env file."""
    import os

    if not os.path.isfile(path):
        click.echo(f"Error: file '{path}' not found.", err=True)
        raise SystemExit(1)

    result = rename_key_in_env_file(path, old_key, new_key)

    if result.ok:
        click.echo(f"✓ {result.message}")
    else:
        click.echo(f"✗ {result.message}", err=True)
        raise SystemExit(1)


@rename_group.command(name="vault")
@click.argument("vault_path", default=".env.vault")
@click.argument("old_key")
@click.argument("new_key")
@click.option(
    "--password",
    "-p",
    prompt=True,
    hide_input=True,
    help="Vault password.",
)
def rename_vault_cmd(vault_path: str, old_key: str, new_key: str, password: str) -> None:
    """Rename OLD_KEY to NEW_KEY inside an encrypted VAULT_PATH."""
    import os

    if not os.path.isfile(vault_path):
        click.echo(f"Error: vault '{vault_path}' not found.", err=True)
        raise SystemExit(1)

    try:
        result = rename_key_in_vault(vault_path, password, old_key, new_key)
    except Exception as exc:  # noqa: BLE001
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    if result.ok:
        click.echo(f"✓ {result.message}")
    else:
        click.echo(f"✗ {result.message}", err=True)
        raise SystemExit(1)
