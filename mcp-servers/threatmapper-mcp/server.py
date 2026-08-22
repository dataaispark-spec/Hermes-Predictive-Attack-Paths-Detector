#!/usr/bin/env python3
"""Synthetic-data MCP server: threatmapper-mcp (works offline)."""
from __future__ import annotations
import json, os
from typing import Any

from mcp.server.mcpserver import MCPServer

mcp = MCPServer("threatmapper-mcp")

MODE = os.getenv("THREATMAPPER_MODE", "synthetic").lower()
SYNTHETIC_VULNS = [
    {"id": "tm-v-1", "cve": "CVE-2024-1234", "title": "RCE in web framework", "severity": "critical", "cvss": 9.8, "epss": 0.91, "node": "web-prod-1"},
    {"id": "tm-v-2", "cve": "CVE-2023-9999", "title": "SQL injection", "severity": "high", "cvss": 8.6, "epss": 0.55, "node": "api.example.com"},
]
SYNTHETIC_PATHS = [
    {"id": "tm-path-1", "score": 0.89, "nodes": ["web-prod-1", "api.example.com", "prod-db"], "description": "Internet RCE to database"},
]
SYNTHETIC_TOPOLOGY = {"web-prod-1": {"neighbours": ["api.example.com"], "zone": "dmz"}}

@mcp.tool()
def tm_list_vulnerabilities(severity: list[str] | None = None, limit: int = 50) -> str:
    """List prioritised vulnerabilities (synthetic)."""
    vulns = SYNTHETIC_VULNS
    if severity:
        sevs = [s.lower() for s in severity]
        vulns = [v for v in vulns if v["severity"] in sevs]
    return json.dumps({"mode": MODE, "vulnerabilities": vulns[:limit]}, indent=2)

@mcp.tool()
def tm_attack_paths(limit: int = 20) -> str:
    """Top attack paths (synthetic)."""
    return json.dumps({"mode": MODE, "paths": SYNTHETIC_PATHS[:limit]}, indent=2)

@mcp.tool()
def tm_node_topology(node_id: str) -> str:
    """Node topology (synthetic)."""
    topo = SYNTHETIC_TOPOLOGY.get(node_id, {"neighbours": [], "zone": "unknown"})
    return json.dumps({"mode": MODE, "node_id": node_id, **topo}, indent=2)

if __name__ == "__main__":
    mcp.run()
