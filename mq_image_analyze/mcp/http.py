"""Loopback HTTP adapter for mq-agent's MCP bridge."""
from __future__ import annotations

import json
from urllib.parse import urlsplit

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware

from mq_image_analyze.mcp.server import mcp

app = FastAPI(title="mq-image-analyze MCP", docs_url=None, redoc_url=None)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "[::1]"])

_LOOPBACK_ORIGINS = {"localhost", "127.0.0.1", "::1"}


@app.middleware("http")
async def reject_foreign_origin(request: Request, call_next):
    """Browsers send Origin; mq-agent does not. A web page can reach a loopback
    port, and some tools can upload an image (cloud-verify), so a request from
    any non-loopback origin is refused before a tool runs — not left to CORS."""
    origin = request.headers.get("origin")
    if origin is not None and urlsplit(origin).hostname not in _LOOPBACK_ORIGINS:
        return JSONResponse({"detail": "Cross-origin requests are not accepted"}, status_code=403)
    return await call_next(request)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "name": "mq-image-analyze", "tool_count": len(await mcp.list_tools())}


@app.get("/tools")
async def tools() -> dict:
    return {"tools": [
        {"name": tool.name, "description": tool.description, "inputSchema": tool.inputSchema, "class": "A"}
        for tool in await mcp.list_tools()
    ]}


@app.post("/tools/{name}")
async def call_tool(name: str, arguments: dict) -> dict:
    registered = {tool.name for tool in await mcp.list_tools()}
    if name not in registered:
        raise HTTPException(status_code=404, detail="Unknown image tool")
    try:
        result = await mcp.call_tool(name, arguments)
        if isinstance(result, dict):
            return result
        if isinstance(result, tuple):
            result = result[0]
        # Image tools return a JSON string, represented as MCP text content.
        return json.loads(result[0].text)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
