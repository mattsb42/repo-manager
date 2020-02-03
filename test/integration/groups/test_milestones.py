"""Integration test suite for ``repo_manager._groups.milestones``."""
from copy import deepcopy
from typing import Dict, List

import pytest
from github.Milestone import Milestone
from github.Repository import Repository

from repo_manager._groups import milestones
from repo_manager._util import HandlerRequest

from ..integration_test_utils import github_client  # noqa pylint: disable=unused-import
from ..integration_test_utils import integ_repo  # noqa pylint: disable=unused-import
from ..integration_test_utils import INTEG_FLAKE

pytestmark = [pytest.mark.integ, INTEG_FLAKE]

BASELINE = [
    dict(title="my first milestone", description="this is a milestone", state="open"),
    dict(title="my second milestone!", description="we finished this one!", state="closed"),
    dict(
        title="milestone that needs to be completed",
        description="srs bsns",
        state="open",
        due_on="2020-02-02",
    ),
]


def compare_milestone_data(*, actual: List[Milestone], expected: Dict[str, Dict[str, str]]):
    assert len(actual) == len(expected)
    for milestone in actual:
        assert milestone.title in expected
        expected_values = expected[milestone.title]
        assert milestone.description == expected_values.get("description")
        assert milestone.state == expected_values.get("state", "open")
        # Ignoring due_on values for the moment
        # https://github.com/mattsb42/repo-manager/issues/26
        # if "due_on" in expected_values:
        #     assert milestone.due_on == datetime.fromisoformat(expected_values["due_on"])
        # else:
        #     assert milestone.due_on is None


def assert_baseline(repo: Repository):
    milestone_data = list(repo.get_milestones(state="all"))

    check_data = {milestone["title"]: milestone for milestone in BASELINE}

    compare_milestone_data(actual=milestone_data, expected=check_data)


def apply_baseline(repo: Repository):
    request = HandlerRequest(repository=repo, data=deepcopy(BASELINE))
    milestones.apply(request)

    assert_baseline(repo)


@pytest.fixture
def from_baseline(integ_repo, github_client):
    repo = github_client.get_repo(integ_repo)
    yield repo
    apply_baseline(repo)


def test_milestones_baseline(integ_repo, github_client):
    repo = github_client.get_repo(integ_repo)
    apply_baseline(repo)
    assert_baseline(repo)


def _cases():
    remove_milestone = deepcopy(BASELINE)
    del remove_milestone[-1]
    yield pytest.param(remove_milestone, id="remove one milestone")

    add_milestone_minimal = deepcopy(BASELINE)
    add_milestone_minimal.append(dict(title="wow another one"))
    yield pytest.param(add_milestone_minimal, id="add one milestone with minimal config")

    add_milestone_full = deepcopy(BASELINE)
    add_milestone_full.append(
        dict(
            title="we're gonna party like it's",
            description="yesterday",
            state="closed",
            due_on="2000-01-01",
        )
    )
    yield pytest.param(add_milestone_full, id="add one milestone with full config")

    change_description = deepcopy(BASELINE)
    to_be_updated = change_description.pop()
    to_be_updated["description"] += "::foo bar baz"
    change_description.append(to_be_updated)
    yield pytest.param(change_description, id="change milestone description")

    reverse = {"closed": "open", "open": "closed"}
    change_state = deepcopy(BASELINE)
    new_state = change_state.pop()
    new_state["state"] = reverse[new_state["state"]]
    change_state.append(new_state)
    yield pytest.param(change_state, id="change milestone state")


@pytest.mark.parametrize("new_milestones", _cases())
def test_milestones(from_baseline, new_milestones):
    repo = from_baseline

    request = HandlerRequest(repository=repo, data=deepcopy(new_milestones))
    milestones.apply(request)

    expected_milestones = {milestone["title"]: milestone for milestone in new_milestones}

    actual_milestones = list(repo.get_milestones(state="all"))

    compare_milestone_data(actual=actual_milestones, expected=expected_milestones)
