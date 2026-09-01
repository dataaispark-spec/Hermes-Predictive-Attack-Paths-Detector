# Temporal integration

**Repo:** [https://github.com/dataaispark-spec/Hermes-Predictive-Attack-Paths-Detector](https://github.com/dataaispark-spec/Hermes-Predictive-Attack-Paths-Detector)

Optional durable workflows for attack-path pipelines that must survive process restarts and wait for **human approval** before high-impact steps (e.g. ticket creation).

- Compose: `deploy/docker-compose.temporal.yml`
- Workflow: `temporal/workflows/attack_path_pipeline.py`
- Runbook: `temporal/README.md`

Use when you need stronger guarantees than a single Hermes session. Not required for the offline MITRE / agent-path demo.
