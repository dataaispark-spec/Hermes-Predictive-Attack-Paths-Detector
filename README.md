# Hermes Predictive Attack Paths Detector

**Repository:** [https://github.com/dataaispark-spec/Hermes-Predictive-Attack-Paths-Detector](https://github.com/dataaispark-spec/Hermes-Predictive-Attack-Paths-Detector)  
**Version:** 1.3.1 · **License:** MIT  
**Former name:** `hermes-skandashield-bots` (same project, renamed for clarity)

Open-source **starter kit** to build an AI-assisted cybersecurity capability that answers:

> *How could an attacker — or a compromised AI agent — realistically reach our critical systems, and what should we fix first?*

It is inspired by the product direction of [SkandaShield](https://skandashield.com/platform) (**predict attack paths before they are walked**), but this repository is **not** the commercial SkandaShield product. It is a practical blueprint: specialised **Hermes** bots, a **Neo4j** knowledge graph, **MCP** tool adapters, **OPA** policy gates, optional **Temporal** workflows, and **MITRE ATT&CK / ATLAS** mapping — including **AI-agent and MCP tool-chain paths**.

---

## Table of contents

1. [What this project is](#what-this-project-is)
2. [What this project is not](#what-this-project-is-not)
3. [Who it is for](#who-it-is-for)
4. [How it works](#how-it-works)
5. [Specialist bots](#specialist-bots)
6. [AI-agent attack paths + MITRE](#ai-agent-attack-paths--mitre)
7. [Repository layout](#repository-layout)
8. [Quick start](#quick-start)
9. [Full stack demo (Docker)](#full-stack-demo-docker)
10. [Configuration & safety](#configuration--safety)
11. [Documentation index](#documentation-index)
12. [Roadmap](#roadmap)
13. [Related projects](#related-projects)
14. [License](#license)

---

## What this project is

| Capability | Description |
|------------|-------------|
| **Predictive attack paths** | Rank multi-hop paths (vulns + identity + reachability + **agents/tools**) instead of dumping another alert queue |
| **Specialist Hermes bots** | Separate SOUL personas (mapper, triage, path synthesis, agent-path detector, anomaly, remediation) |
| **Shared graph** | Neo4j model for assets, identities, findings, classic paths, **agents**, **AgentAttackPath**, **Technique** |
| **MCP adapters** | Nuclei, BloodHound (template), cloud inventory, ThreatMapper, external surface, **agent-path**, anomaly |
| **Governance** | OPA Rego default-deny + MCP policy gateway before high-impact actions |
| **Durable pipelines** | Optional Temporal `AttackPathPipeline` with human approval signal |
| **LLM routing** | Local-first probe + cybersecurity model preference (`llm-router/`) |
| **MITRE alignment** | Every modelled hop maps to **ATT&CK Enterprise** and, where relevant, **ATLAS** |

**Lab honesty:** Collectors and agent inventory ship as **synthetic / template** implementations so you can demo without production credentials. Wire live APIs when ready.

---

## What this project is not

- Not a replacement for **BloodHound CE**, **Wiz**, **XM Cyber**, **CrowdStrike APA**, or commercial CTEM
- Not a turnkey SOC or guaranteed production APA appliance
- Not live core-banking or live agent control-plane integration out of the box
- Not affiliated with or endorsed by SkandaShield as a product

Use it **beside** identity graphs and scanners: this kit is the **reasoning + policy + agent-path layer** you own.

---

## Who it is for

- **AppSec / CloudSec / Identity** teams exploring path-centric risk and agentic tooling risk  
- **Platform / SRE** engineers who want Neo4j + MCP + policy as code  
- **Security architects** designing open alternatives to closed “AI SOC” copilots  
- **Builders** learning Hermes Bot Mode, MCP, and ATT&CK-labelled path models  

---

## How it works

```
1. COLLECT   Cloud, identity, vulns, exposure, AI agents/MCP  → MCP tool servers
2. MAP       Assets, identities, findings, agents, tools      → Neo4j
3. ROUTE     Local LLM first (prefer cyber models)            → llm-router / Hermes
4. REASON    Specialist bots rank classic + agent paths       → SOUL.md bots
5. LABEL     Each hop → MITRE ATT&CK / ATLAS                  → mitre/
6. GOVERN    OPA default-deny + human approval                → policies / gateway
7. ACT       Remediation guidance; tickets only when allowed
8. SEE       Grafana / Cypher / bot chat                      → top paths to fix
```

**Classic path example:** Internet web → RCE finding → pivot → production DB.  
**Agent path example:** Prompt injection → MCP tool abuse → secrets read / ticket create.

---

## Specialist bots

| Bot | Directory | Mission |
|-----|-----------|---------|
| Asset & Identity Mapper | `bots/asset-identity-mapper/` | Discover and normalise assets & identities |
| Vulnerability Triage | `bots/vuln-triage/` | Deduplicate and prioritise findings |
| Attack-Path Synthesizer | `bots/attack-path-synthesizer/` | Rank multi-hop infra/identity paths (+ hybrid) |
| **Agent Attack-Path Detector** | `bots/agent-attack-path-detector/` | **AI agent / MCP / A2A paths** |
| Anomaly Detector | `bots/anomaly-detector/` | Behaviour vs baselines |
| Remediation Guidance | `bots/remediation-guidance/` | Engineer-ready fixes (propose-only under policy) |

Each bot is defined by a **`SOUL.md`** for Hermes Bot Mode.

---

## AI-agent attack paths + MITRE

Full guide: **[docs/AGENT_ATTACK_PATHS_AND_MITRE.md](docs/AGENT_ATTACK_PATHS_AND_MITRE.md)**

```bash
# Hop catalogue
python mitre/mapper.py --list-hops

# One hop → ATT&CK / ATLAS
python mitre/mapper.py --hop prompt_injection

# Template path
python mitre/mapper.py --path-template agent-path-prompt-to-secrets

# Rank synthetic agent paths (no Neo4j required)
python scripts/detect_agent_attack_paths.py
```

| Example path | ATT&CK (sample) | ATLAS (sample) |
|--------------|-----------------|----------------|
| Prompt → tool → secrets | T1059, T1048, T1567 | AML.T0051, AML.T0054 |
| Poisoned MCP → shell | T1195, T1059 | AML.T0010, AML.T0011 |
| RAG poison → malicious ticket | T1078, T1098 | AML.T0043, AML.T0051 |

Graph labels: `Agent`, `MCPServer`, `Tool`, `AgentAttackPath`, `Technique` — see `neo4j/schema.cypher` and `neo4j/agent_paths.cypher`.

---

## Repository layout

```
Hermes-Predictive-Attack-Paths-Detector/
├── README.md                 ← you are here
├── VERSION
├── bots/                     ← Hermes SOUL.md personas
├── mitre/                    ← ATT&CK / ATLAS mapping + mapper.py
├── mcp-servers/              ← tool adapters (incl. agent-path-mcp)
├── mcp-gateway/              ← OPA-backed authorize / proxy skeleton
├── neo4j/                    ← schema + Cypher examples
├── policies/                 ← Rego + data.json
├── deploy/                   ← Docker Compose overlays
├── llm-router/               ← local-first + cyber preference
├── temporal/                 ← durable AttackPathPipeline starter
├── scripts/                  ← seed, detect, mock collectors
├── ui/grafana/               ← path dashboard provisioning
├── docs/                     ← architecture, ops, MITRE, OPA, …
└── tests/rego/               ← policy tests
```

---

## Quick start

### Prerequisites

- Git, Python **3.11+**
- Optional: Docker / Docker Compose v2, Neo4j 5.x, Hermes Agent (Bot Mode)

### Clone (canonical URL)

```bash
git clone https://github.com/dataaispark-spec/Hermes-Predictive-Attack-Paths-Detector.git
cd Hermes-Predictive-Attack-Paths-Detector
```

### Offline agent-path + MITRE demo (fastest)

```bash
python mitre/mapper.py --list-hops
python scripts/detect_agent_attack_paths.py
python scripts/detect_agent_attack_paths.py --json
```

### With Neo4j

```bash
# Start Neo4j (Compose or existing instance), then:
pip install neo4j
python scripts/seed_graph.py --password '<neo4j-password>'
python scripts/detect_agent_attack_paths.py \
  --uri bolt://localhost:7687 --password '<neo4j-password>'
```

---

## Full stack demo (Docker)

```bash
cd deploy
# Edit default passwords in docker-compose*.yml before any shared environment
docker compose -f docker-compose.yml -f docker-compose.opa.yml -f docker-compose.ui.yml up -d
cd ..

pip install mcp pydantic neo4j
python scripts/seed_graph.py --password '<neo4j-password>'
python scripts/mock_test_collectors.py
python scripts/detect_agent_attack_paths.py --uri bolt://localhost:7687 --password '<neo4j-password>'
```

**Optional Temporal**

```bash
cd deploy && docker compose -f docker-compose.temporal.yml up -d && cd ..
pip install -r temporal/requirements.txt
export PYTHONPATH=$(pwd)
python temporal/worker.py
python temporal/scripts/start_pipeline.py --wait-hours 0.01
```

**Optional LiteLLM**

```bash
cd deploy && docker compose -f docker-compose.litellm.yml up -d
# http://127.0.0.1:4000
```

Install Hermes separately (official installer / Docker) and point Bot Mode at the `bots/*/SOUL.md` files and MCP servers under `deploy/hermes-mcp-example.yaml`.

---

## Configuration & safety

| Practice | Why |
|----------|-----|
| Rotate Compose default passwords | Lab defaults are not production secrets |
| Prefer `terminal.backend: docker` for Hermes | Contain tool execution |
| OPA **default-deny** + tool allow-lists | Bots must not freely create tickets or run destructive tools |
| Human approval / Temporal signal | High-impact actions stay gated |
| Treat logs, tickets, RAG as **hostile input** | Prompt-injection surface for agents |
| Keep Neo4j / data ports private | Graph holds sensitive topology |
| Prefer **local LLMs** for identity/graph context | Data residency and leakage control |

Rego: `policies/` · Gateway: `mcp-gateway/` · Ops: `docs/ops/`.

---

## Documentation index

| Document | Contents |
|----------|----------|
| **[docs/AGENT_ATTACK_PATHS_AND_MITRE.md](docs/AGENT_ATTACK_PATHS_AND_MITRE.md)** | AI-agent paths + ATT&CK/ATLAS |
| [docs/OVERVIEW.md](docs/OVERVIEW.md) | Plain-language purpose |
| [docs/HOW_WE_DIFFER.md](docs/HOW_WE_DIFFER.md) | vs VM, CTEM, CNAPP, path platforms |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Logical / physical design |
| [docs/LLM_ROUTER.md](docs/LLM_ROUTER.md) | Local-first + cyber LLM routing |
| [docs/OPA_INTEGRATION.md](docs/OPA_INTEGRATION.md) | Policy engine |
| [docs/TEMPORAL.md](docs/TEMPORAL.md) | Durable pipelines |
| [docs/NUCLEI_MCP.md](docs/NUCLEI_MCP.md) | Nuclei MCP hardening notes |
| [docs/COLLECTORS_AND_UI.md](docs/COLLECTORS_AND_UI.md) | Collectors + Grafana |
| [docs/ops/INSTALL_AND_DEPLOY.md](docs/ops/INSTALL_AND_DEPLOY.md) | Install paths |
| [docs/ops/OPERATIONS.md](docs/ops/OPERATIONS.md) | Day-2 operations |
| [temporal/README.md](temporal/README.md) | Temporal runbook |

---

## Roadmap

| Phase | Focus | Status |
|-------|--------|--------|
| P0 Foundation | Bots, Neo4j, Docker, OPA, synthetic MCP, Grafana | In repo |
| P1 Durable process | Temporal AttackPathPipeline + approval | In repo (starter) |
| P1b LLM router | Local-first, cyber preference | In repo |
| **P1c Agent paths + MITRE** | **Agent detector, mapper, schema** | **In repo (v1.3.x)** |
| P2 Live data | Real BloodHound / cloud / ThreatMapper / agent registries | Next |
| P3 Production hardening | Secrets, SSO, Neo4j HA, SIEM export | Planned |
| P4 Scale & UX | Richer path UI, continuous re-score | Planned |

---

## Related projects

| Project | Role |
|---------|------|
| [NousResearch Hermes Agent](https://github.com/NousResearch/hermes-agent) | Runtime for Bot Mode |
| [SpecterOps BloodHound](https://github.com/SpecterOps/BloodHound) | Identity attack-path gold standard (complement, not replace) |
| [dataaispark-spec/bfsi-agents-fraud-lab](https://github.com/dataaispark-spec/bfsi-agents-fraud-lab) | Sister multi-agent **BFSI fraud** lab |

**Rename note:** Older clones or docs may still say `hermes-skandashield-bots`. Use:

```text
https://github.com/dataaispark-spec/Hermes-Predictive-Attack-Paths-Detector
```

---

## License

MIT — see repository license file if present; otherwise treat contributions under MIT unless stated otherwise.
