#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AI_SERVANT_EXE="$ROOT/dist/ai-servant" python3 "$ROOT/example/__main__.py"
