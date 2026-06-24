"""Configuration loading and validation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from configlib import load_yaml


class ConfigError(Exception):
    """Raised when the YAML config cannot be used."""


@dataclass(frozen=True)
class MarkdownSource:
    display_path: str
    path: Path


@dataclass(frozen=True)
class InvocationConfig:
    config_path: Path
    cwd: Path
    model: str | None
    tasks: list[MarkdownSource]
    rules: list[MarkdownSource]
    skills: list[MarkdownSource]


def load_invocation_config(config_path: Path) -> InvocationConfig:
    resolved_config_path = config_path.expanduser().resolve()
    if not resolved_config_path.is_file():
        raise ConfigError(f"config file not found: {config_path}")

    try:
        raw_config = load_yaml(resolved_config_path)
    except Exception as exc:  # configlib normalizes parser and file failures.
        raise ConfigError(f"failed to read config: {exc}") from exc

    if not isinstance(raw_config, dict):
        raise ConfigError("config must be a YAML mapping")

    base_dir = resolved_config_path.parent
    cwd = _resolve_cwd(raw_config.get("cwd"), base_dir)

    return InvocationConfig(
        config_path=resolved_config_path,
        cwd=cwd,
        model=_resolve_model(raw_config.get("model")),
        tasks=_resolve_markdown_sources(raw_config, "tasks", base_dir, required_non_empty=True),
        rules=_resolve_markdown_sources(raw_config, "rules", base_dir, required_non_empty=False),
        skills=_resolve_markdown_sources(raw_config, "skills", base_dir, required_non_empty=False),
    )


def _resolve_cwd(raw_cwd: Any, base_dir: Path) -> Path:
    if raw_cwd is None:
        cwd = base_dir
    elif isinstance(raw_cwd, str):
        cwd = _resolve_path(raw_cwd, base_dir)
    else:
        raise ConfigError("cwd must be a path string")

    if not cwd.is_dir():
        raise ConfigError(f"cwd must resolve to a directory: {cwd}")
    return cwd


def _resolve_model(raw_model: Any) -> str | None:
    if raw_model is None:
        return None
    if not isinstance(raw_model, str):
        raise ConfigError("model must be a string")
    model = raw_model.strip()
    if not model:
        raise ConfigError("model must not be empty")
    return model


def _resolve_markdown_sources(
    raw_config: dict[str, Any],
    key: str,
    base_dir: Path,
    *,
    required_non_empty: bool,
) -> list[MarkdownSource]:
    if key not in raw_config:
        raise ConfigError(f"{key} must be configured")

    raw_values = raw_config[key]
    if not isinstance(raw_values, list):
        raise ConfigError(f"{key} must be a list of file paths")
    if required_non_empty and not raw_values:
        raise ConfigError(f"{key} must not be empty")

    sources: list[MarkdownSource] = []
    for index, raw_value in enumerate(raw_values, start=1):
        if not isinstance(raw_value, str):
            raise ConfigError(f"{key}[{index}] must be a file path string")
        path = _resolve_path(raw_value, base_dir)
        if not path.is_file():
            raise ConfigError(f"{key}[{index}] must resolve to a file: {path}")
        sources.append(MarkdownSource(display_path=_display_path(raw_value, path), path=path))
    return sources


def _resolve_path(raw_path: str, base_dir: Path) -> Path:
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        path = base_dir / path
    return path.resolve()


def _display_path(raw_path: str, resolved_path: Path) -> str:
    if Path(raw_path).is_absolute():
        return resolved_path.as_posix()
    return Path(raw_path).as_posix()
