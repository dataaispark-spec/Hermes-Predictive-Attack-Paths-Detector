#!/usr/bin/env python3
"""Send human_approve signal to a running AttackPathPipeline."""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from temporalio.client import Client

from temporal.config import TEMPORAL_HOST


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workflow-id", required=True)
    args = parser.parse_args()

    client = await Client.connect(TEMPORAL_HOST)
    handle = client.get_workflow_handle(args.workflow_id)
    await handle.signal("human_approve")
    print(f"Signaled human_approve on {args.workflow_id}")


if __name__ == "__main__":
    asyncio.run(main())
