# Analysis: LLM-first vs full third-party stack

**Branch:** `brainstorm/llm-first-slim-profile`  
**Canonical product repo:** https://github.com/dataaispark-spec/Hermes-Predictive-Attack-Paths-Detector  
**Date context:** 2026-09 (brainstorm capture)

---

## 1. Question

Is it really required to use all the third-party tools currently wired in the repository?  
Why not rely on **very specialized / customized LLMs** to think, observe, orchestrate, detect, predict, and protect proactively?

---

## 2. Short answer

| Claim | Verdict |
|-------|---------|
| Every third-party component is mandatory for the *idea* | **No** |
| Specialized LLMs can replace *all* sense, memory, and governance | **No** |
| Specialized LLMs should own reasoning, ranking, explanation, proposal | **Yes** |
| Proactive *protect* needs policy + human/control plane beyond the model | **Yes** |

Third-party tools accelerate **sense / memory / govern**. They are not the thesis. The thesis is **path-centric, evidence-grounded prediction** (including AI-agent paths), with safe action.

---

## 3. What the current `main` stack layers do

| Layer | Examples on main | Job |
|-------|------------------|-----|
| Sense | MCP collectors (Nuclei, BloodHound template, cloud, ThreatMapper, agent-path, …) | Facts about the environment |
| Memory | Neo4j | Durable topology: assets, agents, paths, techniques |
| Reason | Hermes bots + LLMs + MITRE mapper | Rank paths, explain, propose |
| Govern | OPA, MCP gateway, human approval, Temporal | Constrain automation |
| Act | Tickets / remediation guidance (gated) | Change the real world |
| Observe UX | Grafana | Human visibility |
| LLM routing | llm-router, optional LiteLLM | Local-first + cyber preference |

**LLMs primarily sit in Reason (and soft Orchestrate).** They are weak as the sole Sense, durable Memory, or Act layer unless those jobs are rebuilt around them with structure and gates.

---

## 4. What is *not* required on day one

For a research pilot or internal verification, these can be **deferred** without killing the concept:

- Temporal (durable workflow) — optional until multi-step approval must survive restarts  
- Grafana — optional until operators need dashboards  
- LiteLLM — optional if a single local/cloud model is enough  
- Full mesh of MCP servers — start with **one** real or file-based inventory feed  
- Neo4j — can start with strict JSON/SQLite tables until path queries demand a graph DB  
- Hermes Bot Mode — can prototype with plain Python + LLM API + SOUL-like prompts  

---

## 5. What you still cannot drop (if honest about “detect / predict / protect”)

1. **Grounding** — evidence from the estate (inventory, vulns, agent tools, identity), not only model prose.  
2. **State** — paths and decisions that persist and can be audited.  
3. **Control** — limits on high-impact actions (shell, IAM, ticket create), especially when agents are in the path.

Without these: **persuasive advisor**, not proactive defender.

---

## 6. Failure modes of pure-LLM architectures

| Failure | Why |
|---------|-----|
| Hallucinated paths | Invented edges not present in the estate |
| Poisoned context | Logs, tickets, RAG, tool output → prompt injection |
| No continuous observe | Models do not natively sit on telemetry pipes |
| No durable map | Context window ≠ multi-month enterprise topology |
| Unsafe act | Auto-remediate without policy is itself an attack path |
| Non-determinism | Same inputs, different rankings across runs |
| Weak audit | Boards need IDs, CVEs, technique tags, not only narrative |

---

## 7. Recommended LLM-centric but grounded loop

```
Environment signals  →  thin collectors (1–2 feeds or file inventory)
         ↓
Structured world model (graph DB *or* strict tables)
         ↓
Specialized LLMs
   • Observer  – summarize deltas vs baseline
   • Predictor – path / agent-tool hypotheses
   • Critic    – require evidence IDs; reject ungrounded hops
   • Advisor   – remediation language for engineers
         ↓
Policy gate (thin OPA or even code allow-list) + human for high impact
         ↓
Optional act (ticket, config suggestion)
```

MITRE ATT&CK / ATLAS remains the **shared hop language** whether human or model fills labels.

**Job split**

| Verb | Primary mechanism | LLM role |
|------|-------------------|----------|
| Observe | Telemetry / inventory | Summarize |
| Detect | Rules, queries, baselines | Correlate |
| Predict | Path search on real map + score | Rank / what-if / explain |
| Protect | Controls + gated change | Propose only by default |

---

## 8. Proposed “slim profile” relative to main

| Keep | Slim default | Full kit on main |
|------|--------------|------------------|
| Reason | Predictor + Critic prompts / scripts | All Hermes bots |
| MITRE | `mitre/` mapper | Same |
| Sense | File or single MCP | Many MCP servers |
| Memory | JSON/SQLite stub → optional Neo4j | Neo4j first-class |
| Govern | Minimal allow-list module | Full OPA + gateway |
| Orchestration | Single Python loop | Temporal + Compose mesh |

**Merge rule:** Slim profile should be **additive** (`profiles/llm-first-slim/`), not a deletion of the full stack on `main`.

---

## 9. Verification ideas (before merge)

1. Run `profiles/llm-first-slim/run_slim_demo.py` offline — produces ranked paths with MITRE IDs from structured inventory only.  
2. Compare output quality vs `scripts/detect_agent_attack_paths.py` on main (agent-path synthetic set).  
3. Threat-model: inject hostile “finding” text; confirm Critic rejects paths without evidence IDs.  
4. Decide: document-only merge vs also ship slim profile code.  
5. Explicitly list which Compose services remain **recommended** vs **optional** in root README (if docs merge accepted).

---

## 10. Bottom line

- **Required:** grounded observation + durable estate model + constrained action.  
- **High leverage:** specialized/custom LLMs for think, orchestrate, explain, prioritize.  
- **Insufficient alone:** LLM as only observer, only database, and only protector.  
- **Repo direction:** offer an **LLM-first slim profile** for pilots; keep full Hermes/Neo4j/OPA/MCP kit for enterprise-shaped deployments.
