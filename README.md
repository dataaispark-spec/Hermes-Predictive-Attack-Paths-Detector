# Hermes SkandaShield Bots - Predictive Attack Paths

**Open-source starter kit** for an AI-assisted cybersecurity platform that finds *how* attackers could reach critical systems — including **AI-agent / MCP tool-chain paths** — mapped to **MITRE ATT&CK** and **ATLAS**.

Inspired by [SkandaShield](https://skandashield.com/platform): **predict attack paths before they are walked**.

> **v1.3.0** — AI agent attack-path detection + MITRE mapping  
> Overview: [docs/OVERVIEW.md](docs/OVERVIEW.md) · Agent paths: **[docs/AGENT_ATTACK_PATHS_AND_MITRE.md](docs/AGENT_ATTACK_PATHS_AND_MITRE.md)**

---

## What is new (agent paths)

```bash
python mitre/mapper.py --list-hops
python scripts/detect_agent_attack_paths.py    # offline ranked paths + ATT&CK/ATLAS
```

| Bot | Role |
|-----|------|
| Asset & Identity Mapper | Apps, cloud, identities |
| Vulnerability Triage | Finding prioritisation |
| Attack-Path Synthesizer | Classic + hybrid paths |
| **Agent Attack-Path Detector** | **AI agent / MCP / A2A paths** |
| Anomaly Detector | Behaviour baselines |
| Remediation Guidance | Engineer-ready fixes (policy-gated) |

---

## Purpose

Answer: *“If someone influences this agent or foothold, what realistic path reaches our crown jewels — and what do we fix first?”*

Stack: **Hermes Bot Mode** · **Neo4j** · **MCP** · **OPA** · optional **Temporal** · **local-first LLM router**.

**Not** a full commercial product — enterprise-oriented kit (templates, synthetic demos, extension points).

---

## Quick start

```bash
git clone https://github.com/dataaispark-spec/hermes-skandashield-bots.git
cd hermes-skandashield-bots

# Agent paths + MITRE (no Docker required)
python mitre/mapper.py --path-template agent-path-prompt-to-secrets
python scripts/detect_agent_attack_paths.py

# Full stack demo
cd deploy
docker compose -f docker-compose.yml -f docker-compose.opa.yml -f docker-compose.ui.yml up -d
cd ..
pip install neo4j
python scripts/seed_graph.py --password <neo4j-password>
python scripts/detect_agent_attack_paths.py --uri bolt://localhost:7687 --password <neo4j-password>
```

---

## MITRE mapping

- Catalog: `mitre/attck_mapping.json` (hop types → ATT&CK + ATLAS)
- CLI: `mitre/mapper.py`
- Graph: `Technique` nodes linked from `AgentAttackPath` / `AttackPath`

Details: [docs/AGENT_ATTACK_PATHS_AND_MITRE.md](docs/AGENT_ATTACK_PATHS_AND_MITRE.md)

---

## Documentation

| Doc | Content |
|-----|---------|
| [AGENT_ATTACK_PATHS_AND_MITRE.md](docs/AGENT_ATTACK_PATHS_AND_MITRE.md) | **Agent paths + ATT&CK/ATLAS** |
| [OVERVIEW.md](docs/OVERVIEW.md) | Purpose & value |
| [HOW_WE_DIFFER.md](docs/HOW_WE_DIFFER.md) | vs VM, CTEM, CNAPP, path tools |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Architecture |
| [LLM_ROUTER.md](docs/LLM_ROUTER.md) | Local-first routing |
| [OPA_INTEGRATION.md](docs/OPA_INTEGRATION.md) | Policy |
| [TEMPORAL.md](docs/TEMPORAL.md) | Durable pipelines |

## License

MIT
