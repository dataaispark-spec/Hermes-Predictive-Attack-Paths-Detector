# Hermes SkandaShield Bots - Predictive Attack Paths Detection 

**Open-source starter kit to build an AI-assisted cybersecurity platform** that finds *how* attackers could reach critical systems — not just more alerts — using specialist AI agents, a knowledge graph, and strong safety controls.

Inspired by the product direction of [SkandaShield](https://skandashield.com/platform): **predict attack paths before they are walked**, prioritise by real exploitability, and give engineers a short list of things worth fixing.

> Plain-language summary: **[docs/OVERVIEW.md](docs/OVERVIEW.md)**  
> How we differ from other platforms: **[docs/HOW_WE_DIFFER.md](docs/HOW_WE_DIFFER.md)**  
> LLM routing (local-first + cyber models): **[docs/LLM_ROUTER.md](docs/LLM_ROUTER.md)**

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
- **Dynamic LLM router** — local models first, then next-best cloud; prefer cybersecurity-oriented LLMs when the task is security-related

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
| LLM cost / data residency | **Local-first** routing; cloud only when local is unavailable |
| “Where do we start?” | Docker Compose demo, seed data, and step-by-step install docs |

**Who benefits:** Security / AppSec / CloudSec · Platform / SRE · Leadership · Builders learning agentic security architecture.

---

## How it works (simple view)

```
1. COLLECT   Cloud, identity, vulns, exposure  → MCP tool servers
2. MAP       Assets & identities & findings   → Neo4j knowledge graph
3. ROUTE     Local LLM first (cyber models if security task) → else cloud
4. REASON    Specialist Hermes Bots rank paths and anomalies
5. GOVERN    OPA + policy gateway allow only safe / approved actions
6. ACT       Remediation guidance; tickets only after human approval
7. SEE       Grafana (and Bot chat) show top paths worth fixing
```

| Bot | Job |
|-----|-----|
| Asset & Identity Mapper | Continuously discover apps, cloud, identities |
| Vulnerability Triage | Deduplicate and prioritise findings |
| Attack-Path Synthesizer | Build and score multi-hop attack paths |
| Anomaly Detector | Flag unusual behaviour vs baselines |
| Remediation Guidance | Propose fixes for engineers (policy-gated) |

Optional **Temporal** workflow: collect → score path → wait for approval → ticket (survives restarts).

---

## Dynamic LLM router (local-first + cyber preference)

**Full guide:** [docs/LLM_ROUTER.md](docs/LLM_ROUTER.md)

| Priority | Backend | When used |
|----------|---------|-----------|
| 1 | **Ollama / vLLM / LM Studio** | Healthy local inference |
| 2 | **Cyber local models** (Foundation-Sec, SecGPT, …) | Security-related prompts |
| 3 | **LiteLLM proxy** (optional) | Unified gateway on your network |
| 4 | **OpenRouter / Anthropic / OpenAI** | Local unavailable or no local models |

Built on existing best practice:

- **Hermes** `fallback_providers` + `provider_routing` for runtime failover  
- **LiteLLM** as optional self-hosted multi-provider proxy  
- Thin **`llm-router/router.py`** for probe + cyber heuristic + Hermes snippet export  

```bash
python llm-router/router.py --prompt "Rank attack paths for this CVE"
python llm-router/router.py --prompt "attack path" --hermes   # paste into Hermes config
```

Merge [llm-router/hermes_local_first.yaml](llm-router/hermes_local_first.yaml) into `~/.hermes/config.yaml` for a ready local-first chain.

---

## How it is different from current platforms

**Full comparison:** **[docs/HOW_WE_DIFFER.md](docs/HOW_WE_DIFFER.md)**

| This kit | Typical commercial platforms |
|----------|------------------------------|
| **You own** agents, graph, policy, pipelines as code | **Vendor owns** the product |
| Specialist **Hermes bots** + **OPA default-deny** | Vendor AI copilots / closed workflows |
| **MCP** into *your* Neo4j | Connectors into *their* data plane |
| **Local-first LLM** with cyber model preference | Usually cloud-only copilots |
| MIT templates; pilot with synthetic data | Subscription SaaS day one |

Not a replacement for Tenable, Wiz, XM Cyber, BloodHound Enterprise, CyCognito, or Splunk/Sentinel — designed to work **beside** them.

---

## Benefits

1. **Path-centric risk** — Chained weaknesses to critical systems  
2. **Specialist agents** — Clear roles instead of one overloaded bot  
3. **Safety by design** — Default-deny policy, tool allow-lists, human approval  
4. **Works with what you have** — MCP adapters beside existing tools  
5. **Local-first AI** — Prefer on-prem LLMs; fall back to cloud intelligently  
6. **Cyber LLM preference** — Domain models when the task is security-related  
7. **Demo in a day** — Synthetic collectors + seed graph + Grafana  
8. **Open and extensible** — MIT; synthetic today, live APIs when ready  

---

## Roadmap

| Phase | Focus | Status |
|-------|--------|--------|
| **P0 — Foundation** | Bots, Neo4j, Docker, OPA, synthetic MCP, Grafana, docs | **In repo** |
| **P1 — Durable process** | Temporal AttackPathPipeline + approval signal | **In repo (starter)** |
| **P1b — LLM router** | Local-first probe, cyber preference, LiteLLM optional, Hermes export | **In repo** |
| **P2 — Live data** | Real BloodHound / cloud / ThreatMapper / ASM feeds | Next |
| **P3 — Production hardening** | Secrets, SSO, Neo4j HA, SIEM export, CI policy | Planned |
| **P4 — Scale & UX** | MCP proxy, richer path UI, continuous re-score | Planned |
| **P5 — Ecosystem** | Optional A2A, deeper routines, per-Bot auto model pin | Future |

---

## What is in the box

- 5 Bot `SOUL.md` templates · Neo4j schema + seed + Grafana  
- Hardened Nuclei MCP + synthetic collectors  
- OPA + MCP Policy Gateway · Temporal starter  
- **LLM router** (`llm-router/`) + optional LiteLLM Compose  
- Full documentation  

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
python llm-router/router.py --prompt "attack path CVE"   # optional model probe
```

### Optional Temporal

```bash
cd deploy && docker compose -f docker-compose.temporal.yml up -d
cd .. && pip install -r temporal/requirements.txt && export PYTHONPATH=$(pwd)
python temporal/worker.py
python temporal/scripts/start_pipeline.py --wait-hours 0.01
```

### Optional LiteLLM multi-provider proxy

```bash
cd deploy && docker compose -f docker-compose.litellm.yml up -d
# http://127.0.0.1:4000
```

---

## Documentation

| Doc | Content |
|-----|---------|
| **[docs/OVERVIEW.md](docs/OVERVIEW.md)** | Plain-language purpose & value |
| **[docs/HOW_WE_DIFFER.md](docs/HOW_WE_DIFFER.md)** | vs VM, CTEM, CNAPP, path, SIEM, BAS |
| **[docs/LLM_ROUTER.md](docs/LLM_ROUTER.md)** | **Local-first + cyber LLM routing** |
| **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** | Logical & physical architecture |
| **[docs/ops/INSTALL_AND_DEPLOY.md](docs/ops/INSTALL_AND_DEPLOY.md)** | Install (Linux / macOS / WSL2 / cloud) |
| **[docs/TEMPORAL.md](docs/TEMPORAL.md)** | Durable pipelines |
| [docs/ops/OPERATIONS.md](docs/ops/OPERATIONS.md) | Day-to-day operations |
| [docs/OPA_INTEGRATION.md](docs/OPA_INTEGRATION.md) | Policy engine |
| [temporal/README.md](temporal/README.md) | Temporal runbook |

---

## Safety

- Prefer `terminal.backend: docker`  
- MCP tool filtering + OPA **default-deny**  
- Tickets need `human_approved` / Temporal signal  
- Prefer **local LLMs** for sensitive graph/identity context  
- Rotate default passwords; keep data-plane ports private  

## License

MIT
