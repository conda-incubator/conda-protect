"""
These are mostly just integration tests that make sure this plugin
works at a high level.
"""
import pytest
from conda.testing import conda_cli  # noqa: F401
from conda.exceptions import DryRunExit

from conda_protect.main import GUARDFILE_NAME, CondaProtectError, GUARD_COMMAND_NAME


@pytest.fixture()
def conda_environment(conda_cli, tmp_path):  # noqa: F811
    environment = tmp_path.joinpath("tmp_env")

    out, err, code = conda_cli(
        "create", "--yes", "--quiet", "--prefix", str(environment)
    )

    assert err == ""

    yield environment

    # remove environment
    out, err, code = conda_cli("env", "remove", "--yes", "--prefix", str(environment))
    assert err == ""


def test_guard_file_created(mocker, conda_cli, conda_environment):  # noqa: F811
    """
    When an environment is guarded, a conda_protect file will be written to its root.
    """
    mocker.patch("sys.argv", ["conda", GUARD_COMMAND_NAME, str(conda_environment)])

    out, err, code = conda_cli(GUARD_COMMAND_NAME, str(conda_environment))

    assert err == ""
    assert conda_environment.joinpath(GUARDFILE_NAME).is_file()

    # remove conda_protect
    out, err, code = conda_cli(GUARD_COMMAND_NAME, str(conda_environment))

    assert err == ""


def test_guarded_command_fails(mocker, conda_cli, conda_environment):  # noqa: F811
    """
    When an environment is guarded, running a modifying command on it should fail.
    """
    mocker.patch("sys.argv", ["conda", GUARD_COMMAND_NAME, str(conda_environment)])

    out, err, code = conda_cli(GUARD_COMMAND_NAME, str(conda_environment))

    assert err == ""

    with pytest.raises(CondaProtectError):
        conda_cli("install", "--prefix", str(conda_environment), "ca-certificates")

    # remove conda_protect
    out, err, code = conda_cli(GUARD_COMMAND_NAME, str(conda_environment))

    assert err == ""


def test_dry_run_continues(mocker, conda_cli, conda_environment):
    """
    When `--dry-run` is used, the environment is not guarded
    """
    mocker.patch("sys.argv", ["conda", GUARD_COMMAND_NAME, str(conda_environment)])

    out, err, code = conda_cli(GUARD_COMMAND_NAME, str(conda_environment))

    assert err == ""

    with pytest.raises(DryRunExit):
        conda_cli("install", "--dry-run", "--prefix", str(conda_environment), "ca-certificates")

    # remove conda_protect
    out, err, code = conda_cli(GUARD_COMMAND_NAME, str(conda_environment))

    assert err == ""


def test_ensure_help_works(conda_cli):
    """
    Makes sure that both `-h` and `--help` work to print command help
    """
    out, err, code = conda_cli(GUARD_COMMAND_NAME, "-h")

    assert "Usage: conda protect" in out

    out, err, code = conda_cli(GUARD_COMMAND_NAME, "--help")

    assert "Usage: conda protect" in out
