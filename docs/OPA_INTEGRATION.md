# OPA integration

**Repo:** [https://github.com/dataaispark-spec/Hermes-Predictive-Attack-Paths-Detector](https://github.com/dataaispark-spec/Hermes-Predictive-Attack-Paths-Detector)

- Policies: `policies/skandashield.rego`, `policies/data.json`
- Gateway: `mcp-gateway/gateway.py`
- Compose: `deploy/docker-compose.opa.yml`
- Tests: `tests/rego/`, `scripts/run_rego_tests.sh`

Default posture: **deny** high-impact tools (e.g. unrestricted shell, ticket create) unless input satisfies allow rules (role, human_approved, etc.).

Package naming may still use `skandashield` in Rego for continuity; the **project name** is Hermes Predictive Attack Paths Detector.
