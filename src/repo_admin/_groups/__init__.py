"""Handlers for all data groups."""
import importlib
from functools import partial
from typing import Any, Callable, Dict

import yaml

from .._util import Inputs, RepoContext

__all__ = ("parse_config", "apply_config")


def _load_handler(group: str) -> Callable[[RepoContext, str, Any], None]:
    try:
        handler = importlib.import_module(f"{__name__}.{group}")
    except Exception:
        raise Exception(f"Unknown config group '{group}'")

    return handler.apply


def parse_config(inputs: Inputs, context: RepoContext) -> Dict[str, Callable[[], None]]:
    with open(inputs.config_file, "r") as raw:
        raw_config = yaml.safe_load(raw)

    repo = inputs.github.get_repo(full_name_or_id=f"{context.owner}/{context.repo}")
    return {
        group: partial(_load_handler(group), repo, data)
        for group, data in raw_config.items()
    }


def apply_config(config: Dict[str, Callable[[], None]]):
    for prepped in config.values():
        prepped()
