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
MARKETPLACE_DIR = ROOT / "marketplace" / "baijimu-platform"
MARKETPLACE_SKILL = MARKETPLACE_DIR / "SKILL.md"
FIXED_TIME = (2026, 1, 1, 0, 0, 0)
EXPECTED = {"SKILL.md"}
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")


def fail(message: str) -> None:
    raise SystemExit(f"error: {message}")


def read_version() -> str:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not SEMVER.fullmatch(version):
        fail(f"VERSION must be a stable semantic version, got {version!r}")
    return version


def split_frontmatter(skill_text: str) -> tuple[str, str]:
    match = re.match(r"\A---\n(.*?)\n---\n", skill_text, re.DOTALL)
    if not match:
        fail("SKILL.md must start with YAML frontmatter")
    return match.group(1), skill_text[match.end() :]


def render_marketplace(skill_text: str, version: str) -> str:
    frontmatter, body = split_frontmatter(skill_text)
    description = next(
        (line for line in frontmatter.splitlines() if line.startswith("description:")),
        None,
    )
    if description is None:
        fail("SKILL.md frontmatter must contain description")
    market_frontmatter = [
        "---",
        "name: baijimu-platform",
        description,
        f"version: {version}",
        "author: Baijimu",
        "license: MIT-0",
        "platforms: [openclaw, hermes]",
        "metadata:",
        "  openclaw:",
        "    requires:",
        "      bins: [baijimu]",
        "    install:",
        "      - kind: node",
        '        package: "@baijimu/cli"',
        "        bins: [baijimu]",
        "    homepage: https://github.com/momoplan/baijimu-platform-skill",
        "  hermes:",
        "    tags: [baijimu, lowcode, automation, cli]",
        "    requires_toolsets: [terminal]",
        "---",
    ]
    return "\n".join(market_frontmatter) + "\n" + body


def validate() -> tuple[list[Path], str]:
    files = [SKILL / relative for relative in sorted(EXPECTED)]
    missing = [path for path in files if not path.is_file()]
    if missing:
        fail(f"missing skill files: {missing}")
    relative = {path.relative_to(SKILL).as_posix() for path in files}
    if relative != EXPECTED:
        fail(f"skill files differ from expected text-only layout: {sorted(relative)}")

    skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    frontmatter, _ = split_frontmatter(skill_text)
    keys = []
    for line in frontmatter.splitlines():
        if not line.strip() or line.startswith((" ", "\t")):
            continue
        keys.append(line.split(":", 1)[0])
    if keys != ["name", "description"]:
        fail(f"frontmatter must contain only name and description, got {keys}")
    if "name: baijimu-platform" not in frontmatter:
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

    if "references/" in skill_text:
        fail("SKILL.md must not depend on bundled references; use versioned official docs")
    return files, skill_text


def build(files: list[Path], marketplace_text: str) -> str:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    if MARKETPLACE_DIR.exists():
        shutil.rmtree(MARKETPLACE_DIR)
    MARKETPLACE_DIR.mkdir(parents=True)
    MARKETPLACE_SKILL.write_text(marketplace_text, encoding="utf-8")
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
    skill_files, source_text = validate()
    release_version = read_version()
    marketplace = render_marketplace(source_text, release_version)
    sha256 = build(skill_files, marketplace)
    print(f"validated {len(skill_files)} text files")
    print(f"generated {MARKETPLACE_SKILL}")
    print(f"built {ARCHIVE}")
    print(f"sha256 {sha256}")
