"""CLI command for indexing repositories."""

import click
from code_graph.indexer.main import Indexer


@click.command()
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option(
    "--languages",
    default="python,typescript,go,java",
    help="Comma-separated list of languages to index",
)
@click.option(
    "--exclude",
    multiple=True,
    help="Glob pattern to exclude (can be repeated)",
)
@click.option(
    "--no-embeddings",
    is_flag=True,
    help="Skip computing semantic embeddings",
)
@click.option(
    "--parallel",
    type=int,
    default=8,
    help="Number of parallel workers",
)
@click.option("--force", is_flag=True, help="Force re-index even if up-to-date")
@click.pass_context
def index(
    ctx: click.Context,
    path: str,
    languages: str,
    exclude: tuple[str, ...],
    no_embeddings: bool,
    parallel: int,
    force: bool,
) -> None:
    """Index a repository.

    Performs full indexing of a repository, parsing all supported files
    and building the code graph.

    \b
    Examples:
        code-graph index
        code-graph index /path/to/repo --languages python,typescript
        code-graph index --exclude "tests/**" --force
    """
    verbose = ctx.obj.get("verbose", False)

    click.echo(f"🔍 Indexing repository: {path}")

    if verbose:
        click.echo(f"  Languages: {languages}")
        click.echo(f"  Parallel workers: {parallel}")
        click.echo(f"  Embeddings: {'disabled' if no_embeddings else 'enabled'}")

    try:
        # Create indexer and index repository
        indexer = Indexer()

        # Store in context for other commands to access
        ctx.obj["indexer"] = indexer

        click.echo("\n📊 Indexing in progress...")
        result = indexer.index_repository(path)

        # Display results
        if result.success:
            click.echo(f"\n✅ Indexing completed successfully!")
            click.echo(f"\n📈 Statistics:")
            click.echo(f"  Files indexed: {result.files_indexed}")
            click.echo(f"  Functions found: {result.functions_found}")

            if result.errors:
                click.echo(f"\n⚠️  {len(result.errors)} files had errors:")
                for error in result.errors[:5]:  # Show first 5 errors
                    click.echo(f"    • {error}")
                if len(result.errors) > 5:
                    click.echo(f"    ... and {len(result.errors) - 5} more")
        else:
            click.echo(f"\n❌ Indexing failed")
            if result.errors:
                for error in result.errors:
                    click.echo(f"  • {error}")

    except Exception as e:
        click.echo(f"\n❌ Error during indexing: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
