# Collectors and UI

**Repo:** [https://github.com/dataaispark-spec/Hermes-Predictive-Attack-Paths-Detector](https://github.com/dataaispark-spec/Hermes-Predictive-Attack-Paths-Detector)

## MCP collectors (`mcp-servers/`)

| Server | Role |
|--------|------|
| nuclei-mcp | Hardened scan adapter |
| bloodhound-mcp | Identity graph template |
| cloud-inventory-mcp | Cloud assets template |
| threatmapper-mcp | Runtime/vuln template |
| external-surface-mcp | Exposure / look-alike heuristics |
| anomaly-detector-mcp | Baseline anomalies |
| **agent-path-mcp** | **AI agent inventory + path scores** |

Most bodies are **synthetic** until live credentials and APIs are configured.

## UI

Grafana provisioning under `ui/grafana/` (attack path dashboard). Wire Neo4j datasource after Compose is up.

## Scripts

- `scripts/seed_graph.py` — classic sample paths  
- `scripts/detect_agent_attack_paths.py` — agent paths + MITRE  
- `scripts/mock_test_collectors.py` — smoke collectors  
