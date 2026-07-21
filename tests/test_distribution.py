from __future__ import annotations

import hashlib
import subprocess
import sys
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
            self.assertEqual(
                names,
                [
                    "baijimu-platform/SKILL.md",
                    "baijimu-platform/references/cli-and-runtime-entrypoints.md",
                    "baijimu-platform/references/desktop-and-bridge-agent.md",
                    "baijimu-platform/references/platform-map.md",
                ],
            )
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


if __name__ == "__main__":
    unittest.main()
