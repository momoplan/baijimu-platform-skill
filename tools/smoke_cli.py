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

print(f"CLI smoke passed: {version}; {len(COMMANDS)} command families")
