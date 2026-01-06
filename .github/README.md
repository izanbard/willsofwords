***
[![Quality: Black](https://img.shields.io/badge/quality-black-%23000000.svg?style=for-the-badge&logo=black&logoColor=white&logoSize=auto)](https://github.com/psf/black)
[![Quality: Flake8](https://img.shields.io/badge/quality-flake8-%23201B44.svg?style=for-the-badge&logo=pycqa&logoColor=white&logoSize=auto)](https://github.com/psf/black)
[![Security: Bandit](https://img.shields.io/badge/security-bandit-yellow.svg?style=for-the-badge&logo=pycqa&logoColor=white&logoSize=auto)](https://github.com/PyCQA/bandit)
---
[![Tests: Status](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/izanbard/e530f17b6f8744b1a720db17ebda376d/raw/build.json&style=for-the-badge)](https://github.com/izanbard/willsofwords/actions)
[![Coverage: Status](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/izanbard/e530f17b6f8744b1a720db17ebda376d/raw/coverage.json&style=for-the-badge)](https://github.com/izanbard/willsofwords/actions)
***

# Wills of Words Application

An application for creating word search books

This project is under dev and not suitable for use of any kind


## Dev Installation

### Backend

#### Requirements

* Python3.12

#### Prepare

It is strongly recommended that you use a separate python environment for this work. These instructions assume the use of venv
on linux, other envs and OSes are available, and if you prefer them, then please amend the instructions as required:

##### Check out the code

```shell
$ git clone git@github.com:<<Repo>>
$ cd <<folder>>
```

##### Prepare the venv

```shell
$ python -m venv venv
$ source venv/bin/activate
(venv) $ pip install -U pip
```

A requirements.txt is committed with this repo and can be used, but it is recommended to recompile the requirements.txt file from
the pyproject.toml – especially if developing on Windows (you monster).

```shell
(venv) $ pip install pip-tools
(venv) $ pip-compile --extra dev pyproject.toml
```

(if you are not planning on developing you can/should omit the `--extra dev` argument)

Install the requirements

```shell
(venv) $ pip install -r requirements.txt
```

##### Install pre-commit hooks

```shell
(venv) $ pre-commit install
```

The pre-commit hooks:

* `black` (using rules in `pyproject.yaml`)
* `flake8` (using the rules in `.flake8`)
