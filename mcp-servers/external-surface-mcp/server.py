#!/usr/bin/env python3
"""External attack-surface MCP with synthetic ASM feed."""
from __future__ import annotations
import json, os
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("external-surface-mcp")
BRAND_DOMAINS = [d.strip() for d in os.getenv("BRAND_DOMAINS", "example.com,contoso.io").split(",") if d.strip()]
SYNTHETIC_EXPOSURES = [
    {"asset_id": "aws-ec2-i-0abc", "exposure_type": "open_port", "detail": "TCP/22 open to 0.0.0.0/0", "severity": "high"},
    {"asset_id": "aws-s3-public-logs", "exposure_type": "public_bucket", "detail": "S3 bucket allows public list", "severity": "high"},
    {"asset_id": "az-vm-app1", "exposure_type": "tls_weak", "detail": "TLS 1.0 enabled", "severity": "medium"},
]

def _lookalike(candidate: str, brand: str) -> float:
    c, b = candidate.lower(), brand.lower()
    if c == b: return 0.0
    if c.replace("0", "o").replace("1", "l") == b: return 0.85
    if abs(len(c) - len(b)) > 3: return 0.1
    common = sum(1 for ch in set(c) if ch in b)
    return min(0.95, common / max(len(b), 1) * 0.7)

@mcp.tool()
def surface_check_lookalikes(candidates: list[str], brands: list[str] | None = None) -> str:
    """Score look-alike / typosquat risk."""
    brands = brands or BRAND_DOMAINS
    results = []
    for cand in candidates:
        best = max((_lookalike(cand, b), b) for b in brands)
        results.append({
            "candidate": cand, "closest_brand": best[1], "score": round(best[0], 3),
            "risk": "high" if best[0] >= 0.7 else "medium" if best[0] >= 0.4 else "low",
        })
    return json.dumps(results, indent=2)

@mcp.tool()
def surface_internet_facing_summary(asset_ids: list[str] | None = None) -> str:
    """Synthetic ASM exposure feed."""
    ids = set(asset_ids or [])
    exposures = [e for e in SYNTHETIC_EXPOSURES if not ids or e["asset_id"] in ids]
    return json.dumps({"mode": "synthetic", "count": len(exposures), "exposures": exposures}, indent=2)

@mcp.tool()
def surface_register_exposure(asset_id: str, exposure_type: str, detail: str, severity: str = "medium") -> str:
    """Register an exposure finding."""
    return json.dumps({
        "id": f"exp-{asset_id}-{exposure_type}", "asset_id": asset_id,
        "type": exposure_type, "detail": detail, "severity": severity,
        "source": "external-surface-mcp",
    }, indent=2)

if __name__ == "__main__":
    mcp.run()
