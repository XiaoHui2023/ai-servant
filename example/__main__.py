"""Run the ai-servant example end to end with a local fake Claude CLI."""

from __future__ import annotations

import os
import platform
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="ai-servant-example-") as temp_dir:
        temp = Path(temp_dir)
        fake_bin = temp / "bin"
        workspace = temp / "workspace"
        config_dir = temp / "config"
        fake_bin.mkdir()
        workspace.mkdir()
        config_dir.mkdir()

        _write_fake_claude(fake_bin, temp / "prompt.md")
        config_path = _write_config(config_dir, workspace)
        command = _ai_servant_command(config_path)
        env = os.environ.copy()
        env["PATH"] = str(fake_bin) + os.pathsep + env.get("PATH", "")

        completed = subprocess.run(command, text=True, capture_output=True, env=env, cwd=ROOT)
        if completed.returncode != 0:
            print(completed.stderr, file=sys.stderr)
            return completed.returncode

        expected = "FAKE_CLAUDE_OK --model sonnet --print"
        if expected not in completed.stdout:
            print(f"missing expected output: {expected}", file=sys.stderr)
            print(completed.stdout, file=sys.stderr)
            return 1

        prompt = (temp / "prompt.md").read_text(encoding="utf-8")
        checks = [
            "# ai-servant invocation",
            "## Rules\n\n### rules/base.md\n\nAlways run non-interactively.",
            "## Skills\n\n### skills/testing.md\n\nVerify observable behavior.",
            "## Tasks\n\n### tasks/demo.md\n\nPrint a concise success message.",
        ]
        for check in checks:
            if check not in prompt:
                print(f"prompt missing expected text: {check}", file=sys.stderr)
                return 1

    print("example ok")
    return 0


def _ai_servant_command(config_path: Path) -> list[str]:
    frozen_exe = os.environ.get("AI_SERVANT_EXE")
    if frozen_exe:
        return [frozen_exe, str(config_path)]
    return [sys.executable, str(ROOT / "src"), str(config_path)]


def _write_config(config_dir: Path, workspace: Path) -> Path:
    paths = {
        "tasks/demo.md": "Print a concise success message.\n",
        "rules/base.md": "Always run non-interactively.\n",
        "skills/testing.md": "Verify observable behavior.\n",
    }
    for rel_path, content in paths.items():
        path = config_dir / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    config_path = config_dir / "config.yaml"
    config_path.write_text(
        "\n".join(
            [
                f"cwd: {workspace.as_posix()}",
                "model: sonnet",
                "tasks:",
                "  - tasks/demo.md",
                "rules:",
                "  - rules/base.md",
                "skills:",
                "  - skills/testing.md",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return config_path


def _write_fake_claude(fake_bin: Path, prompt_path: Path) -> None:
    if platform.system() == "Windows":
        helper = fake_bin / "fake_claude.py"
        helper.write_text(
            "\n".join(
                [
                    "from __future__ import annotations",
                    "import sys",
                    f"prompt_path = {str(prompt_path)!r}",
                    "with open(prompt_path, 'w', encoding='utf-8') as fh:",
                    "    fh.write(sys.stdin.read())",
                    "print('FAKE_CLAUDE_OK ' + ' '.join(sys.argv[1:]))",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        script = fake_bin / "claude.bat"
        script.write_text(
            "\n".join(
                [
                    "@echo off",
                    f"\"{sys.executable}\" \"{helper}\" %*",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        return

    script = fake_bin / "claude"
    script.write_text(
        "\n".join(
            [
                "#!/usr/bin/env sh",
                f"cat > \"{prompt_path}\"",
                'printf "FAKE_CLAUDE_OK %s\\n" "$*"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    script.chmod(0o755)


if __name__ == "__main__":
    raise SystemExit(main())
