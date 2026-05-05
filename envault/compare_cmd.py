"""CLI commands for comparing .env files and vaults."""

import click
from pathlib import Path

from envault.env_compare import compare_env_texts, format_compare_result
from envault.vault import unlock


@click.group(name="compare")
def compare_group():
    """Compare two .env files or vaults."""


@compare_group.command(name="env")
@click.argument("left", type=click.Path(exists=True))
@click.argument("right", type=click.Path(exists=True))
@click.option("--mask", is_flag=True, default=False, help="Hide values in output.")
def compare_env_cmd(left: str, right: str, mask: bool):
    """Compare two .env files and show differences."""
    left_text = Path(left).read_text()
    right_text = Path(right).read_text()
    result = compare_env_texts(left_text, right_text)
    click.echo(f"Summary: {result.summary()}")
    if result.has_differences:
        click.echo(format_compare_result(result, mask_values=mask))
        raise SystemExit(1)


@compare_group.command(name="vault")
@click.argument("left", type=click.Path(exists=True))
@click.argument("right", type=click.Path(exists=True))
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option("--mask", is_flag=True, default=False, help="Hide values in output.")
def compare_vault_cmd(left: str, right: str, password: str, mask: bool):
    """Compare two encrypted vault files and show differences."""
    try:
        left_text = unlock(Path(left), password)
        right_text = unlock(Path(right), password)
    except Exception as exc:
        raise click.ClickException(f"Failed to decrypt vault: {exc}") from exc

    result = compare_env_texts(left_text, right_text)
    click.echo(f"Summary: {result.summary()}")
    if result.has_differences:
        click.echo(format_compare_result(result, mask_values=mask))
        raise SystemExit(1)
