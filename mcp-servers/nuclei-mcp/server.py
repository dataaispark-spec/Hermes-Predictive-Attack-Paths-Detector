#!/usr/bin/env python3
"""
Hardened Nuclei MCP server for SkandaShield.
- Severity allow-list
- Rate limiting (simple token bucket)
- Target allow-list
- Audit log of every scan
- Hard caps on findings returned
"""

from __future__ import annotations

import asyncio
import json
import os
import time
import tempfile
from collections import deque
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("nuclei-mcp")

ALLOWED_SEVERITIES = set(
    s.strip().lower()
    for s in os.getenv("NUCLEI_ALLOWED_SEVERITIES", "info,low,medium").split(",")
)
MAX_TARGETS = int(os.getenv("NUCLEI_MAX_TARGETS", "10"))
MAX_FINDINGS = int(os.getenv("NUCLEI_MAX_FINDINGS", "200"))
RATE_LIMIT_PER_MIN = int(os.getenv("NUCLEI_RATE_LIMIT_PER_MIN", "5"))
TARGET_ALLOWLIST = [
    t.strip() for t in os.getenv("NUCLEI_TARGET_ALLOWLIST", "").split(",") if t.strip()
]
AUDIT_LOG = os.getenv("NUCLEI_AUDIT_LOG", "/tmp/nuclei-mcp-audit.jsonl")

_request_times: deque[float] = deque()


def _rate_limit_ok() -> bool:
    now = time.time()
    while _request_times and now - _request_times[0] > 60:
        _request_times.popleft()
    if len(_request_times) >= RATE_LIMIT_PER_MIN:
        return False
    _request_times.append(now)
    return True


def _targets_allowed(targets: list[str]) -> tuple[bool, str]:
    if len(targets) > MAX_TARGETS:
        return False, f"max {MAX_TARGETS} targets allowed"
    if TARGET_ALLOWLIST:
        for t in targets:
            if not any(t.startswith(a) or a in t for a in TARGET_ALLOWLIST):
                return False, f"target {t} not in allowlist"
    return True, ""


def _audit(event: dict) -> None:
    try:
        with open(AUDIT_LOG, "a") as f:
            f.write(json.dumps({"ts": time.time(), **event}) + "\n")
    except Exception:
        pass


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="nuclei_scan",
            description=(
                "Run a limited Nuclei scan. Severity and target controls are enforced. "
                "Default severities: info,low,medium. Not for destructive testing."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "targets": {"type": "array", "items": {"type": "string"}},
                    "severity": {"type": "array", "items": {"type": "string"}, "default": ["info", "low"]},
                    "timeout_minutes": {"type": "integer", "default": 5, "minimum": 1, "maximum": 15},
                },
                "required": ["targets"],
            },
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    if name != "nuclei_scan":
        return [TextContent(type="text", text=json.dumps({"error": f"unknown tool {name}"}))]

    args = arguments or {}
    targets = args.get("targets") or []
    requested_sev = [s.lower() for s in (args.get("severity") or ["info", "low"])]
    severities = [s for s in requested_sev if s in ALLOWED_SEVERITIES] or list(ALLOWED_SEVERITIES)[:2]
    timeout = min(int(args.get("timeout_minutes", 5)), 15) * 60

    if not targets:
        return [TextContent(type="text", text=json.dumps({"error": "no targets"}))]

    ok, msg = _targets_allowed(targets)
    if not ok:
        _audit({"event": "denied", "reason": msg, "targets": targets})
        return [TextContent(type="text", text=json.dumps({"error": msg}))]

    if not _rate_limit_ok():
        _audit({"event": "rate_limited", "targets": targets})
        return [TextContent(type="text", text=json.dumps({"error": "rate limit exceeded"}))]

    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as fh:
        fh.write("\n".join(targets))
        targets_file = fh.name
    out_file = targets_file + ".json"

    cmd = ["nuclei", "-l", targets_file, "-json-export", out_file, "-severity", ",".join(severities), "-silent", "-timeout", "10", "-retries", "1"]

    try:
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        try:
            await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            proc.kill()
            _audit({"event": "timeout", "targets": targets})
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

        findings = findings[:MAX_FINDINGS]
        result = {"targets": targets, "severity_filter": severities, "finding_count": len(findings), "findings": findings}
        _audit({"event": "scan_ok", "targets": targets, "count": len(findings)})
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except FileNotFoundError:
        return [TextContent(type="text", text=json.dumps({"error": "nuclei binary not found in PATH"}))]
    finally:
        Path(targets_file).unlink(missing_ok=True)
        Path(out_file).unlink(missing_ok=True)


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
