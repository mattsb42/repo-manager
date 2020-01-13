import pytest

import repo_admin

from .functional_test_utils import vector_file

pytestmark = [pytest.mark.local, pytest.mark.functional]


@pytest.fixture(autouse=True)
def github_actions_environment(monkeypatch):
    monkeypatch.setenv("INPUT_GITHUB-TOKEN", "an-token")
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo-name")


def test_pytestmark(monkeypatch):
    monkeypatch.setenv("INPUT_CONFIG-FILE", vector_file("settings.yml"))

    repo_admin.cli([])
    raise Exception()
