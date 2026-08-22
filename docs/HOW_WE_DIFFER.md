# How this kit is different from current platforms

This document explains **what Hermes SkandaShield Bots is *not***, and how it differs from common commercial and open security products.

**Fair framing:** those products are mature SaaS/platforms. **This repository is an open architecture kit and working templates** — not a drop-in replacement for any of them.

Legend used in vendor tables:

| Symbol | Meaning |
|--------|--------|
| **Strong** | Core strength of that product |
| **Partial** | Present but not the main value |
| **Limited / N/A** | Not the product’s job or not offered as open self-hosted code |
| **Kit** | This repository (Hermes SkandaShield Bots) |

---

## One-line difference

| This kit | Typical commercial platforms |
|----------|------------------------------|
| **You own the design** — agents, graph, policy, pipelines as code | **Vendor owns the product** — configure and consume their console |
| **Path reasoning + specialist AI bots + OPA gates** as a *buildable* stack | **Packaged discovery, prioritisation, dashboards** as a *bought* service |

---

## What we optimise for

1. Path-first prioritisation (“what chains to crown jewels?”)  
2. Specialist Hermes bots with clear roles  
3. Policy-as-code (OPA) before high-impact actions  
4. Open MCP connectors into **your** graph  
5. Optional Temporal durable approve-and-act pipelines  
6. Self-hosted / no mandatory vendor tenancy  

Synthetic collectors exist so you can validate the *operating model* before production credentials.

---

## Master capability matrix (vendors vs this kit)

| Capability | Tenable One | Qualys VMDR | Rapid7 InsightVM / Exposure | Wiz | Orca | XM Cyber | BloodHound Ent. | CrowdStrike Exposure | CyCognito | Splunk / Sentinel | **This kit** |
|------------|:-----------:|:-----------:|:---------------------------:|:---:|:----:|:--------:|:-----------------:|:--------------------:|:---------:|:-----------------:|:------------:|
| Vulnerability scanning engine | Strong | Strong | Strong | Partial | Partial | Limited | N/A | Partial | Limited | Limited | **Limited** (uses Nuclei template / external scanners) |
| Multi-cloud posture (CSPM) | Strong | Strong | Strong | **Strong** | **Strong** | Partial | N/A | Strong | Limited | Limited | **Partial** (inventory MCP; not full CSPM) |
| Attack-path / graph prioritisation | Strong | Partial | Strong | **Strong** | Strong | **Strong** | **Strong** (identity) | Strong | Partial | Limited | **Strong** (design focus; open Neo4j) |
| Identity / AD attack paths | Partial | Limited | Partial | Partial | Partial | Strong | **Strong** | Partial | N/A | Limited | **Partial→Strong** (BloodHound MCP roadmap) |
| External attack surface (EASM) | Strong | Strong | Strong | Partial | Partial | Limited | N/A | Strong | **Strong** | Limited | **Partial** (surface MCP heuristics) |
| SIEM / real-time detection | Limited | Limited | Limited | Limited | Limited | N/A | N/A | **Strong** (Falcon) | N/A | **Strong** | **N/A** (not a SIEM) |
| Specialist multi-agent AI (open) | Partial | Partial | Partial | Partial | Partial | Limited | Limited | Partial | Limited | Partial | **Strong** (Hermes Bot Mode) |
| Policy-as-code before tickets (OPA) | Partial | Partial | Partial | Partial | Partial | Partial | Limited | Partial | Limited | Playbooks | **Strong** (OPA default-deny) |
| Durable workflow engine (open) | Vendor WF | Vendor WF | Vendor WF | Vendor WF | Vendor WF | Vendor WF | Limited | Vendor WF | Limited | SOAR | **Strong** (Temporal starter) |
| Self-host full stack / MIT templates | N/A | N/A | N/A | N/A | N/A | N/A | Partial (CE exists) | N/A | N/A | Partial | **Strong** |
| You control agent SOUL / tools | Limited | Limited | Limited | Limited | Limited | Limited | Limited | Limited | Limited | Limited | **Strong** |
| Production maturity / SLA | **Strong** | **Strong** | **Strong** | **Strong** | **Strong** | **Strong** | **Strong** | **Strong** | **Strong** | **Strong** | **Pilot** (harden per roadmap) |

---

## Specific vendor comparison tables

### Tenable (Vulnerability Management / Tenable One)

| Dimension | Tenable | This kit |
|-----------|---------|----------|
| Primary job | Scan, inventory, exposure management at scale | Path reasoning + agentic prioritisation kit |
| Data plane | Tenable cloud / sensors | Your Neo4j (+ optional feeds from Tenable later) |
| Prioritisation | VPR, exposure scores, asset criticality | Multi-hop path score + bot triage |
| AI | Vendor features inside platform | Open Hermes specialist bots |
| Actions | Built-in remediation workflows | OPA-gated; human_approved tickets |
| Best fit | Enterprise VM/CTEM program of record | Ownable agent/graph layer **beside** Tenable |
| Replace Tenable? | — | **No** |

