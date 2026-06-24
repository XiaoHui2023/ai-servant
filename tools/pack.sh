#!/usr/bin/env bash
# Pack ai-servant as a PyInstaller onefile executable.
# Usage: ./tools/pack.sh [src]
# Outputs: dist/ai-servant and dist/ai-servant-<version>-<platform>.tar.gz.
# Linux builds run staticx by default and require patchelf. Set
# PACK_LINUX_SKIP_STATICX=1 only when intentionally building a non-static Linux
# artifact. Windows users should run tools\pack.bat instead.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${1:-src}"
PYTHON_CMD=()

ensure_venv() {
  if [[ -x "$ROOT/.venv/bin/python" ]]; then
    PYTHON_CMD=("$ROOT/.venv/bin/python")
  elif [[ -x "$ROOT/.venv/Scripts/python.exe" ]]; then
    PYTHON_CMD=("$ROOT/.venv/Scripts/python.exe")
  else
    python3 -m venv "$ROOT/.venv"
    PYTHON_CMD=("$ROOT/.venv/bin/python")
  fi
  echo "==> Python: ${PYTHON_CMD[*]}"
  "${PYTHON_CMD[@]}" -V
}

apply_staticx_linux() {
  local dist_name="$1"
  local pyi_out="$ROOT/dist/${dist_name}"
  if [[ ! -f "$pyi_out" ]]; then
    return 0
  fi
  if ! command -v patchelf >/dev/null 2>&1; then
    echo "error: Linux staticx builds require patchelf" >&2
    exit 1
  fi
  "${PYTHON_CMD[@]}" -m pip install -q --upgrade --force-reinstall staticx
  local staticx="$ROOT/.venv/bin/staticx"
  local tmp_out="$ROOT/dist/.${dist_name}-staticx.tmp"
  rm -f "$tmp_out"
  echo "==> staticx --no-compress: $pyi_out"
  "$staticx" --no-compress "$pyi_out" "$tmp_out"
  mv -f "$tmp_out" "$pyi_out"
  chmod +x "$pyi_out"
}

build_src() {
  echo "==> PyInstaller: ai-servant-cli.spec"
  "${PYTHON_CMD[@]}" -m PyInstaller --clean --noconfirm "$ROOT/ai-servant-cli.spec"
  if [[ -f "$ROOT/dist/ai-servant.exe" ]]; then
    echo "created $ROOT/dist/ai-servant.exe"
    return 0
  fi
  if [[ ! -f "$ROOT/dist/ai-servant" ]]; then
    echo "error: dist/ai-servant was not created" >&2
    exit 1
  fi
  if [[ "$(uname -s 2>/dev/null || true)" == "Linux" && "${PACK_LINUX_SKIP_STATICX:-}" != "1" ]]; then
    apply_staticx_linux "ai-servant"
  fi
  echo "created $ROOT/dist/ai-servant"
}

case "$TARGET" in
  src) ;;
  *) echo "usage: ./tools/pack.sh [src]" >&2; exit 1 ;;
esac

ensure_venv
"${PYTHON_CMD[@]}" -m pip install -q -U pip setuptools wheel
"${PYTHON_CMD[@]}" -m pip install -q --upgrade --force-reinstall -e .
"${PYTHON_CMD[@]}" -m pip install -q --upgrade --force-reinstall "pyinstaller>=6.0"

rm -rf "$ROOT/build" "$ROOT/dist"
build_src
echo "==> Bundle release archive"
"${PYTHON_CMD[@]}" "$ROOT/tools/bundle_release.py"
echo "PyInstaller output: $ROOT/dist"
