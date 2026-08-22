#!/usr/bin/env python3
"""
Minimal behavioural anomaly detector MCP (working template).
- Maintains simple per-entity baselines (count / rate) in memory
- Flags deviations above configurable z-score / threshold
- Emits Anomaly-shaped records for the shared graph
This is a statistical starter, not a full UEBA product.
"""

from __future__ import annotations

import json
import math
import os
import time
from collections import defaultdict
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("anomaly-detector-mcp")

_baselines: dict[str, list[float]] = defaultdict(list)
WINDOW = int(os.getenv("ANOMALY_WINDOW", "20"))
Z_THRESHOLD = float(os.getenv("ANOMALY_Z_THRESHOLD", "3.0"))
_recent_anomalies: list[dict] = []


def _zscore(values: list[float], current: float) -> float:
    if len(values) < 5:
        return 0.0
    mean = sum(values) / len(values)
    var = sum((x - mean) ** 2 for x in values) / len(values)
    std = math.sqrt(var) if var > 0 else 1e-6
    return abs(current - mean) / std


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="anomaly_observe",
            description="Record an observation for an entity and return whether it is anomalous",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {"type": "string"},
                    "metric": {"type": "string"},
                    "value": {"type": "number"},
                    "timestamp": {"type": "number"},
                },
                "required": ["entity_id", "metric", "value"],
            },
        ),
        Tool(
            name="anomaly_list_recent",
            description="List recent anomalies (from in-memory buffer)",
            inputSchema={
                "type": "object",
                "properties": {"limit": {"type": "integer", "default": 20}},
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    args = arguments or {}
    if name == "anomaly_observe":
        entity = args["entity_id"]
        metric = args["metric"]
        value = float(args["value"])
        key = f"{entity}:{metric}"
        history = _baselines[key]
        z = _zscore(history, value)
        history.append(value)
        if len(history) > WINDOW:
            history.pop(0)
        is_anom = z >= Z_THRESHOLD
        record = {
            "entity_id": entity,
            "metric": metric,
            "value": value,
            "zscore": round(z, 3),
            "is_anomaly": is_anom,
            "observed_at": args.get("timestamp") or time.time(),
        }
        if is_anom:
            _recent_anomalies.append(record)
            if len(_recent_anomalies) > 200:
                _recent_anomalies.pop(0)
        return [TextContent(type="text", text=json.dumps(record, indent=2))]
    if name == "anomaly_list_recent":
        limit = int(args.get("limit", 20))
        return [TextContent(type="text", text=json.dumps(_recent_anomalies[-limit:], indent=2))]
    return [TextContent(type="text", text=json.dumps({"error": f"unknown tool {name}"}))]


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
