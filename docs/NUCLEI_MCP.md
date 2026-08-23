# Nuclei MCP integration

Hardened wrapper around [ProjectDiscovery Nuclei](https://github.com/projectdiscovery/nuclei) for Hermes bots.

## Features

| Control | Env / behaviour |
|---------|------------------|
| Severity allow-list | `NUCLEI_ALLOWED_SEVERITIES` (default `info,low,medium`) |
| Tag allow-list | `NUCLEI_ALLOWED_TAGS` (default `ssl,tls,http,dns,tech,cve,misconfig,exposure`; `*` = unrestricted) |
| Template path allow-list | `NUCLEI_TEMPLATE_ALLOW_DIRS` — custom `-t` only under these dirs |
| Target allow-list | `NUCLEI_TARGET_ALLOWLIST` |
| Rate limit | `NUCLEI_RATE_LIMIT_PER_MIN` |
| Caps | `NUCLEI_MAX_TARGETS`, `NUCLEI_MAX_FINDINGS` |
| Audit | `NUCLEI_AUDIT_LOG` JSONL |
| Neo4j upsert | `NUCLEI_NEO4J_UPSERT=true` + `NEO4J_URI` / `NEO4J_USER` / `NEO4J_PASSWORD` |

OPA (gateway) further restricts **which bot** may call `nuclei_scan` and when **human_approved** is required.

## Tool: `nuclei_scan`

```json
{
  "targets": ["https://scanme.sh"],
  "severity": ["info", "low"],
  "tags": ["ssl", "http"],
  "templates": [],
  "timeout_minutes": 5,
  "upsert_graph": true
}
```

- **tags** must be in `NUCLEI_ALLOWED_TAGS` (unless `*`).
- **templates** paths must sit under `NUCLEI_TEMPLATE_ALLOW_DIRS` when set; otherwise custom templates are rejected by default.
- **upsert_graph** writes `:Finding` + `:Asset` + `HAS_VULN` when Neo4j upsert is enabled on the server.

## Hermes config example

```yaml
mcp_servers:
  nuclei:
    command: "python"
    args: ["/path/to/mcp-servers/nuclei-mcp/server.py"]
    env:
      NUCLEI_ALLOWED_SEVERITIES: "info,low,medium"
      NUCLEI_ALLOWED_TAGS: "ssl,tls,http,dns,tech,cve,misconfig,exposure"
      NUCLEI_TEMPLATE_ALLOW_DIRS: "/opt/nuclei-templates/approved"
      NUCLEI_TARGET_ALLOWLIST: "https://scanme.sh,.staging.example.com"
      NUCLEI_RATE_LIMIT_PER_MIN: "3"
      NUCLEI_NEO4J_UPSERT: "true"
      NEO4J_URI: "bolt://127.0.0.1:7687"
      NEO4J_USER: "neo4j"
      NEO4J_PASSWORD: "<rotate-me>"
    tools:
      include: ["nuclei_scan"]
```

Requires `nuclei` on `PATH` and optionally `pip install neo4j`.

## OPA rules (summary)

See [policies/skandashield.rego](../policies/skandashield.rego):

| Condition | Result |
|-----------|--------|
| Bot not `vuln-triage` or `asset-identity-mapper` | Deny |
| Severity only info/low/medium, scope not production | Allow |
| Severity high/critical **or** `context.scope == "production"` | Allow only if `context.human_approved == true` |

Example gateway input:

```json
{
  "bot": "vuln-triage",
  "tool": "nuclei_scan",
  "args": { "severity": ["low"], "targets": ["https://scanme.sh"] },
  "context": { "scope": "lab", "human_approved": false }
}
```

## Graph mapping

```cypher
MERGE (a:Asset {id: $aid})
MERGE (f:Finding {id: $fid})
SET f.source = 'nuclei', f.template_id = $template_id, f.severity = $severity, ...
MERGE (a)-[:HAS_VULN]->(f)
```

Finding ids are stable hashes of `template-id|matched-at`.

## Safety notes

- Prefer scanner in Docker with no host network and read-only template mounts.
- Do not set `NUCLEI_ALLOWED_TAGS=*` in production.
- Keep production targets behind human approval via OPA.
- Path ranking still happens in Neo4j + attack-path bot — Nuclei only supplies findings.
