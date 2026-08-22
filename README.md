# Hermes SkandaShield Bots

**Open-source starter kit to build an AI-assisted cybersecurity platform** that finds *how* attackers could reach critical systems — not just more alerts — using specialist AI agents, a knowledge graph, and strong safety controls.

Inspired by the product direction of [SkandaShield](https://skandashield.com/platform): **predict attack paths before they are walked**, prioritise by real exploitability, and give engineers a short list of things worth fixing.

> Plain-language summary: **[docs/OVERVIEW.md](docs/OVERVIEW.md)**

---

## Purpose of this repository

Security teams are drowning in scanner output, cloud misconfigurations, and identity sprawl. Most tools report *what already went wrong* or *what is theoretically vulnerable*. They rarely answer:

> “If someone got a foothold *here*, what is the shortest realistic path to *our crown jewels* — and what should we fix first?”

This repository is a **practical blueprint and working templates** so your organisation can assemble that capability with:

- **Hermes Agent + Bot Mode** — a team of specialised AI bots (not one generic chatbot)
- **Neo4j** — a shared map of assets, identities, findings, and attack paths
- **MCP tool servers** — safe connectors to scanners, cloud inventory, identity graphs, etc.
- **OPA policies** — default-deny rules so bots cannot create tickets or run dangerous actions without approval
- **Optional Temporal** — durable pipelines that survive crashes and wait for human approval

It is **not** a full commercial product. It is an **enterprise-oriented kit**: architecture, configs, synthetic demos, and clear extension points so you can pilot in weeks and harden toward production.

---

## How it helps an organisation

| Challenge | How this kit helps |
|-----------|---------------------|
| Alert fatigue | Ranks **attack paths** and choke points instead of raw CVE volume |
| Siloed tools | Connects cloud, identity, and vuln data into **one graph** |
| Slow triage | Specialist bots draft prioritisation and **engineer-ready** remediation guidance |
| Risky automation | **OPA + human approval** before tickets or high-impact actions |
| Vendor lock-in | Open components (Hermes, Neo4j, OPA, MCP, Temporal) you control |
| “Where do we start?” | Docker Compose demo, seed data, and step-by-step install docs |

**Who benefits**

- **Security / AppSec / CloudSec** — clearer priorities and path-based risk
- **Platform / SRE** — integrations sit *beside* existing SIEM/scanners, not replace them overnight
- **Leadership** — measurable move from “more findings” to “fewer high-impact paths”
- **Builders** — a reference architecture for agentic security platforms

---

## How it works (simple view)

```
1. COLLECT   Cloud, identity, vulns, exposure  → MCP tool servers
2. MAP       Assets & identities & findings   → Neo4j knowledge graph
3. REASON    Specialist Hermes Bots rank paths and anomalies
4. GOVERN    OPA + policy gateway allow only safe / approved actions
5. ACT       Remediation guidance; tickets only after human approval
6. SEE       Grafana (and Bot chat) show top paths worth fixing
```

**The five bots**

| Bot | Job |
|-----|-----|
| Asset & Identity Mapper | Continuously discover apps, cloud, identities |
| Vulnerability Triage | Deduplicate and prioritise findings |
| Attack-Path Synthesizer | Build and score multi-hop attack paths |
| Anomaly Detector | Flag unusual behaviour vs baselines |
| Remediation Guidance | Propose fixes for engineers (policy-gated) |

Optional **Temporal** workflow runs a durable loop: collect → score path → wait for approval → create ticket — even if a process restarts mid-way.

---

## Benefits

1. **Path-centric risk** — Focus on chained weaknesses that reach sensitive systems, not only isolated CVEs.
2. **Specialist agents** — Clear roles (map, triage, path, anomaly, remediate) instead of one overloaded agent.
3. **Safety by design** — Default-deny policy, tool allow-lists, human approval for tickets, Docker sandbox for commands.
4. **Works with what you have** — MCP adapters plug into scanners, cloud APIs, identity tools, and ticketing over time.
5. **Demo in a day** — Synthetic collectors + seed graph + Grafana so you can show value before live integrations.
6. **Enterprise architecture** — Documented logical/physical design, install across Linux/macOS/WSL2/cloud, and ops guides.
7. **Auditable automation** — Gateway audit lines, OPA decisions, optional Temporal event history.
8. **Open and extensible** — MIT-licensed templates; swap synthetic mode for real APIs when ready.

---

## Roadmap

| Phase | Focus | Status |
|-------|--------|--------|
| **P0 — Foundation** | Hermes Bot personas, Neo4j schema, Docker stack, OPA + gateway, synthetic MCP collectors, seed data, Grafana, docs | **In repo** |
| **P1 — Durable process** | Temporal `AttackPathPipeline`, human approval signal, soft-fail Neo4j/Gateway activities | **In repo (starter)** |
| **P2 — Live data** | Real BloodHound CE / cloud SDK / ThreatMapper / ASM feeds behind existing MCP tool signatures | Next |
| **P3 — Production hardening** | Secret managers, SSO on UIs, Neo4j HA/Aura, OPA in CI, SIEM export of audits, stricter Nuclei isolation | Planned |
| **P4 — Scale & UX** | Full MCP authorize proxy, richer path visualisation UI, scheduled continuous re-score, multi-tenant patterns | Planned |
| **P5 — Ecosystem** | Optional A2A peers, deeper Hermes routines, LangGraph only where deterministic graphs help | Future |

We deliberately ship **working templates** first (synthetic offline demos + clear interfaces) so organisations can validate the *model* of work before connecting production credentials.

---

## What is in the box

- 5 specialised Bot `SOUL.md` templates
- Neo4j schema + seed script + Grafana dashboards
- Hardened Nuclei MCP + synthetic BloodHound / cloud / ThreatMapper / anomaly / external-surface MCPs
- OPA policies + Rego tests + MCP Policy Gateway
- Docker Compose (Neo4j, OPA, Gateway, Grafana)
- Temporal starter (`AttackPathPipeline` + approval signal)
- Architecture, install, and operations documentation

---

## Quick start (local demo)

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

Grafana: http://localhost:3000 · Full Hermes config: [docs/ops/INSTALL_AND_DEPLOY.md](docs/ops/INSTALL_AND_DEPLOY.md)

### Optional Temporal pipeline

```bash
cd deploy && docker compose -f docker-compose.temporal.yml up -d
cd .. && pip install -r temporal/requirements.txt && export PYTHONPATH=$(pwd)
python temporal/worker.py
python temporal/scripts/start_pipeline.py --wait-hours 0.01
python temporal/scripts/signal_approve.py --workflow-id <id>
# UI: http://localhost:8088
```

---

## Documentation

| Doc | Content |
|-----|---------|
| **[docs/OVERVIEW.md](docs/OVERVIEW.md)** | Plain-language purpose, value, roadmap |
| **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** | Logical & physical architecture |
| **[docs/ops/INSTALL_AND_DEPLOY.md](docs/ops/INSTALL_AND_DEPLOY.md)** | Install on Linux / macOS / WSL2 / cloud |
| **[docs/TEMPORAL.md](docs/TEMPORAL.md)** | Durable pipelines |
| [docs/ops/OPERATIONS.md](docs/ops/OPERATIONS.md) | Day-to-day operations |
| [docs/OPA_INTEGRATION.md](docs/OPA_INTEGRATION.md) | Policy engine |
| [docs/GAP_CLOSURE.md](docs/GAP_CLOSURE.md) | Mapping vs commercial platform ideas |
| [temporal/README.md](temporal/README.md) | Temporal runbook |

---

## Safety

- Prefer `terminal.backend: docker` in Hermes
- MCP tool filtering + OPA **default-deny**
- Tickets require `human_approved: true` (and/or Temporal approval signal)
- **Rotate all default passwords** before any shared or production use
- Keep Neo4j, OPA, and Temporal off the public internet

---

## License

MIT

---

*Built as an open reference implementation of path-first, agent-assisted cybersecurity operations — for teams that want to understand and own the design.*
