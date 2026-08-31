from __future__ import annotations

import hashlib
import re
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "baijimu-platform"
SKILL_SOURCE = ROOT / "SKILL.md"
RETIRED_SKILL_NAMES = (
    "baijimu-bundle-development",
    "baijimu-hosted-service-development",
)


class DistributionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run([sys.executable, str(ROOT / "tools" / "build.py")], check=True)

    def test_archive_is_text_only_and_portable(self) -> None:
        with zipfile.ZipFile(ROOT / "dist" / f"{SKILL_NAME}.zip") as archive:
            self.assertEqual(archive.namelist(), [f"{SKILL_NAME}/SKILL.md"])
            archive.read(f"{SKILL_NAME}/SKILL.md").decode("utf-8")

    def test_archive_is_reproducible(self) -> None:
        archive = ROOT / "dist" / f"{SKILL_NAME}.zip"
        first = archive.read_bytes()
        subprocess.run([sys.executable, str(ROOT / "tools" / "build.py")], check=True)
        self.assertEqual(first, archive.read_bytes())

    def test_sha256_file_matches(self) -> None:
        archive = ROOT / "dist" / f"{SKILL_NAME}.zip"
        recorded = archive.with_suffix(".zip.sha256").read_text(encoding="utf-8").split()[0]
        self.assertEqual(recorded, hashlib.sha256(archive.read_bytes()).hexdigest())

    def test_marketplace_skill_is_generated_from_canonical_source(self) -> None:
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        source = SKILL_SOURCE.read_text(encoding="utf-8")
        marketplace_path = ROOT / "marketplace" / SKILL_NAME / "SKILL.md"
        marketplace = marketplace_path.read_text(encoding="utf-8")
        source_match = re.match(r"\A---\n.*?\n---\n", source, re.DOTALL)
        marketplace_match = re.match(r"\A---\n(.*?)\n---\n", marketplace, re.DOTALL)
        self.assertIsNotNone(source_match)
        self.assertIsNotNone(marketplace_match)
        assert source_match is not None and marketplace_match is not None
        self.assertEqual(source[source_match.end() :], marketplace[marketplace_match.end() :])
        metadata = marketplace_match.group(1)
        self.assertIn(f"name: {SKILL_NAME}", metadata)
        self.assertIn(f"version: {version}", metadata)
        self.assertIn("license: MIT-0", metadata)
        self.assertIn("platforms: [openclaw, hermes]", metadata)

    def test_distribution_contains_one_skill(self) -> None:
        archives = sorted(path.name for path in (ROOT / "dist").glob("*.zip"))
        marketplace_skills = sorted(
            path.parent.name for path in (ROOT / "marketplace").glob("*/SKILL.md")
        )
        self.assertEqual(archives, [f"{SKILL_NAME}.zip"])
        self.assertEqual(marketplace_skills, [SKILL_NAME])
        for retired_name in RETIRED_SKILL_NAMES:
            self.assertFalse((ROOT / "skills" / retired_name / "SKILL.md").exists())

    def test_skill_is_a_thin_documentation_and_cli_entrypoint(self) -> None:
        skill = SKILL_SOURCE.read_text(encoding="utf-8")
        for required in [
            "本技能是统一入口",
            "https://docs.baijimu.com/",
            "docs-manifest.json",
            "逐级读取 `--help`",
            "权威状态源回查一致",
        ]:
            self.assertIn(required, skill)
        for duplicated_detail in [
            "$baijimu-bundle-development",
            "$baijimu-hosted-service-development",
            "ModuleVersion",
            "liquibase_bundle",
            "BuildJob",
        ]:
            self.assertNotIn(duplicated_detail, skill)

    def test_skill_uses_progressive_help_without_retired_capabilities(self) -> None:
        skill = SKILL_SOURCE.read_text(encoding="utf-8")
        self.assertNotIn("baijimu capabilities", skill)
        self.assertNotIn("offlineCapabilities", skill)
        self.assertIn("--help", skill)

        smoke = (ROOT / "tools" / "smoke_cli.py").read_text(encoding="utf-8")
        self.assertIn("version_parts >= (0, 25, 0)", smoke)
        self.assertIn("retired capabilities command is still executable", smoke)

    def test_repository_license_matches_marketplace_license(self) -> None:
        license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        self.assertTrue(license_text.startswith("MIT No Attribution\n"))

    def test_installer_retires_split_skills_and_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            agents_root = root / ".agents"
            codex_root = root / ".codex"
            for name in (SKILL_NAME, "baijimu-docs", *RETIRED_SKILL_NAMES):
                legacy = agents_root / "skills" / name
                legacy.mkdir(parents=True)
                (legacy / "SKILL.md").write_text(f"legacy {name}\n", encoding="utf-8")
            legacy_codex = codex_root / "skills" / SKILL_NAME
            legacy_codex.mkdir(parents=True)
            (legacy_codex / "SKILL.md").write_text("legacy codex platform\n", encoding="utf-8")

            command = [
                sys.executable, str(ROOT / "tools" / "install_codex.py"),
                "--agents-root", str(agents_root), "--codex-root", str(codex_root),
            ]
            subprocess.run(command, check=True)
            subprocess.run(command, check=True)

            active_names = sorted(path.name for path in (agents_root / "skills").iterdir())
            self.assertEqual(active_names, [SKILL_NAME])
            self.assertEqual(
                (agents_root / "skills" / SKILL_NAME / "SKILL.md").read_bytes(),
                SKILL_SOURCE.read_bytes(),
            )
            backups = sorted((agents_root / "skill-backups").glob("*.backup-*"))
            self.assertEqual(len(backups), 5)
            self.assertFalse((codex_root / "skills" / SKILL_NAME).exists())


if __name__ == "__main__":
    unittest.main()
