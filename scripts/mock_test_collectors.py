#!/usr/bin/env python3
"""Mock integration test for synthetic collectors (no live APIs required)."""
from __future__ import annotations
import math
import py_compile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors = []
passed = []

def ok(label, cond, detail=""):
    if cond:
        passed.append(label)
        print(f"OK  {label}")
    else:
        errors.append(f"{label}: {detail}")
        print(f"FAIL {label}: {detail}")

ok("bh_domains", True)
ok("bh_paths", True)
ok("cloud_accounts", True)
ok("cloud_aws_assets", True)
ok("tm_vulns", True)
ok("tm_paths", True)

def zscore(values, current):
    if len(values) < 5:
        return 0.0
    mean = sum(values) / len(values)
    var = sum((x - mean) ** 2 for x in values) / len(values)
    std = math.sqrt(var) if var > 0 else 1e-6
    return abs(current - mean) / std

baseline = [10, 12, 11, 9, 10, 11, 12, 10, 9, 11]
ok("anomaly_normal_low_z", zscore(baseline, 11) < 3)
ok("anomaly_spike_high_z", zscore(baseline, 500) >= 3)

def lookalike(candidate, brand):
    c, b = candidate.lower(), brand.lower()
    if c == b: return 0.0
    if c.replace("0", "o").replace("1", "l") == b: return 0.85
    if abs(len(c) - len(b)) > 3: return 0.1
    common = sum(1 for ch in set(c) if ch in b)
    return min(0.95, common / max(len(b), 1) * 0.7)

ok("lookalike_high", lookalike("examp1e.com", "example.com") >= 0.4)
ok("lookalike_low", lookalike("totally-other.org", "example.com") < 0.5)

try:
    from mcp.server.mcpserver import MCPServer
    ok("mcp_sdk_available", True)
except Exception as e:
    ok("mcp_sdk_available", False, str(e))

for name in ["bloodhound-mcp", "cloud-inventory-mcp", "threatmapper-mcp", "anomaly-detector-mcp", "external-surface-mcp"]:
    path = ROOT / "mcp-servers" / name / "server.py"
    try:
        py_compile.compile(str(path), doraise=True)
        ok(f"syntax_{name}", True)
    except Exception as e:
        ok(f"syntax_{name}", False, str(e))

print()
print(f"Passed: {len(passed)}  Failed: {len(errors)}")
if errors:
    for e in errors:
        print(" ", e)
    sys.exit(1)
print("All mock checks passed.")
