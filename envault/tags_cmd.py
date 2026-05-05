"""CLI commands for tag management."""

from __future__ import annotations

import click

from envault.tags import (
    add_tag,
    all_tags,
    keys_for_tag,
    remove_tag,
    tags_for_key,
)


@click.group("tags")
def tags_group() -> None:
    """Manage tags for env variable keys."""


@tags_group.command("add")
@click.argument("key")
@click.argument("tag")
@click.option("--dir", "directory", default=".", show_default=True, help="Working directory.")
def add_tag_cmd(key: str, tag: str, directory: str) -> None:
    """Assign TAG to KEY."""
    add_tag(key, tag, directory)
    click.echo(f"Tagged '{key}' with '{tag}'.")


@tags_group.command("remove")
@click.argument("key")
@click.argument("tag")
@click.option("--dir", "directory", default=".", show_default=True, help="Working directory.")
def remove_tag_cmd(key: str, tag: str, directory: str) -> None:
    """Remove TAG from KEY."""
    remove_tag(key, tag, directory)
    click.echo(f"Removed tag '{tag}' from '{key}'.")


@tags_group.command("list")
@click.option("--key", default=None, help="Show tags for a specific key.")
@click.option("--tag", default=None, help="Show keys for a specific tag.")
@click.option("--dir", "directory", default=".", show_default=True, help="Working directory.")
def list_tags_cmd(key: str | None, tag: str | None, directory: str) -> None:
    """List tags or tagged keys."""
    if key:
        result = tags_for_key(key, directory)
        if result:
            click.echo(f"Tags for '{key}': {', '.join(result)}")
        else:
            click.echo(f"No tags found for '{key}'.")
    elif tag:
        result = keys_for_tag(tag, directory)
        if result:
            click.echo(f"Keys tagged '{tag}': {', '.join(result)}")
        else:
            click.echo(f"No keys found with tag '{tag}'.")
    else:
        tags = all_tags(directory)
        if tags:
            click.echo("All tags: " + ", ".join(tags))
        else:
            click.echo("No tags defined.")
