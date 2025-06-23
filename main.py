#!/usr/bin/env python3
"""Main entry point for Claude Code Action."""

import click
import sys
from .entrypoints.prepare import main as prepare_main
from .entrypoints.update_comment_link import main as update_comment_main


@click.group()
@click.version_option()
def cli():
    """Claude Code Action CLI."""
    pass


@cli.command()
def prepare():
    """Prepare the Claude action by checking trigger conditions and setting up context."""
    prepare_main()


@cli.command()
def update_comment():
    """Update comment with job link."""
    update_comment_main()


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()