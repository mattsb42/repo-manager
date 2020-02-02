"""Unit test suite for ``repo_admin._groups``."""
import pytest

import repo_admin._groups

pytestmark = [pytest.mark.local, pytest.mark.unit]


def test_load_handler(mocker):
    mocker.patch.object(repo_admin._groups, "importlib")

    test = repo_admin._groups._load_handler("foo")

    assert test is repo_admin._groups.importlib.import_module.return_value.apply


def test_apply_config(mocker):
    init = dict(foo=mocker.Mock(), bar=mocker.Mock(), baz=mocker.Mock())

    repo_admin._groups.apply_config(init)

    for each in init.values():
        each.assert_called_once_with()
