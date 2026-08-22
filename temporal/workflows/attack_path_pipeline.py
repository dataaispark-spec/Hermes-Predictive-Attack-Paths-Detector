"""
AttackPathPipeline — durable path: collect → synthesize → graph → (wait approval) → ticket.

Signals:
  human_approve()  — operator approval for ticket creation
"""
from __future__ import annotations

from datetime import timedelta
from typing import Any

from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import TimeoutError as TemporalTimeoutError

with workflow.unsafe.imports_passed_through():
    from temporal.activities.collectors import (
        authorize_ticket,
        collect_cloud_inventory,
        collect_vulnerabilities,
        create_ticket_stub,
        synthesize_attack_paths,
        upsert_neo4j_paths,
    )


@workflow.defn(name="AttackPathPipeline")
class AttackPathPipeline:
    def __init__(self) -> None:
        self._approved: bool = False
        self._status: str = "started"

    @workflow.signal
    def human_approve(self) -> None:
        self._approved = True
        self._status = "approved"

    @workflow.query
    def status(self) -> dict[str, Any]:
        return {"status": self._status, "approved": self._approved}

    @workflow.run
    async def run(self, account_id: str = "123456789012", wait_approval_hours: float = 24.0) -> dict[str, Any]:
        retry = RetryPolicy(maximum_attempts=3, initial_interval=timedelta(seconds=2))
        short = timedelta(minutes=5)

        self._status = "collecting"
        inventory = await workflow.execute_activity(
            collect_cloud_inventory,
            account_id,
            start_to_close_timeout=short,
            retry_policy=retry,
        )
        vulns = await workflow.execute_activity(
            collect_vulnerabilities,
            20,
            start_to_close_timeout=short,
            retry_policy=retry,
        )

        self._status = "synthesizing"
        paths_payload = await workflow.execute_activity(
            synthesize_attack_paths,
            args=[inventory, vulns],
            start_to_close_timeout=short,
            retry_policy=retry,
        )

        self._status = "upserting"
        upsert = await workflow.execute_activity(
            upsert_neo4j_paths,
            paths_payload,
            start_to_close_timeout=short,
            retry_policy=retry,
        )

        paths = paths_payload.get("paths") or []
        top = paths[0] if paths else {}
        score = float(top.get("score") or 0.0)

        if score < 0.5:
            self._status = "below_threshold"
            return {
                "outcome": "skipped_low_score",
                "score": score,
                "upsert": upsert,
                "path": top,
            }

        self._status = "awaiting_approval"
        try:
            await workflow.wait_condition(
                lambda: self._approved,
                timeout=timedelta(hours=wait_approval_hours),
            )
        except (TemporalTimeoutError, TimeoutError):
            self._status = "approval_timeout"
            return {
                "outcome": "approval_timeout",
                "score": score,
                "upsert": upsert,
                "path": top,
            }

        self._status = "authorizing"
        auth = await workflow.execute_activity(
            authorize_ticket,
            args=["remediation-guidance", True],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry,
        )
        if not auth.get("allow"):
            self._status = "denied_by_policy"
            return {
                "outcome": "policy_denied",
                "auth": auth,
                "path": top,
                "upsert": upsert,
            }

        self._status = "creating_ticket"
        ticket = await workflow.execute_activity(
            create_ticket_stub,
            args=[top, "human_approved_high_score_path"],
            start_to_close_timeout=short,
            retry_policy=retry,
        )
        self._status = "completed"
        return {
            "outcome": "ticket_created",
            "ticket": ticket,
            "path": top,
            "upsert": upsert,
            "auth": auth,
        }
