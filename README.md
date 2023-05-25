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

To lock an environment, simply run the following command:

```
conda envlock base
base is locked 🔒
```

Now, when you try to run a command against this environment, conda will exit early:

```
conda install -n base python
```
