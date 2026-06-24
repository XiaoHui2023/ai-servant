"""Command-line entry point."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from claude import run_claude
from config import ConfigError, load_invocation_config
from prompt_markdown import MarkdownInputError, load_markdown_files, render_invocation


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a non-interactive Claude CLI task from a YAML config.")
    parser.add_argument("config", type=Path, help="YAML config file")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        invocation_config = load_invocation_config(args.config)
        rules = load_markdown_files(invocation_config.rules)
        skills = load_markdown_files(invocation_config.skills)
        tasks = load_markdown_files(invocation_config.tasks)
        prompt = render_invocation(rules=rules, skills=skills, tasks=tasks)
    except (ConfigError, MarkdownInputError) as exc:
        print(f"ai-servant: {exc}", file=sys.stderr)
        return 1

    return run_claude(prompt, cwd=invocation_config.cwd, model=invocation_config.model)
