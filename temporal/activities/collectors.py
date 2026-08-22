"""Activities that simulate / call synthetic collectors and Neo4j upserts."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from temporalio import activity

SYNTHETIC_CLOUD_ASSETS = [
    {
        "id": "aws-ec2-i-0abc",
        "name": "web-prod-1",
        "type": "host",
        "provider": "aws",
        "account_id": "123456789012",
        "internet_facing": True,
        "criticality": "high",
    },
    {
        "id": "aws-rds-prod",
        "name": "prod-db",
        "type": "host",
        "provider": "aws",
        "account_id": "123456789012",
        "internet_facing": False,
        "criticality": "critical",
    },
]

SYNTHETIC_FINDINGS = [
    {
        "id": "tm-v-1",
        "cve": "CVE-2024-1234",
        "title": "RCE in web framework",
        "severity": "critical",
        "cvss": 9.8,
        "epss": 0.91,
        "node": "web-prod-1",
    },
]

SYNTHETIC_PATH = {
    "id": "path-wf-1",
    "score": 0.89,
    "nodes": ["web-prod-1", "api.example.com", "prod-db"],
    "description": "Internet RCE → API → database",
    "likelihood": 0.85,
    "impact": 0.95,
}


@activity.defn(name="collect_cloud_inventory")
async def collect_cloud_inventory(account_id: str) -> dict[str, Any]:
    """Synthetic cloud inventory for the given account."""
    activity.logger.info("collect_cloud_inventory account=%s", account_id)
    assets = [a for a in SYNTHETIC_CLOUD_ASSETS if a["account_id"] == account_id]
    if not assets:
        assets = SYNTHETIC_CLOUD_ASSETS
    return {
        "mode": "synthetic",
        "account_id": account_id,
        "assets": assets,
        "collected_at": datetime.now(timezone.utc).isoformat(),
    }


@activity.defn(name="collect_vulnerabilities")
async def collect_vulnerabilities(limit: int = 20) -> dict[str, Any]:
    """Synthetic vulnerability list (ThreatMapper-shaped)."""
    activity.logger.info("collect_vulnerabilities limit=%s", limit)
    return {"mode": "synthetic", "vulnerabilities": SYNTHETIC_FINDINGS[:limit]}


@activity.defn(name="synthesize_attack_paths")
async def synthesize_attack_paths(inventory: dict[str, Any], vulns: dict[str, Any]) -> dict[str, Any]:
    """Build ranked path records from inventory + vulns (synthetic)."""
    activity.logger.info(
        "synthesize_attack_paths assets=%s vulns=%s",
        len(inventory.get("assets") or []),
        len(vulns.get("vulnerabilities") or []),
    )
    path = dict(SYNTHETIC_PATH)
    path["source_account"] = inventory.get("account_id")
    path["finding_ids"] = [v["id"] for v in (vulns.get("vulnerabilities") or [])]
    return {"paths": [path]}


@activity.defn(name="upsert_neo4j_paths")
async def upsert_neo4j_paths(paths_payload: dict[str, Any]) -> dict[str, Any]:
    """Upsert AttackPath nodes into Neo4j. Soft-fails if Neo4j is unreachable."""
    from temporal.config import NEO4J_PASSWORD, NEO4J_URI, NEO4J_USER

    paths = paths_payload.get("paths") or []
    activity.logger.info("upsert_neo4j_paths n=%s uri=%s", len(paths), NEO4J_URI)
    written = 0
    try:
        from neo4j import GraphDatabase

        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        with driver.session() as session:
            for p in paths:
                session.run(
                    """
                    MERGE (ap:AttackPath {id: $id})
                    SET ap.score = $score,
                        ap.description = $description,
                        ap.likelihood = $likelihood,
                        ap.impact = $impact,
                        ap.nodes = $nodes,
                        ap.updated_at = datetime()
                    """,
                    id=p["id"],
                    score=p.get("score", 0.0),
                    description=p.get("description", ""),
                    likelihood=p.get("likelihood", 0.0),
                    impact=p.get("impact", 0.0),
                    nodes=p.get("nodes") or [],
                )
                written += 1
        driver.close()
        return {"ok": True, "written": written}
    except Exception as e:
        activity.logger.warning("Neo4j upsert skipped: %s", e)
        return {"ok": False, "written": 0, "error": str(e), "paths_json": json.dumps(paths)}


@activity.defn(name="authorize_ticket")
async def authorize_ticket(bot: str, human_approved: bool) -> dict[str, Any]:
    """Call MCP Gateway / OPA authorize for jira.create_issue. Fail-closed if gateway down."""
    import httpx
    from temporal.config import GATEWAY_URL

    payload = {
        "bot": bot,
        "tool": "jira.create_issue",
        "args": {},
        "context": {"human_approved": human_approved},
    }
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.post(f"{GATEWAY_URL.rstrip('/')}/authorize", json=payload)
            data = r.json() if r.content else {}
            allow = bool(data.get("allow", data.get("result", {}).get("allow", False)))
            return {"allow": allow, "raw": data, "source": "gateway"}
    except Exception as e:
        activity.logger.warning("Gateway unavailable: %s", e)
        return {"allow": False, "error": str(e), "source": "fail_closed"}


@activity.defn(name="create_ticket_stub")
async def create_ticket_stub(path: dict[str, Any], reason: str) -> dict[str, Any]:
    """Stub ticketing activity (no real Jira)."""
    tid = f"TICKET-{path.get('id', 'unknown')}"
    activity.logger.info("create_ticket_stub id=%s reason=%s", tid, reason)
    return {
        "ticket_id": tid,
        "title": f"Remediate attack path {path.get('id')}",
        "description": path.get("description"),
        "score": path.get("score"),
        "status": "created_stub",
    }
