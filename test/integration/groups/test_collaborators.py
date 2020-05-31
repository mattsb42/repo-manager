"""Integration test suite for ``repo_manager._groups.collaborators``."""
from copy import deepcopy
from typing import Dict, List

import pytest
from github.NamedUser import NamedUser
from github.Repository import Repository

from repo_manager._groups import collaborators
from repo_manager._util import HandlerRequest, permission_to_string

from ..integration_test_utils import github_client  # noqa pylint: disable=unused-import
from ..integration_test_utils import integ_repo  # noqa pylint: disable=unused-import
from ..integration_test_utils import INTEG_FLAKE, baseline_wait
from .test_teams import no_teams_but_return_to_baseline  # noqa pylint: disable=unused-import

pytestmark = [pytest.mark.integ, INTEG_FLAKE]

BASELINE = [
    dict(username="mattsb42-admin-bot", permission="admin"),
    dict(username="mattsb42-bot", permission="push"),
]
# mattsb42-meta org has two org admins who also show up as admin collaborators
OVERHEAD = {
    "mattsb42": dict(username="mattsb42", permission="admin"),
    "mattsb42-aws": dict(username="mattsb42-aws", permission="admin"),
}


def compare_invite_data(*, actual: List[NamedUser], expected: Dict[str, Dict[str, str]]):
    assert len(actual) == len(expected)

    for user in actual:
        assert user.login in expected
        assert user.permissions is None


def compare_collaborator_data(*, actual: List[NamedUser], expected: Dict[str, Dict[str, str]]):
    i_expected = deepcopy(expected)
    i_expected.update(OVERHEAD)

    assert len(actual) == len(i_expected)
    for user in actual:
        assert user.login in i_expected
        expected_values = i_expected[user.login]
        permissions = permission_to_string(user.permissions)
        assert permissions == expected_values["permission"]


def assert_baseline(repo: Repository):
    user_data = list(repo.get_collaborators())
    invited_users = [invite.invitee for invite in repo.get_pending_invitations()]

    check_data = {user["username"]: user for user in BASELINE}

    compare_invite_data(actual=invited_users, expected={})
    compare_collaborator_data(actual=user_data, expected=check_data)


def apply_baseline(repo: Repository):
    request = HandlerRequest(repository=repo, data=deepcopy(BASELINE))
    collaborators.apply(request)
    baseline_wait()

    assert_baseline(repo)


@pytest.fixture
def from_baseline(no_teams_but_return_to_baseline):
    repo, _ = no_teams_but_return_to_baseline
    yield repo
    apply_baseline(repo)


def test_collaborators_baseline(integ_repo, github_client):
    repo = github_client.get_repo(integ_repo)
    apply_baseline(repo)
    assert_baseline(repo)


def _cases():
    add_user = deepcopy(BASELINE)
    invite = dict(username="mattsb42-test-collaborator-1", permission="pull")
    add_user.append(invite)
    yield pytest.param(add_user, [invite], id="add one outside collaborator")

    # NOTE: We need to be very careful to NOT remove mattsb42-admin-bot
    remove_user = deepcopy(BASELINE)
    remove_user = [user for user in remove_user if user["username"] != "mattsb42-bot"]
    yield pytest.param(remove_user, [], id="remove one collaborator")

    change_user_permissions = deepcopy(BASELINE)
    change_user_permissions = [
        user for user in change_user_permissions if user["username"] != "mattsb42-bot"
    ]
    change_user_permissions.append(dict(username="mattsb42-bot", permission="pull"))
    yield pytest.param(change_user_permissions, [], id="change collaborator permission")


@pytest.mark.parametrize("new_users, expected_invites", _cases())
def test_collaborators(from_baseline, new_users, expected_invites):
    repo = from_baseline

    request = HandlerRequest(repository=repo, data=deepcopy(new_users))
    collaborators.apply(request)

    expected_user_invites = {user["username"]: user for user in expected_invites}
    expected_users = {
        user["username"]: user
        for user in new_users
        if user["username"] not in expected_user_invites
    }

    actual_users = list(repo.get_collaborators())
    invited_users = [invite.invitee for invite in repo.get_pending_invitations()]

    compare_invite_data(actual=invited_users, expected=expected_user_invites)
    compare_collaborator_data(actual=actual_users, expected=expected_users)
