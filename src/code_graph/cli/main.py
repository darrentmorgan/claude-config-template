"""Main CLI entry point for code-graph tool."""

import click

from code_graph.cli.commands import index_cmd, query_cmd, status_cmd


@click.group()
@click.version_option(version="0.1.0")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--quiet", "-q", is_flag=True, help="Suppress non-error output")
@click.pass_context
def cli(ctx: click.Context, verbose: bool, quiet: bool) -> None:
    """Code Graph Indexer - Intelligent context retrieval for multi-agent workflows.

    Index repositories, query for relevant code, and explore relationships.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["quiet"] = quiet


# Register commands
cli.add_command(index_cmd.index)
cli.add_command(query_cmd.query)
cli.add_command(status_cmd.status)


if __name__ == "__main__":
    cli()
