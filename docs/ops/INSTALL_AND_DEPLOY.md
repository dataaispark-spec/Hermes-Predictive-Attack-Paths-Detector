# Full Installation, Configuration, Customisation & Deployment Guide

Step-by-step instructions for **Linux, macOS, WSL2, Docker, and cloud (AWS / Azure / GCP)**.  
Examples use placeholders — replace passwords, paths, and account IDs before production use.

---

## Table of contents

1. [Prerequisites by platform](#1-prerequisites-by-platform)
2. [Install Hermes Agent](#2-install-hermes-agent)
3. [Clone the kit](#3-clone-the-kit)
4. [Local Docker stack (recommended)](#4-local-docker-stack-recommended)
5. [Hermes configuration (full example)](#5-hermes-configuration-full-example)
6. [Create the five Bots](#6-create-the-five-bots)
7. [Seed data & verify](#7-seed-data--verify)
8. [Customisation](#8-customisation)
9. [Cloud deployment](#9-cloud-deployment)
10. [Troubleshooting](#10-troubleshooting)
11. [Production checklist](#11-production-checklist)

---

## 1. Prerequisites by platform

### Common

| Component | Version / notes |
|-----------|-----------------|
| Docker | 24+ with Compose v2 (`docker compose version`) |
| Python | 3.11 or 3.12 (for MCP servers & seed script) |
| Git | Any recent |
| Optional | `opa` CLI, `nuclei`, `uv` / `uvx` |

### Linux (Ubuntu 22.04 / 24.04 example)

```bash
sudo apt update
sudo apt install -y git curl python3 python3-pip python3-venv docker.io docker-compose-v2
sudo usermod -aG docker $USER
# log out and back in for docker group
```

### macOS

```bash
# Homebrew
brew install git python@3.12
# Docker Desktop from https://www.docker.com/products/docker-desktop/
# Ensure "Docker Compose" is enabled in Docker Desktop settings
```

### Windows (WSL2)

1. Install WSL2 + Ubuntu from Microsoft Store.
2. Inside Ubuntu, follow the **Linux** steps above.
3. Install Docker Desktop for Windows with **WSL2 backend** enabled.
4. Run all commands inside the WSL2 Ubuntu shell (not PowerShell).

### Verify

```bash
docker --version
docker compose version
python3 --version   # >= 3.11
git --version
```

---

## 2. Install Hermes Agent

### Option A — Official installer (Linux / macOS / WSL2)

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
source ~/.bashrc    # or ~/.zshrc
hermes --version
hermes doctor
hermes setup        # interactive: model provider, API keys
```

### Option B — Docker-only Hermes

```bash
mkdir -p ~/.hermes
docker run -it --rm -v ~/.hermes:/opt/data nousresearch/hermes-agent setup
```

### Option C — MCP extras if missing

```bash
cd ~/.hermes/hermes-agent   # path may vary
uv pip install -e ".[mcp]" 2>/dev/null || true
```

---

## 3. Clone the kit

```bash
git clone https://github.com/dataaispark-spec/hermes-skandashield-bots.git
cd hermes-skandashield-bots
export KIT_ROOT=$(pwd)
```

Install Python deps for local MCP servers and seed script:

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows WSL: same
pip install -U pip
pip install mcp pydantic neo4j httpx fastapi uvicorn
pip install -r mcp-servers/nuclei-mcp/requirements.txt
```

---

## 4. Local Docker stack (recommended)

### 4.1 Change default passwords

Edit before first start:

- `deploy/docker-compose.yml` → `NEO4J_AUTH` (e.g. `neo4j/YourStrongPasswordHere`)
- `deploy/docker-compose.ui.yml` → `GF_SECURITY_ADMIN_PASSWORD`
- `ui/grafana/provisioning/datasources/neo4j.yaml` → matching Neo4j password

### 4.2 Start services

```bash
cd $KIT_ROOT/deploy

# Full stack: Neo4j + OPA + MCP Gateway + Grafana
docker compose \
  -f docker-compose.yml \
  -f docker-compose.opa.yml \
  -f docker-compose.ui.yml \
  up -d

docker compose -f docker-compose.yml -f docker-compose.opa.yml -f docker-compose.ui.yml ps
```

### 4.3 Health checks

```bash
curl -s http://localhost:8181/health          # OPA
curl -s http://localhost:8080/health          # MCP Gateway
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:7474   # Neo4j browser
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3000   # Grafana
```

| Service | URL / port |
|---------|------------|
| Neo4j Browser | http://localhost:7474 |
| Neo4j Bolt | bolt://localhost:7687 |
| OPA | http://localhost:8181 |
| MCP Gateway | http://localhost:8080 |
| Grafana | http://localhost:3000 |

---

## 5. Hermes configuration (full example)

Create or edit `~/.hermes/config.yaml`.

**Path note:** replace `/absolute/path/to/hermes-skandashield-bots` with `$KIT_ROOT`.

```yaml
terminal:
  backend: docker
  timeout: 180

model:
  default: anthropic/claude-sonnet-4
  provider: openrouter

mcp_servers:
  neo4j:
    command: "uvx"
    args: ["mcp-neo4j-cypher"]
    env:
      NEO4J_URI: "bolt://localhost:7687"
      NEO4J_USERNAME: "neo4j"
      NEO4J_PASSWORD: "YourStrongPasswordHere"
    tools:
      include: ["get_neo4j_schema", "read_neo4j_cypher", "write_neo4j_cypher"]

  nuclei:
    command: "python"
    args: ["/absolute/path/to/hermes-skandashield-bots/mcp-servers/nuclei-mcp/server.py"]
    env:
      NUCLEI_ALLOWED_SEVERITIES: "info,low,medium"
      NUCLEI_RATE_LIMIT_PER_MIN: "5"
      NUCLEI_TARGET_ALLOWLIST: "http://lab.,https://staging."
    tools:
      include: ["nuclei_scan"]

  bloodhound:
    command: "python"
    args: ["/absolute/path/to/hermes-skandashield-bots/mcp-servers/bloodhound-mcp/server.py"]
    env:
      BLOODHOUND_MODE: "synthetic"
    tools:
      include: ["bh_list_domains", "bh_shortest_paths_to_da", "bh_export_graph_fragment"]

  cloud_inventory:
    command: "python"
    args: ["/absolute/path/to/hermes-skandashield-bots/mcp-servers/cloud-inventory-mcp/server.py"]
    env:
      CLOUD_MODE: "synthetic"
    tools:
      include: ["cloud_list_accounts", "cloud_inventory_assets", "cloud_internet_facing"]

  threatmapper:
    command: "python"
    args: ["/absolute/path/to/hermes-skandashield-bots/mcp-servers/threatmapper-mcp/server.py"]
    env:
      THREATMAPPER_MODE: "synthetic"
    tools:
      include: ["tm_list_vulnerabilities", "tm_attack_paths", "tm_node_topology"]

  anomaly:
    command: "python"
    args: ["/absolute/path/to/hermes-skandashield-bots/mcp-servers/anomaly-detector-mcp/server.py"]
    env:
      ANOMALY_WINDOW: "20"
      ANOMALY_Z_THRESHOLD: "3.0"
    tools:
      include: ["anomaly_observe", "anomaly_list_recent", "anomaly_seed_baseline"]

  external_surface:
    command: "python"
    args: ["/absolute/path/to/hermes-skandashield-bots/mcp-servers/external-surface-mcp/server.py"]
    env:
      BRAND_DOMAINS: "yourcompany.com,yourbrand.io"
    tools:
      include: ["surface_check_lookalikes", "surface_internet_facing_summary", "surface_register_exposure"]
```

Secrets in `~/.hermes/.env` (never commit):

```bash
NEO4J_PASSWORD=YourStrongPasswordHere
```

Verify:

```bash
hermes chat
# Ask: "List available MCP tools" or "Call bh_list_domains"
```

Also see `deploy/hermes-mcp-example.yaml` in the repo.

---

## 6. Create the five Bots

1. Open Hermes Desktop → Bots / Profiles (or use CLI for your Hermes version).
2. Create one Bot per name: `asset-identity-mapper`, `vuln-triage`, `attack-path-synthesizer`, `anomaly-detector`, `remediation-guidance`.
3. Paste each `bots/<name>/SOUL.md` into that Bot’s system / soul instructions.
4. Attach only the MCP tools that Bot should use (least privilege).

**Remediation Guidance** stays propose-only; OPA denies ticket creation until `human_approved: true`.

---

## 7. Seed data & verify

```bash
cd $KIT_ROOT
source .venv/bin/activate
python scripts/seed_graph.py \
  --uri bolt://localhost:7687 \
  --user neo4j \
  --password YourStrongPasswordHere

python scripts/mock_test_collectors.py
# Expect: All mock checks passed.

bash scripts/run_rego_tests.sh   # needs opa CLI
```

Grafana: http://localhost:3000 → **SkandaShield Attack Paths**.

OPA deny test:

```bash
curl -s -X POST http://localhost:8080/authorize \
  -H "Content-Type: application/json" \
  -d '{"bot":"remediation-guidance","tool":"jira.create_issue","args":{},"context":{"human_approved":false}}'
# Expect allow: false
```

---

## 8. Customisation

### Collectors synthetic → live

| Server | Env |
|--------|-----|
| BloodHound | `BLOODHOUND_MODE=live`, `BLOODHOUND_API_URL`, `BLOODHOUND_TOKEN` |
| Cloud | `CLOUD_MODE=live` + provider credentials |
| ThreatMapper | `THREATMAPPER_MODE=live`, `THREATMAPPER_URL`, `THREATMAPPER_API_KEY` |

### Brand domains

```yaml
env:
  BRAND_DOMAINS: "acme.com,acme.io"
```

### Nuclei safety

```yaml
env:
  NUCLEI_ALLOWED_SEVERITIES: "info,low"
  NUCLEI_TARGET_ALLOWLIST: "https://staging.example.com"
  NUCLEI_RATE_LIMIT_PER_MIN: "3"
```

### OPA policy

Edit `policies/skandashield.rego`, restart OPA, run `bash scripts/run_rego_tests.sh`.

### Anomaly thresholds

```yaml
env:
  ANOMALY_WINDOW: "30"
  ANOMALY_Z_THRESHOLD: "2.5"
```

---

## 9. Cloud deployment

Always keep Neo4j, OPA, and Grafana on private networks. Do not expose Bolt or OPA publicly.

### AWS (EC2 + Docker)

```bash
# Amazon Linux 2023 or Ubuntu EC2
sudo yum install -y docker git   # or apt on Ubuntu
sudo systemctl enable --now docker
sudo usermod -aG docker ec2-user

git clone https://github.com/dataaispark-spec/hermes-skandashield-bots.git
cd hermes-skandashield-bots/deploy
# Edit passwords in compose files
docker compose -f docker-compose.yml -f docker-compose.opa.yml -f docker-compose.ui.yml up -d
```

Security groups: allow only your IP/bastion to ports 3000, 7474, 8080, 8181, 8642.

### Azure (VM + Docker)

```bash
sudo apt update && sudo apt install -y docker.io docker-compose-v2 git
sudo usermod -aG docker $USER
# re-login, then same clone + compose
```

Use NSG + Key Vault for secrets.

### GCP (Compute Engine + Docker)

```bash
sudo apt update && sudo apt install -y docker.io docker-compose-v2 git
sudo usermod -aG docker $USER
# same compose workflow
```

Use VPC firewall rules + Secret Manager.

### Kubernetes (outline)

1. Namespace `skandashield`.
2. Neo4j (Helm/operator), OPA, MCP Gateway, Grafana as Deployments.
3. ConfigMap for `policies/`; Secrets for passwords.
4. Hermes with in-cluster `bolt://neo4j:7687`.
5. NetworkPolicies: Bots → Gateway → OPA only for tool paths.

### Managed Neo4j (Aura)

```yaml
env:
  NEO4J_URI: "neo4j+s://xxxx.databases.neo4j.io"
  NEO4J_USERNAME: "neo4j"
  NEO4J_PASSWORD: "<aura-password>"
```

---

## 10. Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| MCP tools not listed | Wrong path / missing deps | Absolute path; `pip install mcp` |
| Neo4j connection refused | Bad password / not healthy | `docker compose logs neo4j` |
| OPA always deny | Policy not loaded | Restart opa; check `/v1/policies` |
| Grafana empty | No data / wrong DS password | `seed_graph.py`; fix neo4j.yaml |
| Nuclei binary not found | Not on PATH | Install nuclei or lab-only |
| Docker permission denied | Not in docker group | `usermod -aG docker $USER` |

---

## 11. Production checklist

- [ ] All default passwords rotated
- [ ] Neo4j/Grafana not public
- [ ] Nuclei allowlist = lab/staging only
- [ ] OPA + mock tests pass
- [ ] `terminal.backend: docker`
- [ ] Secrets only in `.env` / secret manager
- [ ] Neo4j volume backups
- [ ] Audit logs retained
- [ ] Document who may set `human_approved: true`

---

## Quick reference — one-shot local demo

```bash
cd hermes-skandashield-bots
python3 -m venv .venv && source .venv/bin/activate
pip install mcp pydantic neo4j

# Edit passwords in deploy/*.yml
cd deploy
docker compose -f docker-compose.yml -f docker-compose.opa.yml -f docker-compose.ui.yml up -d
cd ..
python scripts/seed_graph.py --password YourStrongPasswordHere
python scripts/mock_test_collectors.py

# Configure ~/.hermes/config.yaml (section 5), create Bots (section 6)
# Open http://localhost:3000 and hermes chat
```

Day-to-day operations: [OPERATIONS.md](./OPERATIONS.md).
