#!/usr/bin/env python3
"""
LLM-first slim profile demo (brainstorm branch).

Grounded path hypotheses from file inventory + critic (evidence_id required).
Uses mitre/mapper.py when present; otherwise prints hop_hint only.

  python profiles/llm-first-slim/run_slim_demo.py
  python profiles/llm-first-slim/run_slim_demo.py --json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, List

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROFILE = os.path.dirname(os.path.abspath(__file__))
INV_PATH = os.path.join(PROFILE, "inventory.sample.json")

sys.path.insert(0, ROOT)


def load_inventory(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def try_map_hop(hop_hint: str | None) -> Dict[str, Any]:
    if not hop_hint:
        return {}
    try:
        from mitre.mapper import map_hop

        return map_hop(hop_hint)
    except Exception:
        return {"hop_type": hop_hint, "attck": [], "atlas": [], "name": hop_hint}


def critic_accept_edge(edge: Dict[str, Any]) -> bool:
    """Reject ungrounded edges — core slim-profile safety rule."""
    eid = edge.get("evidence_id")
    return bool(eid and str(eid).strip())


def build_paths(inv: Dict[str, Any]) -> List[Dict[str, Any]]:
    by_id = {a["id"]: a for a in inv.get("assets", [])}
    by_id.update({a["id"]: a for a in inv.get("agents", [])})
    paths: List[Dict[str, Any]] = []

    for edge in inv.get("edges", []):
        if not critic_accept_edge(edge):
            continue
        src = by_id.get(edge["from"], {"id": edge["from"]})
        dst = by_id.get(edge["to"], {"id": edge["to"]})
        hop = try_map_hop(edge.get("hop_hint"))
        # Simple score: prefer paths ending at critical + agent exposure
        impact = 0.9 if dst.get("criticality") == "critical" else 0.5
        if src.get("internet_facing") or src.get("privileges") in ("high", "critical", "medium"):
            impact = min(0.99, impact + 0.05)
        score = round(0.55 + impact * 0.4, 3)
        paths.append(
            {
                "path_id": f"slim:{edge['from']}->{edge['to']}",
                "from": edge["from"],
                "to": edge["to"],
                "edge_type": edge.get("type"),
                "evidence_id": edge.get("evidence_id"),
                "score": score,
                "mitre": hop,
                "status": "proposed",
                "action": "propose_only",
            }
        )

    # Multi-hop classic: web -> api -> db if both edges exist with evidence
    e1 = next(
        (
            e
            for e in inv.get("edges", [])
            if e.get("from") == "asset-web-1"
            and e.get("to") == "asset-api-1"
            and critic_accept_edge(e)
        ),
        None,
    )
    e2 = next(
        (
            e
            for e in inv.get("edges", [])
            if e.get("from") == "asset-api-1"
            and e.get("to") == "asset-db-1"
            and critic_accept_edge(e)
        ),
        None,
    )
    if e1 and e2:
        paths.append(
            {
                "path_id": "slim:web->api->db",
                "hops": [e1["from"], e1["to"], e2["to"]],
                "evidence_ids": [e1["evidence_id"], e2["evidence_id"]],
                "score": 0.91,
                "description": "Internet web → api → prod-db (evidence-grounded)",
                "status": "proposed",
                "action": "propose_only",
            }
        )

    paths.sort(key=lambda p: p.get("score", 0), reverse=True)
    return paths


def main() -> int:
    ap = argparse.ArgumentParser(description="LLM-first slim profile demo")
    ap.add_argument("--inventory", default=INV_PATH)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    inv = load_inventory(args.inventory)
    paths = build_paths(inv)

    # Demonstrate critic rejecting a poisoned edge without evidence
    rejected = {"from": "attacker", "to": "asset-db-1", "evidence_id": ""}
    assert critic_accept_edge(rejected) is False

    if args.json:
        print(json.dumps({"paths": paths, "profile": "llm-first-slim"}, indent=2))
        return 0

    print("=" * 60)
    print(" LLM-first slim profile — grounded paths (propose-only)")
    print("=" * 60)
    for i, p in enumerate(paths, 1):
        print(f"\n#{i} score={p.get('score')}  {p.get('path_id')}")
        if p.get("description"):
            print(f"  {p['description']}")
        if p.get("evidence_id"):
            print(f"  evidence: {p['evidence_id']}")
        if p.get("evidence_ids"):
            print(f"  evidence: {', '.join(p['evidence_ids'])}")
        m = p.get("mitre") or {}
        if m:
            att = ",".join(m.get("attck") or []) or "-"
            atl = ",".join(m.get("atlas") or []) or "-"
            print(f"  MITRE ATT&CK: {att}  ATLAS: {atl}")
        print(f"  action: {p.get('action')}")
    print("\nCritic: edges without evidence_id are rejected.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
