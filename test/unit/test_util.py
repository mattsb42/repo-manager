"""Unit test suite for ``repo_manager._util``."""
from dataclasses import dataclass
from typing import Dict, Sequence

import pytest

import repo_manager._util
from repo_manager._util import (
    _load_from_environment,
    load_context,
    load_inputs,
    permission_to_string,
)
from repo_manager.exceptions import RepoAdminError, UserConfigError

pytestmark = [pytest.mark.local, pytest.mark.unit]


@pytest.fixture
def mock_github(mocker):
    mocker.patch.object(repo_manager._util, "Github")
    mocker.patch.object(repo_manager._util, "GitHub")


def apply_environment_variables(patcher, variables: Dict[str, str]):
    for name, value in variables.items():
        if value is None:
            patcher.delenv(name, raising=False)
        else:
            patcher.setenv(name, value)


_BASELINE = {"INPUT_GITHUB-TOKEN": "foo"}


@pytest.mark.parametrize(
    "environment_variables, config_file, debug",
    (
        pytest.param(_BASELINE, ".github/settings.yml", False, id="only token provided"),
        pytest.param(
            dict(**_BASELINE, **{"INPUT_DEBUG": "true"}),
            ".github/settings.yml",
            True,
            id="debug 'true'",
        ),
        pytest.param(
            dict(**_BASELINE, **{"INPUT_DEBUG": "foo"}),
            ".github/settings.yml",
            False,
            id="debug other",
        ),
        pytest.param(
            dict(**_BASELINE, **{"INPUT_DEBUG": ""}),
            ".github/settings.yml",
            False,
            id="debug empty",
        ),
        pytest.param(
            dict(**_BASELINE, **{"INPUT_CONFIG-FILE": "bar"}),
            "bar",
            False,
            id="config filename set",
        ),
        pytest.param(
            dict(**_BASELINE, **{"INPUT_CONFIG-FILE": ""}),
            ".github/settings.yml",
            False,
            id="config filename empty",
        ),
        pytest.param(
            {"INPUT_GITHUB-TOKEN": "foo", "INPUT_CONFIG-FILE": "bar", "INPUT_DEBUG": "true"},
            "bar",
            True,
            id="all inputs provided",
        ),
    ),
)
def test_load_inputs(
    environment_variables: Dict[str, str], config_file: str, debug: bool, mock_github, monkeypatch
):
    apply_environment_variables(monkeypatch, environment_variables)

    test = load_inputs()

    repo_manager._util.Github.assert_called_once_with(environment_variables["INPUT_GITHUB-TOKEN"])
    repo_manager._util.GitHub.assert_called_once_with(
        token=environment_variables["INPUT_GITHUB-TOKEN"], paginate=True
    )
    assert test.github is repo_manager._util.Github.return_value
    assert test.agithub is repo_manager._util.GitHub.return_value
    assert test.config_file == config_file
    assert test.debug is debug


@pytest.mark.parametrize(
    "environment_variables, expected_owner, expected_repo",
    (
        pytest.param(
            {"GITHUB_REPOSITORY": "foo/bar", "INPUT_GITHUB-REPOSITORY": ""},
            "foo",
            "bar",
            id="default set, input set but empty",
        ),
        pytest.param(
            {"GITHUB_REPOSITORY": "foo/bar", "INPUT_GITHUB-REPOSITORY": None},
            "foo",
            "bar",
            id="default set, input not set",
        ),
        pytest.param(
            {"GITHUB_REPOSITORY": "foo/bar", "INPUT_GITHUB-REPOSITORY": "baz/wow"},
            "baz",
            "wow",
            id="default set, input set",
        ),
        pytest.param(
            {"GITHUB_REPOSITORY": None, "INPUT_GITHUB-REPOSITORY": "baz/wow"},
            "baz",
            "wow",
            id="default not set, input set",
        ),
    ),
)
def test_load_context(
    environment_variables: Dict[str, str], expected_owner: str, expected_repo: str, monkeypatch
):
    apply_environment_variables(monkeypatch, environment_variables)

    test = load_context()

    assert test.owner == expected_owner
    assert test.repo == expected_repo


@pytest.mark.parametrize(
    "environment_variables, expected_error_message",
    (
        pytest.param(
            {"GITHUB_REPOSITORY": "foo/bar", "INPUT_GITHUB-REPOSITORY": "baz"},
            r"Invalid repository name *",
            id="default set, input set but invalid",
        ),
        pytest.param(
            {"GITHUB_REPOSITORY": "foo"},
            r"Invalid repository name *",
            id="default set but invalid value, input not set",
        ),
        pytest.param(
            {"GITHUB_REPOSITORY": "", "INPUT_GITHUB-REPOSITORY": ""},
            "Repository name not set",
            id="default set but empty value, input set but empty",
        ),
        pytest.param(
            {"GITHUB_REPOSITORY": None, "INPUT_GITHUB-REPOSITORY": None},
            "Repository name not set",
            id="default not set, input not set",
        ),
        pytest.param(
            {"GITHUB_REPOSITORY": None, "INPUT_GITHUB-REPOSITORY": ""},
            "Repository name not set",
            id="default not set, input set but empty",
        ),
    ),
)
def test_load_context_fail(
    environment_variables: Dict[str, str], expected_error_message: str, monkeypatch
):
    apply_environment_variables(monkeypatch, environment_variables)

    with pytest.raises(UserConfigError) as excinfo:
        load_context()

    excinfo.match(expected_error_message)


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


@pytest.mark.parametrize(
    "environment_variables, names, default, expected_value",
    (
        pytest.param(dict(A="1", B="2", C="3"), ("A", "B"), "bar", "1", id="first value found"),
        pytest.param(
            dict(A="1", B="2", C="3", D=None), ("D", "B"), "bar", "2", id="first value not set"
        ),
        pytest.param(dict(A="", B="2", C="3"), ("A", "B"), "bar", "2", id="first value empty"),
        pytest.param(
            dict(A=None, B=None), ("A", "B"), "bar", "bar", id="no values set with default"
        ),
        pytest.param(
            dict(A="", B=""), ("A", "B"), "bar", "bar", id="all values set but empty with default"
        ),
    ),
)
def test_load_from_environment(
    environment_variables: Dict[str, str],
    names: Sequence[str],
    default: str,
    expected_value: str,
    monkeypatch,
):
    apply_environment_variables(monkeypatch, environment_variables)
    test = _load_from_environment(*names, kind="Test", default=default)

    assert test == expected_value


@pytest.mark.parametrize(
    "environment_variables, names",
    (
        pytest.param(dict(A=None, B=None), ("A", "B"), id="no values set"),
        pytest.param(dict(A="", B=""), ("A", "B"), id="all values set but empty"),
    ),
)
def test_load_from_environment_fails(
    environment_variables: Dict[str, str], names: Sequence[str], monkeypatch
):
    apply_environment_variables(monkeypatch, environment_variables)

    with pytest.raises(UserConfigError) as excinfo:
        _load_from_environment(*names, kind="Test")

    excinfo.match("Test not set")
