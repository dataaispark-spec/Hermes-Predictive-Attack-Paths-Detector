# AI agent attack paths + MITRE ATT&CK / ATLAS

## Goal

Extend SkandaShield-style **predictive attack paths** beyond hosts and identities to **AI agents**, **MCP tool servers**, and **agent-to-agent** trust — and **label every hop** with:

- **MITRE ATT&CK Enterprise** (classic tactics/techniques)
- **MITRE ATLAS** where the step is AI/ML-specific (prompt injection, poisoned tools/RAG, jailbreak)

## Components (v1.3.0)

| Path | Role |
|------|------|
| `bots/agent-attack-path-detector/SOUL.md` | Hermes Bot persona |
| `bots/attack-path-synthesizer/SOUL.md` | Updated for hybrid + MITRE |
| `mitre/attck_mapping.json` | Hop types → ATT&CK/ATLAS IDs + path templates |
| `mitre/mapper.py` | CLI / library mapper |
| `mcp-servers/agent-path-mcp/` | Synthetic agent inventory + path scoring |
| `scripts/detect_agent_attack_paths.py` | Offline detector (+ optional Neo4j write) |
| `neo4j/schema.cypher` | `Agent`, `AgentAttackPath`, `Technique`, … |
| `neo4j/agent_paths.cypher` | Example Cypher |

## Quick demo (no Neo4j required)

```bash
cd hermes-skandashield-bots

# List hop → technique map
python mitre/mapper.py --list-hops

# Map one hop
python mitre/mapper.py --hop prompt_injection

# Full path template
python mitre/mapper.py --path-template agent-path-prompt-to-secrets

# Rank synthetic agent paths
python scripts/detect_agent_attack_paths.py
python scripts/detect_agent_attack_paths.py --json
```

Optional graph write:

```bash
python scripts/detect_agent_attack_paths.py \
  --uri bolt://localhost:7687 --password '<neo4j-password>'
```

## Example path (lab)

**agent-path-prompt-to-secrets** via Support Agent:

| Hop | ATT&CK | ATLAS |
|-----|--------|--------|
| prompt_injection | T1059 | AML.T0051, AML.T0054 |
| mcp_tool_abuse | T1059, T1106 | AML.T0051 |
| exfiltration | T1048, T1567 | — |

## Design notes

- **Synthetic by default** — same honesty as other collectors; wire live agent registries later.
- **Hostile input** — treat tool output, tickets, and RAG as injection surfaces (see SOUL rules).
- **Not a substitute for BloodHound** — complements identity graphs with an **agent tool-graph** layer.
- **ATLAS IDs** follow public MITRE ATLAS naming; keep `attck_mapping.json` updated as ATLAS evolves.

## Related

- Classic paths: Attack-Path Synthesizer Bot + `scripts/seed_graph.py`
- Policy: OPA still gates high-impact tools (tickets, shell write)
