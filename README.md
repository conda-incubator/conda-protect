# conda-envlock 🔐

Lock and unlock conda environments to avoid mistakenly modifying them.

In conda, it's sometimes nice to set certain environments as "off-limits". This can especially
be true for the base environment. This plugin that allows you to lock arbitrary environments,
and it will cause conda to exit early on the following commands if an environment is locked:

- install
- create
- update
- remove
- env remove
- env update (*still not fully supported*)

## Install

You can install this plugin by running the following command:

```
conda install -c thath conda-envlock
```

## Usage

Conda envlock comes with several subcommands. These can all be found under `conda el`:

```
Usage: conda el [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  list  List environments in conda and show whether they are locked
  lock  Locks or unlocks environments
```

### Locking and unlocking environments

To lock an environment, run the `lock` subcommand:

```commandline
$ conda el lock base
base is 🔐 locked
```

Now, when you try to run a command against this environment, conda will exit early:

```commandline
$ conda install -n base python

CondaEnvLockError: Environment "base" is currently locked. Run `conda envlock 'base'` to unlock it
```

If you want to unlock it to add/modify anything, just run the `lock` subcommand again:

```commandline
$ conda el lock base
base is unlocked 🔓
```

### Listing environments and showing lock status

Conda envlock also contains a `list` subcommand that comes in handy when you've forgotten which environments you locked:

```commandline
$ conda el list
                        Conda Environments
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Name      ┃ Prefix                                ┃ Status    ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ -         │ /tmp/user1-test-env-one               │ 🔐 locked │
│ base      │ /home/user1/opt/conda/                │ 🔐 locked │
│ test_env1 │ /home/user1/opt/conda/envs/test_env1  │ 🔐 locked │
│ test_env2 │ /home/user1/opt/conda/envs/test_env2  │           │
│ test_env3 │ /home/user1/opt/conda/envs/test_env3  │           │
└───────────┴───────────────────────────────────────┴───────────┘
```

You can also list just the locked environments with the `--locked` option:

```commandline
$ conda el list --locked
                        Conda Environments
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Name      ┃ Prefix                                ┃ Status    ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ -         │ /tmp/user1-test-env-one               │ 🔐 locked │
│ base      │ /home/user1/opt/conda/                │ 🔐 locked │
│ test_env1 │ /home/user1/opt/conda/envs/test_env1  │ 🔐 locked │
└───────────┴───────────────────────────────────────┴───────────┘
```
