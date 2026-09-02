# Manual merge checklist — `brainstorm/llm-first-slim-profile` → `main`

**Do not auto-merge.** Reviewers own the decision.

## Repo

https://github.com/dataaispark-spec/Hermes-Predictive-Attack-Paths-Detector

## Branch

`brainstorm/llm-first-slim-profile`

---

## A. Docs-only merge (low risk)

- [ ] Read `docs/brainstorm/LLM_FIRST_SLIM_ANALYSIS.md`
- [ ] Agree wording does not over-claim production APA
- [ ] Agree slim profile is **optional**, full stack remains default
- [ ] Move or copy analysis under `docs/` on main (e.g. `docs/LLM_FIRST_SLIM_ANALYSIS.md`)
- [ ] Add a short “Optional profiles” pointer in root `README.md`
- [ ] Changelog note: brainstorm accepted / deferred

## B. Code merge (`profiles/llm-first-slim/`)

- [ ] `run_slim_demo.py` runs with stdlib only (or documented minimal deps)
- [ ] Does not break existing `scripts/detect_agent_attack_paths.py`
- [ ] No removal of MCP/Neo4j/OPA from default path
- [ ] Security: no auto-remediation; propose-only
- [ ] Critic requires evidence-style IDs for accepted hops
- [ ] Tests or smoke documented in profile README

## C. Reject / park

- [ ] If rejected, leave branch open with comment “parked” or delete after archiving analysis into an issue
- [ ] Record decision date and owner

## D. Post-merge

- [ ] Update roadmap row: LLM-first slim profile experimental / supported
- [ ] Close related discussion issue if any
