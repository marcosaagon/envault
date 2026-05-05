"""CLI commands for the watch feature."""

import click
from pathlib import Path

from envault.vault import lock
from envault.watch import EnvWatcher
from envault.audit import record_event


@click.group(name="watch")
def watch_group():
    """Watch .env files and auto-lock on change."""


@watch_group.command(name="start")
@click.argument("env_file", default=".env")
@click.option("--vault", "vault_file", default=".env.vault", show_default=True,
              help="Destination vault file.")
@click.option("--password", prompt=True, hide_input=True,
              help="Password used to encrypt on change.")
@click.option("--interval", default=1.0, show_default=True,
              help="Poll interval in seconds.")
def watch_start_cmd(env_file: str, vault_file: str, password: str, interval: float):
    """Watch ENV_FILE and re-lock it to VAULT on every change."""
    env_path = Path(env_file)
    vault_path = Path(vault_file)

    if not env_path.exists():
        raise click.ClickException(f"File not found: {env_file}")

    def _on_change(path: Path) -> None:
        lock(path, vault_path, password)
        record_event("watch_lock", {"env": str(path), "vault": str(vault_path)})
        click.echo(f"[watch] Locked {path} -> {vault_path}")

    watcher = EnvWatcher(env_path, _on_change, poll_interval=interval)
    watcher.start()
    click.echo(f"Watching {env_file} (interval={interval}s). Press Ctrl+C to stop.")
    try:
        import time
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        watcher.stop()
        click.echo("Watcher stopped.")
