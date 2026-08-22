#!/usr/bin/env python3
"""Anomaly detector MCP with optional Neo4j persistence (synthetic baselines work offline)."""
from __future__ import annotations
import json, math, os, time
from collections import defaultdict
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("anomaly-detector-mcp")
WINDOW = int(os.getenv("ANOMALY_WINDOW", "20"))
Z_THRESHOLD = float(os.getenv("ANOMALY_Z_THRESHOLD", "3.0"))
NEO4J_URI = os.getenv("ANOMALY_NEO4J_URI", "")
NEO4J_USER = os.getenv("ANOMALY_NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("ANOMALY_NEO4J_PASSWORD", "")
_baselines: dict[str, list[float]] = defaultdict(list)
_recent: list[dict] = []
_driver = None

def _driver():
    global _driver
    if not NEO4J_URI or not NEO4J_PASSWORD:
        return None
    if _driver is None:
        try:
            from neo4j import GraphDatabase
            _driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        except Exception:
            return None
    return _driver

def _zscore(values, current):
    if len(values) < 5:
        return 0.0
    mean = sum(values) / len(values)
    var = sum((x - mean) ** 2 for x in values) / len(values)
    std = math.sqrt(var) if var > 0 else 1e-6
    return abs(current - mean) / std

@mcp.tool()
def anomaly_seed_baseline(entity_id: str, metric: str, values: list[float]) -> str:
    """Seed baseline values for demos."""
    key = f"{entity_id}:{metric}"
    _baselines[key] = values[-WINDOW:]
    return json.dumps({"ok": True, "key": key, "n": len(_baselines[key])})

@mcp.tool()
def anomaly_observe(entity_id: str, metric: str, value: float, timestamp: float | None = None) -> str:
    """Record observation; flag anomaly by z-score. Optionally persists to Neo4j."""
    key = f"{entity_id}:{metric}"
    history = _baselines[key]
    z = _zscore(history, value)
    history.append(value)
    if len(history) > WINDOW:
        history.pop(0)
    is_anom = z >= Z_THRESHOLD
    record = {
        "entity_id": entity_id, "metric": metric, "value": value,
        "zscore": round(z, 3), "is_anomaly": is_anom,
        "observed_at": timestamp or time.time(),
        "persist_neo4j": bool(_driver()),
    }
    if is_anom:
        _recent.append(record)
        d = _driver()
        if d:
            try:
                with d.session() as s:
                    s.run(
                        "MERGE (n:Anomaly {id: $id}) SET n.entity_id=$entity_id, n.metric=$metric, n.value=$value, n.zscore=$zscore, n.observed_at=$observed_at",
                        id=f"anom-{entity_id}-{int(record['observed_at'])}",
                        entity_id=entity_id, metric=metric, value=value,
                        zscore=record["zscore"], observed_at=record["observed_at"],
                    )
            except Exception:
                pass
    return json.dumps(record, indent=2)

@mcp.tool()
def anomaly_list_recent(limit: int = 20) -> str:
    """List recent anomalies."""
    return json.dumps(_recent[-limit:], indent=2)

if __name__ == "__main__":
    mcp.run()
