"""CLI commands for filtering .env keys by prefix, suffix, or pattern."""

from __future__ import annotations

import sys

import click

from envault.crypto import decrypt
from envault.env_filter import filter_env_text
from envault.vault import unlock


@click.group("filter")
def filter_group() -> None:
    """Filter keys from .env files or vaults."""


def _filter_options(fn):
    fn = click.option("--prefix", default=None, help="Key must start with this string.")(fn)
    fn = click.option("--suffix", default=None, help="Key must end with this string.")(fn)
    fn = click.option("--pattern", default=None, help="Glob pattern for key name.")(fn)
    fn = click.option("--regex", default=None, help="Regex pattern for key name.")(fn)
    fn = click.option("--invert", is_flag=True, default=False, help="Invert the match.")(fn)
    return fn


@filter_group.command("env")
@click.argument("env_file", type=click.Path(exists=True))
@_filter_options
def filter_env_cmd(
    env_file: str,
    prefix: str | None,
    suffix: str | None,
    pattern: str | None,
    regex: str | None,
    invert: bool,
) -> None:
    """Filter keys from a plaintext .env file."""
    text = open(env_file).read()
    result = filter_env_text(text, prefix=prefix, suffix=suffix, pattern=pattern, regex=regex, invert=invert)
    click.echo(result.filtered_text)
    click.echo(f"# {result.summary()}", err=True)
    if not result.ok:
        sys.exit(1)


@filter_group.command("vault")
@click.argument("vault_file", type=click.Path(exists=True))
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@_filter_options
def filter_vault_cmd(
    vault_file: str,
    password: str,
    prefix: str | None,
    suffix: str | None,
    pattern: str | None,
    regex: str | None,
    invert: bool,
) -> None:
    """Filter keys from an encrypted vault file."""
    try:
        text = unlock(vault_file, password)
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    result = filter_env_text(text, prefix=prefix, suffix=suffix, pattern=pattern, regex=regex, invert=invert)
    click.echo(result.filtered_text)
    click.echo(f"# {result.summary()}", err=True)
    if not result.ok:
        sys.exit(1)
