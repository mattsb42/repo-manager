"""Integration test suite for ``repo_manager._groups.teams``."""
from copy import deepcopy
from typing import Dict, List

import pytest
from github.Organization import Organization
from github.Repository import Repository
from github.Team import Team

from repo_manager._groups import teams
from repo_manager._util import HandlerRequest

from ..integration_test_utils import github_client  # noqa pylint: disable=unused-import
from ..integration_test_utils import integ_repo  # noqa pylint: disable=unused-import
from ..integration_test_utils import REPO_ORG

pytestmark = [pytest.mark.integ]


BASELINE = [dict(name="bots", permission="pull")]


def compare_team_permissions(*, actual: List[Team], expected: Dict[str, Dict[str, str]]):
    assert len(actual) == len(expected)
    for team in actual:
        assert team.name in expected
        expected_values = expected[team.name]
        assert team.permission == expected_values["permission"]


def assert_baseline(repo: Repository):
    team_data = list(repo.get_teams())

    check_data = {team["name"]: team for team in BASELINE}

    compare_team_permissions(actual=team_data, expected=check_data)


def apply_baseline(repo: Repository, org: Organization):
    request = HandlerRequest(repository=repo, data=deepcopy(BASELINE), organization=org)
    teams.apply(request)

    assert_baseline(repo)


@pytest.fixture
def from_baseline(integ_repo, github_client):
    repo = github_client.get_repo(integ_repo)
    org = github_client.get_organization(REPO_ORG)
    yield repo, org
    apply_baseline(repo, org)


@pytest.fixture
def no_teams_but_return_to_baseline(integ_repo, github_client):
    repo = github_client.get_repo(integ_repo)
    org = github_client.get_organization(REPO_ORG)
    request = HandlerRequest(repository=repo, data=[], organization=org)
    teams.apply(request)
    current_teams = list(repo.get_teams())
    assert len(current_teams) == 0
    yield repo, org
    apply_baseline(repo, org)


@pytest.fixture
def push_bots_return_to_baseline(integ_repo, github_client):
    repo = github_client.get_repo(integ_repo)
    org = github_client.get_organization(REPO_ORG)
    request = HandlerRequest(
        repository=repo, data=[dict(name="bots", permission="push")], organization=org
    )
    teams.apply(request)
    yield repo, org
    apply_baseline(repo, org)


def test_teams_baseline(integ_repo, github_client):
    repo = github_client.get_repo(integ_repo)
    org = github_client.get_organization(REPO_ORG)
    apply_baseline(repo, org)
    assert_baseline(repo)


def _cases():
    change_permission = deepcopy(BASELINE)
    change_permission[0]["permission"] = "push"
    yield pytest.param(change_permission, id="change team permissions")

    add_team = deepcopy(BASELINE)
    add_team.append(dict(name="admins", permission="pull"))
    yield pytest.param(add_team, id="add team permission")

    yield pytest.param([], id="remove team permission")


@pytest.mark.parametrize("new_data", _cases())
def test_teams(from_baseline, new_data):
    repo, org = from_baseline

    request = HandlerRequest(repository=repo, data=deepcopy(new_data), organization=org)

    teams.apply(request)

    expected_data = {team["name"]: team for team in new_data}

    team_data = list(repo.get_teams())

    compare_team_permissions(actual=team_data, expected=expected_data)
