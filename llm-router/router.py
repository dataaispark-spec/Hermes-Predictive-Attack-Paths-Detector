#!/usr/bin/env python3
"""
SkandaShield dynamic LLM router — local-first, cyber-preferring, multi-provider.

Strategy (in order):
  1. Probe local endpoints (Ollama, vLLM, LM Studio, llama.cpp server)
  2. Prefer cybersecurity-specialised local models when task looks cyber
  3. Fall back to next healthy local general model
  4. Then cloud / OpenRouter / direct providers from config chain

Works standalone and can emit Hermes-compatible model selection hints.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import urllib.request
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

DEFAULT_CONFIG = Path(__file__).resolve().parent / "router_config.yaml"

CYBER_KEYWORDS = re.compile(
    r"\b("
    r"cve|cvss|exploit|vulnerability|vulnerabilities|malware|ransomware|"
    r"phishing|lateral\s*movement|privilege\s*escalation|attack\s*path|"
    r"mitre|att&ck|ioc|threat\s*intel|siem|xdr|cnapp|cspm|easm|"
    r"bloodhound|active\s*directory|kerberos|ntlm|zero[-\s]?day|"
    r"penetration|pentest|red\s*team|blue\s*team|soc|incident\s*response|"
    r"remediation|nuclei|nmap|payload|shellcode|c2|command\s*and\s*control|"
    r"misconfiguration|exposure|choke\s*point|identity\s*path|"
    r"owasp|nist|iso\s*27001|gdpr|hipaa|"
    r"firewall|ids|ips|waf|dlp|edr"
    r")\b",
    re.I,
)


@dataclass
class Endpoint:
    name: str
    kind: str
    base_url: str
    models: list[str] = field(default_factory=list)
    cyber_models: list[str] = field(default_factory=list)
    api_key_env: str = ""
    local: bool = False
    priority: int = 100
    timeout_s: float = 2.0
    healthy: bool | None = None
    last_error: str = ""


@dataclass
class RouteDecision:
    provider: str
    model: str
    base_url: str
    local: bool
    cyber_preferred: bool
    reason: str
    api_key_env: str = ""
    fallbacks: list[dict[str, str]] = field(default_factory=list)

    def to_hermes_snippet(self) -> dict[str, Any]:
        primary: dict[str, Any] = {
            "provider": "custom" if self.local or self.provider in ("ollama", "vllm", "lmstudio", "ollama-local", "vllm-local", "lmstudio-local") else self.provider,
            "default": self.model,
        }
        if self.base_url:
            primary["base_url"] = self.base_url
        if self.api_key_env:
            primary["api_key_env"] = self.api_key_env
        fb = []
        for f in self.fallbacks:
            entry = {
                "provider": f.get("provider", "custom"),
                "model": f["model"],
            }
            if f.get("base_url"):
                entry["base_url"] = f["base_url"]
            if f.get("api_key_env"):
                entry["api_key_env"] = f["api_key_env"]
            fb.append(entry)
        return {"model": primary, "fallback_providers": fb, "route_reason": self.reason}


def _http_get(url: str, timeout: float, headers: dict[str, str] | None = None) -> tuple[int, str]:
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "skandashield-llm-router/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        return 0, str(e)


def probe_endpoint(ep: Endpoint) -> bool:
    url = ep.base_url.rstrip("/")
    if ep.kind == "ollama":
        candidates = [f"{url}/api/tags", f"{url}/api/version"]
    else:
        candidates = [f"{url}/models", f"{url}/v1/models", url]

    headers: dict[str, str] = {}
    if ep.api_key_env:
        key = os.environ.get(ep.api_key_env, "")
        if key:
            headers["Authorization"] = f"Bearer {key}"

    for c in candidates:
        status, body = _http_get(c, ep.timeout_s, headers)
        if status and 200 <= status < 500:
            ep.healthy = True
            ep.last_error = ""
            if ep.kind == "ollama" and status == 200 and "/api/tags" in c:
                try:
                    data = json.loads(body)
                    names = [m.get("name", "") for m in data.get("models", []) if m.get("name")]
                    if names:
                        ep.models = names
                except json.JSONDecodeError:
                    pass
            return True
        ep.last_error = body[:200]
    ep.healthy = False
    return False


def is_cyber_task(text: str) -> bool:
    if not text:
        return False
    return bool(CYBER_KEYWORDS.search(text))


def default_endpoints() -> list[Endpoint]:
    return [
        Endpoint(
            name="ollama-local",
            kind="ollama",
            base_url=os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
            models=["llama3.1:8b", "qwen2.5:14b", "mistral:7b"],
            cyber_models=[
                "foundation-sec:8b",
                "foundation-sec-instruct:8b",
                "secgpt:7b",
                "llama3.1:8b",
            ],
            local=True,
            priority=10,
        ),
        Endpoint(
            name="vllm-local",
            kind="openai_compatible",
            base_url=os.environ.get("VLLM_BASE_URL", "http://127.0.0.1:8000/v1"),
            models=["local-model"],
            cyber_models=["foundation-sec-8b-instruct", "local-model"],
            local=True,
            priority=20,
            api_key_env="VLLM_API_KEY",
        ),
        Endpoint(
            name="lmstudio-local",
            kind="openai_compatible",
            base_url=os.environ.get("LMSTUDIO_BASE_URL", "http://127.0.0.1:1234/v1"),
            models=["local-model"],
            cyber_models=["local-model"],
            local=True,
            priority=30,
        ),
        Endpoint(
            name="openrouter",
            kind="openrouter",
            base_url="https://openrouter.ai/api/v1",
            models=[
                "anthropic/claude-sonnet-4",
                "openai/gpt-4o",
                "google/gemini-2.5-pro",
            ],
            cyber_models=[
                "anthropic/claude-sonnet-4",
                "openai/gpt-4o",
                "deepseek/deepseek-chat",
            ],
            api_key_env="OPENROUTER_API_KEY",
            local=False,
            priority=200,
        ),
        Endpoint(
            name="anthropic",
            kind="anthropic",
            base_url="https://api.anthropic.com",
            models=["claude-sonnet-4-6"],
            cyber_models=["claude-sonnet-4-6"],
            api_key_env="ANTHROPIC_API_KEY",
            local=False,
            priority=210,
        ),
        Endpoint(
            name="openai",
            kind="openai_compatible",
            base_url="https://api.openai.com/v1",
            models=["gpt-4o", "gpt-4o-mini"],
            cyber_models=["gpt-4o"],
            api_key_env="OPENAI_API_KEY",
            local=False,
            priority=220,
        ),
    ]


def load_config(path: Path) -> list[Endpoint]:
    if not path.exists():
        return default_endpoints()
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text) or {}
    except Exception:
        return default_endpoints()

    endpoints: list[Endpoint] = []
    for item in data.get("endpoints", []):
        endpoints.append(
            Endpoint(
                name=item["name"],
                kind=item.get("kind", "openai_compatible"),
                base_url=item.get("base_url", ""),
                models=list(item.get("models") or []),
                cyber_models=list(item.get("cyber_models") or []),
                api_key_env=item.get("api_key_env", ""),
                local=bool(item.get("local", False)),
                priority=int(item.get("priority", 100)),
                timeout_s=float(item.get("timeout_s", 2.0)),
            )
        )
    return endpoints or default_endpoints()


def pick_model(ep: Endpoint, cyber: bool) -> str | None:
    pool = ep.cyber_models if cyber and ep.cyber_models else ep.models
    if not pool:
        pool = ep.models or ep.cyber_models
    if not pool:
        return None
    if ep.kind == "ollama" and ep.models:
        available = set(ep.models)
        for m in pool:
            if m in available:
                return m
            prefix = m.split(":")[0]
            for a in available:
                if a.startswith(prefix):
                    return a
        return ep.models[0]
    return pool[0]


def route(
    prompt: str = "",
    task_hint: str = "",
    force_cyber: bool | None = None,
    config_path: Path | None = None,
    probe: bool = True,
) -> RouteDecision:
    text = f"{task_hint}\n{prompt}"
    cyber = force_cyber if force_cyber is not None else is_cyber_task(text)

    endpoints = load_config(config_path or DEFAULT_CONFIG)
    endpoints.sort(key=lambda e: (0 if e.local else 1, e.priority))

    healthy: list[tuple[Endpoint, str]] = []
    for ep in endpoints:
        if probe:
            ok = probe_endpoint(ep)
        else:
            ok = True
            ep.healthy = True
        if not ok:
            continue
        if ep.api_key_env and not ep.local:
            if not os.environ.get(ep.api_key_env):
                ep.healthy = False
                ep.last_error = f"missing env {ep.api_key_env}"
                continue
        model = pick_model(ep, cyber)
        if model:
            healthy.append((ep, model))

    if not healthy:
        return RouteDecision(
            provider="none",
            model="",
            base_url="",
            local=False,
            cyber_preferred=cyber,
            reason="no healthy endpoints — start Ollama or set API keys",
        )

    primary_ep, primary_model = healthy[0]
    fallbacks = []
    for ep, model in healthy[1:]:
        fallbacks.append(
            {
                "provider": "custom" if ep.local else ep.name,
                "model": model,
                "base_url": ep.base_url,
                "api_key_env": ep.api_key_env,
            }
        )

    reason = "; ".join(
        [
            "local-first" if primary_ep.local else "cloud",
            "cyber-prefer" if cyber else "general",
            f"endpoint={primary_ep.name}",
        ]
    )
    return RouteDecision(
        provider=primary_ep.name,
        model=primary_model,
        base_url=primary_ep.base_url,
        local=primary_ep.local,
        cyber_preferred=cyber,
        reason=reason,
        api_key_env=primary_ep.api_key_env,
        fallbacks=fallbacks,
    )


def main() -> None:
    p = argparse.ArgumentParser(description="SkandaShield dynamic LLM router")
    p.add_argument("--prompt", default="")
    p.add_argument("--task", default="")
    p.add_argument("--force-cyber", action="store_true")
    p.add_argument("--force-general", action="store_true")
    p.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    p.add_argument("--no-probe", action="store_true")
    p.add_argument("--hermes", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    force: bool | None = None
    if args.force_cyber:
        force = True
    if args.force_general:
        force = False

    decision = route(
        prompt=args.prompt,
        task_hint=args.task,
        force_cyber=force,
        config_path=args.config,
        probe=not args.no_probe,
    )

    if args.hermes:
        print(json.dumps(decision.to_hermes_snippet(), indent=2))
    elif args.json:
        print(json.dumps(asdict(decision), indent=2))
    else:
        print(f"provider:  {decision.provider}")
        print(f"model:     {decision.model}")
        print(f"base_url:  {decision.base_url}")
        print(f"local:     {decision.local}")
        print(f"cyber:     {decision.cyber_preferred}")
        print(f"reason:    {decision.reason}")
        if decision.fallbacks:
            print("fallbacks:")
            for f in decision.fallbacks:
                print(f"  - {f.get('model')} @ {f.get('base_url') or f.get('provider')}")


if __name__ == "__main__":
    main()
