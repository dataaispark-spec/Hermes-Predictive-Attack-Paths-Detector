# OPA Policy Engine Integration Guide

This document closes the policy-engine gap identified in the architecture analysis.

## Components added

| Path | Purpose |
|------|---------|
| `policies/skandashield.rego` | Full starter Rego package tailored to the five Bots |
| `policies/data.json` | Optional external data (bot roles, environment flags) |
| `mcp-gateway/` | Minimal FastAPI skeleton that queries OPA before allowing tool calls |
| `deploy/docker-compose.opa.yml` | Adds OPA + gateway to the existing stack |

## Quick start

```bash
cd hermes-skandashield-bots/deploy
docker compose -f docker-compose.yml -f docker-compose.opa.yml up -d

# Verify OPA
curl -s http://localhost:8181/health

# Test a decision
curl -s -X POST http://localhost:8080/authorize \
  -H "Content-Type: application/json" \
  -d '{
    "bot": "remediation-guidance",
    "tool": "jira.create_issue",
    "args": {},
    "context": {"human_approved": false}
  }' | jq
# Expected: allow=false
```

## Policy summary (five Bots)

- **asset-identity-mapper** – may write non-destructive graph updates
- **vuln-triage** – read + nuclei_scan
- **attack-path-synthesizer** – may write non-destructive graph updates (paths)
- **anomaly-detector** – read-only
- **remediation-guidance** – ticket creation only when `context.human_approved == true`

All other combinations default to deny.

## Production hardening checklist

1. Replace the skeleton gateway with a full MCP protocol proxy (or client-side interceptor).
2. Bind Bot identity cryptographically (signed session token from Hermes).
3. Ship OPA decision logs to SIEM / OpenTelemetry.
4. Add rate limits and circuit breaker around OPA.
5. Unit-test Rego with `opa test policies/`.
6. Use OPA Bundles or OPAL for hot-reload of policies.
7. Fail closed on OPA unavailability (already implemented in skeleton).

## Integration with Hermes

Point high-impact MCP servers at the gateway (or wrap tool calls with a pre-flight `/authorize` request). Keep the Remediation Guidance Bot in propose-only mode until a human sets `human_approved: true`.
