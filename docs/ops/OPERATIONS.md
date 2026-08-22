# SkandaShield Hermes Kit – Operations Guide

> **Full install / config / cloud deploy:** [INSTALL_AND_DEPLOY.md](./INSTALL_AND_DEPLOY.md)  
> **Architecture:** [../ARCHITECTURE.md](../ARCHITECTURE.md)  
> **Temporal pipelines:** [../TEMPORAL.md](../TEMPORAL.md)

## Architecture reminder

```
Collectors (MCP) → Hermes Bots → MCP Gateway → OPA
                 ↘     Neo4j     ↙
                      Grafana
Optional: Temporal AttackPathPipeline (durable approve → ticket)
```

## 1. Start core stack

```bash
cd deploy
docker compose -f docker-compose.yml -f docker-compose.opa.yml -f docker-compose.ui.yml up -d
```

## 2. Seed + mock tests

```bash
python scripts/seed_graph.py --password <password>
python scripts/mock_test_collectors.py
```

## 3. MCP + Bots

Wire `~/.hermes/config.yaml` from `deploy/hermes-mcp-example.yaml`.  
Load `bots/*/SOUL.md` into Hermes profiles.

## 4. OPA

`bash scripts/run_rego_tests.sh` · Gateway `http://localhost:8080/authorize`

## 5. Grafana

http://localhost:3000 — **SkandaShield Attack Paths**

## 6. Temporal (optional)

```bash
docker compose -f deploy/docker-compose.temporal.yml up -d
export PYTHONPATH=$(pwd)
python temporal/worker.py
python temporal/scripts/start_pipeline.py --wait-hours 0.01
python temporal/scripts/signal_approve.py --workflow-id <id>
```

UI: http://localhost:8088

## 7. Module map

| Module | Path |
|--------|------|
| Collectors | `mcp-servers/*` |
| Bots | `bots/*/SOUL.md` |
| Policy | `policies/skandashield.rego` |
| Graph | Neo4j + `scripts/seed_graph.py` |
| Durable pipeline | `temporal/` |

## 8. Safety

Rotate passwords · Nuclei allowlist · OPA deny unapproved tickets · `terminal.backend: docker`
