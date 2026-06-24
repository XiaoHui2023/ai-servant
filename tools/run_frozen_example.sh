#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "==> Frozen executable metadata"
ls -la "$ROOT/dist/ai-servant"
file "$ROOT/dist/ai-servant" || true
echo "==> Frozen executable help smoke"
"$ROOT/dist/ai-servant" --help
echo "==> Full frozen example"
AI_SERVANT_EXE="$ROOT/dist/ai-servant" python3 "$ROOT/example/__main__.py"
