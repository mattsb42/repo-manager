"""Integration test suite for ``repo_manager._groups.branches``."""
import os
from copy import deepcopy
from typing import Any, Dict, List

import agithub.GitHub
import pytest
from github.Repository import Repository

from repo_manager._groups import branches
from repo_manager._util import HandlerRequest

from ..integration_test_utils import github_client  # noqa pylint: disable=unused-import
from ..integration_test_utils import integ_repo  # noqa pylint: disable=unused-import
from .test_teams import push_bots_return_to_baseline  # noqa pylint: disable=unused-import

pytestmark = [pytest.mark.integ]

BASELINE = [
    dict(
        name="master",
        protection=dict(
            required_status_checks=None,
            enforce_admins=False,
            required_pull_request_reviews=None,
            restrictions=None,
            required_linear_history=False,
            allow_force_pushes=False,
            allow_deletions=False,
        ),
    )
]
NOT_SET = object()


def _compare_status_checks(actual_value, expected_value):
    """Compare required_status_checks.

    request format:

    # Required. Require branches to be up to date before merging.
    strict: true
    # Required. The list of status checks to require in order to merge into this branch
    contexts: []
    """
    if expected_value is None:
        assert actual_value is NOT_SET
        return

    for key in ("contexts", "strict"):
        actual = actual_value[key]
        expected = expected_value.get(key, NOT_SET)

        if expected is not NOT_SET:
            assert actual == expected


def _compare_pull_request_reviews(actual_value, expected_value):
    """Compare required_pull_request_reviews.

    request format:

    # The number of approvals required. (1-6)
    required_approving_review_count: 1
    # Dismiss approved reviews automatically when a new commit is pushed.
    dismiss_stale_reviews: true
    # Blocks merge until code owners have reviewed.
    require_code_owner_reviews: true
    # Specify which users and teams can dismiss pull request reviews.
    # Pass an empty dismissal_restrictions object to disable.
    # User and team dismissal_restrictions are only available for organization-owned repositories.
    # Omit this parameter for personal repositories.
    dismissal_restrictions:
        users: []
        teams: []
    """
    if expected_value is None:
        assert actual_value is NOT_SET
        return

    for key in (
        "required_approving_review_count",
        "dismiss_stale_reviews",
        "require_code_owner_reviews",
    ):
        actual = actual_value.get(key, NOT_SET)
        expected = expected_value.get(key, NOT_SET)
        if expected is NOT_SET:
            continue
        assert actual is not NOT_SET
        assert actual == expected

    expected_users = expected_value.get("dismissal_restrictions", {}).get("users", NOT_SET)
    if expected_users is not NOT_SET:
        actual_users = sorted(
            [user["login"] for user in actual_value["dismissal_restrictions"]["users"]]
        )
        assert actual_users == sorted(expected_users)

    expected_teams = expected_value.get("dismissal_restrictions", {}).get("teams", NOT_SET)
    if expected_teams is not NOT_SET:
        actual_teams = sorted(
            [team["slug"] for team in actual_value["dismissal_restrictions"]["teams"]]
        )
        assert actual_teams == sorted(expected_teams)


def _compare_restrictions(actual_value, expected_value):
    """Compare restrictions.

    request format:

    apps: []
    users: []
    teams: []
    """
    if expected_value is None:
        assert actual_value is NOT_SET
        return

    # compare users
    expected_users = sorted(expected_value["users"])
    actual_users = sorted([user["login"] for user in actual_value["users"]])
    assert actual_users == expected_users
    # compare teams
    expected_teams = sorted(expected_value["teams"])
    actual_teams = sorted([team["slug"] for team in actual_value["teams"]])
    assert actual_teams == expected_teams
    # compare apps
    expected_apps = sorted(expected_value.get("apps", []))
    actual_apps = sorted([app["slug"] for app in actual_value["apps"]])
    assert actual_apps == expected_apps


def _compare_simple(actual_value, expected_value):
    assert actual_value["enabled"] == expected_value


