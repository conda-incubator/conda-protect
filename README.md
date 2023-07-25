# conda-guard 🔐

Guard conda environments to avoid mistakenly modifying them.

In conda, it's sometimes nice to set certain environments as "off-limits". This can especially
be true for the base environment. This plugin that allows you to guard arbitrary environments,
and it will cause conda to exit early on the following commands if an environment is guarded:

- install
- create
- update
- remove
- env remove
- env update (*still not fully supported*)

## Install

You can install this plugin by running the following command:

```
conda install -c thath conda-guard
```

## Usage

Conda guard installs several new subcommands for conda: one for guarding environments `guard`
and one for listing guarded environments `glist`. These commands are explained in further
detail below:

### Guarding environments

To guard an environment, run the `guard` subcommand:

```commandline
$ conda guard base
base is 🔐 guarded
```

Now, when you try to run a command against this environment, conda will exit early:

```commandline
$ conda install -n base python

CondaGuardError: Environment "base" is currently guarded. Run `conda guard 'base'` to remove guard.
```

If you want to remove a guard to add/modify anything, just run the `guard` subcommand again:

```commandline
$ conda guard base
base is unlocked 🔓
```

### Listing environments and showing guard status

Conda guard also installs a `glist` subcommand that comes in handy when you've forgotten which
environments are guarded:

```commandline
$ conda glist
                        Conda Environments
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Name      ┃ Prefix                                ┃ Status     ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ -         │ /tmp/user1-test-env-one               │ 🔐 guarded │
│ base      │ /home/user1/opt/conda/                │ 🔐 guarded │
│ test_env1 │ /home/user1/opt/conda/envs/test_env1  │ 🔐 guarded │
│ test_env2 │ /home/user1/opt/conda/envs/test_env2  │            │
│ test_env3 │ /home/user1/opt/conda/envs/test_env3  │            │
└───────────┴───────────────────────────────────────┴────────────┘
```

You can also list just the guarded environments with the `--guarded` option:

```commandline
$ conda glist --guarded
                        Conda Environments
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Name      ┃ Prefix                                ┃ Status     ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ -         │ /tmp/user1-test-env-one               │ 🔐 guarded │
│ base      │ /home/user1/opt/conda/                │ 🔐 guarded │
│ test_env1 │ /home/user1/opt/conda/envs/test_env1  │ 🔐 guarded │
└───────────┴───────────────────────────────────────┴────────────┘
```
