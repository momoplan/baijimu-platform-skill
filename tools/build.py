#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import re
import shutil
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT
DIST = ROOT / "dist"
ARCHIVE = DIST / "baijimu-platform.zip"
HASH_FILE = DIST / "baijimu-platform.zip.sha256"
FIXED_TIME = (2026, 1, 1, 0, 0, 0)
EXPECTED = {
    "SKILL.md",
    "references/cli-and-runtime-entrypoints.md",
    "references/desktop-and-bridge-agent.md",
    "references/platform-map.md",
}


def fail(message: str) -> None:
    raise SystemExit(f"error: {message}")


def validate() -> list[Path]:
    files = [SKILL / relative for relative in sorted(EXPECTED)]
    missing = [path for path in files if not path.is_file()]
    if missing:
        fail(f"missing skill files: {missing}")
    relative = {path.relative_to(SKILL).as_posix() for path in files}
    if relative != EXPECTED:
        fail(f"skill files differ from expected text-only layout: {sorted(relative)}")

    skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", skill_text, re.DOTALL)
    if not match:
        fail("SKILL.md must start with YAML frontmatter")
    keys = []
    for line in match.group(1).splitlines():
        if not line.strip() or line.startswith((" ", "\t")):
            continue
        keys.append(line.split(":", 1)[0])
    if keys != ["name", "description"]:
        fail(f"frontmatter must contain only name and description, got {keys}")
    if "name: baijimu-platform" not in match.group(1):
        fail("frontmatter name must be baijimu-platform")

    for path in files:
        if path.is_symlink():
            fail(f"symlinks are not allowed: {path}")
        data = path.read_bytes()
        if b"\0" in data:
            fail(f"binary content is not allowed: {path}")
        text = data.decode("utf-8")
        if "/Users/" in text or "lc_pat_" in text:
            fail(f"local path or token-shaped content found: {path}")
        if path.suffix.lower() != ".md":
            fail(f"distribution accepts Markdown only: {path}")

    for reference in re.findall(r"`(references/[^`]+\.md)`", skill_text):
        if not (SKILL / reference).is_file():
            fail(f"missing referenced file: {reference}")
    return files


def build(files: list[Path]) -> str:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    with zipfile.ZipFile(ARCHIVE, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            relative = path.relative_to(SKILL).as_posix()
            info = zipfile.ZipInfo(f"baijimu-platform/{relative}", FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    digest = hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()
    HASH_FILE.write_text(f"{digest}  {ARCHIVE.name}\n", encoding="utf-8")
    return digest


if __name__ == "__main__":
    skill_files = validate()
    sha256 = build(skill_files)
    print(f"validated {len(skill_files)} text files")
    print(f"built {ARCHIVE}")
    print(f"sha256 {sha256}")
