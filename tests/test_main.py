"""
These are mostly just integration tests that make sure this plugin
works at a high level.
"""
import pytest
from conda.testing import conda_cli  # noqa: F401

from schutz.main import GUARDFILE_NAME, CondaSchutzError, GUARD_COMMAND_NAME


@pytest.fixture()
def conda_environment(conda_cli, tmp_path):  # noqa: F811
    environment = tmp_path.joinpath("tmp_env")

    out, err, code = conda_cli(
        "create", "--yes", "--quiet", "--prefix", str(environment)
    )

    assert err == ""

    yield environment

    # remove environment
    out, err, code = conda_cli("env", "remove", "--prefix", str(environment))
    assert err == ""


def test_guard_file_created(mocker, conda_cli, conda_environment):  # noqa: F811
    """
    When an environment is guarded, a schutz file will be written to its root.
    """
    mocker.patch("sys.argv", ["conda", GUARD_COMMAND_NAME, str(conda_environment)])

    out, err, code = conda_cli(GUARD_COMMAND_NAME, str(conda_environment))

    assert err == ""
    assert conda_environment.joinpath(GUARDFILE_NAME).is_file()

    # remove schutz
    out, err, code = conda_cli(GUARD_COMMAND_NAME, str(conda_environment))

    assert err == ""


def test_guarded_command_fails(mocker, conda_cli, conda_environment):  # noqa: F811
    """
    When an environment is guarded, running a modifying command on it should fail.
    """
    mocker.patch("sys.argv", ["conda", GUARD_COMMAND_NAME, str(conda_environment)])

    out, err, code = conda_cli(GUARD_COMMAND_NAME, str(conda_environment))

    assert err == ""

    with pytest.raises(CondaSchutzError):
        conda_cli("install", "--prefix", str(conda_environment), "python")

    # remove schutz
    out, err, code = conda_cli(GUARD_COMMAND_NAME, str(conda_environment))

    assert err == ""
