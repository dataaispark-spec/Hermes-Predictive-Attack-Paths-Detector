# Overview — Hermes Predictive Attack Paths Detector

**Canonical repository:** [https://github.com/dataaispark-spec/Hermes-Predictive-Attack-Paths-Detector](https://github.com/dataaispark-spec/Hermes-Predictive-Attack-Paths-Detector)

## Purpose

Security teams drown in scanner output and identity sprawl. Most tools report *what is wrong in isolation*. This kit focuses on **chained, realistic attack paths** — including paths that go through **AI agents and MCP tools** — and labels hops with **MITRE ATT&CK** and **ATLAS**.

## Value

- Rank a **short list** of paths to crown jewels, not raw CVE volume  
- Unify cloud, identity, vuln, and **agent** context in **Neo4j**  
- Specialist **Hermes** bots instead of one generic chatbot  
- **OPA** + human approval before high-impact automation  
- Open components you control (no mandatory SaaS path engine)

## Scope honesty

Synthetic collectors and agent inventory by default. Production requires live integrations (BloodHound, cloud APIs, agent registries). This is a **pilot / architecture kit**, not a finished commercial APA platform.

## Name history

Previously published as `hermes-skandashield-bots`. Functionality continues under **Hermes-Predictive-Attack-Paths-Detector**.
