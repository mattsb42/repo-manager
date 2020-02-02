"""Integration test suite for ``repo_manager._groups.labels``."""
from copy import deepcopy
from typing import Dict, List

import pytest
from github.Label import Label
from github.Repository import Repository

from repo_manager._groups import labels
from repo_manager._util import HandlerRequest

from ..integration_test_utils import github_client  # noqa pylint: disable=unused-import
from ..integration_test_utils import integ_repo  # noqa pylint: disable=unused-import

pytestmark = [pytest.mark.integ]


BASELINE = [
    dict(name="foo", color="336699", description="oh noes!"),
    dict(name="bar", color="#339933", description="oh yeah!"),
    dict(name="baz", color="000099", description="this one has numbers for color!"),
]


def compare_label_data(*, actual: List[Label], expected: Dict[str, Dict[str, str]]):
    assert len(actual) == len(expected)
    for label in actual:
        assert label.name in expected
        expected_values = expected[label.name]
        assert label.color == expected_values["color"].strip("#")
        assert label.description == expected_values["description"]


def assert_baseline(repo: Repository):
    label_data = list(repo.get_labels())

    check_data = {label["name"]: label for label in BASELINE}

    compare_label_data(actual=label_data, expected=check_data)


def apply_baseline(repo: Repository):
    request = HandlerRequest(repository=repo, data=deepcopy(BASELINE))
    labels.apply(request)

    assert_baseline(repo)


@pytest.fixture
def from_baseline(integ_repo, github_client):
    repo = github_client.get_repo(integ_repo)
    yield repo
    apply_baseline(repo)


def test_labels_baseline(integ_repo, github_client):
    repo = github_client.get_repo(integ_repo)
    apply_baseline(repo)
    assert_baseline(repo)


def _cases():
    remove_labels = deepcopy(BASELINE)
    del remove_labels[-1]
    yield pytest.param(remove_labels, id="remove one label")

    yield pytest.param([], id="clear all labels")

    add_label = deepcopy(BASELINE)
    add_label.append(
        dict(name="new label", color="123456", description="this label did't exist before")
    )
    yield pytest.param(add_label, id="add one label")

    change_description = deepcopy(BASELINE)
    change_description[-1]["description"] = "new description for this label!"
    yield pytest.param(change_description, id="change label description")

    change_color = deepcopy(BASELINE)
    change_color[0]["color"] = "000000"
    yield pytest.param(change_color, id="change label color")

    change_name = deepcopy(BASELINE)
    change_name[0]["oldname"] = change_name[0]["name"]
    change_name[0]["name"] = "new label name"
    yield pytest.param(change_name, id="change label name")


@pytest.mark.parametrize("new_labels", _cases())
def test_labels(from_baseline, new_labels):
    repo = from_baseline

    request = HandlerRequest(repository=repo, data=deepcopy(new_labels))
    labels.apply(request)

    expected_labels = {label["name"]: label for label in new_labels}

    actual_labels = list(repo.get_labels())

    compare_label_data(actual=actual_labels, expected=expected_labels)


def test_rename_label_twice(from_baseline):
    repo = from_baseline

    change_name = deepcopy(BASELINE)
    change_name[0]["oldname"] = change_name[0]["name"]
    change_name[0]["name"] = "new label name"

    # Apply the labels the first time.
    request = HandlerRequest(repository=repo, data=deepcopy(change_name))
    labels.apply(request)

    expected_labels = {label["name"]: label for label in change_name}

    round_one_labels = list(repo.get_labels())

    compare_label_data(actual=round_one_labels, expected=expected_labels)

    # Apply the labels a second time.
    # This means that the label with 'oldname' still has that setting.
    request = HandlerRequest(repository=repo, data=deepcopy(change_name))
    labels.apply(request)

    round_two_labels = list(repo.get_labels())

    compare_label_data(actual=round_two_labels, expected=expected_labels)
