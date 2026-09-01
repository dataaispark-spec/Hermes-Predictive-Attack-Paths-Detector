# How we differ

**Project:** [Hermes-Predictive-Attack-Paths-Detector](https://github.com/dataaispark-spec/Hermes-Predictive-Attack-Paths-Detector)  
*(formerly `hermes-skandashield-bots`)*

This kit is an **open, agent-orchestrated path layer** you run and extend. It is not a managed CTEM/APA SaaS.

| Dimension | This repository | Typical commercial platforms |
|-----------|-----------------|------------------------------|
| Ownership | You own agents, graph, policy, pipelines as code | Vendor owns product & data plane |
| Agents | Specialist Hermes bots + SOUL.md | Closed copilots / fixed workflows |
| Graph | Your Neo4j via MCP | Vendor graph |
| AI-agent paths | First-class AgentAttackPath + ATLAS | Often identity/cloud only |
| MITRE | Explicit hop → ATT&CK/ATLAS map | Varies; not always exportable as code |
| LLM | Local-first router option | Usually cloud-only |
| Policy | OPA default-deny in-repo | Proprietary gates |
| Cost model | MIT templates; infra you pay for | Subscription |

**Complements, does not replace:** BloodHound CE/Enterprise, XM Cyber, CrowdStrike APA, Wiz, Tenable, SIEM/SOAR, BAS tools. Ingest their signals; rank paths and agent tool risk here.

For vendor-style comparison tables and narrative, keep this doc updated as integrations mature.
