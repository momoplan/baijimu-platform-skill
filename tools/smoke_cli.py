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

version_parts = tuple(int(part) for part in version.split("."))
if version_parts >= (0, 25, 0):
    if "capabilities" in help_text:
        raise SystemExit("error: retired capabilities command remains in top-level help")
    retired = subprocess.run(
        [binary, "capabilities"], text=True, capture_output=True
    )
    if retired.returncode == 0:
        raise SystemExit("error: retired capabilities command is still executable")

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
if version_parts >= (0, 18, 0):
    version_help = subprocess.run(
        [binary, "bundle", "module", "version", "--help"],
        check=True,
        text=True,
        capture_output=True,
    ).stdout
    if "create" not in version_help:
        raise SystemExit("error: CLI 0.18.0+ is missing bundle module version create")
if version_parts >= (0, 48, 1):
    capability_help = subprocess.run(
        [binary, "bundle", "capability", "--help"],
        check=True,
        text=True,
        capture_output=True,
    ).stdout
    for command in ["scopes", "client", "token"]:
        if command not in capability_help:
            raise SystemExit(
                f"error: CLI 0.48.1+ is missing bundle capability {command}"
            )

print(f"CLI smoke passed: {version}; {len(COMMANDS)} command families")
