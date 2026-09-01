#!/usr/bin/env python3
"""
Map attack-path hop types / free-text steps to MITRE ATT&CK + ATLAS IDs.

  python mitre/mapper.py --hop prompt_injection
  python mitre/mapper.py --text "agent shell tool reads secrets"
  python mitre/mapper.py --path-template agent-path-prompt-to-secrets
"""
from __future__ import annotations

import argparse
import json
import os
import re
from typing import Any, Dict, List

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP_PATH = os.path.join(ROOT, "mitre", "attck_mapping.json")


def load_mapping() -> Dict[str, Any]:
    with open(MAP_PATH, encoding="utf-8") as f:
        return json.load(f)


def map_hop(hop_type: str, data: Dict[str, Any] | None = None) -> Dict[str, Any]:
    data = data or load_mapping()
    hop = data["hop_types"].get(hop_type)
    if not hop:
        return {"hop_type": hop_type, "attck": [], "atlas": [], "name": "Unknown"}
    return {
        "hop_type": hop_type,
        "name": hop.get("name"),
        "attck": hop.get("attck", []),
        "atlas": hop.get("atlas", []),
        "notes": hop.get("notes", ""),
    }


def map_path_template(template_id: str, data: Dict[str, Any] | None = None) -> Dict[str, Any]:
    data = data or load_mapping()
    for t in data.get("agent_path_templates", []):
        if t["id"] == template_id:
            hops = [map_hop(h, data) for h in t["hops"]]
            attck = sorted({i for h in hops for i in h["attck"]})
            atlas = sorted({i for h in hops for i in h["atlas"]})
            return {
                "id": template_id,
                "description": t["description"],
                "hops": hops,
                "attck_ids": attck,
                "atlas_ids": atlas,
            }
    return {"id": template_id, "error": "unknown template"}


def map_text(text: str, data: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
    """Heuristic keyword → hop type matches."""
    data = data or load_mapping()
    text_l = text.lower()
    keywords = {
        "prompt_injection": ["prompt injection", "jailbreak", "ignore previous", "system prompt"],
        "tool_poisoning": ["poisoned tool", "malicious mcp", "supply chain"],
        "mcp_tool_abuse": ["mcp", "tool call", "tool abuse"],
        "command_execution": ["shell", "bash", "exec", "command"],
        "exfiltration": ["exfil", "secret", "exfiltrat", "data out"],
        "token_abuse": ["token", "api key", "oauth"],
        "rag_poisoning": ["rag", "vector store", "poisoned doc"],
        "ticket_or_change": ["jira", "servicenow", "ticket", "change request"],
        "valid_account": ["valid account", "stolen credential", "compromised user"],
        "public_exploit": ["rce", "public facing", "internet exploit"],
    }
    hits = []
    for hop, kws in keywords.items():
        if any(k in text_l for k in kws):
            hits.append(map_hop(hop, data))
    return hits


def format_ids(mapped: Dict[str, Any]) -> str:
    parts = []
    if mapped.get("attck"):
        parts.append("ATT&CK:" + ",".join(mapped["attck"]))
    if mapped.get("atlas"):
        parts.append("ATLAS:" + ",".join(mapped["atlas"]))
    return " ".join(parts) if parts else "(unmapped)"


def main() -> int:
    ap = argparse.ArgumentParser(description="MITRE ATT&CK / ATLAS hop mapper")
    ap.add_argument("--hop", help="Hop type key from attck_mapping.json")
    ap.add_argument("--text", help="Free text to heuristically map")
    ap.add_argument("--path-template", help="agent_path_templates id")
    ap.add_argument("--list-hops", action="store_true")
    args = ap.parse_args()
    data = load_mapping()

    if args.list_hops:
        for k, v in data["hop_types"].items():
            print(f"{k:24} attck={v.get('attck', [])} atlas={v.get('atlas', [])}  {v.get('name')}")
        return 0
    if args.hop:
        m = map_hop(args.hop, data)
        print(json.dumps(m, indent=2))
        return 0
    if args.path_template:
        print(json.dumps(map_path_template(args.path_template, data), indent=2))
        return 0
    if args.text:
        print(json.dumps(map_text(args.text, data), indent=2))
        return 0
    ap.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
