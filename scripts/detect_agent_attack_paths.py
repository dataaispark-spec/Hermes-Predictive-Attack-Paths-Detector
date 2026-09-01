#!/usr/bin/env python3
"""
Detect and rank AI-agent attack paths; map hops to MITRE ATT&CK / ATLAS.
Runs fully offline (synthetic inventory). Optional Neo4j write if credentials given.

  python scripts/detect_agent_attack_paths.py
  python scripts/detect_agent_attack_paths.py --json
  python scripts/detect_agent_attack_paths.py --uri bolt://localhost:7687 --password <pw>
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "mcp-servers", "agent-path-mcp"))

from server import detect_paths, list_agents, list_mcp_servers  # type: ignore  # noqa: E402


def print_report(paths: list) -> None:
    print("=" * 64)
    print(" AI-agent attack paths (synthetic lab) + MITRE mapping")
    print("=" * 64)
    for i, p in enumerate(paths, 1):
        m = p.get("mitre") or {}
        print(f"\n#{i} score={p['score']}  {p['path_id']}")
        print(f"  agent: {p['agent']['name']} ({p['agent']['privileges']})")
        print(f"  {p.get('description')}")
        print(f"  ATT&CK: {', '.join(m.get('attck_ids') or []) or '-'}")
        print(f"  ATLAS:  {', '.join(m.get('atlas_ids') or []) or '-'}")
        for h in m.get("hops") or []:
            ids = ",".join((h.get("attck") or []) + (h.get("atlas") or []))
            print(f"    - {h.get('hop_type')}: {h.get('name')} [{ids}]")
    print("\n" + "=" * 64)


def write_neo4j(uri: str, user: str, password: str, paths: list) -> None:
    try:
        from neo4j import GraphDatabase
    except ImportError:
        raise SystemExit("pip install neo4j")
    driver = GraphDatabase.driver(uri, auth=(user, password))
    now = datetime.now(timezone.utc).isoformat()
    with driver.session() as session:
        for a in list_agents():
            session.run(
                """
                MERGE (ag:Agent {id: $id})
                SET ag.name = $name, ag.exposure = $exposure, ag.privileges = $privileges,
                    ag.internet_facing = $internet_facing, ag.tools = $tools, ag.last_seen = $now
                """,
                id=a["id"],
                name=a["name"],
                exposure=a["exposure"],
                privileges=a["privileges"],
                internet_facing=a["internet_facing"],
                tools=a["tools"],
                now=now,
            )
        for p in paths:
            m = p.get("mitre") or {}
            session.run(
                """
                MERGE (ap:AgentAttackPath {id: $id})
                SET ap.score = $score, ap.likelihood = $likelihood, ap.impact = $impact,
                    ap.description = $description, ap.status = 'open', ap.domain = 'ai_agent',
                    ap.attck_ids = $attck, ap.atlas_ids = $atlas, ap.created_at = $now
                WITH ap
                MATCH (ag:Agent {id: $agent_id})
                MERGE (ap)-[:INVOLVES_AGENT]->(ag)
                """,
                id=p["path_id"],
                score=p["score"],
                likelihood=p["likelihood"],
                impact=p["impact"],
                description=p.get("description") or "",
                attck=m.get("attck_ids") or [],
                atlas=m.get("atlas_ids") or [],
                agent_id=p["agent"]["id"],
                now=now,
            )
            for tech in (m.get("attck_ids") or []) + (m.get("atlas_ids") or []):
                session.run(
                    """
                    MERGE (t:Technique {id: $tid})
                    SET t.framework = CASE WHEN $tid STARTS WITH 'AML' THEN 'ATLAS' ELSE 'ATT&CK' END
                    WITH t
                    MATCH (ap:AgentAttackPath {id: $pid})
                    MERGE (ap)-[:USES_TECHNIQUE]->(t)
                    """,
                    tid=tech,
                    pid=p["path_id"],
                )
        print("Neo4j: agents + AgentAttackPath + Technique links written.")
    driver.close()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--uri", default=os.getenv("NEO4J_URI", ""))
    ap.add_argument("--user", default=os.getenv("NEO4J_USER", "neo4j"))
    ap.add_argument("--password", default=os.getenv("NEO4J_PASSWORD", ""))
    args = ap.parse_args()

    paths = detect_paths()
    if args.json:
        print(json.dumps({"agents": list_agents(), "mcp": list_mcp_servers(), "paths": paths}, indent=2))
    else:
        print_report(paths)

    if args.uri and args.password:
        write_neo4j(args.uri, args.user, args.password, paths)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
