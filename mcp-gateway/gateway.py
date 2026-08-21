#!/usr/bin/env python3
"""
MCP Policy Gateway – upgraded skeleton.
- Authorizes every tools/call via OPA (fail-closed)
- Emits OpenTelemetry traces + metrics
- Provides a simple HTTP proxy path that can be extended to full MCP protocol
"""

from __future__ import annotations

import os
import time
import uuid
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

# OpenTelemetry (optional – gracefully degrades if not installed)
try:
    from opentelemetry import trace, metrics
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
    from opentelemetry.sdk.resources import Resource

    resource = Resource.create({"service.name": "skandashield-mcp-gateway"})
    trace.set_tracer_provider(TracerProvider(resource=resource))
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    reader = PeriodicExportingMetricReader(ConsoleMetricExporter())
    metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[reader]))
    tracer = trace.get_tracer(__name__)
    meter = metrics.get_meter(__name__)
    auth_counter = meter.create_counter("mcp_gateway_authorize_total")
    auth_latency = meter.create_histogram("mcp_gateway_authorize_latency_ms")
    OTEL_ENABLED = True
except Exception:
    OTEL_ENABLED = False
    tracer = None
    auth_counter = None
    auth_latency = None

OPA_URL = os.getenv("OPA_URL", "http://opa:8181/v1/data/skandashield/authz")
OPA_TIMEOUT = float(os.getenv("OPA_TIMEOUT", "2.0"))
UPSTREAM_MAP = {
    "neo4j": os.getenv("UPSTREAM_NEO4J", ""),
    "nuclei": os.getenv("UPSTREAM_NUCLEI", ""),
}

app = FastAPI(title="SkandaShield MCP Policy Gateway", version="0.2.0")


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
            return bool(data.get("allow", False)), data.get("reason", "no reason")
        except Exception as e:
            return False, f"OPA error (fail-closed): {e}"


@app.post("/authorize", response_model=Decision)
async def authorize(call: ToolCall):
    start = time.perf_counter()
    decision_id = f"dec-{uuid.uuid4().hex[:12]}"
    payload = {
        "bot": call.bot,
        "tool": call.tool,
        "args": call.args,
        "context": call.context,
        "session_id": call.session_id,
    }

    if OTEL_ENABLED and tracer:
        with tracer.start_as_current_span("authorize") as span:
            span.set_attribute("bot", call.bot)
            span.set_attribute("tool", call.tool)
            allow, reason = await query_opa(payload)
            span.set_attribute("allow", allow)
            span.set_attribute("reason", reason)
    else:
        allow, reason = await query_opa(payload)

    latency = (time.perf_counter() - start) * 1000
    if OTEL_ENABLED and auth_counter and auth_latency:
        auth_counter.add(1, {"bot": call.bot, "tool": call.tool, "allow": str(allow)})
        auth_latency.record(latency, {"bot": call.bot})

    print(f"[AUDIT] {decision_id} bot={call.bot} tool={call.tool} allow={allow} reason={reason} latency_ms={latency:.1f}")
    return Decision(allow=allow, reason=reason, decision_id=decision_id, latency_ms=round(latency, 2))


@app.get("/health")
async def health():
    return {"status": "ok", "opa_url": OPA_URL, "otel": OTEL_ENABLED}


@app.post("/proxy/{server}")
async def proxy_tool_call(server: str, call: ToolCall, request: Request):
    decision = await authorize(call)
    if not decision.allow:
        raise HTTPException(status_code=403, detail={"reason": decision.reason, "decision_id": decision.decision_id})

    upstream = UPSTREAM_MAP.get(server)
    if not upstream:
        return {"forwarded": False, "decision": decision.model_dump(), "note": "configure UPSTREAM_* env vars"}

    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(f"{upstream}/tools/call", json=call.model_dump())
        return {"forwarded": True, "decision_id": decision.decision_id, "upstream_status": r.status_code, "body": r.text}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
