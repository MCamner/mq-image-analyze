from __future__ import annotations

import typer


def serve_mcp(
    transport: str = typer.Option("stdio", help="Transport: 'stdio' (default) or 'sse'"),
) -> None:
    """Start the MCP server — exposes analyze_image, extract_palette, reverse_prompt, compare_images, analyze_ui."""
    from mq_image_analyze.mcp.server import mcp
    mcp.run(transport=transport)
