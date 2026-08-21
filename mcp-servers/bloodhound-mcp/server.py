#!/usr/bin/env python3
"""
BloodHound CE / Adalanche-style collector MCP server (skeleton).
Exposes read-only tools to pull identity attack-path data and write
normalised nodes into the shared Neo4j graph via a separate write path.
Requires BloodHound CE API or a local SharpHound/AzureHound JSON dump.
"""

from __future__ import annotations

import json
import os
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("bloodhound-mcp")

BH_API = os.getenv("BLOODHOUND_API_URL", "http://localhost:8080")
BH_TOKEN = os.getenv("BLOODHOUND_TOKEN", "")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="bh_list_domains",
            description="List domains known to BloodHound CE",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="bh_shortest_paths_to_da",
            description="Return shortest paths to Domain Admin (or equivalent high-value targets)",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {"type": "string"},
                    "limit": {"type": "integer", "default": 20},
                },
            },
        ),
        Tool(
            name="bh_export_graph_fragment",
            description="Export a normalised graph fragment (nodes + edges) ready for Neo4j upsert",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {"type": "string"},
                    "include_sessions": {"type": "boolean", "default": True},
                },
                "required": ["domain"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    args = arguments or {}
    if name == "bh_list_domains":
        result = {"domains": ["EXAMPLE.LOCAL"], "note": "skeleton – wire to BloodHound CE API"}
    elif name == "bh_shortest_paths_to_da":
        result = {
            "domain": args.get("domain", "EXAMPLE.LOCAL"),
            "paths": [],
            "note": "skeleton – implement against /api/v2/graphs/cypher or equivalent",
        }
    elif name == "bh_export_graph_fragment":
        result = {
            "nodes": [],
            "edges": [],
            "domain": args.get("domain"),
            "note": "skeleton – map BH objects to Asset/Identity nodes",
        }
    else:
        result = {"error": f"unknown tool {name}"}
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
