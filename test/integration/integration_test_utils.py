"""Helper tools for ``repo_manager`` integration tests."""
import os
import time
from collections import defaultdict

import github
import pytest
from agithub.GitHub import GitHub

__all__ = (
    "INTEG_FLAKE",
    "integ_repo",
    "github_client",
    "agithub_client",
    "REPO_ORG",
    "private_integ_repo",
    "baseline_wait",
)

REPO_ORG = "mattsb42-meta"


def baseline_wait():
    """Flaky does not trigger if tests fail, and resetting to baseline is having issues with eventual consistency."""
    time.sleep(0.5)


class RetryBackoff:
    def __init__(self, step_size=1):
        self._step_size = step_size
        self._test_records = defaultdict(int)

    def __call__(self, err, name, test, plugin):
        # First call sleep time is always 0
        # because flaky calls this on every call,
        # not just on retries.
        time.sleep(self._test_records[name])
        self._test_records[name] += self._step_size
        return True


INTEG_FLAKE = pytest.mark.flaky(max_runs=3, rerun_filter=RetryBackoff())


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
