from __future__ import annotations

import typer


def serve(
    host: str = typer.Option("127.0.0.1", "--host", help="Bind address"),
    port: int = typer.Option(8000, "--port", "-p", help="Port"),
    reload: bool = typer.Option(False, "--reload", help="Auto-reload on code changes"),
) -> None:
    """Start the mq-image web UI at http://localhost:8000"""
    try:
        import uvicorn
    except ImportError:
        typer.echo("uvicorn not installed. Run: pip install uvicorn", err=True)
        raise typer.Exit(1)

    typer.echo(f"Starting mq-image web UI → http://{host}:{port}")
    uvicorn.run(
        "mq_image_analyze.web.server:app",
        host=host,
        port=port,
        reload=reload,
    )