### Qualys (VMDR / Cloud Platform)

| Dimension | Qualys | This kit |
|-----------|--------|----------|
| Primary job | Continuous VM, policy compliance, cloud agents | Path-first bot + graph templates |
| Strength | Broad sensor coverage, compliance packs | Transparent policy (Rego) + bot roles |
| UI | Mature Qualys console | Grafana + Hermes chat |
| Integration | APIs into Qualys | MCP into your stack; can consume Qualys exports later |
| Replace Qualys? | — | **No** |

### Rapid7 (InsightVM / Exposure Command)

| Dimension | Rapid7 | This kit |
|-----------|--------|----------|
| Primary job | VM + exposure command + automation | Open path + agent orchestration kit |
| Strength | Insight platform, remediation projects | MIT code, Temporal approval pipeline |
| Attack paths | Productised in Exposure Command | Neo4j + Attack-Path Synthesizer bot |
| Replace Rapid7? | — | **No** |

### Microsoft (Defender VM / Security Exposure Management / Sentinel)

| Dimension | Microsoft security stack | This kit |
|-----------|--------------------------|----------|
| Primary job | M365/Azure-native exposure, XDR, SIEM | Cloud-agnostic self-hosted kit |
| Strength | Deep M365/Azure identity + Sentinel SOAR | Works across clouds; not tied to Entra-only |
| Attack paths | Native graph features in SEM / Defender | Open Cypher model you edit |
| AI | Security Copilot (vendor) | Hermes bots you configure |
| Replace Microsoft stack? | — | **No** — complementary graph/agent layer |

### Wiz

| Dimension | Wiz | This kit |
|-----------|-----|----------|
| Primary job | Agentless CNAPP; Security Graph; toxic combinations | Not a CNAPP |
| Strength | Fast multi-cloud discovery + path context | Specialist bots + OPA + Temporal you host |
| Data ownership | Wiz tenant | Your Neo4j / infra |
| AI agents | Platform features | Hermes Bot Mode (open personas) |
| Replace Wiz? | — | **No** — use Wiz findings as inputs when integrated |

### Orca Security

| Dimension | Orca | This kit |
|-----------|------|----------|
| Primary job | Agentless CNAPP, side-scanning, risk prioritisation | Path/agent kit |
| Strength | Cloud workload context without heavy agents | Policy-gated mobilisation, open workflows |
| Replace Orca? | — | **No** |

### Palo Alto Prisma Cloud

| Dimension | Prisma Cloud | This kit |
|-----------|-------------|----------|
| Primary job | CNAPP + network/cloud runtime in Palo ecosystem | Independent open stack |
| Strength | Enterprise Palo integration, compliance | Vendor-neutral MCP/Hermes |
| Replace Prisma? | — | **No** |

### XM Cyber

| Dimension | XM Cyber | This kit |
|-----------|----------|----------|
| Primary job | Continuous attack-path management / exposure | Open path **templates** + agents |
| Strength | Mature attack-graph analytics, choke points | You own graph schema + bot logic + OPA |
| UI | Product path visualisation | Grafana (richer UI on roadmap) |
| Replace XM Cyber? | — | **No** for enterprise path product needs |

### BloodHound Enterprise (SpecterOps) / BloodHound CE

| Dimension | BloodHound | This kit |
|-----------|------------|----------|
| Primary job | Identity attack-path management (AD/Entra) | Multi-domain path kit (cloud+vuln+identity) |
| Strength | Best-in-class AD relationship graph | Combines identity *with* vulns/cloud in one Neo4j model |
| Open core | CE available | Full kit MIT templates |
| Integration | BH as source | `bloodhound-mcp` (synthetic now; live API next) |
| Replace BloodHound? | — | **No** — preferred **data source** for identity paths |

### CrowdStrike (Falcon + Exposure Management)

| Dimension | CrowdStrike | This kit |
|-----------|-------------|----------|
| Primary job | Endpoint XDR + exposure module | Not XDR |
| Strength | Runtime detection, threat intel, managed assets | Offline/path planning and fix prioritisation |
| AI | Charlotte / platform AI | Hermes specialists |
| Replace Falcon? | — | **No** |

### CyCognito / Attaxion / EdgeScan (EASM)

| Dimension | EASM vendors | This kit |
|-----------|--------------|----------|
| Primary job | Discover internet-facing assets & exposures | Consume exposure signals into paths |
| Strength | Crawling, attribution, continuous EASM | Look-alike heuristics + graph join |
| Replace EASM? | — | **No** |

### Axonius / JupiterOne / runZero / Armis (CAASM / asset)

