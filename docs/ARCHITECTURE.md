# Enterprise Architecture Design — Hermes SkandaShield Kit

End-to-end **logical** and **physical** architecture for the open SkandaShield-style kit (Hermes + Neo4j + OPA + optional Temporal).

---

## 1. Design principles

| Principle | Application |
|-----------|-------------|
| Predict, don’t just detect | Attack-path synthesis on a shared graph |
| Least privilege | MCP allow-lists + OPA default-deny |
| Sit alongside tools | MCP adapters, not SIEM replacement |
| Human in the loop | Tickets need `human_approved` / Temporal signals |
| Durable source of truth | Neo4j |
| Fail closed | Gateway denies if OPA down |
| Durable processes | Optional Temporal for long-running pipelines |

---

## 2. End-to-end logical diagram

```
EXTERNAL SOURCES (cloud, AD, scanners, ASM, ticketing)
        |
        v
MCP COLLECTORS (bloodhound, cloud, threatmapper, nuclei, anomaly, surface)
        |
        +------------------+------------------+
        v                  v                  v
  HERMES BOTS      MCP POLICY GATEWAY ---> OPA (Rego)
  (5 specialists)   authorize + audit
        |                  |
        | Cypher           | allow
        v                  v
     NEO4J <---------------+
        |
        +---------> GRAFANA + HUMAN OPERATORS

Optional control plane:
  TEMPORAL AttackPathPipeline
    activities: collect / synthesize / Neo4j / authorize / ticket
    signal: human_approve
```

**Control plane:** Hermes + OPA + Gateway (+ Temporal for durable loops).  
**Data plane:** Collectors → Neo4j → UI / Bots.

---

## 3. Component catalogue

### 3.1 Hermes Bots
`asset-identity-mapper`, `vuln-triage`, `attack-path-synthesizer`, `anomaly-detector`, `remediation-guidance` — SOUL.md personas + MCP tools.

### 3.2 MCP servers
Synthetic-by-default collectors; hardened Nuclei; Neo4j Cypher MCP for graph I/O.

### 3.3 MCP Policy Gateway + OPA
PEP/PDP: authorize high-impact tools; tickets only when approved.

### 3.4 Neo4j
Labels: Asset, Identity, Finding, AttackPath, Anomaly.

### 3.5 Grafana
Prioritised path tables over Neo4j.

### 3.6 Temporal (optional)

| Piece | Role |
|-------|------|
| `AttackPathPipeline` workflow | Durable collect → score → wait approval → ticket |
| Activities | Synthetic inventory/vulns, Neo4j upsert, Gateway authorize, ticket stub |
| Signal `human_approve` | Human-in-the-loop |
| Deploy | `deploy/docker-compose.temporal.yml` (:7233, UI :8088) |
| Code | `temporal/` — see [TEMPORAL.md](./TEMPORAL.md) |

Hermes = interactive specialists; Temporal = crash-safe enterprise process runtime.

---

## 4. Connections

| From | To | Mechanism |
|------|-----|-----------|
| Hermes | MCP | stdio |
| Client / Temporal activity | Gateway | HTTP `/authorize` |
| Gateway | OPA | HTTP data API |
| Neo4j MCP / Temporal activity | Neo4j | Bolt |
| Operator | Temporal | Signal `human_approve` |
| Grafana | Neo4j | Bolt plugin |

### Sequence (Temporal path)

1. Start `AttackPathPipeline`  
2. Activities collect + synthesize (synthetic or later live MCP)  
3. Upsert AttackPath to Neo4j  
4. Wait for `human_approve` (durable)  
5. Authorize via Gateway/OPA  
6. Create ticket stub (or real Jira activity later)

---

## 5. Logical layers

Ingestion → Normalisation → Reasoning → Governance → Presentation → Gated action (Temporal optional for steps 1–6 durability).

---

## 6. Physical design

**Pilot host:** Compose Neo4j, OPA, Gateway, Grafana; optional Temporal+Postgres; Hermes + workers on host.

**Enterprise tiers:** Management (CI/secrets) → Control (Hermes, Gateway, OPA, Temporal workers) → Data (Neo4j/Aura) → Presentation (SSO) → Collectors (isolated).

**Ports (private):** 7474, 7687, 8181, 8080, 3000, 7233, 8088.

**Cloud:** AWS/Azure/GCP VMs or K8s; Temporal Cloud optional; Neo4j Aura optional.

---

## 7–10. Data, security, scale, topologies

Same as kit baseline: private networks, SSO, Vault, OPA in CI, Neo4j backups, HA for production. Topologies: laptop Compose → single VM → split → K8s → Aura hybrid.

---

## 11. Extension points

Live collectors; full MCP proxy; richer Temporal activities calling Hermes/MCP; SIEM export; interactive path UI; multi-tenant graphs.

---

## 12. Related docs

| Doc | Focus |
|-----|--------|
| [TEMPORAL.md](./TEMPORAL.md) | Temporal integration |
| [INSTALL_AND_DEPLOY.md](./ops/INSTALL_AND_DEPLOY.md) | Install steps |
| [OPERATIONS.md](./ops/OPERATIONS.md) | Ops |
| [OPA_INTEGRATION.md](./OPA_INTEGRATION.md) | Policy |

---

## 13. Architect checklist

- [ ] Private Bolt / OPA / Gateway / Temporal  
- [ ] SSO on UIs  
- [ ] Secrets not in git  
- [ ] OPA + Temporal versioning in CI  
- [ ] Neo4j backup drill  
- [ ] Human approval process (Bot and/or Temporal signal)  
- [ ] Audit to SIEM  

*Hermes Bots · MCP · Gateway · OPA · Neo4j · Grafana · Temporal (optional).*
