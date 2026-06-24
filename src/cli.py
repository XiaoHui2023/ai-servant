"""CLI 参数与入口逻辑。"""

from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI Servant 本地工具")
    parser.add_argument("-v", "--version", action="version", version="0.0.0")
    return parser


def main(argv: list[str] | None = None) -> None:
    build_parser().parse_args(argv)
