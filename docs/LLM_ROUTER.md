# Dynamic LLM Router

Local-first, multi-provider routing with **preference for cybersecurity-oriented models** when the task looks security-related.

## Why not only Hermes built-ins?

Hermes already supports:

- **`fallback_providers`** — ordered failover when the primary model errors
- **`provider_routing`** — OpenRouter sub-provider preferences

Those are excellent for *runtime failover*. This kit adds a **selection layer** that:

1. **Probes** local Ollama / vLLM / LM Studio before any cloud call  
2. **Classifies** prompts (cyber vs general) with keyword heuristics  
3. **Prefers** cyber-specialised local models (Foundation-Sec, SecGPT, …) when present  
4. Emits a **Hermes-ready** `model` + `fallback_providers` snippet  
5. Optionally fronts everything with **LiteLLM** (industry-standard open proxy)

## Architecture

```
Bot / Hermes / Temporal activity
        │
        ▼
 llm-router/router.py   ← local-first probe + cyber preference
        │
   ┌───────────────────────────────┐
   │ Local healthy?                              │
   │   yes → Ollama / vLLM / LM Studio / LiteLLM │
   │   no  → OpenRouter / Anthropic / OpenAI     │
   └────────────────────────────────┘
```

## Existing solutions we integrate (not reinvent)

| Solution | Role in this kit |
|----------|------------------|
| **Hermes `fallback_providers`** | Native runtime failover after a model is chosen |
| **Hermes `provider_routing`** | OpenRouter quality/cost/order preferences |
| **LiteLLM** (optional Compose) | Self-hosted OpenAI-compatible multi-provider gateway |
| **Ollama / vLLM / LM Studio** | Local inference backends |
| **OpenRouter** | Broad cloud catalog when local is down |
| **Foundation-Sec / SecGPT** (HF) | Cyber-specialised weights to run locally when available |

We **build** the thin router (`router.py`) because Hermes does not auto-probe “local first + cyber model preference” out of the box. We **do not** replace LiteLLM or Hermes failover.

## Cyber-oriented models (preference list)

When the prompt matches security keywords (CVE, attack path, BloodHound, MITRE, …), the router prefers `cyber_models` on each endpoint:

| Model family | Notes |
|--------------|--------|
| **Foundation-Sec-8B / Instruct / Reasoning** (Cisco Foundation AI) | Cyber-specialised Llama 3.1 derivatives; run via Ollama/vLLM after conversion |
| **SecGPT** (Clouditera family) | Security-corpus instruction models |
| Strong general cloud (Claude / GPT-4o) | Used when local cyber weights are absent |

Always review license and acceptable-use before deploying specialised security models.

## Quick start

```bash
cd hermes-skandashield-bots

# Probe machine and print decision
python llm-router/router.py --prompt "Rank attack paths for this CVE and BloodHound edge"

# JSON / Hermes snippet
python llm-router/router.py --prompt "attack path" --json
python llm-router/router.py --prompt "attack path" --hermes

# Force modes
python llm-router/router.py --force-cyber --no-probe
python llm-router/router.py --force-general --prompt "Write a haiku"
```

### Wire into Hermes

1. Copy [llm-router/hermes_local_first.yaml](../llm-router/hermes_local_first.yaml) keys into `~/.hermes/config.yaml`  
2. Or paste output of `router.py --hermes`  
3. Use `hermes fallback list` / `hermes fallback add` to maintain the chain  
4. Optionally pin Bot profiles (e.g. attack-path-synthesizer) to a cyber local model  

### Optional LiteLLM gateway

```bash
export LITELLM_MASTER_KEY=sk-change-me
# optional cloud keys
export OPENAI_API_KEY=... ANTHROPIC_API_KEY=... OPENROUTER_API_KEY=...

cd deploy
docker compose -f docker-compose.litellm.yml up -d
# Proxy: http://127.0.0.1:4000
```

Point Hermes `model.base_url` at the proxy, or keep using `router.py` which already lists `litellm-proxy` after pure local endpoints.

## Configuration

Edit [llm-router/router_config.yaml](../llm-router/router_config.yaml):

- `local: true` + low `priority` → tried first  
- `cyber_models` → preferred when cyber heuristic matches  
- `api_key_env` → cloud endpoints skipped if env missing  

## Security notes

- Prefer **local** for sensitive graph / identity context (data residency).  
- Set OpenRouter `provider_routing.data_collection: deny` when using cloud.  
- Rotate `LITELLM_MASTER_KEY`.  
- Do not send production secrets or customer PII to third-party model APIs without policy approval.  
- OPA still governs **tools**; the router only selects **which model thinks**.  

## Roadmap

| Item | Status |
|------|--------|
| Local-first probe + cyber keyword routing | **In repo** |
| Hermes fallback snippet export | **In repo** |
| LiteLLM Compose optional path | **In repo** |
| Per-Bot automatic model pin from router | Planned |
| Embed Foundation-Sec GGUF pull script | Planned |
| Latency/cost-aware scoring | Future |
