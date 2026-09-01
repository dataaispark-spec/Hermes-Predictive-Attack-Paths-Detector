#!/usr/bin/env python3
"""
Synthetic MCP server: AI-agent inventory + attack-path detection with MITRE mapping.
Lab mode — no live agent control plane required.

Run (stdio MCP):
  python mcp-servers/agent-path-mcp/server.py

Or call helpers from scripts/detect_agent_attack_paths.py
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, List

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from mitre.mapper import load_mapping, map_hop, map_path_template  # noqa: E402

# Synthetic agent estate (replace with real inventory later)
SYNTHETIC_AGENTS = [
    {
        "id": "agent-support-bot",
        "name": "Customer Support Agent",
        "exposure": "user_facing",
        "tools": ["rag_search", "ticket_create", "crm_read"],
        "privileges": "medium",
        "internet_facing": True,
    },
    {
        "id": "agent-secops-bot",
        "name": "SecOps Triage Agent",
        "exposure": "internal",
        "tools": ["siem_query", "neo4j_read", "shell_readonly", "ticket_create"],
        "privileges": "high",
        "internet_facing": False,
    },
    {
        "id": "agent-devops-bot",
        "name": "DevOps Deploy Agent",
        "exposure": "internal",
        "tools": ["kubectl", "cloud_iam_read", "secrets_read", "shell"],
        "privileges": "critical",
        "internet_facing": False,
    },
]

SYNTHETIC_MCP = [
    {"id": "mcp-neo4j", "name": "Neo4j MCP", "tools": ["cypher_read", "cypher_write"], "risk": "high"},
    {"id": "mcp-shell", "name": "Shell MCP", "tools": ["bash"], "risk": "critical"},
    {"id": "mcp-tickets", "name": "Jira MCP", "tools": ["create_issue"], "risk": "medium"},
    {"id": "mcp-secrets", "name": "Vault MCP", "tools": ["read_secret"], "risk": "critical"},
]


def list_agents() -> List[Dict[str, Any]]:
    return SYNTHETIC_AGENTS


def list_mcp_servers() -> List[Dict[str, Any]]:
    return SYNTHETIC_MCP


def score_path(template_id: str, agent_id: str) -> Dict[str, Any]:
    data = load_mapping()
    mapped = map_path_template(template_id, data)
    agent = next((a for a in SYNTHETIC_AGENTS if a["id"] == agent_id), SYNTHETIC_AGENTS[0])
    priv_w = {"medium": 0.6, "high": 0.8, "critical": 1.0}.get(agent["privileges"], 0.5)
    exp_w = 0.3 if agent.get("internet_facing") else 0.1
    tool_w = min(1.0, len(agent.get("tools", [])) * 0.15)
    base = 0.55
    score = round(min(0.99, base + priv_w * 0.25 + exp_w + tool_w * 0.2), 3)
    return {
        "path_id": f"{template_id}::{agent_id}",
        "agent": agent,
        "score": score,
        "likelihood": round(score * 0.9, 3),
        "impact": priv_w,
        "mitre": mapped,
        "description": mapped.get("description"),
        "status": "open",
        "domain": "ai_agent",
    }


def detect_paths() -> List[Dict[str, Any]]:
    data = load_mapping()
    out = []
    for t in data.get("agent_path_templates", []):
        # Bind template to plausible agent
        if "ticket" in t["id"] or "prompt" in t["id"]:
            agent_id = "agent-support-bot"
        elif "shell" in t["id"] or "tool-poison" in t["id"]:
            agent_id = "agent-devops-bot"
        else:
            agent_id = "agent-secops-bot"
        out.append(score_path(t["id"], agent_id))
    out.sort(key=lambda x: x["score"], reverse=True)
    return out


def main_stdio_demo() -> None:
    """Print inventory + paths (works without MCP SDK for lab smoke)."""
    print(json.dumps({"agents": list_agents(), "mcp": list_mcp_servers(), "paths": detect_paths()}, indent=2))


if __name__ == "__main__":
    main_stdio_demo()
