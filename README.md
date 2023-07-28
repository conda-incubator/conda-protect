# conda-protect 🔐

Protect conda environments to avoid mistakenly modifying them.

In conda, it's sometimes nice to set certain environments as "off-limits". This can especially
be true for the base environment. This plugin that allows you to protect arbitrary environments,
and it will cause conda to exit early on the following commands if an environment is protected:

- install
- create
- update
- remove
- env remove
- env update (*still not fully supported*)

## Install

You can install this plugin by running the following command:

```
conda install -c thath conda-protect
```

## Usage

Conda protect installs several new subcommands for conda: one for protecting environments `protect`
and one for listing guarded environments `plist`. These commands are explained in further
detail below:

### Protecting environments

To guard an environment, run the `protect` subcommand:

```commandline
$ conda protect base
base is 🔐 protected
```

Now, when you try to run a command against this environment, conda will exit early:

```commandline
$ conda install -n base python

CondaProtectError: Environment "base" is currently protected. Run `conda protect 'base'` to remove protection.
```

If you want to remove a protection to add/modify anything, just run the `protect` subcommand again:

```commandline
$ conda protect base
base is unprotected 🔓
```

### Listing environments and showing protection status

Conda protect also installs a `plist` subcommand that comes in handy when you've forgotten which
environments are protected:

```commandline
$ conda plist
                        Conda Environments
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Name      ┃ Prefix                                ┃ Status       ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ -         │ /tmp/user1-test-env-one               │ 🔐 protected │
│ base      │ /home/user1/opt/conda/                │ 🔐 protected │
│ test_env1 │ /home/user1/opt/conda/envs/test_env1  │ 🔐 protected │
│ test_env2 │ /home/user1/opt/conda/envs/test_env2  │              │
│ test_env3 │ /home/user1/opt/conda/envs/test_env3  │              │
└───────────┴───────────────────────────────────────┴──────────────┘
```

You can also list just the protected environments with the `--protected` option:

```commandline
$ conda plist --protected
                        Conda Environments
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Name      ┃ Prefix                                ┃ Status       ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ -         │ /tmp/user1-test-env-one               │ 🔐 protected │
│ base      │ /home/user1/opt/conda/                │ 🔐 protected │
│ test_env1 │ /home/user1/opt/conda/envs/test_env1  │ 🔐 protected │
└───────────┴───────────────────────────────────────┴──────────────┘
```
