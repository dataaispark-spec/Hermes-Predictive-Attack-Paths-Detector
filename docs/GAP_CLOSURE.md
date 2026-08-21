# Gap Closure Report – Hermes SkandaShield Bots

This document records how the remaining gaps from the Architecture Analysis (sections 3–5) and the OPA investigation have been closed or partially closed by the current repository state.

## P0 – Security & Safety

| Gap | Status | Artefact / Action |
|-----|--------|-------------------|
| Rotate Neo4j password / secrets | Documented | README + compose comments; operator must change `skandashield-change-me` |
| Harden Nuclei MCP | Partial | Skeleton exists; rate-limit / template allow-list still TODO |
| Enforce MCP tool filtering | Closed | Example configs use `tools.include` |
| Remediation propose-only | Closed | SOUL.md + OPA rule requiring `human_approved` |
| Policy engine between Bots and tools | **Closed** | OPA + MCP Gateway skeleton + starter Rego |

## P1 – Functional Completeness

| Gap | Status | Artefact / Action |
|-----|--------|-------------------|
| Real collectors (BloodHound, ThreatMapper…) | Open | MCP pattern ready; implementations still needed |
| Expand Neo4j schema (temporal, path materialisation) | Partial | schema.cypher + examples.cypher provide foundation |
| Validation gate before “actionable” | Partial | OPA can enforce; optional LangGraph still recommended |

## P2 – Operational Maturity

| Gap | Status | Artefact / Action |
|-----|--------|-------------------|
| Observability | Partial | Gateway emits `[AUDIT]` lines; full OTel still TODO |
| Neo4j HA | Open | Operator decision (Aura / Cluster) |
| Scheduled routines | Documented | Hermes routines/cron; not yet pre-populated |

## P3 – Platform Ambition

| Gap | Status | Artefact / Action |
|-----|--------|-------------------|
| LangGraph / Temporal coordinator | Open | Recommended hybrid remains valid |
| Policy engine (OPA) | **Closed** | Full starter package + gateway |
| UI / Grafana for attack paths | Open | Future work |

## Architecture Blueprint Update

```
[External Scanners / Cloud / AD]
          |
          v
+---------------------+ 
|  Hermes Bots (5)    |
+----------+----------+
           | tools/call
           v
+---------------------+     POST /authorize
|  MCP Policy Gateway |--------------------> OPA (Rego)
+----------+----------+
           | allow only
           v
+---------------------+ 
|  Real MCP Servers   |  (Neo4j, Nuclei, future collectors)
+----------+----------+
           |
           v
+---------------------+ 
|  Neo4j Knowledge    |
|  Graph              |
+---------------------+
```

## Validation Matrix (updated)

| SkandaShield Capability | Coverage after gap closure |
|-------------------------|----------------------------|
| Continuous visibility | Partial (collectors still missing) |
| Attack-path reasoning & scoring | Partial → stronger (OPA protects writes) |
| AI-assisted prioritisation | Partial |
| Behavioural anomaly detection | Partial |
| Integrations | Partial (MCP + policy layer ready) |
| Attack surface monitoring | Missing |
| Sits alongside existing tools | Covered |
| Engineer-ready guidance | Covered + OPA-enforced human approval |
| Predict, don’t just detect | Partial → stronger governance |
| Live in weeks | Covered (compose + policies) |

## Next recommended actions (still open)

1. Implement BloodHound / cloud inventory MCP servers.
2. Replace gateway skeleton with full MCP protocol proxy or client-side interceptor.
3. Add OpenTelemetry exporter to the gateway.
4. Optional LangGraph coordinator for deterministic validate → rank → gate loops.
5. Lightweight Grafana dashboard over Neo4j for path visualisation.
