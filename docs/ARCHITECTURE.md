# Architecture — Hermes Predictive Attack Paths Detector

**Canonical repo:** [https://github.com/dataaispark-spec/Hermes-Predictive-Attack-Paths-Detector](https://github.com/dataaispark-spec/Hermes-Predictive-Attack-Paths-Detector)

## Logical view

```
[Collectors / MCP servers]
        │
        ▼
[Neo4j knowledge graph]  ←── Assets, Identities, Findings,
        │                    Agents, MCPServers, Tools,
        │                    AttackPath, AgentAttackPath, Technique
        ▼
[Hermes specialist bots] ←── SOUL.md + tools via MCP (+ OPA gateway)
        │
        ├── Attack-Path Synthesizer (classic / hybrid)
        └── Agent Attack-Path Detector (agent / MCP / A2A)
        │
        ▼
[MITRE mapper]  ←── ATT&CK + ATLAS IDs on hops
        │
        ▼
[Policy] OPA default-deny → optional Temporal approval → remediation / tickets
        │
        ▼
[Observe] Grafana, Cypher, bot transcripts
```

## Physical view (lab Compose)

| Service | Role |
|---------|------|
| Neo4j | Graph store |
| OPA | Policy decisions |
| mcp-gateway | Authorize tool calls |
| Grafana | Path dashboards |
| Temporal (optional) | Durable pipeline + signals |
| LiteLLM (optional) | Multi-provider LLM proxy |
| Hermes (host or container) | Bot runtime |

## Data domains

1. **Infrastructure / identity** — classic attack paths  
2. **AI agents** — tools, MCP, privileges, exposure  
3. **Techniques** — shared MITRE nodes linked from both path types  

## Trust boundaries

- Untrusted: scanner text, ticket text, RAG chunks, user prompts  
- Trusted compute: policy engine, Neo4j ACLs, human approval gates  
- High impact: shell write, IAM change, ticket create — deny by default  

See also: `docs/AGENT_ATTACK_PATHS_AND_MITRE.md`, `docs/OPA_INTEGRATION.md`, `docs/TEMPORAL.md`.
