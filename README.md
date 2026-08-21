# Hermes SkandaShield Bots

Deployment kit for building a **SkandaShield-style AI-Enabled Cybersecurity Platform** using **Hermes Agent + Bot Mode**.

This repository provides:

- Sample `SOUL.md` templates for 5 specialised Bots
- Minimal Neo4j knowledge-graph schema + useful Cypher examples
- Skeleton MCP server for one security tool (Nuclei wrapper example)
- Docker Compose that starts Hermes + Neo4j together

## Quick Start

1. Install Hermes Agent (CLI or Docker) – see [official docs](https://hermes-agent.nousresearch.com/)
2. Clone this repo
3. Copy the `bots/*/SOUL.md` files into the corresponding Hermes profiles
4. Start the stack with `docker compose -f deploy/docker-compose.yml up -d`
5. Configure MCP servers in `~/.hermes/config.yaml` (examples included)
6. Create the five Bots in Hermes Desktop / CLI and point them at the shared Neo4j graph

## Bots

| Bot | Purpose |
|-----|---------|
| `asset-identity-mapper` | Continuous discovery of applications, cloud assets, identities |
| `vuln-triage` | Ingest, deduplicate and prioritise vulnerability findings |
| `attack-path-synthesizer` | Build and rank multi-hop attack paths |
| `anomaly-detector` | Behavioural baseline learning and deviation detection |
| `remediation-guidance` | Produce engineer-ready tickets and fix guidance (gated) |

## Safety Notes

- Always run tool execution with `terminal.backend: docker` (or stricter)
- Use MCP tool filtering (`include` / `exclude`) aggressively
- Keep human approval gates for ticket creation and any auto-remediation
- Never give Bots unrestricted write access to production systems without review

## License

MIT – use freely, improve, and contribute back.
