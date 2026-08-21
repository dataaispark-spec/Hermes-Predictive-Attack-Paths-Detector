# Gap Closure Report – Hermes SkandaShield Bots

This document records how the remaining gaps from the Architecture Analysis (sections 3–5) and the OPA investigation have been closed or partially closed by the current repository state.

## P0 – Security & Safety

| Gap | Status | Artefact / Action |
|-----|--------|-------------------|
| Rotate Neo4j password / secrets | Documented | README + compose comments; operator must change `skandashield-change-me` |
| Harden Nuclei MCP | Partial | Skeleton exists; rate-limit / template allow-list still TODO |
| Enforce MCP tool filtering | Closed | Example configs use `tools.include` |
| Remediation propose-only | Closed | SOUL.md + OPA rule requiring `human_approved` |
| Policy engine between Bots and tools | **Closed** | OPA + MCP Gateway + starter Rego |

## P1 – Functional Completeness

| Gap | Status | Artefact / Action |
|-----|--------|-------------------|
| Real collectors (BloodHound, cloud inventory, ThreatMapper) | **Closed (skeletons)** | `mcp-servers/bloodhound-mcp`, `cloud-inventory-mcp`, `threatmapper-mcp` |
| Expand Neo4j schema (temporal, path materialisation) | Partial | schema.cypher + examples.cypher provide foundation |
| Validation gate before “actionable” | Partial | OPA can enforce; optional LangGraph still recommended |

## P2 – Operational Maturity

| Gap | Status | Artefact / Action |
|-----|--------|-------------------|
| Observability | **Closed (console + OTLP-ready)** | Gateway emits OTel traces/metrics + `[AUDIT]` lines |
| Neo4j HA | Open | Operator decision (Aura / Cluster) |
| Scheduled routines | Documented | Hermes routines/cron; not yet pre-populated |

## P3 – Platform Ambition

| Gap | Status | Artefact / Action |
|-----|--------|-------------------|
| LangGraph / Temporal coordinator | Open | Recommended hybrid remains valid |
| Policy engine (OPA) | **Closed** | Full starter package + gateway |
| UI / Grafana for attack paths | **Closed** | `ui/grafana/` + `deploy/docker-compose.ui.yml` |
| Full MCP protocol proxy | **Partial → upgraded** | Gateway now has authorize-then-forward `/proxy/{server}`; full stdio bridging still extendable |

## Architecture Blueprint Update

```
[External Scanners / Cloud / AD / BloodHound / ThreatMapper]
          |
          v
+---------------------+ 
|  Hermes Bots (5)    |
+----------+----------+
           | tools/call
           v
+---------------------+     POST /authorize (+ OTel)
|  MCP Policy Gateway |--------------------> OPA (Rego)
+----------+----------+
           | allow only
           v
+---------------------+ 
|  Real MCP Servers   |  (Neo4j, Nuclei, BloodHound, Cloud, ThreatMapper)
+----------+----------+
           |
           v
+---------------------+         Grafana
|  Neo4j Knowledge    | <------ dashboards
|  Graph              |
+---------------------+
```

## Validation Matrix (updated)

| SkandaShield Capability | Coverage after gap closure |
|-------------------------|----------------------------|
| Continuous visibility | Partial → stronger (collector MCP skeletons present) |
| Attack-path reasoning & scoring | Partial → stronger (OPA + Grafana) |
| AI-assisted prioritisation | Partial |
| Behavioural anomaly detection | Partial |
| Integrations | Partial → stronger (MCP collectors + policy layer) |
| Attack surface monitoring | Partial (cloud_internet_facing tool) |
| Sits alongside existing tools | Covered |
| Engineer-ready guidance | Covered + OPA-enforced human approval |
| Predict, don’t just detect | Partial → stronger governance |
| Live in weeks | Covered (compose + policies + UI) |

## Remaining recommended actions

1. Replace collector skeletons with real API/SDK implementations (credentials via env).
2. Extend gateway to full MCP stdio/HTTP protocol bridging if needed.
3. Point OTel exporters at a real collector (Jaeger/Tempo/OTLP endpoint).
4. Optional LangGraph coordinator for deterministic validate → rank → gate loops.
5. Harden Nuclei MCP (template allow-list, rate limits).
