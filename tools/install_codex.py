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
SKILL_NAMES = (
    "baijimu-platform",
    "baijimu-bundle-development",
    "baijimu-hosted-service-development",
)


def main() -> None:
    default_agents_root = Path(os.environ.get("AGENTS_HOME", Path.home() / ".agents"))
    default_codex_root = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    parser = argparse.ArgumentParser(description="Install the Baijimu skill suite into Codex")
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

    archives = {name: ROOT / "dist" / f"{name}.zip" for name in SKILL_NAMES}
    missing = [path for path in archives.values() if not path.is_file()]
    if missing:
        raise SystemExit(f"error: distribution archives are missing: {missing}")

    with tempfile.TemporaryDirectory(prefix="baijimu-skills-") as temp_dir:
        temp = Path(temp_dir)
        sources: dict[str, Path] = {}
        for name, archive_path in archives.items():
            with zipfile.ZipFile(archive_path) as archive:
                archive.extractall(temp)
            source = temp / name
            if not (source / "SKILL.md").is_file():
                raise SystemExit(f"error: archive does not contain {name}/SKILL.md")
            sources[name] = source

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
            if legacy.exists() or legacy.is_symlink():
                move_to_backup(legacy, f"legacy-codex-{legacy_name}")

        if all(
            (skills_root / name / "SKILL.md").is_file()
            and (skills_root / name / "SKILL.md").read_bytes() == (source / "SKILL.md").read_bytes()
            for name, source in sources.items()
        ):
            print(f"already installed {', '.join(SKILL_NAMES)}")
            return

        backups: dict[str, Path | None] = {}
        installed: list[Path] = []
        try:
            for name, source in sources.items():
                target = skills_root / name
                backups[name] = move_to_backup(target, name)
                shutil.copytree(source, target)
                installed.append(target)
        except Exception:
            for target in installed:
                if target.exists():
                    shutil.rmtree(target)
            for name, backup in backups.items():
                target = skills_root / name
                if backup is not None and not target.exists():
                    shutil.move(str(backup), str(target))
            raise

    for name in SKILL_NAMES:
        print(f"installed {skills_root / name}")
        if backups.get(name) is not None:
            print(f"backup {backups[name]}")


if __name__ == "__main__":
    main()
