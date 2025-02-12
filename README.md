# py-flat-orm

[![PyPI - Version](https://img.shields.io/pypi/v/py-flat-orm.svg)](https://pypi.org/project/py-flat-orm)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/py-flat-orm.svg)](https://pypi.org/project/py-flat-orm)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install py-flat-orm
```

## Get Started

This project is set up using `hatch`. 
* Run `xi_init.ps1` or `xi_init.sh` to apply `pyproject.toml`
  - run `exit` (deactivate env) first if you get `Cannot remove active environment: py-flat-orm`  
* Run other `.ps1` or `.sh` files for relevant tasks
* `x1` means execution, and generally the 1st thing to run
* run `hatch -h` 

## Project Creation - IMPORTANT
- pyproject.toml - has to define `[tool.hatch.envs.py_flat_orm]` to match the name of the env you want to create
- env creation - `hatch env create py_flat_orm`, has to match `pyproject.toml` definition
- `path = ".venv"` - important - make the directory local
- `paths = []` - mark "src" as root, should not put "src" here, it would mess up auto import, need to go to settings to add local interpreter

```ini
[tool.hatch.envs.py_flat_orm]
python = "3.9"
path = ".venv"
paths = [] # should not put "src" here, it would mess up auto import, need to go to settings to add local interpreter
dependencies = [
    "numpy>=1.21.0,<2.0.0",
]

[tool.hatch.envs.default]
dependencies = [
    "pytest",
    "pytest-cov",
]
```

```shell
hatch env remove py_flat_orm
hatch env create py_flat_orm
hatch shell py_flat_orm

# `py_flat_orm:` is needed for specific env
hatch run py_flat_orm:test-cov
```

### Initialisation
* This project is generated using `hatch new py-flat-orm`
* `pyproject.toml` is then edited to include `[tool.hatch.envs.py-flat-orm]` etc.
* script files e.g. `x*.ps1` are added 
* set up with git 
* Run e.g. `xi_init.ps1` to apply `pyproject.toml`

### Sync Dependencies
* run `hatch shell` to activate env, it also syncs dependencies

### Tests Data
* use `./test_data` directory put test data
  * test data cannot be put into `./tests`, otherwise when running `hatch test`, it treats them as tests to execute
  * you can pattern exclude these files but that requires more project config

### Test in PyCharm
* mark `tests` as Test Root, allows right-clicking directories inside to run tests
* run tests from root, and save test config as a file e.g. `test.run.xml`
* IMPORTANT: unmark `tests` as Test Root once `test.run.xml` is generated
  - if `tests` is marked as root, you CANNOT run a single test file, 
  - because it treats `tests` as root and can't find files within `src`
  - you can verify this by putting `import sys; print(sys.path)` at the top of a test file and run it

### Static Analysis
* add dependency `mypy`
* each package needs to add an empty `py.typed` file to make pycharm happy
* so each package has `__init__.py` and `py.typed`, seems pointless, just live with it

### Publish
* `hatch build`
* `hatch publish` - ask chatGPT how to set up a PyPI Account

## License

`py-flat-orm` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
