#!/usr/bin/env python3
"""Start an AttackPathPipeline workflow execution."""
from __future__ import annotations

import argparse
import asyncio
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from temporalio.client import Client

from temporal.config import TASK_QUEUE, TEMPORAL_HOST
from temporal.workflows.attack_path_pipeline import AttackPathPipeline


async def main() -> None:
    parser = argparse.ArgumentParser(description="Start AttackPathPipeline")
    parser.add_argument("--account-id", default="123456789012")
    parser.add_argument(
        "--wait-hours",
        type=float,
        default=0.01,
        help="Hours to wait for human_approve signal (default ~36s for demos)",
    )
    parser.add_argument("--workflow-id", default=None)
    args = parser.parse_args()

    wid = args.workflow_id or f"attack-path-{args.account_id}-{uuid.uuid4().hex[:8]}"
    client = await Client.connect(TEMPORAL_HOST)
    handle = await client.start_workflow(
        AttackPathPipeline.run,
        args=[args.account_id, args.wait_hours],
        id=wid,
        task_queue=TASK_QUEUE,
    )
    print(f"Started workflow_id={handle.id} run_id={handle.result_run_id}")
    print(f"Approve with: python temporal/scripts/signal_approve.py --workflow-id {handle.id}")
    print(f"Query status: python temporal/scripts/query_status.py --workflow-id {handle.id}")


if __name__ == "__main__":
    asyncio.run(main())
