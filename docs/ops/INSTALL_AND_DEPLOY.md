# Full Installation, Configuration, Customisation & Deployment Guide

Step-by-step for **Linux, macOS, WSL2, Docker, and cloud (AWS / Azure / GCP)**. Replace passwords and paths before production.

Full detail for Hermes/MCP/Neo4j/OPA remains as in prior revisions; this file includes the **Temporal** section at the end.

---

## 1–11. Core stack

Follow sections in the repository history / parallel docs:

1. Prerequisites (Docker Compose v2, Python 3.11+)
2. Install Hermes Agent
3. Clone kit + venv
4. `docker compose -f docker-compose.yml -f docker-compose.opa.yml -f docker-compose.ui.yml up -d`
5. Full `~/.hermes/config.yaml` (see `deploy/hermes-mcp-example.yaml`)
6. Create five Bots from `bots/*/SOUL.md`
7. `python scripts/seed_graph.py` + `mock_test_collectors.py`
8. Customisation (synthetic→live, Nuclei, OPA)
9. Cloud (AWS/Azure/GCP/K8s)
10. Troubleshooting table
11. Production checklist

One-shot local demo:

```bash
cd hermes-skandashield-bots
pip install mcp pydantic neo4j
cd deploy
docker compose -f docker-compose.yml -f docker-compose.opa.yml -f docker-compose.ui.yml up -d
cd ..
python scripts/seed_graph.py --password YourStrongPasswordHere
```

Day-to-day: [OPERATIONS.md](./OPERATIONS.md).

---

## 12. Temporal durable pipeline (optional)

Crash-safe **collect → path score → human approval → ticket**:

```bash
# Start Temporal + UI
cd deploy
docker compose -f docker-compose.temporal.yml up -d
# UI http://localhost:8088  |  gRPC localhost:7233

# Worker + demo (repo root)
cd ..
pip install -r temporal/requirements.txt
export PYTHONPATH=$(pwd)
python temporal/worker.py &npython temporal/scripts/start_pipeline.py --wait-hours 0.01
# Approve:
python temporal/scripts/signal_approve.py --workflow-id <id from output>
python temporal/scripts/query_status.py --workflow-id <id> --wait-result
```

Details: [../TEMPORAL.md](../TEMPORAL.md) and [../../temporal/README.md](../../temporal/README.md).

| Port | Service |
|------|---------|
| 7233 | Temporal frontend |
| 8088 | Temporal Web UI |
