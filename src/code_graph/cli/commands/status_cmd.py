"""CLI command for showing index status."""

import click


@click.command()
@click.option("--detailed", is_flag=True, help="Show detailed statistics")
@click.pass_context
def status(ctx: click.Context, detailed: bool) -> None:
    """Show index status.

    Displays current index statistics and health information.

    \b
    Examples:
        code-graph status
        code-graph status --detailed
    """
    click.echo("📊 Code Graph Status\n")

    # Get indexer from context
    indexer = ctx.obj.get("indexer")

    if not indexer:
        click.echo("⚠️  No index found. Run 'code-graph index' to create an index.\n")
        click.echo("Repository: Not indexed")
        click.echo("Last indexed: Never")
        click.echo("Index size: 0 MB\n")

        click.echo("Graph Statistics:")
        click.echo("├─ Files: 0")
        click.echo("├─ Modules: 0")
        click.echo("├─ Classes: 0")
        click.echo("├─ Functions: 0")
        click.echo("├─ Tests: 0")
        click.echo("└─ Total Nodes: 0\n")

        click.echo("Relationships:")
        click.echo("└─ Total Edges: 0\n")
        return

    # Get statistics from graph store
    store = indexer.store
    num_files = len(store.files)
    num_functions = len(store.functions)
    num_edges = len(store.edges)

    # Calculate total nodes
    total_nodes = num_files + num_functions

    click.echo(f"✅ Index is active\n")

    click.echo("Graph Statistics:")
    click.echo(f"├─ Files: {num_files}")
    click.echo(f"├─ Functions: {num_functions}")
    click.echo(f"└─ Total Nodes: {total_nodes}\n")

    click.echo("Relationships:")
    click.echo(f"└─ Total Edges: {num_edges}\n")

    if detailed and store.files:
        click.echo("Recent Files:")
        for file_id, file_node in list(store.files.items())[:10]:
            click.echo(f"  • {file_node.path}")
        if num_files > 10:
            click.echo(f"  ... and {num_files - 10} more\n")

    click.echo("Storage: In-memory (MVP)")
    click.echo("Memgraph: ⚠️  Not yet integrated (planned)")
    click.echo("WAL: ⚠️  Not yet implemented (planned)\n")
