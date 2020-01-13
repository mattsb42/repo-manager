"""Utility helpers."""
import os
from dataclasses import dataclass

from github import Github
from github.Permissions import Permissions

__all__ = ("load_inputs", "load_context", "Inputs", "RepoContext", "permission_to_string")


@dataclass
class Inputs:
    github: Github
    config_file: str
    debug: bool


def load_inputs() -> Inputs:
    token = os.environ["INPUT_GITHUB-TOKEN"]
    config = os.environ.get("INPUT_CONFIG-FILE", ".github/settings.yml")
    debug = bool(os.environ.get("INPUT_DEBUG", ""))
    return Inputs(github=Github(token), config_file=config, debug=debug)


@dataclass
class RepoContext:
    owner: str
    repo: str


def load_context() -> RepoContext:
    raw_repo = os.environ["GITHUB_REPOSITORY"]
    owner, repo = raw_repo.split("/", 1)
    return RepoContext(owner=owner, repo=repo)


def permission_to_string(permission: Permissions) -> str:
    if permission.admin:
        return "admin"

    if permission.push:
        return "push"

    if permission.pull:
        return "pull"

    raise Exception("Unknown permissions type!")
