#!/usr/bin/env python3
"""
External attack-surface / exposure monitoring MCP (working template).
- Look-alike / typosquat domain checks (basic heuristics)
- Exposure registration shaped for Neo4j
- Placeholder for internet-facing ASM feeds
"""

from __future__ import annotations

import json
import os
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("external-surface-mcp")

BRAND_DOMAINS = [
    d.strip() for d in os.getenv("BRAND_DOMAINS", "example.com").split(",") if d.strip()
]


def _lookalike_score(candidate: str, brand: str) -> float:
    c, b = candidate.lower(), brand.lower()
    if c == b:
        return 0.0
    if c.replace("0", "o").replace("1", "l") == b:
        return 0.85
    if abs(len(c) - len(b)) > 3:
        return 0.1
    common = sum(1 for ch in set(c) if ch in b)
    return min(0.95, common / max(len(b), 1) * 0.7)


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="surface_check_lookalikes",
            description="Score candidate domains for look-alike / typosquat risk against brand domains",
            inputSchema={
                "type": "object",
                "properties": {
                    "candidates": {"type": "array", "items": {"type": "string"}},
                    "brands": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["candidates"],
            },
        ),
        Tool(
            name="surface_internet_facing_summary",
            description="Summarise known internet-facing signals (placeholder for ASM feed)",
            inputSchema={
                "type": "object",
                "properties": {"asset_ids": {"type": "array", "items": {"type": "string"}}},
            },
        ),
        Tool(
            name="surface_register_exposure",
            description="Register an external exposure finding (shaped for Neo4j Finding/Asset)",
            inputSchema={
                "type": "object",
                "properties": {
                    "asset_id": {"type": "string"},
                    "exposure_type": {"type": "string"},
                    "detail": {"type": "string"},
                    "severity": {"type": "string", "default": "medium"},
                },
                "required": ["asset_id", "exposure_type", "detail"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    args = arguments or {}
    if name == "surface_check_lookalikes":
        candidates = args.get("candidates") or []
        brands = args.get("brands") or BRAND_DOMAINS
        results = []
        for cand in candidates:
            best = max((_lookalike_score(cand, b), b) for b in brands)
            results.append({
                "candidate": cand,
                "closest_brand": best[1],
                "score": round(best[0], 3),
                "risk": "high" if best[0] >= 0.7 else "medium" if best[0] >= 0.4 else "low",
            })
        return [TextContent(type="text", text=json.dumps(results, indent=2))]
    if name == "surface_internet_facing_summary":
        return [TextContent(type="text", text=json.dumps({
            "note": "Wire to real ASM / httpx / shodan feed",
            "asset_ids": args.get("asset_ids") or [],
            "exposures": [],
        }, indent=2))]
    if name == "surface_register_exposure":
        finding = {
            "id": f"exp-{args['asset_id']}-{args['exposure_type']}",
            "asset_id": args["asset_id"],
            "type": args["exposure_type"],
            "detail": args["detail"],
            "severity": args.get("severity", "medium"),
            "source": "external-surface-mcp",
        }
        return [TextContent(type="text", text=json.dumps(finding, indent=2))]
    return [TextContent(type="text", text=json.dumps({"error": f"unknown tool {name}"}))]


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
