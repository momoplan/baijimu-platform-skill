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
    default_agents_root = Path(os.environ.get("AGENTS_HOME", Path.home() / ".agents"))
    default_codex_root = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    parser = argparse.ArgumentParser(description="Install the universal Baijimu skill into Codex")
    parser.add_argument("--agents-root", type=Path, default=default_agents_root)
    parser.add_argument(
        "--codex-root",
        type=Path,
        default=default_codex_root,
        help="legacy Codex root inspected only for migration",
    )
    args = parser.parse_args()
    agents_root = args.agents_root.expanduser().resolve()
    codex_root = args.codex_root.expanduser().resolve()
    skills_root = agents_root / "skills"
    backups_root = agents_root / "skill-backups"
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
        backups_root.mkdir(parents=True, exist_ok=True)

        def move_to_backup(path: Path, label: str) -> Path | None:
            if not path.exists() and not path.is_symlink():
                return None
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            backup_path = backups_root / f"{label}.backup-{stamp}"
            if backup_path.exists() or backup_path.is_symlink():
                raise SystemExit(f"error: backup path already exists: {backup_path}")
            shutil.move(str(path), str(backup_path))
            print(f"migrated {path} -> {backup_path}")
            return backup_path

        for legacy in sorted(skills_root.glob("baijimu-platform.backup-*")):
            move_to_backup(legacy, "baijimu-platform")

        move_to_backup(skills_root / "baijimu-docs", "baijimu-docs")
        for legacy_name in ("baijimu-platform", "baijimu-docs"):
            legacy = codex_root / "skills" / legacy_name
            if legacy.resolve() != target.resolve():
                move_to_backup(legacy, f"legacy-codex-{legacy_name}")

        if (
            (target / "SKILL.md").is_file()
            and (target / "SKILL.md").read_bytes() == (source / "SKILL.md").read_bytes()
        ):
            print(f"already installed {target}")
            return

        backup = move_to_backup(target, "baijimu-platform")
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
