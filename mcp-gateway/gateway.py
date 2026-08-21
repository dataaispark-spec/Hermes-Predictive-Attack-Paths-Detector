#!/usr/bin/env python3
"""
Minimal MCP Policy Gateway skeleton.
Sits between Hermes and real MCP servers.
On every tools/call it enriches the request and asks OPA for allow/deny.
This is intentionally simple – production should add auth, mTLS, rate limits, audit shipping.
"""

from __future__ import annotations

import os
import time
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

OPA_URL = os.getenv("OPA_URL", "http://opa:8181/v1/data/skandashield/authz")
OPA_TIMEOUT = float(os.getenv("OPA_TIMEOUT", "2.0"))

app = FastAPI(title="SkandaShield MCP Policy Gateway", version="0.1.0")


class ToolCall(BaseModel):
    bot: str
    tool: str
    args: dict[str, Any] = {}
    context: dict[str, Any] = {}
    session_id: str | None = None


class Decision(BaseModel):
    allow: bool
    reason: str
    decision_id: str
    latency_ms: float


async def query_opa(payload: dict) -> tuple[bool, str]:
    async with httpx.AsyncClient(timeout=OPA_TIMEOUT) as client:
        try:
            r = await client.post(OPA_URL, json={"input": payload})
            r.raise_for_status()
            data = r.json().get("result", {})
            allow = bool(data.get("allow", False))
            reason = data.get("reason", "no reason returned")
            return allow, reason
        except Exception as e:
            # Fail closed
            return False, f"OPA error (fail-closed): {e}"


@app.post("/authorize", response_model=Decision)
async def authorize(call: ToolCall):
    start = time.perf_counter()
    payload = {
        "bot": call.bot,
        "tool": call.tool,
        "args": call.args,
        "context": call.context,
        "session_id": call.session_id,
    }
    allow, reason = await query_opa(payload)
    latency = (time.perf_counter() - start) * 1000
    decision_id = f"dec-{int(time.time()*1000)}"
    # In production: emit structured audit log / OpenTelemetry span here
    print(f"[AUDIT] {decision_id} bot={call.bot} tool={call.tool} allow={allow} reason={reason}")
    return Decision(allow=allow, reason=reason, decision_id=decision_id, latency_ms=round(latency, 2))


@app.get("/health")
async def health():
    return {"status": "ok", "opa_url": OPA_URL}


# Placeholder for real MCP proxying – production gateway would speak full MCP protocol
# and only forward tools/call after a successful /authorize decision.
@app.post("/proxy/{server}/{path:path}")
async def proxy_placeholder(server: str, path: str, request: Request):
    raise HTTPException(
        status_code=501,
        detail="Full MCP protocol proxy not implemented in this skeleton. "
               "Use /authorize from a thin client-side interceptor or extend this service.",
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
