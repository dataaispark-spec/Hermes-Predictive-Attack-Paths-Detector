# Hermes SkandaShield Bots

Deployment kit for a **SkandaShield-style AI cybersecurity platform** using **Hermes Agent + Bot Mode** + **OPA** + optional **Temporal**.

## Documentation (start here)

| Doc | Content |
|-----|---------|
| **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** | End-to-end logical & physical architecture |
| **[docs/ops/INSTALL_AND_DEPLOY.md](docs/ops/INSTALL_AND_DEPLOY.md)** | Install/config: Linux, macOS, WSL2, AWS/Azure/GCP/K8s |
| **[docs/TEMPORAL.md](docs/TEMPORAL.md)** | Durable AttackPathPipeline (Temporal) |
| [temporal/README.md](temporal/README.md) | Temporal worker & scripts runbook |
| [docs/ops/OPERATIONS.md](docs/ops/OPERATIONS.md) | Day-to-day operations |
| [docs/OPA_INTEGRATION.md](docs/OPA_INTEGRATION.md) | OPA + policy gateway |
| [docs/GAP_CLOSURE.md](docs/GAP_CLOSURE.md) | Coverage vs SkandaShield platform |
| [docs/COLLECTORS_AND_UI.md](docs/COLLECTORS_AND_UI.md) | Collectors & Grafana |

## What you get

- 5 specialised Bot `SOUL.md` templates
- Neo4j schema + seed script + Grafana dashboards
- Hardened Nuclei MCP + synthetic BloodHound / cloud / ThreatMapper / anomaly / external-surface MCPs
- OPA policies + Rego tests + MCP Policy Gateway
- Docker Compose stack (Neo4j, OPA, Gateway, Grafana)
- **Temporal** starter: durable `AttackPathPipeline` + `human_approve` signal

## Quick Start (local demo)

```bash
git clone https://github.com/dataaispark-spec/hermes-skandashield-bots.git
cd hermes-skandashield-bots
# Edit passwords in deploy/docker-compose*.yml
cd deploy
docker compose -f docker-compose.yml -f docker-compose.opa.yml -f docker-compose.ui.yml up -d
cd ..
pip install mcp pydantic neo4j
python scripts/seed_graph.py --password <neo4j-password>
python scripts/mock_test_collectors.py
```

### Optional Temporal pipeline

```bash
cd deploy && docker compose -f docker-compose.temporal.yml up -d
cd .. && pip install -r temporal/requirements.txt
export PYTHONPATH=$(pwd)
python temporal/worker.py
python temporal/scripts/start_pipeline.py --wait-hours 0.01
python temporal/scripts/signal_approve.py --workflow-id <id>
# UI: http://localhost:8088
```

## Bots

| Bot | Purpose |
|-----|---------|
| `asset-identity-mapper` | Apps, cloud, identities |
| `vuln-triage` | Prioritise findings |
| `attack-path-synthesizer` | Rank multi-hop paths |
| `anomaly-detector` | Behavioural deviations |
| `remediation-guidance` | Engineer-ready guidance (OPA-gated) |

## Safety

- `terminal.backend: docker`
- MCP tool filtering + OPA default-deny
- Tickets require `human_approved: true`
- Rotate all default passwords before shared use

## License

MIT
