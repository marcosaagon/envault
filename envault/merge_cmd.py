"""CLI commands for merging .env files and vaults."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from envault.merge import ConflictStrategy, merge_envs, parse_env, serialize_env
from envault.vault import lock, unlock


@click.group("merge")
def merge_group() -> None:
    """Merge .env files or encrypted vaults."""


@merge_group.command("env")
@click.argument("base_file", type=click.Path(exists=True))
@click.argument("theirs_file", type=click.Path(exists=True))
@click.option("--output", "-o", default=None, help="Output file (default: stdout)")
@click.option(
    "--strategy",
    type=click.Choice([s.value for s in ConflictStrategy], case_sensitive=False),
    default=ConflictStrategy.OURS.value,
    show_default=True,
    help="Conflict resolution strategy.",
)
def merge_env_cmd(base_file: str, theirs_file: str, output: str | None, strategy: str) -> None:
    """Merge two plain .env files."""
    base_text = Path(base_file).read_text()
    theirs_text = Path(theirs_file).read_text()

    base_env = parse_env(base_text)
    theirs_env = parse_env(theirs_text)

    result = merge_envs(base_env, theirs_env, ConflictStrategy(strategy))

    if result.added:
        click.echo(f"[merge] Added keys: {', '.join(result.added)}", err=True)
    if result.overwritten:
        click.echo(f"[merge] Overwritten keys (theirs): {', '.join(result.overwritten)}", err=True)
    if result.has_conflicts and ConflictStrategy(strategy) == ConflictStrategy.OURS:
        click.echo(
            f"[merge] Conflicts kept (ours): {', '.join(c.key for c in result.conflicts)}",
            err=True,
        )

    merged_text = serialize_env(result.merged)

    if output:
        Path(output).write_text(merged_text)
        click.echo(f"[merge] Written to {output}")
    else:
        click.echo(merged_text, nl=False)


@merge_group.command("vault")
@click.argument("base_vault", type=click.Path(exists=True))
@click.argument("theirs_vault", type=click.Path(exists=True))
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option("--output", "-o", required=True, help="Output vault file path.")
@click.option(
    "--strategy",
    type=click.Choice([s.value for s in ConflictStrategy], case_sensitive=False),
    default=ConflictStrategy.OURS.value,
    show_default=True,
)
def merge_vault_cmd(base_vault: str, theirs_vault: str, password: str, output: str, strategy: str) -> None:
    """Merge two encrypted vault files using the same password."""
    try:
        base_text = unlock(base_vault, password)
        theirs_text = unlock(theirs_vault, password)
    except Exception as exc:
        click.echo(f"[error] Failed to decrypt vault: {exc}", err=True)
        sys.exit(1)

    base_env = parse_env(base_text)
    theirs_env = parse_env(theirs_text)

    result = merge_envs(base_env, theirs_env, ConflictStrategy(strategy))

    if result.added:
        click.echo(f"[merge] Added keys: {', '.join(result.added)}", err=True)
    if result.has_conflicts:
        click.echo(
            f"[merge] Conflicts ({strategy}): {', '.join(c.key for c in result.conflicts)}",
            err=True,
        )

    merged_text = serialize_env(result.merged)
    lock(output, merged_text, password)
    click.echo(f"[merge] Merged vault written to {output}")
