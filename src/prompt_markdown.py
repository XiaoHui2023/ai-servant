"""Markdown input reading and prompt assembly."""

from __future__ import annotations

from dataclasses import dataclass

from config import MarkdownSource
from prompt import INVOCATION_PREAMBLE


class MarkdownInputError(Exception):
    """Raised when a configured Markdown file cannot be read."""


@dataclass(frozen=True)
class MarkdownDocument:
    display_path: str
    content: str


def load_markdown_files(sources: list[MarkdownSource]) -> list[MarkdownDocument]:
    documents: list[MarkdownDocument] = []
    for source in sources:
        try:
            content = source.path.read_text(encoding="utf-8")
        except OSError as exc:
            raise MarkdownInputError(f"failed to read {source.display_path}: {exc}") from exc
        except UnicodeDecodeError as exc:
            raise MarkdownInputError(f"failed to read {source.display_path} as UTF-8: {exc}") from exc
        documents.append(MarkdownDocument(display_path=source.display_path, content=content))
    return documents


def render_invocation(
    *,
    rules: list[MarkdownDocument],
    skills: list[MarkdownDocument],
    tasks: list[MarkdownDocument],
) -> str:
    parts = [
        INVOCATION_PREAMBLE.strip(),
        _render_section("Rules", rules),
        _render_section("Skills", skills),
        _render_section("Tasks", tasks),
    ]
    return "\n\n".join(parts) + "\n"


def _render_section(title: str, documents: list[MarkdownDocument]) -> str:
    lines = [f"## {title}"]
    for document in documents:
        lines.extend(["", f"### {document.display_path}", "", document.content.rstrip()])
    return "\n".join(lines)
