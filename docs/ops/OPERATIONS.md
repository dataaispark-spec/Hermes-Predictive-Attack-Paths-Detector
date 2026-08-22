# SkandaShield Hermes Kit – Operations Guide

This document explains how to run, configure, and operate the full kit so that core modules connect cleanly to the overall architecture.

## Architecture reminder

```
Collectors (BloodHound, Cloud, ThreatMapper, Nuclei, External Surface, Anomaly)
        | MCP
        v
Hermes Bots (5 specialists)  --authorize-->  MCP Gateway  -->  OPA
        |                                         |
        |                                         v (allow only)
        +--------------> Neo4j <------------------+
                              |
                              v
                         Grafana UI
```

## 1. Prerequisites

- Docker + Docker Compose v2
- Python 3.11+ (for local MCP servers and seed script)
- Optional: `opa` CLI (for Rego tests), `nuclei` binary (for real scans)
- Hermes Agent installed (see main README)

## 2. Start the stack

```bash
cd deploy
# Base (Neo4j + Hermes gateway)
docker compose up -d

# Policy engine
docker compose -f docker-compose.yml -f docker-compose.opa.yml up -d

# Visualisation
docker compose -f docker-compose.yml -f docker-compose.opa.yml -f docker-compose.ui.yml up -d
```

**Change default passwords** in `docker-compose.yml` and Grafana before any shared use.

## 3. Seed demo data

```bash
pip install neo4j
python scripts/seed_graph.py --uri bolt://localhost:7687 --user neo4j --password <your-password>
```

This populates Assets, Findings, and AttackPaths so Grafana and Bot reasoning demos work immediately.

## 4. Wire MCP servers into Hermes

Edit `~/.hermes/config.yaml` (example fragment also in `deploy/hermes-mcp-example.yaml`).

Key servers:

- neo4j (graph read/write)
- nuclei (hardened scan)
- anomaly (statistical detector)
- external_surface (look-alike + exposure)
- bloodhound, cloud_inventory, threatmapper (collector skeletons)

See full YAML examples in the repository docs and `deploy/hermes-mcp-example.yaml`.

Install per-server requirements with `pip install -r mcp-servers/<name>/requirements.txt`.

## 5. Create the five Bots

Copy each `bots/*/SOUL.md` into the corresponding Hermes Bot profile.  
Keep Remediation Guidance in propose-only mode; OPA blocks ticket creation until `human_approved: true`.

## 6. Policy engine (OPA)

- Policies: `policies/skandashield.rego`
- Unit tests: `tests/rego/skandashield_test.rego`
- Run tests: `bash scripts/run_rego_tests.sh`

Gateway: `http://localhost:8080/authorize`

## 7. Grafana

- URL: http://localhost:3000
- Dashboard: “SkandaShield Attack Paths”
- Match Neo4j datasource password to your instance.

## 8. Module map (core templates)

| Module | Path | Role |
|--------|------|------|
| Asset / Identity mapping | Bot SOUL + BloodHound + Cloud MCPs | Continuous visibility |
| Vuln triage | Vuln-Triage Bot + Nuclei + ThreatMapper | Prioritisation |
| Attack-path synthesis | Attack-Path-Synthesizer + Neo4j Cypher | Predict, don’t just detect |
| Anomaly detection | Anomaly-Detector Bot + anomaly-detector-mcp | Behavioural signals |
| External surface | external-surface-mcp | Exposure / look-alike |
| Remediation | Remediation-Guidance Bot + OPA gate | Engineer-ready output |
| Policy | OPA + MCP Gateway | Least privilege |
| Visualisation | Grafana | Attack-path tables |
| Seed / demo | scripts/seed_graph.py | Immediate demo data |

## 9. Continuous sync (template)

Schedule Hermes routines or cron to call collector tools and upsert into Neo4j (subject to OPA), then re-score paths.

## 10. Safety checklist

- Rotate all default passwords
- Restrict Nuclei allowlist to lab/staging
- Confirm OPA denies unapproved tickets
- Run Rego tests
- Keep `terminal.backend: docker`
- Do not expose MCP ports publicly without auth

## 11. Template vs production

| Component | State |
|-----------|--------|
| Nuclei MCP | Hardened template (rate limit, severity, audit) |
| Anomaly MCP | Working statistical template |
| External surface MCP | Working look-alike heuristic template |
| BloodHound / Cloud / ThreatMapper | API-shaped skeletons – replace with real SDK calls |
| Seed script | Fully working for demos |
| OPA + tests | Working |
| Grafana | Working with seeded data |

## 12. Next engineering steps

1. Real BloodHound CE / cloud SDK / ThreatMapper clients inside existing tool signatures.
2. Persist anomaly baselines in Neo4j.
3. Point OTel at a real collector.
4. Optional LangGraph coordinator for deterministic loops.
