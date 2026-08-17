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
ARCHIVE = ROOT / "dist" / "baijimu-platform.zip"
HASH_FILE = ROOT / "dist" / "baijimu-platform.zip.sha256"
MARKETPLACE_SKILL = ROOT / "marketplace" / "baijimu-platform" / "SKILL.md"


class DistributionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run([sys.executable, str(ROOT / "tools" / "build.py")], check=True)

    def test_archive_is_text_only_and_portable(self) -> None:
        with zipfile.ZipFile(ARCHIVE) as archive:
            names = archive.namelist()
            self.assertEqual(names, ["baijimu-platform/SKILL.md"])
            for name in names:
                self.assertTrue(name.endswith(".md"))
                archive.read(name).decode("utf-8")

    def test_archive_is_reproducible(self) -> None:
        first = ARCHIVE.read_bytes()
        subprocess.run([sys.executable, str(ROOT / "tools" / "build.py")], check=True)
        self.assertEqual(first, ARCHIVE.read_bytes())

    def test_sha256_matches(self) -> None:
        recorded = HASH_FILE.read_text(encoding="utf-8").split()[0]
        actual = hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()
        self.assertEqual(recorded, actual)

    def test_marketplace_skill_is_generated_from_canonical_source(self) -> None:
        source = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        marketplace = MARKETPLACE_SKILL.read_text(encoding="utf-8")
        source_match = re.match(r"\A---\n.*?\n---\n", source, re.DOTALL)
        marketplace_match = re.match(r"\A---\n(.*?)\n---\n", marketplace, re.DOTALL)
        self.assertIsNotNone(source_match)
        self.assertIsNotNone(marketplace_match)
        assert source_match is not None
        assert marketplace_match is not None
        self.assertEqual(source[source_match.end() :], marketplace[marketplace_match.end() :])

        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        metadata = marketplace_match.group(1)
        self.assertIn(f"version: {version}", metadata)
        self.assertIn("license: MIT-0", metadata)
        self.assertIn("platforms: [openclaw, hermes]", metadata)
        self.assertIn("  openclaw:", metadata)
        self.assertIn("      bins: [baijimu]", metadata)
        self.assertIn('        package: "@baijimu/cli"', metadata)
        self.assertIn("  hermes:", metadata)
        self.assertIn("    requires_toolsets: [terminal]", metadata)

    def test_marketplace_folder_contains_only_the_publishable_skill(self) -> None:
        files = sorted(
            path.relative_to(MARKETPLACE_SKILL.parent).as_posix()
            for path in MARKETPLACE_SKILL.parent.rglob("*")
            if path.is_file()
        )
        self.assertEqual(files, ["SKILL.md"])

    def test_skill_routes_bundle_changes_to_the_canonical_publish_contract(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for required in [
            "https://docs.baijimu.com/development/bundle-development/change-and-release/",
            "https://docs.baijimu.com/development/bundle-development/module-development/http-method-body/",
            "snake_case",
            "创建模块版本",
            "发布不可变 Bundle 版本",
            "回查工作区审核",
            "验证资源台账和真实运行时调用",
            "不得用同一身份自行批准",
            "面向普通用户和开发者的稳定产品契约只以官方文档站为准",
            "不得改用复制这些流程的专项技能",
        ]:
            self.assertIn(required, skill)

    def test_skill_routes_project_git_by_live_main_policy(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for required in [
            "project branch-policy get",
            "`DIRECT`",
            "`PROTECTED`",
            "快进方式直推 `main`",
            "用户可以合并自己的分支",
            "两种策略都禁止删除、强推或非快进覆盖 `main`",
            "https://docs.baijimu.com/concepts/projects/",
        ]:
            self.assertIn(required, skill)
        self.assertNotIn("修改必须通过 `project checkout` 检出 canonical 仓库，在生成的 Codex 分支上", skill)

    def test_repository_license_matches_clawhub_license(self) -> None:
        license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        self.assertTrue(license_text.startswith("MIT No Attribution\n"))
        self.assertIn("without limitation the rights", license_text)

    def test_installer_unifies_legacy_skills_and_is_idempotent(self) -> None:
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
                sys.executable,
                str(ROOT / "tools" / "install_codex.py"),
                "--agents-root",
                str(agents_root),
                "--codex-root",
                str(codex_root),
            ]
            subprocess.run(command, check=True)
            subprocess.run(command, check=True)

            active_names = sorted(path.name for path in (agents_root / "skills").iterdir())
            self.assertEqual(active_names, ["baijimu-platform"])
            backups = sorted((agents_root / "skill-backups").glob("*.backup-*"))
            self.assertEqual(len(backups), 2)
            self.assertFalse((codex_root / "skills" / "baijimu-platform").exists())


if __name__ == "__main__":
    unittest.main()
