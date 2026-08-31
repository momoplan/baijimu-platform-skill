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
SKILL_NAME = "baijimu-platform"
RETIRED_SKILL_NAMES = (
    "baijimu-bundle-development",
    "baijimu-hosted-service-development",
)


def main() -> None:
    default_agents_root = Path(os.environ.get("AGENTS_HOME", Path.home() / ".agents"))
    default_codex_root = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    parser = argparse.ArgumentParser(description="Install the Baijimu platform skill into Codex")
    parser.add_argument("--agents-root", type=Path, default=default_agents_root)
    parser.add_argument(
        "--codex-root", type=Path, default=default_codex_root,
        help="legacy Codex root inspected only for migration",
    )
    args = parser.parse_args()
    agents_root = args.agents_root.expanduser().resolve()
    codex_root = args.codex_root.expanduser().resolve()
    skills_root = agents_root / "skills"
    backups_root = agents_root / "skill-backups"
    archive_path = ROOT / "dist" / f"{SKILL_NAME}.zip"
    if not archive_path.is_file():
        raise SystemExit(f"error: distribution archive is missing: {archive_path}")

    with tempfile.TemporaryDirectory(prefix="baijimu-skill-") as temp_dir:
        temp = Path(temp_dir)
        with zipfile.ZipFile(archive_path) as archive:
            archive.extractall(temp)
        source = temp / SKILL_NAME
        if not (source / "SKILL.md").is_file():
            raise SystemExit(f"error: archive does not contain {SKILL_NAME}/SKILL.md")

        skills_root.mkdir(parents=True, exist_ok=True)
        backups_root.mkdir(parents=True, exist_ok=True)
        migrations: list[tuple[Path, Path]] = []

        def move_to_backup(path: Path, label: str) -> Path | None:
            if not path.exists() and not path.is_symlink():
                return None
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            backup_path = backups_root / f"{label}.backup-{stamp}"
            if backup_path.exists() or backup_path.is_symlink():
                raise RuntimeError(f"backup path already exists: {backup_path}")
            shutil.move(str(path), str(backup_path))
            migrations.append((path, backup_path))
            print(f"migrated {path} -> {backup_path}")
            return backup_path

        target = skills_root / SKILL_NAME
        copy_started = False
        try:
            for legacy in sorted(skills_root.glob("baijimu-platform.backup-*")):
                move_to_backup(legacy, SKILL_NAME)
            move_to_backup(skills_root / "baijimu-docs", "baijimu-docs")
            for retired_name in RETIRED_SKILL_NAMES:
                move_to_backup(skills_root / retired_name, retired_name)
            for legacy_name in (SKILL_NAME, "baijimu-docs", *RETIRED_SKILL_NAMES):
                move_to_backup(
                    codex_root / "skills" / legacy_name,
                    f"legacy-codex-{legacy_name}",
                )

            if (
                (target / "SKILL.md").is_file()
                and (target / "SKILL.md").read_bytes() == (source / "SKILL.md").read_bytes()
            ):
                print(f"already installed {target}")
                return

            move_to_backup(target, SKILL_NAME)
            copy_started = True
            shutil.copytree(source, target)
        except Exception:
            if copy_started and target.exists():
                shutil.rmtree(target)
            for original, backup in reversed(migrations):
                if backup.exists() and not original.exists():
                    original.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(backup), str(original))
            raise

    print(f"installed {target}")


if __name__ == "__main__":
    main()
