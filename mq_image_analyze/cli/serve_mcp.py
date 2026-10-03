from __future__ import annotations

import typer


def serve_mcp(
    transport: str = typer.Option("stdio", help="Transport: 'stdio' (default), 'sse', or 'http'"),
    port: int = typer.Option(8766, min=1, max=65535, help="HTTP bridge port (loopback only)"),
) -> None:
    """Start the MCP server — exposes analyze_image, extract_palette, reverse_prompt, compare_images, analyze_ui."""
    if transport == "http":
        import uvicorn
        uvicorn.run("mq_image_analyze.mcp.http:app", host="127.0.0.1", port=port)
        return
    from mq_image_analyze.mcp.server import mcp
    mcp.run(transport=transport)
