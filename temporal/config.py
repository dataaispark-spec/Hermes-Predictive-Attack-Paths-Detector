"""Shared settings for Temporal workers (env-overridable)."""
from __future__ import annotations

import os

TEMPORAL_HOST = os.getenv("TEMPORAL_HOST", "localhost:7233")
TASK_QUEUE = os.getenv("TEMPORAL_TASK_QUEUE", "skandashield-attack-path")

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "skandashield-change-me")

OPA_URL = os.getenv("OPA_URL", "http://localhost:8181")
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8080")

COLLECTOR_MODE = os.getenv("COLLECTOR_MODE", "synthetic")
