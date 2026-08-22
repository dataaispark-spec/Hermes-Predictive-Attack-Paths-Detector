#!/usr/bin/env python3
"""Run Temporal worker for SkandaShield AttackPathPipeline."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from temporalio.client import Client
from temporalio.worker import Worker

from temporal.activities.collectors import (
    authorize_ticket,
    collect_cloud_inventory,
    collect_vulnerabilities,
    create_ticket_stub,
    synthesize_attack_paths,
    upsert_neo4j_paths,
)
from temporal.config import TASK_QUEUE, TEMPORAL_HOST
from temporal.workflows.attack_path_pipeline import AttackPathPipeline


async def main() -> None:
    client = await Client.connect(TEMPORAL_HOST)
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[AttackPathPipeline],
        activities=[
            collect_cloud_inventory,
            collect_vulnerabilities,
            synthesize_attack_paths,
            upsert_neo4j_paths,
            authorize_ticket,
            create_ticket_stub,
        ],
    )
    print(f"Worker polling queue={TASK_QUEUE} at {TEMPORAL_HOST}")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
