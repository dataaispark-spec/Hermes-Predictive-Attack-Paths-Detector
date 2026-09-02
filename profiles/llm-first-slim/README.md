# Profile: LLM-first slim (experimental)

**Branch:** `brainstorm/llm-first-slim-profile`  
**Status:** Skeleton for verification — not the default product path on `main` until manually merged.

## Intent

Minimal loop:

1. **Structured inventory** (file JSON) — grounding  
2. **Deterministic path hypotheses** from inventory edges  
3. **MITRE labels** via existing `mitre/mapper.py` when available  
4. **Critic rules** — drop hops/paths without evidence IDs  
5. **Propose-only** output — no tickets, no shell  

Optional later: swap file inventory for one MCP; swap rules for a specialized LLM predictor/critic with the same I/O schema.

## Run

From repo root:

```bash
python profiles/llm-first-slim/run_slim_demo.py
python profiles/llm-first-slim/run_slim_demo.py --json
```

## Files

| File | Role |
|------|------|
| `inventory.sample.json` | Synthetic estate (assets, agents, edges) |
| `run_slim_demo.py` | Observe → hypothesize paths → critic → report |
| `README.md` | This file |

## Non-goals

- Replace Neo4j/OPA/Hermes on main  
- Live remediation  
- Claim better accuracy than graph+BloodHound without evidence  
