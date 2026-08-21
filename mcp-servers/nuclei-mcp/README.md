# Nuclei MCP Server (Skeleton)

Minimal Model Context Protocol server that exposes a safe subset of Nuclei scanning capabilities to Hermes Bots.

## Features (skeleton)
- `nuclei_scan` – run a limited Nuclei scan against a target (or list) and return findings
- Tool filtering ready for Hermes `mcp_servers` config

## Safety
- Designed for non-destructive templates only by default
- Rate-limited / scoped targets recommended
- Always run the MCP process itself inside a restricted environment

## Quick run (dev)
```bash
cd mcp-servers/nuclei-mcp
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python server.py
```

Then point Hermes at it via stdio or HTTP.
