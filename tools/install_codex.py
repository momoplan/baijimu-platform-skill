#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "dist" / "baijimu-platform.zip"


def main() -> None:
    default_root = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    parser = argparse.ArgumentParser(description="Install the universal Baijimu skill into Codex")
    parser.add_argument("--codex-root", type=Path, default=default_root)
    args = parser.parse_args()
    skills_root = args.codex_root.expanduser().resolve() / "skills"
    target = skills_root / "baijimu-platform"

    if not ARCHIVE.is_file():
        raise SystemExit("error: distribution archive is missing; run python3 tools/build.py")

    with tempfile.TemporaryDirectory(prefix="baijimu-skill-") as temp_dir:
        temp = Path(temp_dir)
        with zipfile.ZipFile(ARCHIVE) as archive:
            archive.extractall(temp)
        source = temp / "baijimu-platform"
        if not (source / "SKILL.md").is_file():
            raise SystemExit("error: archive does not contain baijimu-platform/SKILL.md")

        skills_root.mkdir(parents=True, exist_ok=True)
        backup = None
        if target.exists() or target.is_symlink():
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            backup = skills_root / f"baijimu-platform.backup-{stamp}"
            if backup.exists():
                raise SystemExit(f"error: backup path already exists: {backup}")
            shutil.move(str(target), str(backup))
        try:
            shutil.copytree(source, target)
        except Exception:
            if backup is not None and not target.exists():
                shutil.move(str(backup), str(target))
            raise

    print(f"installed {target}")
    if backup is not None:
        print(f"backup {backup}")


if __name__ == "__main__":
    main()
