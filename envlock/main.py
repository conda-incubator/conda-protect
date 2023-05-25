from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import NamedTuple

from platformdirs import user_data_dir
from conda.base.context import context
from conda.base.constants import ROOT_ENV_NAME
from conda.core.envs_manager import list_all_known_prefixes
from conda.exceptions import CondaIOError, CondaError
from conda.plugins import hookimpl, CondaPreCommand, CondaSubcommand

#: Name of the plugin; this will appear in certain outputs
PLUGIN_NAME = "conda_envlock"

#: Name of the file where environment locks are kept track of
LOCKED_ENVS_FILE_NAME = "locked_envs.txt"

#: Name of the command used when locking/unlocking environments
COMMAND_NAME = "envlock"


class CondaEnvLockError(CondaError):
    """
    Error raised when we attempt to perform an action on a locked environment
    """


def get_locked_envs_file() -> Path:
    """
    Returns a file that it used to read and write to for locking conda environments.

    We first make sure that the app folder and file exist before returning. If we can't
    write to this file or create the directory, we raise a `CondaIOError`.
    """
    app_dir = Path(user_data_dir(PLUGIN_NAME))

    if not app_dir.exists():
        try:
            app_dir.mkdir(parents=True)
        except OSError as exc:
            raise CondaIOError(f"Unable to create {PLUGIN_NAME} app data directory: {exc}")

    locked_envs_file = app_dir.joinpath(LOCKED_ENVS_FILE_NAME)

    if not locked_envs_file.exists():
        try:
            locked_envs_file.touch()
        except OSError as exc:
            raise CondaIOError(f"Unable to create {PLUGIN_NAME} database: {exc}")

    return locked_envs_file


def lock_environment(env: str) -> bool:
    """
    Toggles an environment to either a locked or unlocked state. This function will
    return `True` when the environment has been locked and `False when the environment
    has been unlocked.
    """
    lockfile = get_locked_envs_file()
    unlocked = False

    try:
        with lockfile.open("r") as fp:
            contents = fp.read().split("\n")
            if env in contents:
                contents.remove(env)
                unlocked = True
    except OSError as exc:
        raise CondaIOError(f"Unable to read the {PLUGIN_NAME} database: {exc}")

    if not unlocked:
        contents.append(env)

    try:
        with lockfile.open("w") as fp:
            fp.write("\n".join(contents))
    except OSError as exc:
        raise CondaIOError(f"Unable to write to the {PLUGIN_NAME} database: {exc}")

    return not unlocked


def is_environment_locked(env: str) -> bool:
    """
    Check to see if the environment has a lock on it
    """
    lockfile = get_locked_envs_file()

    try:
        with lockfile.open("r") as fp:
            contents = fp.read().split("\n")
            return env in contents
    except OSError as exc:
        raise CondaIOError(f"Unable to read the {PLUGIN_NAME} database: {exc}")


class EnvironmentInfo(NamedTuple):
    name: str
    path: str


def get_name_to_prefix_map(prefixes: list[str]) -> dict[str, str]:
    """
    Retrieves a mapping name -> prefix

    TODO: What if there's duplicate names in multiple `envs_dirs`? 🤷‍
          Let's just pretend that never happens 🤫
    """
    mapping = {
        os.path.basename(prefix): prefix
        for prefix in prefixes
        for env_dir in context.envs_dirs
        if prefix.startswith(env_dir)
    }
    mapping[ROOT_ENV_NAME] = context.root_prefix

    return mapping


def get_prefix_to_name_map(prefixes: list[str]) -> dict[str, str]:
    """
    Retrieves a mapping of prefix -> name
    """
    mapping = {
        prefix: os.path.basename(prefix)
        for prefix in prefixes
        for env_dir in context.envs_dirs
        if prefix.startswith(env_dir)
    }
    mapping[context.root_prefix] = ROOT_ENV_NAME

    return mapping


def environment(env: str) -> EnvironmentInfo:
    """
    Makes sure that the environment passed in actually exists
    """
    # Construct two lists with known prefixes and environment names
    prefixes = list_all_known_prefixes()
    name_to_prefix = get_name_to_prefix_map(prefixes)

    if env not in prefixes:
        if env not in name_to_prefix.keys():
            raise ValueError()
        return EnvironmentInfo(name=env, path=name_to_prefix[env])

    return EnvironmentInfo(name=env, path=env)


def create_parser() -> argparse.ArgumentParser:
    """
    Creates a very simple argument parser for our subcommand which only accepts a single argument.
    """
    parser = argparse.ArgumentParser(f"conda {COMMAND_NAME}")

    parser.add_argument("environment", type=environment, help="Environment name")

    return parser


def conda_env_lock(args: list[str]):
    """Lock and unlock environments so changes are not accidentally made to them"""
    parser = create_parser()
    args = parser.parse_args(args)

    locked = lock_environment(args.environment.path)

    print(f"{args.environment.name} is {'locked 🔒' if locked else 'unlocked 🔓'}")


def custom_plugin_pre_commands_action(args):
    """
    Checks to see if the current environment being acted on is locked and if so, raise error to
    exit program early

    TODO: This still doesn't handle `conda env update -f environment.yml`
          We will have to look inside the file and pluck out the environment name
    """
    env = None
    env_name = None
    prefixes = list_all_known_prefixes()

    if hasattr(args, "name") and args.name:
        name_to_prefix = get_name_to_prefix_map(prefixes)
        env = name_to_prefix.get(args.name)
        env_name = args.name

        # We passed in an environment that does not exist. Let the normal program flow catch
        # this error instead
        if env is None:
            return

    if hasattr(args, "prefix") and args.prefix:
        env = args.prefix
        env_name = args.prefix

    # If neither `--prefix` nor `--name` has been provided, we fall back to the the
    # `context.active_prefix` value
    if env is None:
        prefix_to_name = get_prefix_to_name_map(prefixes)
        env = context.active_prefix

        # This "<unknown>" condition shouldn't happen, but it's better than displaying "None"
        env_name = prefix_to_name.get(context.active_prefix, "<unknown>")

    if is_environment_locked(env):
        raise CondaEnvLockError(
            f"Environment \"{env_name}\" is currently locked. Run `conda envlock '{env_name}'` to unlock it"
        )


@hookimpl
def conda_pre_commands():
    yield CondaPreCommand(
        name=f"{PLUGIN_NAME}_pre_command",
        action=custom_plugin_pre_commands_action,
        run_for={"install", "remove", "update", "info", "env_update", "env_remove"},
    )


@hookimpl
def conda_subcommands():
    yield CondaSubcommand(
        name=COMMAND_NAME,
        action=conda_env_lock,
        summary=conda_env_lock.__doc__
    )
