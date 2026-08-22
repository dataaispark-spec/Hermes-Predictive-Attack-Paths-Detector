# Temporal starter — AttackPathPipeline

Durable orchestration for the SkandaShield kit:

**collect → synthesize paths → Neo4j upsert → wait for human approval → OPA/gateway authorize → ticket stub**

Hermes Bots remain specialists; Temporal runs enterprise pipelines that must survive crashes and long approval waits.

## Prerequisites

- Docker Compose
- Python 3.11+
- Optional: Neo4j + MCP Gateway from the main stack (activities soft-fail if missing)

## 1. Start Temporal (dev)

```bash
cd deploy
docker compose -f docker-compose.temporal.yml up -d
# UI: http://localhost:8088
# Frontend gRPC: localhost:7233
```

## 2. Install Python deps

```bash
cd /path/to/hermes-skandashield-bots
python3 -m venv .venv && source .venv/bin/activate
pip install -r temporal/requirements.txt
```

## 3. Run the worker

```bash
export PYTHONPATH=$(pwd)
python temporal/worker.py
```

## 4. Start a pipeline

```bash
export PYTHONPATH=$(pwd)
python temporal/scripts/start_pipeline.py --account-id 123456789012 --wait-hours 0.01
```

## 5. Approve (human-in-the-loop)

```bash
python temporal/scripts/signal_approve.py --workflow-id <workflow_id>
python temporal/scripts/query_status.py --workflow-id <workflow_id> --wait-result
```

## Environment

| Variable | Default |
|----------|---------|
| `TEMPORAL_HOST` | `localhost:7233` |
| `TEMPORAL_TASK_QUEUE` | `skandashield-attack-path` |
| `NEO4J_URI` / `NEO4J_PASSWORD` | match main compose |
| `GATEWAY_URL` | `http://localhost:8080` |

## Architecture

See [docs/TEMPORAL.md](../docs/TEMPORAL.md) and [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md).
