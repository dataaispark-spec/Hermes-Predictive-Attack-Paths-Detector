# Brainstorm branch — LLM-first slim profile

**Branch:** `brainstorm/llm-first-slim-profile`  
**Repo:** [Hermes-Predictive-Attack-Paths-Detector](https://github.com/dataaispark-spec/Hermes-Predictive-Attack-Paths-Detector)  
**Status:** **Proposal only** — for verification and analysis; **manual merge into `main` when ready**

## Why this branch exists

A design discussion asked: *Are all current third-party tools required, or can specialized/custom LLMs think, observe, orchestrate, detect, predict, and protect?*

Conclusion (summary):

- **Not every** Compose service / MCP is required for the *concept*.
- **Specialized LLMs** can own think / rank / explain / propose orchestration.
- **Something outside the LLM** is still required for grounding, durable state, and safe action (observe → map → gate).

This branch captures that analysis and an optional **slim profile** skeleton so reviewers can compare against the full kit on `main` without changing production defaults.

## Contents

| Path | Purpose |
|------|---------|
| [LLM_FIRST_SLIM_ANALYSIS.md](./LLM_FIRST_SLIM_ANALYSIS.md) | Full brainstorm write-up |
| [MERGE_CHECKLIST.md](./MERGE_CHECKLIST.md) | Manual merge / rejection checklist |
| [../profiles/llm-first-slim/](../profiles/llm-first-slim/) | Optional minimal layout (docs + stub code) |

## How to review

```bash
git clone https://github.com/dataaispark-spec/Hermes-Predictive-Attack-Paths-Detector.git
cd Hermes-Predictive-Attack-Paths-Detector
git fetch origin
git checkout brainstorm/llm-first-slim-profile

# Read analysis
less docs/brainstorm/LLM_FIRST_SLIM_ANALYSIS.md

# Optional stub demo (no Neo4j/Docker required)
python profiles/llm-first-slim/run_slim_demo.py
```

## Merge policy

- Do **not** auto-merge to `main`.
- Use [MERGE_CHECKLIST.md](./MERGE_CHECKLIST.md).
- Prefer merging **docs first**, then any slim-profile code as an *optional* path that does not remove the full stack.
