"""CLI command for querying relevant code."""

import click
import json
from code_graph.retrieval.query_engine import QueryEngine


@click.command()
@click.argument("query", type=str)
@click.option("--max-results", type=int, default=12, help="Maximum files to return")
@click.option("--hops", type=int, default=2, help="Maximum relationship hops")
@click.option(
    "--format",
    type=click.Choice(["text", "json", "files-only"]),
    default="text",
    help="Output format",
)
@click.option(
    "--execution-log",
    type=click.Path(exists=True),
    help="Include execution signals from log file",
)
@click.pass_context
def query(
    ctx: click.Context,
    query: str,
    max_results: int,
    hops: int,
    format: str,
    execution_log: str | None,
) -> None:
    """Query for relevant code.

    Retrieves relevant code files and functions for a natural language
    task description using hybrid scoring.

    \b
    Examples:
        code-graph query "add email validation to user registration"
        code-graph query "fix the authentication timeout" --execution-log error.log
        code-graph query "refactor payment module" --format json
    """
    verbose = ctx.obj.get("verbose", False)

    click.echo(f"🔍 Query: \"{query}\"")
    if verbose:
        click.echo(f"  Max results: {max_results}")
        click.echo(f"  Max hops: {hops}")

    try:
        # Get indexer from context (set by index command)
        indexer = ctx.obj.get("indexer")
        if not indexer:
            click.echo("\n⚠️  No index found. Please run 'code-graph index' first.", err=True)
            return

        # Create query engine
        engine = QueryEngine(graph=indexer.store)

        # Execute query
        click.echo("\n📊 Searching code graph...")
        results = engine.query(query, top_n=max_results)

        # Format and display results
        if format == "json":
            # JSON output
            output = {
                "query": query,
                "total_confidence": results.total_confidence,
                "max_hops": results.max_hops,
                "timestamp": results.retrieval_timestamp.isoformat(),
                "files": [
                    {
                        "path": f.file_path,
                        "relevance_score": f.relevance_score,
                        "rationale": f.rationale,
                    }
                    for f in results.files
                ],
            }
            click.echo(json.dumps(output, indent=2))

        elif format == "files-only":
            # Just file paths
            for file_ref in results.files:
                click.echo(file_ref.file_path)

        else:  # text format
            # Rich text output
            if not results.files:
                click.echo("\n❌ No relevant files found.")
                return

            click.echo(f"\n📄 Results ({len(results.files)} files, confidence: {results.total_confidence:.2f})\n")

            for i, file_ref in enumerate(results.files, 1):
                # Star rating based on score
                stars = "⭐" * min(5, int(file_ref.relevance_score * 5))
                click.echo(f"{i}. {file_ref.file_path} (score: {file_ref.relevance_score:.2f}) {stars}")
                click.echo(f"   └─ {file_ref.rationale}\n")

    except Exception as e:
        click.echo(f"\n❌ Error during query: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
