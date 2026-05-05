"""CLI commands for exporting and importing env/vault data."""
from __future__ import annotations

import sys
from pathlib import Path

import click

from envault.export import export_env_file, export_vault_file, import_to_vault


@click.group(name="export")
def export_group() -> None:
    """Export and import env data in multiple formats."""


@export_group.command(name="env")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--format", "fmt",
    type=click.Choice(["dotenv", "json", "toml"]),
    default="json",
    show_default=True,
    help="Output format.",
)
@click.option("--output", "-o", type=click.Path(path_type=Path), default=None,
              help="Write to file instead of stdout.")
def export_env_cmd(env_file: Path, fmt: str, output: Path | None) -> None:
    """Export a plaintext .env file to the given format."""
    try:
        result = export_env_file(env_file, fmt)  # type: ignore[arg-type]
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    if output:
        output.write_text(result, encoding="utf-8")
        click.echo(f"Exported to {output}")
    else:
        click.echo(result, nl=False)


@export_group.command(name="vault")
@click.argument("vault_file", type=click.Path(exists=True, path_type=Path))
@click.option("--password", "-p", prompt=True, hide_input=True)
@click.option(
    "--format", "fmt",
    type=click.Choice(["dotenv", "json", "toml"]),
    default="json",
    show_default=True,
)
@click.option("--output", "-o", type=click.Path(path_type=Path), default=None)
def export_vault_cmd(vault_file: Path, password: str, fmt: str, output: Path | None) -> None:
    """Decrypt a vault and export its contents to the given format."""
    try:
        result = export_vault_file(vault_file, password, fmt)  # type: ignore[arg-type]
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    if output:
        output.write_text(result, encoding="utf-8")
        click.echo(f"Exported to {output}")
    else:
        click.echo(result, nl=False)


@export_group.command(name="import")
@click.argument("source_file", type=click.Path(exists=True, path_type=Path))
@click.argument("vault_file", type=click.Path(path_type=Path))
@click.option("--password", "-p", prompt=True, hide_input=True, confirmation_prompt=True)
@click.option(
    "--format", "fmt",
    type=click.Choice(["dotenv", "json", "toml"]),
    default="json",
    show_default=True,
)
def import_cmd(source_file: Path, vault_file: Path, password: str, fmt: str) -> None:
    """Import an exported file into an encrypted vault."""
    try:
        source = source_file.read_text(encoding="utf-8")
        import_to_vault(source, fmt, vault_file, password)  # type: ignore[arg-type]
        click.echo(f"Imported into {vault_file}")
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
