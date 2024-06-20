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
* Run `xi_init.ps1` or `xi_init.sh` for configuration
* to other `.ps1` or `.sh` files for relevant tasks
* `x1` means execution, and generally the 1st thing to run
* run `hatch -h` 

## Project Creation

### Initialisation
* This project is generated using `hatch new py-flat-orm`
* `pyproject.toml` is then edited to include `[tool.hatch.envs.py-flat-orm]` etc.
* script files e.g. `x*.ps1` are added 
* set up with git 

### Tests
* use `./test_data` directory put test data
  * test data cannot be put into `./tests`, otherwise when running `hatch test`, it treats them as tests to execute
  * you can pattern exclude these files but that requires more project config

## License

`py-flat-orm` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