COMPLEX_COMPARISONS = dict(
    required_status_checks=_compare_status_checks,
    required_pull_request_reviews=_compare_pull_request_reviews,
    restrictions=_compare_restrictions,
)


def compare_branch_protection_data(*, actual: Dict[str, Any], expected: Dict[str, Any]):
    for branch_name, expected_data in expected.items():
        assert branch_name in actual
        for key, expected_value in expected_data.items():
            # Not all optional values will be present
            actual_value = actual[branch_name].get(key, NOT_SET)
            comparator = COMPLEX_COMPARISONS.get(key, _compare_simple)
            comparator(actual_value, expected_value)


def _get_branch_protections(repo: Repository, branch_names: List[str]) -> Dict[str, Any]:
    actual_config = {}
    token = os.environ["GITHUB_TOKEN"]
    owner = "mattsb42-meta"
    repo_name = "repo-manager-test-client"
    gh = agithub.GitHub.GitHub(token=token)
    for name in branch_names:
        branch = getattr(getattr(getattr(gh.repos, owner), repo_name).branches, name)
        status, data = branch.protection.get(
            headers=dict(Accept="application/vnd.github.luke-cage-preview+json")
        )
        assert status == 200

        actual_config[name] = data
    return actual_config


def assert_baseline(repo: Repository):
    actual_config = _get_branch_protections(repo, [branch["name"] for branch in BASELINE])

    expected_config = {config["name"]: config["protection"] for config in BASELINE}

    compare_branch_protection_data(actual=actual_config, expected=expected_config)


def apply_baseline(repo: Repository):
    request = HandlerRequest(repository=repo, data=deepcopy(BASELINE))
    branches.apply(request)

    assert_baseline(repo)


@pytest.fixture
def from_baseline(push_bots_return_to_baseline):
    repo, _org = push_bots_return_to_baseline
    yield repo
    apply_baseline(repo)


def test_branches_baseline(integ_repo, github_client):
    repo = github_client.get_repo(integ_repo)
    apply_baseline(repo)
    assert_baseline(repo)


def _build_case(field_name: str, value, description: str) -> pytest.param:
    case_data = deepcopy(BASELINE)
    branch_data = case_data.pop()
    branch_data["protection"][field_name] = value
    case_data.append(branch_data)
    return pytest.param(case_data, id=description)


def _cases():
    # do nothing
    yield pytest.param([], id="nothing do nothing")
    # enforce admins
    yield _build_case("enforce_admins", True, "enforce rules for admins")
    # require linear history
    yield _build_case("required_linear_history", True, "require linear history")
    # allow force pushes
    yield _build_case("allow_force_pushes", True, "allow force pushes")
    # allow deletions
    yield _build_case("allow_deletions", True, "allow deletions")
    # REQUIRED PULL REQUEST REVIEWS
    yield _build_case(
        "required_pull_request_reviews",
        dict(
            required_approving_review_count=2,
            dismiss_stale_reviews=True,
            require_code_owner_reviews=True,
            dismissal_restrictions=dict(users=["mattsb42"], teams=["bots"]),
        ),
        "apply required pull request reviews settings",
    )
    # REQUIRED STATUS CHECKS
    yield _build_case(
        "required_status_checks",
        dict(strict=True, contexts=["foo", "bar"]),
        "apply required status checks",
    )
    # RESTRICTIONS
    # add a user
    yield _build_case(
        "restrictions", dict(users=["mattsb42"], teams=[]), "restrict to a single user"
    )
    # add a team
    yield _build_case("restrictions", dict(users=[], teams=["bots"]), "restrict to a single team")


@pytest.mark.parametrize("new_configs", _cases())
def test_branch_protection(from_baseline, new_configs):
    repo = from_baseline

    request = HandlerRequest(repository=repo, data=deepcopy(new_configs))
    branches.apply(request)

    expected_config = {config["name"]: config["protection"] for config in new_configs}

    actual_config = _get_branch_protections(repo, [branch["name"] for branch in new_configs])

    compare_branch_protection_data(actual=actual_config, expected=expected_config)
