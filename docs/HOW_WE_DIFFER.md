# How this kit is different from current platforms

This document explains **what Hermes SkandaShield Bots is *not***, and how it differs from common commercial and open security products. Fair comparison: those products are mature SaaS/platforms; **this repository is an open architecture kit and working templates**, not a drop-in replacement for any of them.

---

## One-line difference

| This kit | Typical commercial platforms |
|----------|------------------------------|
| **You own the design** — agents, graph, policy, and pipelines as code you can change | **Vendor owns the product** — you configure and consume features inside their console |
| **Path reasoning + specialist AI bots + explicit policy gates** as a *buildable* stack | **Packaged discovery, prioritisation, and dashboards** as a *bought* service |

---

## What we are optimising for

1. **Path-first thinking** — “what chains to crown jewels?” not only “how many critical CVEs?”
2. **Specialist agents** (Hermes Bot Mode) with clear roles, not one generic security chatbot
3. **Policy-as-code (OPA)** in front of high-impact actions (tickets, writes)
4. **Open connectors (MCP)** so you plug *your* tools in over time
5. **Optional durable workflows (Temporal)** for approve-and-act pipelines that survive failures
6. **No mandatory cloud tenancy** — run on your VMs/K8s with your Neo4j

We are **not** trying to out-feature a full CNAPP or EASM suite on day one. Synthetic collectors and demos exist so you can validate the *operating model* before connecting production credentials.

---

## Difference by product category

### 1. Vulnerability Management (VM)

**Examples:** Tenable Vulnerability Management / Nessus, Qualys VMDR, Rapid7 InsightVM, Microsoft Defender Vulnerability Management, Greenbone/OpenVAS.

| Typical VM platform | This kit |
|---------------------|----------|
| Excellent at **finding and listing** vulns, severity, assets | Assumes scanners exist; **correlates** findings into graph paths |
| Prioritisation often CVSS / asset tags / threat intel scores | Prioritisation aimed at **multi-hop exploitability** (path score) |
| Closed or semi-open reporting UI | Open Neo4j + Grafana + Bot-written guidance |
| Remediation tracking in their workflow | Tickets only after **OPA + human approval** |

**Use together:** keep your VM scanners; feed results via MCP / SIEM later. This kit does not replace scanning engines.

---

### 2. Continuous Threat Exposure Management (CTEM) / Exposure Assessment

**Examples:** Tenable One, CrowdStrike Falcon Exposure Management, Rapid7 Exposure Command, Microsoft Security Exposure Management, Astelia, Balbix, Vulcan Cyber, SecPod Saner CVEM.

| Typical CTEM / EAP platform | This kit |
|-----------------------------|----------|
| End-to-end **productised** CTEM stages (scope → discover → prioritise → validate → mobilise) | **Blueprint** of prioritise + mobilise with agents and policy |
| Vendor-hosted analytics and UI | Self-hosted graph + bots + optional Temporal |
| Broad asset coverage out of the box | Coverage grows as **you** implement live MCP collectors |
| Commercial SLAs, support, compliance packs | Community/MIT templates; you operate it |

**Use together:** treat commercial CTEM as source of truth for enterprise programs; use this kit to experiment with **agentic triage and path reasoning** you fully control.

---

### 3. Attack path / identity path platforms

**Examples:** XM Cyber, BloodHound Enterprise (SpecterOps), Microsoft attack-path features, Wiz Security Graph / toxic combinations, Orca attack paths, Cloudnosys Attack Path, Stream Security.

| Typical attack-path product | This kit |
|-----------------------------|----------|
| Mature path engines (often proprietary graph) | **Neo4j schema + Cypher + synthesizer Bot** you can inspect |
| Strong UI for path visualisation | Grafana tables + seed data (richer UI is on the roadmap) |
| Deep productisation for AD/cloud | Synthetic + skeleton collectors first; **live BloodHound/cloud next** |
| License per environment | Open templates |

**Use together:** BloodHound CE / enterprise data can feed the graph via MCP; this kit adds **agent roles, OPA gates, and Temporal approval**, which pure path products may not include as open code.

---

### 4. CNAPP / CSPM / Cloud security platforms

**Examples:** Wiz, Orca Security, Prisma Cloud (Palo Alto), Lacework, Sysdig, SentinelOne Singularity Cloud, AWS Security Hub + Detective, Azure Defender for Cloud, Google Security Command Center.

| Typical CNAPP/CSPM | This kit |
|--------------------|----------|
| Agentless (or agent) cloud posture at scale | Not a cloud posture engine |
| Built-in cloud resource inventory | **Cloud inventory MCP** (synthetic today; SDK later) |
| Vendor risk scoring and compliance frameworks | Path-oriented scoring fields you define |
| Multi-cloud product support contracts | DIY integrations |

**Use together:** export high-value findings/assets into Neo4j; bots reason on top. Do not expect this kit to replace Wiz/Orca-class discovery.

---

### 5. External Attack Surface Management (EASM) / CAASM

**Examples:** CyCognito, Attaxion, EdgeScan, BeforeBreach, runZero, Axonius, JupiterOne, Armis (asset-centric).

| Typical EASM/CAASM | This kit |
|--------------------|----------|
| Continuous discovery of internet-facing / all assets | **external-surface MCP** heuristics + synthetic ASM feed |
| Large-scale crawling and attribution | Not a crawler product |
| Vendor asset inventory as system of record | Neo4j is **your** system of record for *path* reasoning |

**Use together:** pipe EASM results into the graph; use look-alike / exposure tools as lightweight complements.

