#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess

COMMAND_PATHS = [
    ("auth",),
    ("workspace",),
    ("workspace", "project"),
    ("workspace", "device"),
    ("workspace", "hosted-service"),
    ("workspace", "local-app"),
    ("runtime",),
    ("runtime", "bundle"),
    ("runtime", "bundle", "resource"),
    ("runtime", "bundle", "installation"),
    ("runtime", "service"),
    ("runtime", "session"),
    ("bundle",),
    ("bundle", "resource"),
    ("bundle", "resource", "module"),
    ("bundle", "resource", "workflow"),
    ("bundle", "resource", "platform-application"),
]
RETIRED_ROOTS = ["capabilities", "codex", "module", "agent", "resource",
                 "platform-app", "rust-build", "project", "api"]

binary = shutil.which("baijimu")
if not binary:
    raise SystemExit("error: baijimu is not installed or not on PATH")
version = subprocess.run([binary, "--version"], check=True, text=True, capture_output=True).stdout.strip()
for path in COMMAND_PATHS:
    result = subprocess.run([binary, *path, "--help"], text=True, capture_output=True)
    if result.returncode:
        raise SystemExit(f"error: installed CLI {version} lacks {' '.join(path)}; check its versioned docs or upgrade")
for root in RETIRED_ROOTS:
    result = subprocess.run([binary, root, "--help"], text=True, capture_output=True)
    if result.returncode == 0:
        raise SystemExit(f"error: retired root {root} is still executable")
print(f"CLI smoke passed: {version}; {len(COMMAND_PATHS)} command paths")
