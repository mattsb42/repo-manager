"""Unit test suite for ``repo_manager``."""
import pytest

import repo_manager

pytestmark = [pytest.mark.local, pytest.mark.unit]


@pytest.fixture
def setup_env(monkeypatch):
    monkeypatch.setenv("INPUT_GITHUB-TOKEN", "foo")
    monkeypatch.setenv("GITHUB_REPOSITORY", "bar/baz")


@pytest.fixture
def patch_actors(mocker, setup_env):
    mocker.patch.object(repo_manager, "parse_config")
    mocker.patch.object(repo_manager, "apply_config")


@pytest.fixture
def patch_logging(mocker):
    mocker.patch.object(repo_manager, "logging")


def test_cli(patch_actors, mocker):
    mocker.patch.object(repo_manager, "load_inputs")
    mocker.patch.object(repo_manager, "load_context")

    repo_manager.cli([])

    repo_manager.load_inputs.assert_called_once_with()
    repo_manager.load_context.assert_called_once_with()
    repo_manager.parse_config.assert_called_once_with(
        repo_manager.load_inputs.return_value, repo_manager.load_context.return_value,
    )
    repo_manager.apply_config.assert_called_once_with(repo_manager.parse_config.return_value)


def test_no_debug(patch_actors, patch_logging):
    repo_manager.cli([])

    repo_manager.logging.getLogger.return_value.setLevel.assert_called_once_with(
        repo_manager.logging.INFO
    )


def test_debug_from_cli(patch_actors, patch_logging):
    repo_manager.cli(["-v"])

    repo_manager.logging.getLogger.return_value.setLevel.assert_called_once_with(
        repo_manager.logging.DEBUG
    )


def test_debug_from_environment(patch_actors, patch_logging, monkeypatch):
    monkeypatch.setenv("INPUT_DEBUG", "foo")
    repo_manager.cli([])

    repo_manager.logging.getLogger.return_value.setLevel.assert_called_once_with(
        repo_manager.logging.DEBUG
    )


def test_debug_from_environment_and_cli(patch_actors, patch_logging, monkeypatch):
    monkeypatch.setenv("INPUT_DEBUG", "foo")
    repo_manager.cli(["-v"])

    repo_manager.logging.getLogger.return_value.setLevel.assert_called_once_with(
        repo_manager.logging.DEBUG
    )