---

### 6. SIEM / XDR / SOC platforms

**Examples:** Splunk, Microsoft Sentinel, Elastic SIEM, Chronicle, CrowdStrike Falcon, SentinelOne, Palo Alto XSIAM, QRadar.

| Typical SIEM/XDR | This kit |
|------------------|----------|
| Real-time detection, correlation, investigation | **Not a SIEM**; anomaly MCP is a simple statistical starter |
| Log-centric operations | Graph-centric path operations |
| Alert queues for analysts | Prioritised **paths** for fix teams |

**Use together:** SIEM remains detection; this kit focuses on **exposure-to-path prioritisation**. Export audits (Gateway/OPA/Temporal) into SIEM later.

---

### 7. Breach & Attack Simulation (BAS) / automated pentest

**Examples:** Picus, Pentera, Cymulate, SafeBreach, AttackIQ, Terra Security.

| Typical BAS / auto-pentest | This kit |
|----------------------------|----------|
| Actively validates controls and exploitability | Models paths from inventory/findings; **does not** safely exploit production |
| Continuous purple-team style testing | Reasoning + policy-gated remediation proposals |

**Use together:** BAS validates; path graph prioritises what to validate first.

---

### 8. Commercial “AI security copilots” / agent products

**Examples:** Vendor copilots inside Tenable/Wiz/CrowdStrike/etc., generic ChatGPT-style SOC assistants, closed multi-agent security startups.

| Typical AI security assistant | This kit |
|-------------------------------|----------|
| Chat over *their* data plane | **Your** graph + **your** bots + **your** policies |
| Opaque model/tool routing | Hermes Bot Mode, SOUL.md, MCP allow-lists, OPA Rego — all visible |
| Often SaaS-only | Self-hostable stack |

**Difference:** we treat AI as **specialist roles with least privilege**, not a single assistant with broad production powers.

---

### 9. SkandaShield (commercial product inspiration)

[SkandaShield Platform](https://skandashield.com/platform) describes AI-enabled path prediction, prioritised fix lists, and integrations with existing tools.

| SkandaShield (product) | This repository (kit) |
|------------------------|------------------------|
| Commercial platform experience | Open **reference implementation** of similar *ideas* |
| Vendor-operated capabilities and support | You assemble and operate components |
| Full product maturity | Templates, synthetic data, roadmap to live feeds |

We **do not claim feature parity**. We claim a **transparent way to learn and build** path-first, agent-assisted operations aligned with that problem statement.

---

## Side-by-side summary

| Dimension | Classic scanners / VM | CTEM / CNAPP / path SaaS | SIEM/XDR | **This kit** |
|-----------|----------------------|---------------------------|----------|--------------|
| Primary output | Finding lists | Exposure scores + paths + UI | Alerts & detections | Ranked paths + bot guidance + policy gates |
| Who owns logic | Vendor | Vendor | Vendor | **You** (code + Rego + SOUL.md) |
| AI role | Optional add-on | Vendor AI features | Copilots | **First-class specialist bots** |
| Action safety | Varies | Workflow products | Playbooks | **OPA default-deny + human approval** |
| Integration style | Agents/APIs into *them* | Connectors into *them* | Log shipping | **MCP into *your* graph** |
| License model | Subscription | Subscription | Subscription | **MIT templates** |
| Production readiness | High | High | High | **Pilot → harden (see roadmap)** |

---

## When to choose this kit vs a commercial platform

**Prefer this kit when you need to:**

- Own and audit agent behaviour and policy
- Prototype path-first ops without a multi-year platform buy
- Teach teams how attack-path + agent orchestration fits together
- Extend with custom MCP tools and Temporal workflows

**Prefer (or keep) commercial platforms when you need to:**

- Enterprise SLA, compliance packs, and 24/7 vendor support
- Immediate multi-cloud discovery at scale
- Polished attack-path UI and board-ready reporting on day one
- Managed CTEM program delivery

**Best practice for many organisations:** run **scanners + CNAPP/CTEM + SIEM as sources of data**, and use **this kit (or its patterns)** for agentic prioritisation, graph reasoning, and gated mobilisation you control.

---

## Platforms and products referenced (checklist)

Listed for orientation only — not an exhaustive market map and not rankings.

**Vulnerability management:** Tenable, Qualys, Rapid7 InsightVM, Microsoft Defender VM, Greenbone/OpenVAS  
**CTEM / exposure:** Tenable One, CrowdStrike Falcon Exposure Management, Rapid7 Exposure Command, Microsoft Security Exposure Management, Astelia, Balbix, Vulcan Cyber, SecPod Saner  
**Attack path / identity:** XM Cyber, BloodHound Enterprise, Wiz Security Graph, Orca, Cloudnosys Attack Path, Stream Security  
**CNAPP / CSPM:** Wiz, Orca, Prisma Cloud, Lacework, Sysdig, SentinelOne Cloud, hyperscaler native security hubs  
**EASM / CAASM:** CyCognito, Attaxion, EdgeScan, BeforeBreach, runZero, Axonius, JupiterOne, Armis  
**SIEM / XDR:** Splunk, Sentinel, Elastic, Chronicle, Falcon, XSIAM, QRadar  
**BAS / validation:** Picus, Pentera, Cymulate, SafeBreach, AttackIQ  
**Inspiration:** [SkandaShield](https://skandashield.com/platform)

---

*Updated with the repository README and [OVERVIEW.md](./OVERVIEW.md). Technical design: [ARCHITECTURE.md](./ARCHITECTURE.md).*
