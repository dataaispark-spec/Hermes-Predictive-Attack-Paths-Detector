# LLM router (local-first + cyber preference)

**Repo:** [https://github.com/dataaispark-spec/Hermes-Predictive-Attack-Paths-Detector](https://github.com/dataaispark-spec/Hermes-Predictive-Attack-Paths-Detector)

## Goal

Prefer **local** inference; when the task is security-related, prefer **cyber-oriented** models; fall back to cloud providers only when local is unavailable.

## Layout

| Path | Role |
|------|------|
| `llm-router/router.py` | Probe + route decision + Hermes snippet export |
| `llm-router/router_config.yaml` | Priority list |
| `llm-router/hermes_local_first.yaml` | Example Hermes merge |
| `llm-router/litellm_config.yaml` | Optional LiteLLM |
| `deploy/docker-compose.litellm.yml` | Optional proxy |

```bash
python llm-router/router.py --prompt "Rank attack paths for this CVE"
python llm-router/router.py --prompt "attack path" --hermes
```

Merge exported config into Hermes (`~/.hermes/config.yaml`) as documented by Hermes Agent.
