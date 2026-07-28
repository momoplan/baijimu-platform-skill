#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess


COMMANDS = [
    "auth",
    "workspace",
    "runtime",
    "bundle",
    "resource",
    "project",
    "agent",
    "module",
    "hosted-service",
    "rust-build",
    "db-profile",
    "platform-app",
    "local-app",
    "api",
]


binary = shutil.which("baijimu")
if not binary:
    raise SystemExit("error: baijimu is not installed or not on PATH")

version = subprocess.run([binary, "--version"], check=True, text=True, capture_output=True).stdout.strip()
help_text = subprocess.run([binary, "--help"], check=True, text=True, capture_output=True).stdout
missing = [command for command in COMMANDS if command not in help_text]
if missing:
    raise SystemExit(f"error: installed CLI is missing command families: {missing}")

for command in COMMANDS:
    subprocess.run([binary, command, "--help"], check=True, text=True, capture_output=True)

capabilities = subprocess.run(
    [binary, "capabilities", "--offline", "--json"],
    check=True,
    text=True,
    capture_output=True,
).stdout
if '"documentation"' not in capabilities or '"offlineCapabilities"' not in capabilities:
    raise SystemExit("error: CLI offline capabilities are missing versioned documentation")

version_parts = tuple(int(part) for part in version.split("."))
if version_parts >= (0, 1, 23):
    bundle_help = subprocess.run(
        [binary, "bundle", "--help"], check=True, text=True, capture_output=True
    ).stdout
    module_help = subprocess.run(
        [binary, "module", "--help"], check=True, text=True, capture_output=True
    ).stdout
    if "module" not in bundle_help:
        raise SystemExit("error: CLI 0.1.23+ is missing bundle module")
    if "\n  create" in module_help or "\n  freeze" in module_help:
        raise SystemExit("error: legacy module publication commands remain publicly visible")

print(f"CLI smoke passed: {version}; {len(COMMANDS)} command families")
