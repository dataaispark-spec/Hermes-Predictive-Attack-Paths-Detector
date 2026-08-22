# Hermes SkandaShield Bots

Deployment kit for building a **SkandaShield-style AI-Enabled Cybersecurity Platform** using **Hermes Agent + Bot Mode** + **OPA policy engine**.

## What you get

- 5 specialised Bot `SOUL.md` templates
- Neo4j schema + Cypher examples + **seed script** for demos
- Hardened **Nuclei** MCP (rate limit, severity allow-list, audit)
- Working **anomaly detector** and **external surface / look-alike** MCP templates
- Collector MCP skeletons (BloodHound, cloud inventory, ThreatMapper)
- OPA policy engine + Rego unit tests
- MCP Policy Gateway (authorize + OTel)
- Grafana attack-path dashboards
- Full **operations guide**: [docs/ops/OPERATIONS.md](docs/ops/OPERATIONS.md)

## Quick Start

1. Install [Hermes Agent](https://hermes-agent.nousresearch.com/)
2. Clone this repo
3. Start stack:
   ```bash
   cd deploy
   docker compose -f docker-compose.yml -f docker-compose.opa.yml -f docker-compose.ui.yml up -d
   ```
4. Seed demo data:
   ```bash
   pip install neo4j
   python scripts/seed_graph.py --password <neo4j-password>
   ```
5. Copy `bots/*/SOUL.md` into Hermes Bot profiles
6. Wire MCP servers in `~/.hermes/config.yaml` (see ops guide)
7. Open Grafana http://localhost:3000 — dashboard **SkandaShield Attack Paths**

## Bots

| Bot | Purpose |
|-----|---------|
| `asset-identity-mapper` | Continuous discovery of applications, cloud assets, identities |
| `vuln-triage` | Ingest, deduplicate and prioritise vulnerability findings |
| `attack-path-synthesizer` | Build and rank multi-hop attack paths |
| `anomaly-detector` | Behavioural baseline learning and deviation detection |
| `remediation-guidance` | Engineer-ready guidance (OPA-gated human approval) |

## Documentation

| Doc | Content |
|-----|---------|
| [docs/ops/OPERATIONS.md](docs/ops/OPERATIONS.md) | **How to run and operate the full kit** |
| [docs/OPA_INTEGRATION.md](docs/OPA_INTEGRATION.md) | OPA + gateway setup |
| [docs/GAP_CLOSURE.md](docs/GAP_CLOSURE.md) | Gap status vs SkandaShield platform |
| [docs/COLLECTORS_AND_UI.md](docs/COLLECTORS_AND_UI.md) | Collectors and Grafana notes |

## Safety

- `terminal.backend: docker`
- MCP tool filtering + OPA default-deny
- Ticket creation requires `human_approved: true`
- Rotate all default passwords before shared use

## License

MIT
