# Overview — What this project is (plain language)

## In one sentence

An **open starter kit** to build AI-assisted security operations that prioritise **attack paths to critical systems**, with specialist bots, a knowledge graph, and strict approval controls.

## Purpose

Help organisations move from “endless alert queues” to a **small, prioritised list of weaknesses that actually chain into real risk** — and to do that with technology they can inspect, extend, and run themselves.

## How it helps the organisation

- **Security teams** get path-based priorities and draft remediation text for engineers.
- **Platform teams** keep existing scanners/SIEM; this kit *sits beside* them via MCP connectors.
- **Risk / leadership** see progress as fewer high-score paths, not more raw findings.
- **Builders** get a documented reference architecture (agents + graph + policy + durable workflows).

## How it works

1. **Collect** inventory and findings (synthetic for demos; real APIs when you are ready).
2. **Store** them in Neo4j as assets, identities, findings, and attack paths.
3. **Reason** with five Hermes specialist bots (map, triage, paths, anomaly, remediation).
4. **Govern** actions with OPA (default deny; tickets need human approval).
5. **Show** top paths in Grafana and Bot chat.
6. **Optionally run** Temporal for long-running collect → approve → ticket pipelines that survive restarts.

## Benefits (short list)

- Path-first prioritisation  
- Specialist agents with clear roles  
- Safety gates (policy + human approval)  
- Open stack, no forced vendor platform  
- Fast demo with seed data  
- Enterprise docs for install and architecture  
- Extensible MCP + Temporal roadmap  

## Roadmap (summary)

| Now | Next | Later |
|-----|------|-------|
| Bots, graph, OPA, synthetic collectors, Grafana, Temporal starter | Live BloodHound/cloud/ThreatMapper feeds | HA, SSO, SIEM export, richer UI, multi-tenant |

See the root [README.md](../README.md) for the full narrative and [ARCHITECTURE.md](./ARCHITECTURE.md) for technical design.
