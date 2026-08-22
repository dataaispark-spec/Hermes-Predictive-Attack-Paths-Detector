# SkandaShield Hermes Kit – Operations Guide

> **Full install / config / cloud deploy:** see **[INSTALL_AND_DEPLOY.md](./INSTALL_AND_DEPLOY.md)**  
> (Linux, macOS, WSL2, Docker, AWS, Azure, GCP, Kubernetes, customisation examples.)

This document covers day-to-day operation so core modules connect cleanly to the architecture.

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

## 1. Start the stack

```bash
cd deploy
docker compose -f docker-compose.yml -f docker-compose.opa.yml -f docker-compose.ui.yml up -d
```

Change default passwords first. Details: [INSTALL_AND_DEPLOY.md](./INSTALL_AND_DEPLOY.md).

## 2. Seed demo data

```bash
pip install neo4j
python scripts/seed_graph.py --uri bolt://localhost:7687 --user neo4j --password <password>
python scripts/mock_test_collectors.py
```

## 3. Wire MCP servers

Full YAML example: [INSTALL_AND_DEPLOY.md §5](./INSTALL_AND_DEPLOY.md) and `deploy/hermes-mcp-example.yaml`.

## 4. Create the five Bots

Copy each `bots/*/SOUL.md` into Hermes Bot profiles. Remediation stays propose-only (OPA enforces `human_approved`).

## 5. Policy engine (OPA)

- Policies: `policies/skandashield.rego`
- Tests: `bash scripts/run_rego_tests.sh`
- Gateway: `http://localhost:8080/authorize`

## 6. Grafana

http://localhost:3000 — dashboard **SkandaShield Attack Paths**.

## 7. Module map

| Module | Path | Role |
|--------|------|------|
| Asset / Identity | Bot + BloodHound + Cloud MCPs | Continuous visibility |
| Vuln triage | Vuln-Triage + Nuclei + ThreatMapper | Prioritisation |
| Attack-path synthesis | Attack-Path-Synthesizer + Neo4j | Predict, don’t just detect |
| Anomaly | anomaly-detector-mcp | Behavioural signals |
| External surface | external-surface-mcp | Exposure / look-alike |
| Remediation | Remediation-Guidance + OPA | Engineer-ready output |
| Policy | OPA + Gateway | Least privilege |
| UI | Grafana | Path tables |

## 8. Continuous sync (template)

Schedule Hermes routines or cron to call collectors, upsert Neo4j (via OPA), re-score paths.

## 9. Safety checklist

- Rotate passwords
- Nuclei allowlist = lab/staging
- OPA denies unapproved tickets
- `terminal.backend: docker`
- No public MCP/Neo4j exposure

## 10. Template vs production

Collectors default to **synthetic** data (offline demos). Set `*_MODE=live` and credentials when wiring real APIs. See INSTALL guide §8.
