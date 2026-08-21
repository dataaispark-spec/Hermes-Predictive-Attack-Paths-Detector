# Collectors, Full Gateway, OpenTelemetry & Grafana UI

This document records the artefacts that close the remaining open items.

## 1. Real collectors (MCP servers)

| Server | Path | Tools (skeleton) |
|--------|------|------------------|
| BloodHound CE / identity | `mcp-servers/bloodhound-mcp/` | `bh_list_domains`, `bh_shortest_paths_to_da`, `bh_export_graph_fragment` |
| Cloud inventory (AWS/Azure/GCP) | `mcp-servers/cloud-inventory-mcp/` | `cloud_list_accounts`, `cloud_inventory_assets`, `cloud_internet_facing` |
| ThreatMapper | `mcp-servers/threatmapper-mcp/` | `tm_list_vulnerabilities`, `tm_attack_paths`, `tm_node_topology` |

All three follow the same pattern as the Nuclei MCP: stdio MCP server, JSON results, ready to be pointed at by Hermes. Replace the placeholder return values with real API / SDK calls and credentials via environment variables.

## 2. Full MCP Policy Gateway (upgraded)

`mcp-gateway/gateway.py` now includes:
- OPA authorization (fail-closed)
- OpenTelemetry traces + metrics (console exporter by default; OTLP-ready)
- `/authorize` decision endpoint
- `/proxy/{server}` authorize-then-forward path (extendable to full MCP protocol)

## 3. OpenTelemetry exporter

Gateway depends on `opentelemetry-api` / `opentelemetry-sdk` / `opentelemetry-exporter-otlp`.  
By default it uses console exporters so you see spans and metrics immediately.  
For production, set `OTEL_EXPORTER_OTLP_ENDPOINT` and switch to OTLP exporters.

## 4. UI / Grafana for path visualisation

- Dashboard JSON: `ui/grafana/dashboards/attack-paths.json`
- Provisioning: `ui/grafana/provisioning/`
- Compose fragment: `deploy/docker-compose.ui.yml`

Start with:
```bash
docker compose -f docker-compose.yml -f docker-compose.opa.yml -f docker-compose.ui.yml up -d
```
Then open http://localhost:3000 (admin / skandashield-change-me).  
Install / enable the Neo4j data source if the plugin did not load automatically, then open the “SkandaShield Attack Paths” dashboard.

## Wiring the new collectors into Hermes

Add to `~/.hermes/config.yaml` (example):

```yaml
mcp_servers:
  bloodhound:
    command: "python"
    args: ["/path/to/mcp-servers/bloodhound-mcp/server.py"]
    tools:
      include: ["bh_list_domains", "bh_shortest_paths_to_da", "bh_export_graph_fragment"]
  cloud_inventory:
    command: "python"
    args: ["/path/to/mcp-servers/cloud-inventory-mcp/server.py"]
    tools:
      include: ["cloud_list_accounts", "cloud_inventory_assets", "cloud_internet_facing"]
  threatmapper:
    command: "python"
    args: ["/path/to/mcp-servers/threatmapper-mcp/server.py"]
    tools:
      include: ["tm_list_vulnerabilities", "tm_attack_paths", "tm_node_topology"]
```

Keep high-impact calls behind the policy gateway / OPA rules.
