#!/usr/bin/env python3
"""Synthetic-data MCP server: cloud-inventory-mcp (works offline)."""
from __future__ import annotations
import json, os
from typing import Any

from mcp.server.mcpserver import MCPServer

mcp = MCPServer("cloud-inventory-mcp")

MODE = os.getenv("CLOUD_MODE", "synthetic").lower()
SYNTHETIC_ACCOUNTS = [
    {"provider": "aws", "account_id": "123456789012", "name": "prod-main"},
    {"provider": "azure", "account_id": "sub-aaaa-bbbb", "name": "corp-subscription"},
    {"provider": "gcp", "account_id": "proj-payments", "name": "payments-prod"},
]
SYNTHETIC_ASSETS = [
    {"id": "aws-ec2-i-0abc", "name": "web-prod-1", "type": "host", "provider": "aws", "account_id": "123456789012", "internet_facing": True, "criticality": "high"},
    {"id": "aws-s3-public-logs", "name": "company-public-logs", "type": "storage", "provider": "aws", "account_id": "123456789012", "internet_facing": True, "criticality": "medium"},
    {"id": "aws-rds-prod", "name": "prod-db", "type": "host", "provider": "aws", "account_id": "123456789012", "internet_facing": False, "criticality": "critical"},
]

@mcp.tool()
def cloud_list_accounts(provider: str = "all") -> str:
    """List cloud accounts (synthetic)."""
    accounts = SYNTHETIC_ACCOUNTS if provider == "all" else [a for a in SYNTHETIC_ACCOUNTS if a["provider"] == provider]
    return json.dumps({"mode": MODE, "accounts": accounts}, indent=2)

@mcp.tool()
def cloud_inventory_assets(provider: str, account_id: str) -> str:
    """Collect assets for account (synthetic)."""
    assets = [a for a in SYNTHETIC_ASSETS if a["provider"] == provider and a["account_id"] == account_id]
    return json.dumps({"mode": MODE, "provider": provider, "account_id": account_id, "assets": assets}, indent=2)

@mcp.tool()
def cloud_internet_facing(provider: str, account_id: str) -> str:
    """Internet-facing assets (synthetic)."""
    facing = [a for a in SYNTHETIC_ASSETS if a["provider"] == provider and a["account_id"] == account_id and a["internet_facing"]]
    return json.dumps({"mode": MODE, "internet_facing": facing}, indent=2)

if __name__ == "__main__":
    mcp.run()