| Dimension | CAASM / asset platforms | This kit |
|-----------|-------------------------|----------|
| Primary job | Unified asset inventory & CMDB-like security view | Path reasoning on top of inventory |
| Strength | Connector breadth, asset truth | AttackPath nodes + bots |
| Replace CAASM? | — | **No** — inventory can feed Neo4j |

### Splunk / Microsoft Sentinel / Elastic / Chronicle (SIEM)

| Dimension | SIEM | This kit |
|-----------|------|----------|
| Primary job | Log detection, investigation, compliance retention | Exposure→path prioritisation |
| Strength | Real-time analytics, SOAR | Graph + agents + policy gates |
| Anomaly | UEBA / ML packs | Simple z-score MCP starter only |
| Replace SIEM? | — | **No** — export audits *to* SIEM |

### Picus / Pentera / Cymulate / SafeBreach / AttackIQ (BAS)

| Dimension | BAS | This kit |
|-----------|-----|----------|
| Primary job | Safely validate controls / emulated attacks | Model paths; propose fixes |
| Strength | Evidence of exploitability in *your* controls | Ranking which paths matter first |
| Replace BAS? | — | **No** — complementary validation vs prioritisation |

### SkandaShield (commercial inspiration)

| Dimension | SkandaShield product | This kit |
|-----------|----------------------|----------|
| Primary job | Commercial AI-enabled path platform | Open reference kit for similar *ideas* |
| Delivery | Vendor product + support | DIY templates + docs |
| Feature parity | Product maturity | **Not claimed** |
| Relationship | Inspiration | Learning / build path, not a clone |

---

## Difference by product category (summary)

### 1. Vulnerability Management
Keep scanners; this kit correlates into paths.  
### 2. CTEM / Exposure platforms
They run the enterprise program; this kit prototypes agentic prioritise + mobilise you control.  
### 3. Attack-path products
They ship mature UIs/engines; this kit ships open Neo4j + synthesizer bot + policy/Temporal.  
### 4. CNAPP / CSPM
They discover cloud posture; this kit is not a posture engine.  
### 5. EASM / CAASM
They inventorise the surface; this kit joins exposure into path reasoning.  
### 6. SIEM / XDR
They detect; this kit prioritises fix paths.  
### 7. BAS
They validate; this kit ranks what to validate/fix.  
### 8. AI copilots
They chat on vendor data; this kit uses least-privilege specialist bots on your graph.

---

## Side-by-side summary

| Dimension | Classic VM | CTEM / CNAPP / path SaaS | SIEM/XDR | **This kit** |
|-----------|------------|---------------------------|----------|--------------|
| Primary output | Finding lists | Scores + paths + UI | Alerts | Ranked paths + bot guidance + policy gates |
| Who owns logic | Vendor | Vendor | Vendor | **You** |
| AI role | Add-on | Vendor AI | Copilots | **Specialist bots** |
| Action safety | Varies | Vendor workflows | Playbooks | **OPA + human approval** |
| Integration | Into vendor | Into vendor | Logs | **MCP into your graph** |
| License | Subscription | Subscription | Subscription | **MIT templates** |
| Maturity | High | High | High | **Pilot → harden** |

---

## When to choose what

**Prefer this kit when you need to:** own/audit agents and policy; prototype path-first ops; teach the architecture; extend MCP/Temporal.

**Prefer commercial platforms when you need:** SLA/support; immediate multi-cloud discovery; polished path UI day one; managed CTEM.

**Common pattern:** **Tenable/Wiz/BloodHound/SIEM as data sources** + **this kit (or its patterns) for agentic prioritisation and gated mobilisation**.

---

## Product checklist (orientation only — not rankings)

**VM:** Tenable, Qualys, Rapid7 InsightVM, Microsoft Defender VM, Greenbone/OpenVAS  
**CTEM:** Tenable One, CrowdStrike Exposure, Rapid7 Exposure Command, Microsoft SEM, Astelia, Balbix, Vulcan, SecPod Saner  
**Path:** XM Cyber, BloodHound Enterprise, Wiz, Orca, Cloudnosys, Stream  
**CNAPP:** Wiz, Orca, Prisma Cloud, Lacework, Sysdig, SentinelOne Cloud  
**EASM/CAASM:** CyCognito, Attaxion, EdgeScan, runZero, Axonius, JupiterOne, Armis  
**SIEM/XDR:** Splunk, Sentinel, Elastic, Chronicle, Falcon, XSIAM, QRadar  
**BAS:** Picus, Pentera, Cymulate, SafeBreach, AttackIQ  
**Inspiration:** [SkandaShield](https://skandashield.com/platform)

---

*See [README.md](../README.md), [OVERVIEW.md](./OVERVIEW.md), [ARCHITECTURE.md](./ARCHITECTURE.md).*
