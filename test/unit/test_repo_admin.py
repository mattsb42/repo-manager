"""Unit test suite for ``repo_admin``."""
import pytest

import repo_admin

pytestmark = [pytest.mark.local, pytest.mark.unit]


@pytest.fixture
def setup_env(monkeypatch):
    monkeypatch.setenv("INPUT_GITHUB-TOKEN", "foo")
    monkeypatch.setenv("GITHUB_REPOSITORY", "bar/baz")


@pytest.fixture
def patch_actors(mocker, setup_env):
    mocker.patch.object(repo_admin, "parse_config")
    mocker.patch.object(repo_admin, "apply_config")


@pytest.fixture
def patch_logging(mocker):
    mocker.patch.object(repo_admin, "logging")


def test_cli(patch_actors, mocker):
    mocker.patch.object(repo_admin, "load_inputs")
    mocker.patch.object(repo_admin, "load_context")

    repo_admin.cli([])

    repo_admin.load_inputs.assert_called_once_with()
    repo_admin.load_context.assert_called_once_with()
    repo_admin.parse_config.assert_called_once_with(
        repo_admin.load_inputs.return_value, repo_admin.load_context.return_value,
    )
    repo_admin.apply_config.assert_called_once_with(repo_admin.parse_config.return_value)


def test_no_debug(patch_actors, patch_logging):
    repo_admin.cli([])

    repo_admin.logging.getLogger.return_value.setLevel.assert_called_once_with(
        repo_admin.logging.INFO
    )


def test_debug_from_cli(patch_actors, patch_logging):
    repo_admin.cli(["-v"])

    repo_admin.logging.getLogger.return_value.setLevel.assert_called_once_with(
        repo_admin.logging.DEBUG
    )


def test_debug_from_environment(patch_actors, patch_logging, monkeypatch):
    monkeypatch.setenv("INPUT_DEBUG", "foo")
    repo_admin.cli([])

    repo_admin.logging.getLogger.return_value.setLevel.assert_called_once_with(
        repo_admin.logging.DEBUG
    )


def test_debug_from_environment_and_cli(patch_actors, patch_logging, monkeypatch):
    monkeypatch.setenv("INPUT_DEBUG", "foo")
    repo_admin.cli(["-v"])

    repo_admin.logging.getLogger.return_value.setLevel.assert_called_once_with(
        repo_admin.logging.DEBUG
    )
