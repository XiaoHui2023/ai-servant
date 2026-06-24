"""Claude CLI subprocess integration."""

from __future__ import annotations

import subprocess
import shutil
import sys
from pathlib import Path


def run_claude(prompt: str, *, cwd: Path, model: str | None = None) -> int:
    executable = shutil.which("claude")
    if executable is None:
        print("ai-servant: Claude CLI executable not found: claude", file=sys.stderr)
        return 1

    command = [executable]
    if model is not None:
        command.extend(["--model", model])
    command.append("--print")

    try:
        completed = subprocess.run(
            command,
            input=prompt,
            text=True,
            cwd=cwd,
        )
    except FileNotFoundError:
        print("ai-servant: Claude CLI executable not found: claude", file=sys.stderr)
        return 1
    return completed.returncode
