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
SKILL_SOURCES = {
    "baijimu-platform": ROOT / "SKILL.md",
    "baijimu-bundle-development": ROOT / "skills" / "baijimu-bundle-development" / "SKILL.md",
    "baijimu-hosted-service-development": ROOT / "skills" / "baijimu-hosted-service-development" / "SKILL.md",
}


class DistributionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run([sys.executable, str(ROOT / "tools" / "build.py")], check=True)

    def test_each_archive_is_text_only_and_portable(self) -> None:
        for name in SKILL_SOURCES:
            with self.subTest(name=name), zipfile.ZipFile(ROOT / "dist" / f"{name}.zip") as archive:
                self.assertEqual(archive.namelist(), [f"{name}/SKILL.md"])
                archive.read(f"{name}/SKILL.md").decode("utf-8")

    def test_archives_are_reproducible(self) -> None:
        first = {
            name: (ROOT / "dist" / f"{name}.zip").read_bytes()
            for name in SKILL_SOURCES
        }
        subprocess.run([sys.executable, str(ROOT / "tools" / "build.py")], check=True)
        for name, content in first.items():
            self.assertEqual(content, (ROOT / "dist" / f"{name}.zip").read_bytes())

    def test_sha256_files_match(self) -> None:
        for name in SKILL_SOURCES:
            archive = ROOT / "dist" / f"{name}.zip"
            recorded = (ROOT / "dist" / f"{name}.zip.sha256").read_text(encoding="utf-8").split()[0]
            self.assertEqual(recorded, hashlib.sha256(archive.read_bytes()).hexdigest())

    def test_marketplace_skills_are_generated_from_canonical_sources(self) -> None:
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        for name, source_path in SKILL_SOURCES.items():
            source = source_path.read_text(encoding="utf-8")
            marketplace_path = ROOT / "marketplace" / name / "SKILL.md"
            marketplace = marketplace_path.read_text(encoding="utf-8")
            source_match = re.match(r"\A---\n.*?\n---\n", source, re.DOTALL)
            marketplace_match = re.match(r"\A---\n(.*?)\n---\n", marketplace, re.DOTALL)
            self.assertIsNotNone(source_match)
            self.assertIsNotNone(marketplace_match)
            assert source_match is not None and marketplace_match is not None
            self.assertEqual(source[source_match.end() :], marketplace[marketplace_match.end() :])
            metadata = marketplace_match.group(1)
            self.assertIn(f"name: {name}", metadata)
            self.assertIn(f"version: {version}", metadata)
            self.assertIn("license: MIT-0", metadata)
            self.assertIn("platforms: [openclaw, hermes]", metadata)
            files = [
                path.relative_to(marketplace_path.parent).as_posix()
                for path in marketplace_path.parent.rglob("*") if path.is_file()
            ]
            self.assertEqual(files, ["SKILL.md"])

    def test_base_skill_routes_without_copying_scenario_manuals(self) -> None:
        skill = SKILL_SOURCES["baijimu-platform"].read_text(encoding="utf-8")
        for required in [
            "$baijimu-bundle-development",
            "$baijimu-hosted-service-development",
            "project branch-policy get",
            "`DIRECT`",
            "`PROTECTED`",
            "不得用同一身份自行批准",
        ]:
            self.assertIn(required, skill)
        self.assertNotIn("完整执行官方 Bundle 修改与发布清单", skill)

    def test_bundle_skill_keeps_bundle_only_product_boundaries(self) -> None:
        skill = SKILL_SOURCES["baijimu-bundle-development"].read_text(encoding="utf-8")
        for required in [
            "Bundle 是生态资源公开审核、市场分发和 Runtime 安装的唯一交付单元",
            "数据库及 `databaseType` 不是 Module 声明",
            "创建模块版本",
            "不可变 Bundle 版本",
            "真实 Runtime service/method",
            "Module 是 Bundle 内部资源",
            "独立审核、上架、安装或升级",
        ]:
            self.assertIn(required, skill)

    def test_hosted_skill_keeps_project_and_migration_boundaries(self) -> None:
        skill = SKILL_SOURCES["baijimu-hosted-service-development"].read_text(encoding="utf-8")
        for required in [
            "Project 是后端应用唯一身份",
            "不存在并列的",
            "`hostedServiceId`",
            "同一个非空完整",
            "`sourceCommitId`",
            "Schema → Data",
            "expand/contract",
            "Rules 不参与",
        ]:
            self.assertIn(required, skill)

    def test_repository_license_matches_marketplace_license(self) -> None:
        license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        self.assertTrue(license_text.startswith("MIT No Attribution\n"))

    def test_installer_migrates_legacy_and_installs_all_skills_idempotently(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            agents_root = root / ".agents"
            codex_root = root / ".codex"
            legacy_docs = agents_root / "skills" / "baijimu-docs"
            legacy_docs.mkdir(parents=True)
            (legacy_docs / "SKILL.md").write_text("legacy docs\n", encoding="utf-8")
            legacy_platform = codex_root / "skills" / "baijimu-platform"
            legacy_platform.mkdir(parents=True)
            (legacy_platform / "SKILL.md").write_text("legacy platform\n", encoding="utf-8")
            command = [
                sys.executable, str(ROOT / "tools" / "install_codex.py"),
                "--agents-root", str(agents_root), "--codex-root", str(codex_root),
            ]
            subprocess.run(command, check=True)
            subprocess.run(command, check=True)

            active_names = sorted(path.name for path in (agents_root / "skills").iterdir())
            self.assertEqual(active_names, sorted(SKILL_SOURCES))
            backups = sorted((agents_root / "skill-backups").glob("*.backup-*"))
            self.assertEqual(len(backups), 2)
            self.assertFalse((codex_root / "skills" / "baijimu-platform").exists())


if __name__ == "__main__":
    unittest.main()
