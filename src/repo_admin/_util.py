"""Utility helpers."""
import os
from dataclasses import dataclass
from typing import Any, Optional

from github import Github
from github.Organization import Organization
from github.Permissions import Permissions
from github.Repository import Repository

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

    repository: Repository
    data: Any
    organization: Optional[Organization] = None


@dataclass
class Inputs:
    """Input values."""

    github: Github
    config_file: str
    debug: bool


def load_inputs() -> Inputs:
    """Load the input values from environment variables."""
    token = os.environ["INPUT_GITHUB-TOKEN"]
    config = os.environ.get("INPUT_CONFIG-FILE", ".github/settings.yml")
    debug = bool(os.environ.get("INPUT_DEBUG", ""))
    return Inputs(github=Github(token), config_file=config, debug=debug)


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

    raise Exception("Unknown permissions type!")
