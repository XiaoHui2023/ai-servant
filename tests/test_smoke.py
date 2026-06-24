"""Core behavior tests."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from claude import run_claude
from cli import build_parser, main
from config import ConfigError, load_invocation_config
from prompt_markdown import load_markdown_files, render_invocation


class CliTest(unittest.TestCase):
    def test_parser_accepts_only_config_path(self) -> None:
        args = build_parser().parse_args(["config.yaml"])
        self.assertEqual(args.config, Path("config.yaml"))

    def test_main_returns_one_for_invalid_config_without_calling_claude(self) -> None:
        with patch("cli.run_claude") as run_claude:
            exit_code = main(["missing.yaml"])
        self.assertEqual(exit_code, 1)
        run_claude.assert_not_called()

    def test_main_calls_claude_with_rendered_prompt_and_resolved_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            target = root / "target"
            target.mkdir()
            (root / "task.md").write_text("Task body.", encoding="utf-8")
            config_path = root / "config.yaml"
            config_path.write_text(
                "cwd: target\nmodel: sonnet\ntasks:\n  - task.md\nrules: []\nskills: []\n",
                encoding="utf-8",
            )
            with patch("cli.run_claude", return_value=7) as run_claude:
                exit_code = main([str(config_path)])

        self.assertEqual(exit_code, 7)
        run_claude.assert_called_once()
        prompt = run_claude.call_args.args[0]
        self.assertIn("### task.md\n\nTask body.", prompt)
        self.assertEqual(run_claude.call_args.kwargs["cwd"], target.resolve())
        self.assertEqual(run_claude.call_args.kwargs["model"], "sonnet")


class ConfigTest(unittest.TestCase):
    def test_load_config_resolves_markdown_from_config_dir_and_cwd_separately(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_dir = root / "configs"
            target_dir = root / "target"
            config_dir.mkdir()
            target_dir.mkdir()
            (config_dir / "task.md").write_text("task", encoding="utf-8")
            (config_dir / "rule.md").write_text("rule", encoding="utf-8")
            (config_dir / "skill.md").write_text("skill", encoding="utf-8")
            config_path = config_dir / "config.yaml"
            config_path.write_text(
                "\n".join(
                    [
                        "cwd: ../target",
                        "tasks:",
                        "  - task.md",
                        "rules:",
                        "  - rule.md",
                        "skills:",
                        "  - skill.md",
                    ]
                ),
                encoding="utf-8",
            )

            loaded = load_invocation_config(config_path)

        self.assertEqual(loaded.cwd, target_dir.resolve())
        self.assertIsNone(loaded.model)
        self.assertEqual(loaded.tasks[0].path, (config_dir / "task.md").resolve())
        self.assertEqual(loaded.tasks[0].display_path, "task.md")

    def test_model_must_be_non_empty_when_configured(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "task.md").write_text("task", encoding="utf-8")
            config_path = root / "config.yaml"
            config_path.write_text(
                'model: "  "\ntasks:\n  - task.md\nrules: []\nskills: []\n',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ConfigError, "model must not be empty"):
                load_invocation_config(config_path)

    def test_tasks_must_be_non_empty(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"
            config_path.write_text("tasks: []\nrules: []\nskills: []\n", encoding="utf-8")
            with self.assertRaisesRegex(ConfigError, "tasks must not be empty"):
                load_invocation_config(config_path)


class MarkdownTest(unittest.TestCase):
    def test_render_invocation_keeps_sections_and_source_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "task.md").write_text("Fix login.", encoding="utf-8")
            (root / "rule.md").write_text("No questions.", encoding="utf-8")
            (root / "skill.md").write_text("Use tests.", encoding="utf-8")
            config_path = root / "config.yaml"
            config_path.write_text(
                "tasks:\n  - task.md\nrules:\n  - rule.md\nskills:\n  - skill.md\n",
                encoding="utf-8",
            )
            loaded = load_invocation_config(config_path)
            prompt = render_invocation(
                rules=load_markdown_files(loaded.rules),
                skills=load_markdown_files(loaded.skills),
                tasks=load_markdown_files(loaded.tasks),
            )

        self.assertIn("# ai-servant invocation", prompt)
        self.assertIn("Do not ask the user questions.", prompt)
        self.assertIn("## Rules\n\n### rule.md\n\nNo questions.", prompt)
        self.assertIn("## Skills\n\n### skill.md\n\nUse tests.", prompt)
        self.assertIn("## Tasks\n\n### task.md\n\nFix login.", prompt)


class ClaudeTest(unittest.TestCase):
    def test_run_claude_passes_model_before_print(self) -> None:
        with patch("claude.shutil.which", return_value="claude"), patch("claude.subprocess.run") as subprocess_run:
            subprocess_run.return_value.returncode = 3
            exit_code = run_claude("prompt", cwd=Path("."), model="claude-sonnet-4-6")

        self.assertEqual(exit_code, 3)
        subprocess_run.assert_called_once()
        self.assertEqual(
            subprocess_run.call_args.args[0],
            ["claude", "--model", "claude-sonnet-4-6", "--print"],
        )


if __name__ == "__main__":
    unittest.main()
