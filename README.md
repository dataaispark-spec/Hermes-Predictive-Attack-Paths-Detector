# Hermes SkandaShield Bots

Deployment kit for building a **SkandaShield-style AI-Enabled Cybersecurity Platform** using **Hermes Agent + Bot Mode** + **OPA policy engine**.

This repository provides:

- Sample `SOUL.md` templates for 5 specialised Bots
- Minimal Neo4j knowledge-graph schema + useful Cypher examples
- Skeleton MCP server for one security tool (Nuclei wrapper example)
- Docker Compose that starts Hermes + Neo4j
- **OPA policy engine** + starter Rego package tailored to the five Bots
- **MCP Policy Gateway** skeleton (authorize-before-forward)
- Gap-closure documentation and architecture updates

## Quick Start

1. Install Hermes Agent (CLI or Docker) – see [official docs](https://hermes-agent.nousresearch.com/)
2. Clone this repo
3. Copy the `bots/*/SOUL.md` files into the corresponding Hermes profiles
4. Start the base stack:
   ```bash
   cd deploy
   docker compose up -d
   ```
5. (Recommended) Start OPA + Policy Gateway:
   ```bash
   docker compose -f docker-compose.yml -f docker-compose.opa.yml up -d
   ```
6. Configure MCP servers in `~/.hermes/config.yaml` (see `deploy/hermes-mcp-example.yaml`)
7. Create the five Bots and point high-impact tools through the policy gateway

## Bots

| Bot | Purpose |
|-----|---------|
| `asset-identity-mapper` | Continuous discovery of applications, cloud assets, identities |
| `vuln-triage` | Ingest, deduplicate and prioritise vulnerability findings |
| `attack-path-synthesizer` | Build and rank multi-hop attack paths |
| `anomaly-detector` | Behavioural baseline learning and deviation detection |
| `remediation-guidance` | Produce engineer-ready tickets and fix guidance (gated by OPA) |

## Policy Engine (OPA)

- Policies live in `policies/skandashield.rego`
- Gateway skeleton: `mcp-gateway/`
- Full guide: [docs/OPA_INTEGRATION.md](docs/OPA_INTEGRATION.md)
- Gap closure status: [docs/GAP_CLOSURE.md](docs/GAP_CLOSURE.md)

## Safety Notes

- Always run tool execution with `terminal.backend: docker` (or stricter)
- Use MCP tool filtering (`include` / `exclude`) aggressively
- Keep human approval gates for ticket creation (enforced by OPA)
- Never give Bots unrestricted write access to production systems without review
- Change the Neo4j password before any real deployment

## License

MIT – use freely, improve, and contribute back.
