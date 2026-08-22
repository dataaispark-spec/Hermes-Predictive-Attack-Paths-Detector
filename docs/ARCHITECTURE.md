# Enterprise Architecture Design — Hermes SkandaShield Kit

This document describes the **end-to-end architecture**: logical design, physical design, component catalogue, integration patterns, data flows, trust boundaries, and enterprise deployment considerations.

It mirrors the product intent of [SkandaShield Platform](https://skandashield.com/platform): *predict attack paths before they are walked*, prioritise by exploitability, and deliver engineer-ready guidance — implemented here as an open agentic kit on Hermes + Neo4j + OPA.

---

## 1. Design principles

| Principle | How it is applied |
|-----------|-------------------|
| Predict, don’t just detect | Attack-path synthesis over a shared knowledge graph, not only alert queues |
| Least privilege | MCP tool allow-lists + OPA default-deny between Bots and high-impact actions |
| Sit alongside existing tools | Collectors and ticketing are adapters (MCP), not a rip-and-replace SIEM |
| Human in the loop | Remediation / tickets require explicit `human_approved` |
| Durable source of truth | Neo4j holds assets, identities, findings, paths, anomalies |
| Fail closed | Gateway denies tools if OPA is unreachable |
| Observable | Gateway audit lines + OpenTelemetry hooks |

---

## 2. End-to-end architecture diagram (logical)

```
┌────────────────────────────────────────────────────────────────────────────┐
│                        EXTERNAL / ENTERPRISE SOURCES                          │
│  Cloud APIs (AWS/Azure/GCP) · AD / Entra · BloodHound CE · ThreatMapper      │
│  Scanners (Nuclei) · SIEM / logs · ASM / DNS · Ticketing (Jira/SNOW)          │
└──────────────────────────────────┬───────────────────────────────────────────┘
                                │  collect / query (read-heavy)
                                ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                     MCP COLLECTOR & TOOL LAYER (stdio)                        │
│  bloodhound-mcp · cloud-inventory-mcp · threatmapper-mcp · nuclei-mcp        │
│  anomaly-detector-mcp · external-surface-mcp · (future: jira, siem, …)       │
└──────────────────────────────────┬───────────────────────────────────────────┘
                                │  tools/call
        ┌──────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌──────────────┐    ┌────────────────────┐    ┌─────────────────┐
│  HERMES BOTS  │    │  MCP POLICY GATEWAY │───►│  OPA (Rego)      │
│  (5 specialists│───►│  authorize + audit  │    │  default deny     │
│   + routines)  │    │  (+ optional proxy) │    │  bot/tool/context│
└──────┬───────┘    └──────────┬──────────┘    └─────────────────┘
        │ write/read            │ allow only
        │ (Cypher via MCP)      │
        ▼                       │
┌──────────────────┐           │
│  NEO4J KNOWLEDGE  │◄──────────┘
│  GRAPH            │
│  Asset · Identity │
│  Finding · Path   │
│  Anomaly          │
└────────┬─────────┘
          │
          ▼
┌──────────────────┐     ┌─────────────────┐
│  GRAFANA UI       │     │  HUMAN OPERATORS │
│  Attack-path      │     │  Approve tickets │
│  dashboards       │     │  Tune policy     │
└──────────────────┘     └─────────────────┘
```

**Control plane:** Hermes Bot Mode + OPA + Gateway.  
**Data plane:** Collectors → Neo4j → queries / dashboards / Bot reasoning.

---

## 3. Component catalogue

### 3.1 Hermes Agent + Bot Mode

| Aspect | Detail |
|--------|--------|
| Role | Orchestration runtime, specialist team, human interface |
| Bots | `asset-identity-mapper`, `vuln-triage`, `attack-path-synthesizer`, `anomaly-detector`, `remediation-guidance` |
| Config | `SOUL.md` per Bot; `~/.hermes/config.yaml` for MCP servers |
| Safety | Prefer `terminal.backend: docker` |

### 3.2 MCP servers (tool adapters)

| Server | Responsibility | Default mode |
|--------|----------------|--------------|
| `bloodhound-mcp` | Identity / AD path fragments | Synthetic |
| `cloud-inventory-mcp` | Cloud accounts & assets | Synthetic |
| `threatmapper-mcp` | Vulns + path-style data | Synthetic |
| `nuclei-mcp` | Controlled scans | Hardened |
| `anomaly-detector-mcp` | Z-score baselines; optional Neo4j | In-memory + optional Bolt |
| `external-surface-mcp` | Look-alike + ASM exposures | Synthetic |
| Neo4j Cypher MCP | Graph read/write | Live |

### 3.3 MCP Policy Gateway

PEP in front of high-impact tools. `POST /authorize`, fail-closed, `[AUDIT]` + OTel. Full stdio multiplex proxy is an extension point; Hermes typically launches MCP via stdio with tool allow-lists.

### 3.4 OPA

PDP. Policy: `policies/skandashield.rego`. Default deny; trusted reads; restricted writes; tickets only with `human_approved`.

### 3.5 Neo4j knowledge graph

Labels: `Asset`, `Identity`, `Finding`, `AttackPath`, `Anomaly`.  
Relationships: `HAS_VULN`, `MEMBER_OF`, `CAN_REACH`, `STARTS_AT`, `ENDS_AT`, `INCLUDES`, `INVOLVES`.  
System of record for prioritisation and path reasoning.

### 3.6 Grafana

Operational UI over Neo4j (top paths, internet-facing findings, choke points).

### 3.7 Utilities

`seed_graph.py`, `mock_test_collectors.py`, `run_rego_tests.sh`.

---

## 4. How components connect

### 4.1 Connection matrix

| From | To | Mechanism | Purpose |
|------|-----|-----------|----------|
| Hermes Bot | MCP server | MCP stdio | Tool invocation |
| Client | Gateway | HTTP `/authorize` | Policy check |
| Gateway | OPA | HTTP data API | Allow/deny |
| Neo4j MCP | Neo4j | Bolt | Cypher |
| Anomaly MCP (opt.) | Neo4j | Bolt | Persist anomalies |
| Grafana | Neo4j | Bolt plugin | Dashboards |
| Collectors (live) | Cloud/AD APIs | HTTPS | Inventory |

### 4.2 Sequence: finding → guidance

1. Collectors produce assets/findings  
2. Mapper / triage Bots upsert Neo4j (OPA-checked writes)  
3. Attack-path synthesizer materialises `AttackPath`  
4. Grafana / chat surfaces top scores  
5. Remediation Bot proposes; OPA denies ticket until `human_approved`  
6. Human approves → ticket tool allowed

### 4.3 Trust boundaries

Untrusted external → Tool execution (sandboxed MCP) → Policy zone (Gateway+OPA) → Data zone (Neo4j) → Consumer zone (Grafana/Hermes/ticketing).

---

## 5. Logical architecture (enterprise)

**Layers:** Ingestion → Normalisation → Reasoning → Governance → Presentation → Gated action.

**SkandaShield mapping:** continuous visibility (collectors+graph), exploitability-ranked paths (AttackPath+synthesizer), AI prioritisation (triage Bot), anomaly (anomaly MCP), integrations (MCP), exposure (external-surface), engineer guidance (remediation+OPA).

**NFRs:** confidentiality (private nets), integrity (OPA on writes), availability (pilot single-node → cluster/Aura), auditability (gateway logs → SIEM).

---

## 6. Physical architecture

### 6.1 Pilot: single-host Docker

Neo4j :7474/:7687, OPA :8181, Gateway :8080, Grafana :3000, Hermes host/container spawning MCP stdio. Volumes for neo4j/grafana/`~/.hermes`.

### 6.2 Enterprise tiers

- **Tier 0** Management: CI/CD, secrets, registry  
- **Tier 1** Control: Hermes, Gateway, OPA (HA)  
- **Tier 2** Data: Neo4j cluster/Aura, backups  
- **Tier 3** Presentation: Grafana + Hermes with SSO  
- **Tier 4** Collectors: isolated jobs; policy-checked writes only

### 6.3 Ports (defaults) — none should be public

7474, 7687, 8181, 8080, 3000, 8642 — restrict to VPN/bastion/SSO.

### 6.4 Cloud

AWS EC2/EKS + Secrets Manager; Azure VM/AKS + Key Vault; GCP GCE/GKE + Secret Manager; optional Neo4j Aura with `neo4j+s://`.

### 6.5 Kubernetes sketch

Namespace `skandashield`; Deployments for opa/gateway/grafana/hermes; Neo4j StatefulSet/operator; ConfigMap for Rego; NetworkPolicies locking Bolt and OPA.

---

## 7. Data design

Lifecycle: Discover → Normalise → Store → Score paths → Prioritise → Propose → (Approve) → Ticket.  
Path `score` combines likelihood and impact fields; version scoring like policy.  
Synthetic mode = offline demos; live mode = real APIs + credentials.

---

## 8. Security architecture

| Control | Kit | Enterprise |
|---------|-----|------------|
| AuthN | Local Grafana admin | SSO |
| AuthZ | OPA Rego | Signed bundles, per-env |
| Secrets | `.env` / placeholders | Vault / cloud SM |
| Isolation | Docker terminal | gVisor / no host mounts |
| Egress | Nuclei allowlist | Proxy allowlists |
| Audit | Gateway logs | SIEM retention |

---

## 9. Scalability & resilience

Pilot: single Hermes/Neo4j/OPA.  
Enterprise: HA Hermes, Neo4j cluster/Aura, OPA replicas, scheduled collectors, health checks, multi-AZ.  
Bottlenecks: LLM latency, heavy path queries, scan volume.

---

## 10. Deployment topologies

| Topology | Use |
|----------|-----|
| Laptop Compose | Demo |
| Single VM Compose | Team pilot |
| Split VM | Light production |
| Kubernetes | Enterprise production |
| Hybrid Aura | Managed graph |

---

## 11. Extension points

Live collectors; full MCP proxy; LangGraph/Temporal gates; SIEM export; interactive path UI; multi-tenant graphs.

---

## 12. Related docs

| Doc | Focus |
|-----|--------|
| [INSTALL_AND_DEPLOY.md](./ops/INSTALL_AND_DEPLOY.md) | Install & deploy steps |
| [OPERATIONS.md](./ops/OPERATIONS.md) | Day-to-day ops |
| [OPA_INTEGRATION.md](./OPA_INTEGRATION.md) | Policy engine |
| [GAP_CLOSURE.md](./GAP_CLOSURE.md) | vs commercial platform |

---

## 13. Architect checklist

- [ ] Private network for Bolt, OPA, Gateway  
- [ ] SSO on Grafana / Hermes UI  
- [ ] Secrets not in git  
- [ ] OPA tests in CI  
- [ ] Neo4j backup/restore drill  
- [ ] Nuclei restricted if used  
- [ ] Human approval process defined  
- [ ] Audit to SIEM  
- [ ] Resource limits on compute  
- [ ] Diagram updated when MCP servers change  

*Architecture aligned with: Hermes Bots · MCP collectors · Gateway · OPA · Neo4j · Grafana.*
