#!/usr/bin/env python3
"""
Hardened Nuclei MCP server for SkandaShield.
- Severity / tag / template-path allow-lists
- Rate limiting (token bucket)
- Target allow-list
- Audit log
- Optional Neo4j upsert of findings
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import time
import tempfile
from collections import deque
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("nuclei-mcp")

ALLOWED_SEVERITIES = set(
    s.strip().lower()
    for s in os.getenv("NUCLEI_ALLOWED_SEVERITIES", "info,low,medium").split(",")
    if s.strip()
)
# Default safe-ish tags; empty env means use this default. Set to "*" to allow any tag (not recommended).
_raw_tags = os.getenv("NUCLEI_ALLOWED_TAGS", "ssl,tls,http,dns,tech,cve,misconfig,exposure")
ALLOWED_TAGS: set[str] | None
if _raw_tags.strip() == "*":
    ALLOWED_TAGS = None  # unrestricted
else:
    ALLOWED_TAGS = {t.strip().lower() for t in _raw_tags.split(",") if t.strip()}

# Comma-separated absolute dirs; templates outside these paths are rejected
TEMPLATE_ALLOW_DIRS = [
    Path(p.strip()).resolve()
    for p in os.getenv("NUCLEI_TEMPLATE_ALLOW_DIRS", "").split(",")
    if p.strip()
]
# If no template dirs configured, refuse custom -t paths (tags only)
REQUIRE_TEMPLATE_DIR = os.getenv("NUCLEI_REQUIRE_TEMPLATE_DIR", "true").lower() in (
    "1",
    "true",
    "yes",
)

MAX_TARGETS = int(os.getenv("NUCLEI_MAX_TARGETS", "10"))
MAX_FINDINGS = int(os.getenv("NUCLEI_MAX_FINDINGS", "200"))
RATE_LIMIT_PER_MIN = int(os.getenv("NUCLEI_RATE_LIMIT_PER_MIN", "5"))
TARGET_ALLOWLIST = [
    t.strip() for t in os.getenv("NUCLEI_TARGET_ALLOWLIST", "").split(",") if t.strip()
]
AUDIT_LOG = os.getenv("NUCLEI_AUDIT_LOG", "/tmp/nuclei-mcp-audit.jsonl")

# Neo4j upsert (optional)
NEO4J_URI = os.getenv("NEO4J_URI", "")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")
NEO4J_UPSERT = os.getenv("NUCLEI_NEO4J_UPSERT", "false").lower() in ("1", "true", "yes")

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


def _tags_allowed(tags: list[str]) -> tuple[bool, str, list[str]]:
    if not tags:
        # default to intersection of safe tags
        if ALLOWED_TAGS is None:
            return True, "", []
        return True, "", sorted(ALLOWED_TAGS)[:4]  # small default set
    normalized = [t.strip().lower() for t in tags if t.strip()]
    if ALLOWED_TAGS is None:
        return True, "", normalized
    bad = [t for t in normalized if t not in ALLOWED_TAGS]
    if bad:
        return False, f"tags not allowed: {bad}; allowed={sorted(ALLOWED_TAGS)}", []
    return True, "", normalized


def _templates_allowed(templates: list[str]) -> tuple[bool, str, list[str]]:
    if not templates:
        return True, "", []
    if not TEMPLATE_ALLOW_DIRS:
        if REQUIRE_TEMPLATE_DIR:
            return (
                False,
                "custom templates rejected: set NUCLEI_TEMPLATE_ALLOW_DIRS to approved paths",
                [],
            )
        return True, "", templates
    resolved: list[str] = []
    for t in templates:
        p = Path(t).expanduser().resolve()
        if not any(str(p).startswith(str(d) + os.sep) or p == d for d in TEMPLATE_ALLOW_DIRS):
            return False, f"template path not under allow dirs: {t}", []
        if not p.exists():
            return False, f"template path does not exist: {t}", []
        resolved.append(str(p))
    return True, "", resolved


def _audit(event: dict) -> None:
    try:
        with open(AUDIT_LOG, "a") as f:
            f.write(json.dumps({"ts": time.time(), **event}) + "\n")
    except Exception:
        pass


def _finding_id(f: dict[str, Any]) -> str:
    tid = f.get("template-id") or f.get("templateID") or f.get("template_id") or "unknown"
    matched = f.get("matched-at") or f.get("matched_at") or f.get("host") or ""
    raw = f"{tid}|{matched}"
    return "nuclei-" + hashlib.sha256(raw.encode()).hexdigest()[:24]


def _asset_id_from_target(target: str, finding: dict[str, Any]) -> str:
    host = finding.get("host") or finding.get("ip") or ""
    if not host:
        try:
            host = urlparse(target).hostname or target
        except Exception:
            host = target
    return f"asset:{host}"


def _upsert_neo4j(targets: list[str], findings: list[dict[str, Any]]) -> dict[str, Any]:
    if not NEO4J_UPSERT or not NEO4J_URI or not NEO4J_PASSWORD:
        return {"upserted": 0, "skipped": True, "reason": "NEO4J upsert disabled or not configured"}
    try:
        from neo4j import GraphDatabase  # type: ignore
    except ImportError:
        return {"upserted": 0, "error": "neo4j driver not installed (pip install neo4j)"}

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    upserted = 0
    try:
        with driver.session() as session:
            for f in findings:
                fid = _finding_id(f)
                info = f.get("info") or {}
                severity = (info.get("severity") or f.get("severity") or "unknown").lower()
                title = info.get("name") or f.get("template-id") or "nuclei-finding"
                template_id = f.get("template-id") or ""
                matched = f.get("matched-at") or f.get("host") or ""
                # pick first target as fallback for asset link
                target = matched if matched.startswith("http") else (targets[0] if targets else matched)
                aid = _asset_id_from_target(target, f)
                session.run(
                    """
                    MERGE (a:Asset {id: $aid})
                    ON CREATE SET a.name = $host, a.type = 'host', a.source = 'nuclei',
                                 a.first_seen = datetime(), a.last_seen = datetime()
                    ON MATCH SET a.last_seen = datetime()
                    MERGE (f:Finding {id: $fid})
                    SET f.source = 'nuclei',
                        f.template_id = $template_id,
                        f.title = $title,
                        f.severity = $severity,
                        f.matched_at = $matched,
                        f.status = 'open',
                        f.last_seen = datetime()
                    ON CREATE SET f.first_seen = datetime()
                    MERGE (a)-[:HAS_VULN]->(f)
                    """,
                    aid=aid,
                    host=aid.replace("asset:", "", 1),
                    fid=fid,
                    template_id=template_id,
                    title=title,
                    severity=severity,
                    matched=matched,
                )
                upserted += 1
    finally:
        driver.close()
    return {"upserted": upserted, "skipped": False}


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="nuclei_scan",
            description=(
                "Run a limited Nuclei scan. Severity, tags, template paths, and targets "
                "are allow-listed server-side. Optional Neo4j upsert when enabled. "
                "Not for destructive or unrestricted testing."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "targets": {"type": "array", "items": {"type": "string"}},
                    "severity": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["info", "low"],
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Nuclei template tags; must be in server allow-list",
                    },
                    "templates": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional template file/dir paths under NUCLEI_TEMPLATE_ALLOW_DIRS",
                    },
                    "timeout_minutes": {
                        "type": "integer",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 15,
                    },
                    "upsert_graph": {
                        "type": "boolean",
                        "default": False,
                        "description": "If true and server has NUCLEI_NEO4J_UPSERT=true, write findings to Neo4j",
                    },
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
    upsert_graph = bool(args.get("upsert_graph", False))

    if not targets:
        return [TextContent(type="text", text=json.dumps({"error": "no targets"}))]

    ok, msg = _targets_allowed(targets)
    if not ok:
        _audit({"event": "denied", "reason": msg, "targets": targets})
        return [TextContent(type="text", text=json.dumps({"error": msg}))]

    ok, msg, tags = _tags_allowed(list(args.get("tags") or []))
    if not ok:
        _audit({"event": "denied", "reason": msg, "targets": targets})
        return [TextContent(type="text", text=json.dumps({"error": msg}))]

    ok, msg, templates = _templates_allowed(list(args.get("templates") or []))
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

    cmd = [
        "nuclei",
        "-l",
        targets_file,
        "-json-export",
        out_file,
        "-severity",
        ",".join(severities),
        "-silent",
        "-timeout",
        "10",
        "-retries",
        "1",
    ]
    if tags:
        cmd.extend(["-tags", ",".join(tags)])
    for tpath in templates:
        cmd.extend(["-t", tpath])

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
            _audit({"event": "timeout", "targets": targets})
            return [TextContent(type="text", text=json.dumps({"error": "scan timed out"}))]

        findings: list[dict[str, Any]] = []
        if Path(out_file).exists():
            raw = Path(out_file).read_text(encoding="utf-8", errors="replace").strip()
            if raw:
                # nuclei -json-export may be JSON array or JSONL depending on version
                try:
                    parsed = json.loads(raw)
                    if isinstance(parsed, list):
                        findings = [x for x in parsed if isinstance(x, dict)]
                    elif isinstance(parsed, dict):
                        findings = [parsed]
                except json.JSONDecodeError:
                    for line in raw.splitlines():
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            findings.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass

        findings = findings[:MAX_FINDINGS]
        graph_meta: dict[str, Any] = {"upserted": 0, "skipped": True}
        if upsert_graph and findings:
            graph_meta = _upsert_neo4j(targets, findings)

        result = {
            "targets": targets,
            "severity_filter": severities,
            "tags": tags,
            "templates": templates,
            "finding_count": len(findings),
            "findings": findings,
            "neo4j": graph_meta,
        }
        _audit(
            {
                "event": "scan_ok",
                "targets": targets,
                "count": len(findings),
                "tags": tags,
                "neo4j": graph_meta,
            }
        )
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except FileNotFoundError:
        return [
            TextContent(
                type="text",
                text=json.dumps({"error": "nuclei binary not found in PATH"}),
            )
        ]
    finally:
        Path(targets_file).unlink(missing_ok=True)
        Path(out_file).unlink(missing_ok=True)


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
