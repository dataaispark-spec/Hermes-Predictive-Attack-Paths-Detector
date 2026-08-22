#!/usr/bin/env python3
"""Query status of AttackPathPipeline."""
from __future__ import annotations

import argparse
import asyncio
import json
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
    parser.add_argument("--wait-result", action="store_true", help="Block until workflow completes")
    args = parser.parse_args()

    client = await Client.connect(TEMPORAL_HOST)
    handle = client.get_workflow_handle(args.workflow_id)
    status = await handle.query("status")
    print("status:", json.dumps(status, indent=2))
    if args.wait_result:
        result = await handle.result()
        print("result:", json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
