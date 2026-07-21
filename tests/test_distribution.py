from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "dist" / "baijimu-platform.zip"
HASH_FILE = ROOT / "dist" / "baijimu-platform.zip.sha256"


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

    def test_installer_keeps_backups_outside_active_skills(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            codex_root = Path(temp_dir)
            legacy = codex_root / "skills" / "baijimu-platform.backup-legacy"
            legacy.mkdir(parents=True)
            (legacy / "SKILL.md").write_text("legacy\n", encoding="utf-8")
            command = [
                sys.executable,
                str(ROOT / "tools" / "install_codex.py"),
                "--codex-root",
                str(codex_root),
            ]
            subprocess.run(command, check=True)
            subprocess.run(command, check=True)

            active_names = sorted(path.name for path in (codex_root / "skills").iterdir())
            self.assertEqual(active_names, ["baijimu-platform"])
            backups = sorted((codex_root / "skill-backups").glob("baijimu-platform.backup-*"))
            self.assertEqual(len(backups), 2)


if __name__ == "__main__":
    unittest.main()
