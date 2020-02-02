"""Utility helpers."""
import os
from dataclasses import dataclass
from typing import Any, Optional

from agithub.base import IncompleteRequest
from agithub.GitHub import GitHub
from github import Github
from github.Organization import Organization
from github.Permissions import Permissions
from github.Repository import Repository

from .exceptions import RepoAdminError

__all__ = (
    "load_inputs",
    "load_context",
    "Inputs",
    "RepoContext",
    "permission_to_string",
    "HandlerRequest",
)


@dataclass
class HandlerRequest:
    """Values for a handler request."""

    data: Any
    repository: Optional[Repository] = None
    arepo: Optional[IncompleteRequest] = None
    organization: Optional[Organization] = None
    aorg: Optional[IncompleteRequest] = None

    def __post_init__(self):
        """Verify that at least one of the repo kinds was provided.

        TEMPORARY: REMOVE ONCE AGITHUB MIGRATION IS COMPLETE
        """
        if self.repository is self.arepo is None:
            raise ValueError("Must provide one of 'repository' or 'arepo'")


@dataclass
class Inputs:
    """Input values."""

    agithub: GitHub
    github: Github
    config_file: str
    debug: bool


def load_inputs() -> Inputs:
    """Load the input values from environment variables."""
    token = os.environ["INPUT_GITHUB-TOKEN"]
    config = os.environ.get("INPUT_CONFIG-FILE", ".github/settings.yml")
    debug = bool(os.environ.get("INPUT_DEBUG", ""))
    return Inputs(
        agithub=GitHub(token=token, paginate=True),
        github=Github(token),
        config_file=config,
        debug=debug,
    )


@dataclass
class RepoContext:
    """Information about the repository."""

    owner: str
    repo: str


def load_context() -> RepoContext:
    """Load the repository context from environment variables."""
    raw_repo = os.environ["GITHUB_REPOSITORY"]
    owner, repo = raw_repo.split("/", 1)
    return RepoContext(owner=owner, repo=repo)


def permission_to_string(permission: Permissions) -> str:
    """Convert a :class:`github.Permissions.Permissions` instance to the corresponding string."""
    if permission.admin:
        return "admin"

    if permission.push:
        return "push"

    if permission.pull:
        return "pull"

    raise RepoAdminError(f"Unknown permissions: {permission!r}")
