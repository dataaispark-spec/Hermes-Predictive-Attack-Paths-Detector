# AI agent attack paths + MITRE ATT&CK / ATLAS

**Repository:** [https://github.com/dataaispark-spec/Hermes-Predictive-Attack-Paths-Detector](https://github.com/dataaispark-spec/Hermes-Predictive-Attack-Paths-Detector)

## Goal

Extend predictive attack paths beyond hosts and identities to **AI agents**, **MCP tool servers**, and **agent-to-agent** trust — and **label every hop** with:

- **MITRE ATT&CK Enterprise**
- **MITRE ATLAS** (AI/ML-specific steps: prompt injection, poisoned tools/RAG, jailbreak)

## Components

| Path | Role |
|------|------|
| `bots/agent-attack-path-detector/SOUL.md` | Hermes Bot persona |
| `bots/attack-path-synthesizer/SOUL.md` | Hybrid + MITRE |
| `mitre/attck_mapping.json` | Hop types → ATT&CK/ATLAS + templates |
| `mitre/mapper.py` | CLI / library |
| `mcp-servers/agent-path-mcp/` | Synthetic inventory + scoring |
| `scripts/detect_agent_attack_paths.py` | Offline detector (+ optional Neo4j) |
| `neo4j/schema.cypher` | Agent / AgentAttackPath / Technique |
| `neo4j/agent_paths.cypher` | Example queries |

## Quick demo (no Neo4j)

```bash
git clone https://github.com/dataaispark-spec/Hermes-Predictive-Attack-Paths-Detector.git
cd Hermes-Predictive-Attack-Paths-Detector

python mitre/mapper.py --list-hops
python mitre/mapper.py --hop prompt_injection
python mitre/mapper.py --path-template agent-path-prompt-to-secrets
python scripts/detect_agent_attack_paths.py
```

Optional graph write:

```bash
python scripts/detect_agent_attack_paths.py \
  --uri bolt://localhost:7687 --password '<neo4j-password>'
```

## Design notes

- Synthetic by default; replace inventory in `agent-path-mcp` with live registries later  
- Treat tool output, tickets, and RAG as **hostile input**  
- Complements BloodHound identity graphs; does not replace them  
- Keep `mitre/attck_mapping.json` updated as ATLAS evolves  
