"""CLI commands for injecting vault variables into subprocesses."""

from __future__ import annotations

import sys

import click

from envault.env_inject import build_injected_env, run_with_vault


@click.group(name="inject")
def inject_group() -> None:
    """Inject decrypted vault variables into a subprocess."""


@inject_group.command(name="run")
@click.option("--vault", default=".env.vault", show_default=True, help="Vault file path.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option(
    "--no-override",
    is_flag=True,
    default=False,
    help="Do not overwrite existing environment variables.",
)
@click.argument("command", nargs=-1, required=True)
def inject_run_cmd(
    vault: str,
    password: str,
    no_override: bool,
    command: tuple,
) -> None:
    """Run COMMAND with vault variables injected into the environment.

    Example:

        envault inject run --vault .env.vault -- python app.py
    """
    try:
        result = run_with_vault(
            list(command),
            vault_path=vault,
            password=password,
            override=not no_override,
        )
        sys.exit(result.returncode)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    except ValueError as exc:
        raise click.ClickException(f"Failed to decrypt vault: {exc}") from exc


@inject_group.command(name="print")
@click.option("--vault", default=".env.vault", show_default=True, help="Vault file path.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option(
    "--no-override",
    is_flag=True,
    default=False,
    help="Do not overwrite existing environment variables.",
)
def inject_print_cmd(vault: str, password: str, no_override: bool) -> None:
    """Print the environment that would be injected (KEY=VALUE lines)."""
    try:
        env = build_injected_env(vault, password, override=not no_override)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    except ValueError as exc:
        raise click.ClickException(f"Failed to decrypt vault: {exc}") from exc

    for key, value in sorted(env.items()):
        click.echo(f"{key}={value}")
