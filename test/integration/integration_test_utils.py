"""Helper tools for ``repo_manager`` integration tests."""
import os

import github
import pytest
from agithub.GitHub import GitHub

__all__ = ("integ_repo", "github_client", "agithub_client", "REPO_ORG", "private_integ_repo")

REPO_ORG = "mattsb42-meta"


@pytest.fixture
def integ_repo(monkeypatch):
    repo = "mattsb42-meta/repo-manager-test-client"
    monkeypatch.setenv("GITHUB_REPOSITORY", repo)
    yield repo


@pytest.fixture
def private_integ_repo(monkeypatch):
    user = os.environ.get("GITHUB_USER", "mattsb42-admin-bot")
    repo = f"{user}/repo-manager-test-client"
    monkeypatch.setenv("GITHUB_REPOSITORY", repo)
    yield repo


@pytest.fixture
def github_client(monkeypatch):
    token = os.environ["GITHUB_TOKEN"]
    monkeypatch.setenv("INPUT_GITHUB-TOKEN", token)
    yield github.Github(login_or_token=token)


@pytest.fixture
def agithub_client(monkeypatch):
    token = os.environ["GITHUB_TOKEN"]
    monkeypatch.setenv("INPUT_GITHUB-TOKEN", token)
    yield GitHub(token=token)
