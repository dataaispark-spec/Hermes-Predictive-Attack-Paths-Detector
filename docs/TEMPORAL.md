# Temporal Integration — SkandaShield Kit

## Role

[Temporal](https://temporal.io) provides **durable execution** for multi-step security pipelines that must survive crashes, retry individual steps, wait for human approval, and leave an event-history audit trail.

It does **not** replace Hermes Bot Mode or OPA. It orchestrates **processes around** them.

## Components in this repo

| Path | Purpose |
|------|---------|
| `deploy/docker-compose.temporal.yml` | Postgres + Temporal + UI |
| `temporal/workflows/attack_path_pipeline.py` | `AttackPathPipeline` |
| `temporal/activities/collectors.py` | Synthetic collect / Neo4j / authorize / ticket |
| `temporal/worker.py` | Worker process |
| `temporal/scripts/*` | Start / signal / query |
| `temporal/README.md` | Quick runbook |

## Pipeline logic

```
collect_cloud_inventory(account_id)
collect_vulnerabilities()
synthesize_attack_paths(inventory, vulns)
upsert_neo4j_paths(paths)
if score < 0.5 → skip
wait_condition(human_approve)
authorize_ticket(...)  # Gateway/OPA fail-closed
create_ticket_stub(path)
```

## Quick start

```bash
cd deploy && docker compose -f docker-compose.temporal.yml up -d
cd .. && pip install -r temporal/requirements.txt
export PYTHONPATH=$(pwd)
python temporal/worker.py
python temporal/scripts/start_pipeline.py --wait-hours 0.01
python temporal/scripts/signal_approve.py --workflow-id <id>
```

UI: http://localhost:8088

## Hybrid with Hermes

| Concern | System |
|---------|--------|
| Specialist reasoning, chat, MCP | Hermes Bots |
| Policy allow/deny | OPA + MCP Gateway |
| Graph system of record | Neo4j |
| Long-running collect→score→approve→ticket | **Temporal** |

## Production notes

- Temporal Cloud or HA self-hosted cluster
- Deterministic Workflow code + versioning
- Secrets via env / secret manager
- Ship history/metrics to enterprise observability
