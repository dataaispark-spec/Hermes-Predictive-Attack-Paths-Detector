# Install and deploy

**Repo:** [https://github.com/dataaispark-spec/Hermes-Predictive-Attack-Paths-Detector](https://github.com/dataaispark-spec/Hermes-Predictive-Attack-Paths-Detector)

## Clone

```bash
git clone https://github.com/dataaispark-spec/Hermes-Predictive-Attack-Paths-Detector.git
cd Hermes-Predictive-Attack-Paths-Detector
```

> Old name `hermes-skandashield-bots` redirects only if GitHub still has a redirect; always prefer the URL above.

## Platforms

| Environment | Notes |
|-------------|--------|
| Linux | Recommended for Docker Compose production-like pilots |
| macOS | Docker Desktop; allocate enough RAM for Neo4j |
| WSL2 | Use Linux containers; store repo on Linux filesystem |
| Cloud VM | Open only UI/gateway ports you need; keep Bolt private |

## Minimal (no Docker)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install neo4j pydantic mcp   # as needed
python mitre/mapper.py --list-hops
python scripts/detect_agent_attack_paths.py
```

## Docker stack

```bash
cd deploy
# Change default passwords first
docker compose -f docker-compose.yml -f docker-compose.opa.yml -f docker-compose.ui.yml up -d
```

Overlays: `docker-compose.temporal.yml`, `docker-compose.litellm.yml`.

## Hermes

Install [Hermes Agent](https://github.com/NousResearch/hermes-agent) via official docs, enable Bot Mode, load `bots/*/SOUL.md`, attach MCP servers from `deploy/hermes-mcp-example.yaml`.

## Post-install checks

```bash
python scripts/detect_agent_attack_paths.py
python scripts/seed_graph.py --password '<pw>'   # if Neo4j up
bash scripts/run_rego_tests.sh                   # if opa CLI present
```
