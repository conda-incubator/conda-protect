from __future__ import annotations

import os
import logging
from pathlib import Path
from typing import NamedTuple
from collections.abc import Sequence

import click
from conda.base.context import context
from conda.base.constants import ROOT_ENV_NAME
from conda.core.envs_manager import list_all_known_prefixes
from conda.exceptions import CondaError
from conda.plugins import hookimpl, CondaPreCommand, CondaSubcommand
from rich import print as r_print
from rich.console import Console
from rich.table import Table

#: Name of the plugin; this will appear in certain outputs
PLUGIN_NAME = "conda_envlock"

#: Name of the lockfile that we create in environments themselves to signal they are locked.
LOCKFILE_NAME = ".locked"

#: Name of the command used when locking/unlocking environments
COMMAND_NAME = "el"

#: Symbol we show for locked environments
LOCKED_SYMBOL = "🔐"

#: Symbol we show for unlocked environments
UNLOCKED_SYMBOL = "🔓"

logger = logging.getLogger("conda_envlock")


class CondaEnvLockError(CondaError):
    """
    Error raised when we attempt to perform an action on a locked environment
    """


class EnvironmentInfo(NamedTuple):
    name: str
    path: Path
    locked: bool


def get_environment_info() -> list[EnvironmentInfo]:
    """
    Returns all environments currently known to conda.
    """
    prefixes = list_all_known_prefixes()
    name_to_prefix = get_name_to_prefix_map(prefixes)

    env_info = []

    for prefix in prefixes:
        if prefix not in name_to_prefix.values():
            path = Path(prefix)
            lockfile = path.joinpath(LOCKFILE_NAME)
            try:
                env_info.append(
                    EnvironmentInfo(name="", path=path, locked=lockfile.exists())
                )
            except OSError as exc:
                logger.warning(
                    f"Could not determine if lockfile '{lockfile}' exists: {exc}"
                )

    for name, prefix in name_to_prefix.items():
        path = Path(prefix)
        lockfile = path.joinpath(LOCKFILE_NAME)
        env_info.append(EnvironmentInfo(name=name, path=path, locked=lockfile.exists()))

    return sorted(env_info, key=lambda env: env.name)


def toggle_environment_lock(env: EnvironmentInfo) -> EnvironmentInfo:
    """
    Toggles an environment to either a locked or unlocked state. This function
    returns an updated `EnvironmentInfo` object.
    """
    if env.locked:
        try:
            env.path.joinpath(LOCKFILE_NAME).unlink()
        except OSError as exc:
            raise CondaEnvLockError(
                f"Unable to remove a lock for the following reason: {exc}"
            )
    else:
        try:
            env.path.joinpath(LOCKFILE_NAME).touch()
        except OSError as exc:
            raise CondaEnvLockError(
                f"Unable to create a lock for the following reason: {exc}"
            )

    return EnvironmentInfo(name=env.name, path=env.path, locked=not env.locked)


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


def display_environment_info_table(environments: Sequence[EnvironmentInfo]) -> None:
    """
    Displays a rich table
    """
    table = Table(title="Conda Environments")

    table.add_column("Name", style="cyan")
    table.add_column("Prefix")
    table.add_column("Status")

    for row in environments:
        table.add_row(
            row.name or "-",
            str(row.path),
            f"{LOCKED_SYMBOL} [green]locked" if row.locked else "",
        )

    console = Console()
    console.print(table)


def validate_environment(ctx, param, value) -> EnvironmentInfo | None:
    """
    Makes sure that the environment passed in actually exists
    """
    # Construct two lists with known prefixes and environment names
    prefixes = list_all_known_prefixes()
    name_to_prefix = get_name_to_prefix_map(prefixes)

    if value not in prefixes:
        if value is not None:
            if value not in name_to_prefix.keys():
                raise click.ClickException("Environment not found")
            path = Path(name_to_prefix[value])
            return EnvironmentInfo(
                name=value, path=path, locked=path.joinpath(LOCKFILE_NAME).exists()
            )
        else:
            return None

    path = Path(value)
    return EnvironmentInfo(
        name=value, path=path, locked=path.joinpath(LOCKFILE_NAME).exists()
    )


@click.group()
def cli():
    pass


@cli.command("lock")
@click.argument("environment", callback=validate_environment, required=False)
def envlock_lock(environment):
    """
    Locks environments
    """
    env = toggle_environment_lock(environment)
    r_print(f"{env.name} is {LOCKED_SYMBOL if env.locked else UNLOCKED_SYMBOL}")


@cli.command("list")
@click.option("--locked", "-l", help="Only show locked environments", is_flag=True)
@click.option("--named", "-n", help="Only show named environments", is_flag=True)
def envlock_list(locked, named):
    """
    List environments in conda and show whether they are locked
    """
    all_environments = get_environment_info()

    if locked:
        all_environments = [env for env in all_environments if env.locked]

    if named:
        all_environments = [env for env in all_environments if env.name]

    display_environment_info_table(all_environments)


def wrapper(args):
    """Lock and unlock environments so changes are not accidentally made to them"""
    cli(args=args, prog_name=f"conda {COMMAND_NAME}")


def custom_plugin_pre_commands_action(command: str, args):
    """
    Checks to see if the current environment being acted on is locked and if so, raise error to
    exit program early

    TODO: This still doesn't handle `conda env update -f environment.yml`
          We will have to look inside the file and pluck out the environment name
    """
    known_envs = get_environment_info()

    if hasattr(args, "name") and args.name:
        lookup_attr = "name"
        value = args.name

    elif hasattr(args, "prefix") and args.prefix:
        lookup_attr = "path"
        value = Path(args.prefix)

    else:
        lookup_attr = "path"
        value = Path(context.active_prefix)

    # Create a list of locked environments; length should be zero or one
    locked_envs = [
        env for env in known_envs if getattr(env, lookup_attr) == value and env.locked
    ]

    if locked_envs:
        env = locked_envs[0]
        raise CondaEnvLockError(
            f'Environment "{env.name or env.path}" is currently locked. '
            "Run `conda envlock '{env.name or env.path}'` to unlock it."
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
    yield CondaSubcommand(name=COMMAND_NAME, action=wrapper, summary=wrapper.__doc__)
