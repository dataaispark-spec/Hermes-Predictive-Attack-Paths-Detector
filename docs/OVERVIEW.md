# Overview — What this project is (plain language)

## In one sentence

An **open starter kit** to build AI-assisted security operations that prioritise **attack paths to critical systems**, with specialist bots, a knowledge graph, and strict approval controls.

## Purpose

Help organisations move from “endless alert queues” to a **small, prioritised list of weaknesses that actually chain into real risk** — with technology they can inspect, extend, and run themselves.

## How it helps the organisation

- **Security teams** — path-based priorities and draft remediation for engineers  
- **Platform teams** — sits *beside* SIEM/scanners via MCP  
- **Leadership** — fewer high-impact paths, not more raw findings  
- **Builders** — reference architecture for agentic security  

## How it works

1. **Collect** inventory and findings (synthetic for demos; real APIs later)  
2. **Store** in Neo4j (assets, identities, findings, paths)  
3. **Reason** with five Hermes specialist bots  
4. **Govern** with OPA (default deny; tickets need human approval)  
5. **Show** top paths in Grafana and Bot chat  
6. **Optionally** Temporal for durable collect → approve → ticket  

## How it differs from current platforms

**Full detail + named product lists:** [HOW_WE_DIFFER.md](./HOW_WE_DIFFER.md)

Short version:

| Others | This kit |
|--------|----------|
| Commercial VM / CTEM / CNAPP / EASM / SIEM **products** | Open **architecture kit** you own |
| Vendor discovery and dashboards | Path reasoning + bots + policy-as-code |
| You configure their platform | You extend MCP, Rego, SOUL.md, Temporal |

Not a replacement for Tenable, Wiz, XM Cyber, CyCognito, Splunk, etc. — designed to **work with** them and add transparent agentic prioritisation.

## Benefits (short list)

- Path-first prioritisation  
- Specialist agents with clear roles  
- Safety gates (policy + human approval)  
- Open stack, no forced vendor platform  
- Fast demo with seed data  
- Enterprise install & architecture docs  
- Extensible MCP + Temporal roadmap  

## Roadmap (summary)

| Now | Next | Later |
|-----|------|-------|
| Bots, graph, OPA, synthetic collectors, Grafana, Temporal starter | Live BloodHound/cloud/ThreatMapper feeds | HA, SSO, SIEM export, richer UI |

See [README.md](../README.md) and [ARCHITECTURE.md](./ARCHITECTURE.md).
