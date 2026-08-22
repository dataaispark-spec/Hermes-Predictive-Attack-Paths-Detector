#!/usr/bin/env python3
"""Synthetic-data MCP server: bloodhound-mcp (works offline)."""
from __future__ import annotations
import json, os
from typing import Any

from mcp.server.mcpserver import MCPServer

mcp = MCPServer("bloodhound-mcp")

MODE = os.getenv("BLOODHOUND_MODE", "synthetic").lower()
SYNTHETIC_DOMAINS = ["CORP.LOCAL", "DMZ.LOCAL"]
SYNTHETIC_PATHS = [
    {"path_id": "bh-path-1", "hops": [{"type": "User", "name": "jdoe@CORP.LOCAL"}, {"type": "Group", "name": "Domain Admins"}], "length": 2, "risk": "critical"},
    {"path_id": "bh-path-2", "hops": [{"type": "User", "name": "svc-backup@CORP.LOCAL"}, {"type": "Group", "name": "Domain Admins"}], "length": 2, "risk": "high"},
]
SYNTHETIC_GRAPH = {
    "nodes": [
        {"id": "user-jdoe", "name": "jdoe@CORP.LOCAL", "type": "user"},
        {"id": "group-da", "name": "Domain Admins", "type": "group", "privileged": True},
    ],
    "edges": [{"from": "user-jdoe", "to": "group-da", "type": "MEMBER_OF"}],
}

@mcp.tool()
def bh_list_domains() -> str:
    """List domains known to BloodHound (synthetic)."""
    return json.dumps({"mode": MODE, "domains": SYNTHETIC_DOMAINS}, indent=2)

@mcp.tool()
def bh_shortest_paths_to_da(domain: str = "CORP.LOCAL", limit: int = 20) -> str:
    """Return shortest paths to Domain Admin (synthetic)."""
    return json.dumps({"mode": MODE, "domain": domain, "paths": SYNTHETIC_PATHS[:limit]}, indent=2)

@mcp.tool()
def bh_export_graph_fragment(domain: str, include_sessions: bool = True) -> str:
    """Export normalised graph fragment for Neo4j (synthetic)."""
    return json.dumps({"mode": MODE, "domain": domain, **SYNTHETIC_GRAPH}, indent=2)

if __name__ == "__main__":
    mcp.run()
