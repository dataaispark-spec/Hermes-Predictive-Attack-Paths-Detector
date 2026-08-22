#!/usr/bin/env python3
"""
Seed the Neo4j graph with sample Assets, Findings, Identities and AttackPaths
so demos and Grafana dashboards have data without live collectors.
Usage:
  python scripts/seed_graph.py --uri bolt://localhost:7687 --user neo4j --password <pw>
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone

try:
    from neo4j import GraphDatabase
except ImportError:
    raise SystemExit("pip install neo4j")


SAMPLE_ASSETS = [
    {"id": "asset-web-1", "name": "www.example.com", "type": "app", "internet_facing": True, "criticality": "high"},
    {"id": "asset-api-1", "name": "api.example.com", "type": "api", "internet_facing": True, "criticality": "critical"},
    {"id": "asset-db-1", "name": "prod-db-01", "type": "host", "internet_facing": False, "criticality": "critical"},
    {"id": "asset-k8s-1", "name": "payments-svc", "type": "k8s", "internet_facing": False, "criticality": "high"},
]

SAMPLE_FINDINGS = [
    {"id": "find-cve-1", "cve": "CVE-2024-1234", "title": "RCE in web framework", "severity": "critical", "cvss": 9.8, "epss": 0.92, "kev": True},
    {"id": "find-misconfig-1", "cve": None, "title": "Public S3 bucket", "severity": "high", "cvss": 7.5, "epss": 0.4, "kev": False},
    {"id": "find-cve-2", "cve": "CVE-2023-5678", "title": "Privilege escalation", "severity": "high", "cvss": 8.1, "epss": 0.65, "kev": True},
]

SAMPLE_PATHS = [
    {
        "id": "path-1",
        "score": 0.91,
        "likelihood": 0.85,
        "impact": 0.95,
        "description": "Internet web \u2192 RCE \u2192 pivot to api \u2192 reach prod-db",
        "start": "asset-web-1",
        "end": "asset-db-1",
    },
    {
        "id": "path-2",
        "score": 0.78,
        "likelihood": 0.7,
        "impact": 0.8,
        "description": "Public bucket \u2192 credential leak \u2192 k8s service account",
        "start": "asset-api-1",
        "end": "asset-k8s-1",
    },
]


def seed(uri: str, user: str, password: str) -> None:
    driver = GraphDatabase.driver(uri, auth=(user, password))
    now = datetime.now(timezone.utc).isoformat()
    with driver.session() as session:
        for a in SAMPLE_ASSETS:
            session.run(
                """
                MERGE (x:Asset {id: $id})
                SET x.name = $name, x.type = $type, x.internet_facing = $internet_facing,
                    x.criticality = $criticality, x.last_seen = $now, x.source = 'seed'
                ON CREATE SET x.first_seen = $now
                """,
                **a, now=now,
            )
        for f in SAMPLE_FINDINGS:
            session.run(
                """
                MERGE (f:Finding {id: $id})
                SET f.cve = $cve, f.title = $title, f.severity = $severity,
                    f.cvss = $cvss, f.epss = $epss, f.kev = $kev, f.status = 'open', f.last_seen = $now
                ON CREATE SET f.first_seen = $now
                """,
                **f, now=now,
            )
        session.run(
            "MATCH (a:Asset {id:'asset-web-1'}), (f:Finding {id:'find-cve-1'}) MERGE (a)-[:HAS_VULN]->(f)"
        )
        session.run(
            "MATCH (a:Asset {id:'asset-api-1'}), (f:Finding {id:'find-misconfig-1'}) MERGE (a)-[:HAS_VULN]->(f)"
        )
        session.run(
            "MATCH (a:Asset {id:'asset-k8s-1'}), (f:Finding {id:'find-cve-2'}) MERGE (a)-[:HAS_VULN]->(f)"
        )
        for p in SAMPLE_PATHS:
            session.run(
                """
                MERGE (path:AttackPath {id: $id})
                SET path.score = $score, path.likelihood = $likelihood, path.impact = $impact,
                    path.description = $description, path.status = 'open', path.created_at = $now
                WITH path
                MATCH (s:Asset {id: $start}), (e:Asset {id: $end})
                MERGE (path)-[:STARTS_AT]->(s)
                MERGE (path)-[:ENDS_AT]->(e)
                """,
                **p, now=now,
            )
        print("Seed complete: assets, findings, paths written.")
    driver.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--uri", default="bolt://localhost:7687")
    ap.add_argument("--user", default="neo4j")
    ap.add_argument("--password", required=True)
    args = ap.parse_args()
    seed(args.uri, args.user, args.password)
