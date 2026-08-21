#!/usr/bin/env python3
"""
Skeleton MCP server exposing a safe Nuclei scan tool for Hermes Bots.
This is intentionally minimal – extend with proper auth, rate limits,
template allow-lists and result normalisation before production use.
"""

from __future__ import annotations

import asyncio
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("nuclei-mcp")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="nuclei_scan",
            description=(
                "Run a limited Nuclei scan against one or more targets and return "
                "JSON findings. Uses only safe/info/low templates by default. "
                "Do not use for destructive testing."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "targets": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of URLs or hosts to scan",
                    },
                    "severity": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["info", "low"],
                        "description": "Allowed severities (info, low, medium, high, critical)",
                    },
                    "timeout_minutes": {
                        "type": "integer",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 30,
                    },
                },
                "required": ["targets"],
            },
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    if name != "nuclei_scan":
        raise ValueError(f"Unknown tool: {name}")

    args = arguments or {}
    targets = args.get("targets") or []
    severities = args.get("severity") or ["info", "low"]
    timeout = int(args.get("timeout_minutes", 5)) * 60

    if not targets:
        return [TextContent(type="text", text=json.dumps({"error": "no targets provided"}))]

    # Write targets to a temporary file
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as fh:
        fh.write("\n".join(targets))
        targets_file = fh.name

    out_file = targets_file + ".json"

    cmd = [
        "nuclei",
        "-l", targets_file,
        "-json-export", out_file,
        "-severity", ",".join(severities),
        "-silent",
        "-timeout", "10",
        "-retries", "1",
    ]

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            proc.kill()
            return [TextContent(type="text", text=json.dumps({"error": "scan timed out"}))]

        findings = []
        if Path(out_file).exists():
            with open(out_file) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            findings.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass

        result = {
            "targets": targets,
            "severity_filter": severities,
            "finding_count": len(findings),
            "findings": findings[:200],  # hard cap for safety
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except FileNotFoundError:
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": "nuclei binary not found in PATH. Install Nuclei first."
            }),
        )]
    finally:
        Path(targets_file).unlink(missing_ok=True)
        Path(out_file).unlink(missing_ok=True)


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
