"""Assemble release archive: dist binaries plus user-facing docs."""

from __future__ import annotations

import platform
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BINARY_NAMES = ("ai-servant",)
RELEASE_PATHS = ("README.md",)


def main() -> int:
    dist = ROOT / "dist"
    tag = f"ai-servant-{_project_version()}-{_platform_tag()}"
    staging_root = dist / ".release-staging"
    bundle_dir = staging_root / tag
    if staging_root.exists():
        shutil.rmtree(staging_root)
    bundle_dir.mkdir(parents=True)

    copied = False
    for name in BINARY_NAMES:
        for candidate in (dist / name, dist / f"{name}.exe"):
            if candidate.is_file():
                shutil.copy2(candidate, bundle_dir / candidate.name)
                copied = True
    if not copied:
        print("error: no executable found in dist", file=sys.stderr)
        return 1

    for rel_path in RELEASE_PATHS:
        src = ROOT / rel_path
        if not src.exists():
            print(f"error: release path not found: {src}", file=sys.stderr)
            return 1
        dest = bundle_dir / rel_path
        if src.is_dir():
            shutil.copytree(src, dest)
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)

    archive_base = dist / tag
    archive_format = "zip" if platform.system() == "Windows" else "gztar"
    for old in (dist / f"{tag}.zip", dist / f"{tag}.tar.gz"):
        if old.is_file():
            old.unlink()
    shutil.make_archive(str(archive_base), archive_format, staging_root, tag)
    shutil.rmtree(staging_root)
    suffix = ".zip" if archive_format == "zip" else ".tar.gz"
    print(f"created {archive_base}{suffix}")
    return 0


def _project_version() -> str:
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'(?m)^version\s*=\s*"([^"]+)"', text)
    if not match:
        raise RuntimeError("version not found in pyproject.toml")
    return match.group(1)


def _platform_tag() -> str:
    return {"Linux": "linux", "Darwin": "macos", "Windows": "windows"}.get(
        platform.system(), platform.system().lower()
    )


if __name__ == "__main__":
    raise SystemExit(main())
