"""Unit test suite for ``repo_manager._util``."""
from dataclasses import dataclass
from typing import Dict

import pytest

import repo_manager._util
from repo_manager._util import load_context, load_inputs, permission_to_string
from repo_manager.exceptions import RepoAdminError

pytestmark = [pytest.mark.local, pytest.mark.unit]


@pytest.fixture
def mock_github(mocker):
    mocker.patch.object(repo_manager._util, "Github")


def apply_environment_variables(patcher, variables: Dict[str, str]):
    for name, value in variables.items():
        patcher.setenv(name, value)


@pytest.mark.parametrize(
    "environment_variables",
    (
        pytest.param({"INPUT_GITHUB-TOKEN": "foo"}, id="only token provided"),
        pytest.param(
            {"INPUT_GITHUB-TOKEN": "foo", "INPUT_CONFIG-FILE": "bar"},
            id="token and config file provided",
        ),
        pytest.param(
            {"INPUT_GITHUB-TOKEN": "foo", "INPUT_DEBUG": "baz"}, id="only token and debug provided",
        ),
        pytest.param(
            {"INPUT_GITHUB-TOKEN": "foo", "INPUT_CONFIG-FILE": "bar", "INPUT_DEBUG": "baz"},
            id="all inputs provided",
        ),
    ),
)
def test_load_inputs(environment_variables: Dict[str, str], mock_github, monkeypatch):
    apply_environment_variables(monkeypatch, environment_variables)

    test = load_inputs()

    repo_manager._util.Github.assert_called_once_with(environment_variables["INPUT_GITHUB-TOKEN"])
    assert test.github is repo_manager._util.Github.return_value
    assert test.config_file == environment_variables.get(
        "INPUT_CONFIG-FILE", ".github/settings.yml"
    )
    assert test.debug is bool("INPUT_DEBUG" in environment_variables)


def test_load_context(monkeypatch):
    monkeypatch.setenv("GITHUB_REPOSITORY", "foo/bar")

    test = load_context()

    assert test.owner == "foo"
    assert test.repo == "bar"


@dataclass
class FakePermissions:
    admin: bool = False
    push: bool = False
    pull: bool = False


@pytest.mark.parametrize(
    "value, expected",
    (
        pytest.param(FakePermissions(admin=True), "admin"),
        pytest.param(FakePermissions(admin=True, push=True), "admin"),
        pytest.param(FakePermissions(admin=True, push=True, pull=True), "admin"),
        pytest.param(FakePermissions(push=True), "push"),
        pytest.param(FakePermissions(push=True, pull=True), "push"),
        pytest.param(FakePermissions(pull=True), "pull"),
    ),
)
def test_permission_to_string_known(value, expected):
    test = permission_to_string(value)

    assert test == expected


def test_permission_to_string_unknown():
    with pytest.raises(RepoAdminError) as excinfo:
        permission_to_string(FakePermissions())

    excinfo.match("Unknown permissions: *")
