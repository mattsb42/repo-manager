"""Handlers for all data groups."""
import importlib
from functools import partial
from typing import Any, Callable, Dict

import yaml
from github.GithubException import UnknownObjectException

from .._util import HandlerRequest, Inputs, RepoContext
from ..exceptions import RepoAdminError

__all__ = ("parse_config", "apply_config")


def _load_handler(group: str) -> Callable[[RepoContext, str, Any], None]:
    try:
        handler = importlib.import_module(f"{__name__}.{group}")
    except Exception:
        raise RepoAdminError(f"Unknown config group '{group}'")

    # mypy doesn't know how to follow module import magic
    return handler.apply  # type: ignore


def parse_config(inputs: Inputs, context: RepoContext) -> Dict[str, Callable[[], None]]:
    """Parse a config file give inputs and context.

    :returns: mapping of group name to curried handlers
    """
    with open(inputs.config_file, "r") as raw:
        raw_config = yaml.safe_load(raw)

    repository = inputs.github.get_repo(full_name_or_id=f"{context.owner}/{context.repo}")
    repo = getattr(getattr(inputs.agithub.repos, context.owner), context.repo)
    try:
        organization = inputs.github.get_organization(context.owner)

    except UnknownObjectException:
        organization = None

    org = getattr(inputs.agithub.orgs, context.owner)
    status, _org_data = org.get()
    if status != 200:
        org = None

    return {
        group: partial(
            _load_handler(group),
            HandlerRequest(
                data=data, repository=repository, arepo=repo, organization=organization, aorg=org
            ),
        )
        for group, data in raw_config.items()
    }


def apply_config(config: Dict[str, Callable[[], None]]):
    """Apply curried config handlers."""
    for prepped in config.values():
        prepped()
