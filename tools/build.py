#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import re
import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
MARKETPLACE = ROOT / "marketplace"
FIXED_TIME = (2026, 1, 1, 0, 0, 0)
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
SKILLS = {
    "baijimu-platform": ROOT / "SKILL.md",
}


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


def render_marketplace(name: str, skill_text: str, version: str) -> str:
    frontmatter, body = split_frontmatter(skill_text)
    description = next(
        (line for line in frontmatter.splitlines() if line.startswith("description:")), None
    )
    if description is None:
        fail(f"{name} frontmatter must contain description")
    market_frontmatter = [
        "---",
        f"name: {name}",
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


def validate() -> dict[str, str]:
    texts: dict[str, str] = {}
    for name, path in SKILLS.items():
        if not path.is_file():
            fail(f"missing skill file: {path}")
        if path.is_symlink():
            fail(f"symlinks are not allowed: {path}")
        data = path.read_bytes()
        if b"\0" in data:
            fail(f"binary content is not allowed: {path}")
        text = data.decode("utf-8")
        if "/Users/" in text or "lc_pat_" in text:
            fail(f"local path or token-shaped content found: {path}")
        frontmatter, _ = split_frontmatter(text)
        keys = [
            line.split(":", 1)[0]
            for line in frontmatter.splitlines()
            if line.strip() and not line.startswith((" ", "\t"))
        ]
        if keys != ["name", "description"]:
            fail(f"{name} frontmatter must contain only name and description, got {keys}")
        if f"name: {name}" not in frontmatter:
            fail(f"frontmatter name must be {name}")
        if "references/" in text:
            fail(f"{name} must use versioned official docs instead of bundled references")
        texts[name] = text
    return texts


def build(texts: dict[str, str], version: str) -> dict[str, str]:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    if MARKETPLACE.exists():
        shutil.rmtree(MARKETPLACE)
    MARKETPLACE.mkdir(parents=True)

    digests: dict[str, str] = {}
    for name, text in texts.items():
        marketplace_dir = MARKETPLACE / name
        marketplace_dir.mkdir(parents=True)
        (marketplace_dir / "SKILL.md").write_text(
            render_marketplace(name, text, version), encoding="utf-8"
        )

        archive_path = DIST / f"{name}.zip"
        with zipfile.ZipFile(
            archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
        ) as archive:
            info = zipfile.ZipInfo(f"{name}/SKILL.md", FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, text.encode("utf-8"))
        digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
        (DIST / f"{name}.zip.sha256").write_text(
            f"{digest}  {archive_path.name}\n", encoding="utf-8"
        )
        digests[name] = digest
    return digests


if __name__ == "__main__":
    skill_texts = validate()
    release_version = read_version()
    skill_digests = build(skill_texts, release_version)
    print(f"validated {len(skill_texts)} skills")
    for skill_name, sha256 in skill_digests.items():
        print(f"built {DIST / f'{skill_name}.zip'}")
        print(f"sha256 {sha256}")
