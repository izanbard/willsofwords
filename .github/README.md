***

[![Language: Python](https://img.shields.io/badge/language-python-%233776AB.svg?style=for-the-badge&logo=python&logoColor=white&logoSize=auto)](https://www.python.org/)
[![Language: JS](https://img.shields.io/badge/language-javascript-%23F7DF1E.svg?style=for-the-badge&logo=javascript&logoColor=white&logoSize=auto)](https://www.javascript.com/)
[![AI: Ollama](https://img.shields.io/badge/ai-ollama-%23000000.svg?style=for-the-badge&logo=ollama&logoColor=white&logoSize=auto)](https://ollama.ai/)
[![AI: Pydantic AI](https://img.shields.io/badge/ai-pydantic--ai-%23E92063.svg?style=for-the-badge&logo=pydantic&logoColor=white&logoSize=auto)](https://ai.pydantic.dev/)
[![Framework: FastAPI](https://img.shields.io/badge/framework-fastapi-%23009688.svg?style=for-the-badge&logo=fastapi&logoColor=white&logoSize=auto)](https://fastapi.tiangolo.com/)
[![Framework: Pydantic](https://img.shields.io/badge/framework-pydantic-%23E92063.svg?style=for-the-badge&logo=pydantic&logoColor=white&logoSize=auto)](https://docs.pydantic.dev/latest/)
[![Framework: Vue](https://img.shields.io/badge/framework-vue.js-%234FC08D.svg?style=for-the-badge&logo=vue.js&logoColor=white&logoSize=auto)](https://vuejs.org/)
[![Framework: Vite](https://img.shields.io/badge/framework-vite-%23646CFF.svg?style=for-the-badge&logo=vite&logoColor=white&logoSize=auto)](https://vite.dev/)
[![Quality: Pytest](https://img.shields.io/badge/quality-pytest-%230A9EDC.svg?style=for-the-badge&logo=pytest&logoColor=white&logoSize=auto)](https://docs.pytest.org/en/latest/)
[![Quality: Black](https://img.shields.io/badge/quality-black-%23000000.svg?style=for-the-badge&logo=black&logoColor=white&logoSize=auto)](https://github.com/psf/black)
[![Quality: Flake8](https://img.shields.io/badge/quality-flake8-%23201B44.svg?style=for-the-badge&logo=pycqa&logoColor=white&logoSize=auto)](https://github.com/psf/black)
[![Security: Bandit](https://img.shields.io/badge/security-bandit-yellow.svg?style=for-the-badge&logo=pycqa&logoColor=white&logoSize=auto)](https://github.com/PyCQA/bandit)

---

[![Tests: Status](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/izanbard/e530f17b6f8744b1a720db17ebda376d/raw/build.json&style=for-the-badge)](https://github.com/izanbard/willsofwords/actions)
[![Coverage: Status](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/izanbard/e530f17b6f8744b1a720db17ebda376d/raw/coverage.json&style=for-the-badge)](https://github.com/izanbard/willsofwords/actions)
[![Quality: Status](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/izanbard/e530f17b6f8744b1a720db17ebda376d/raw/qodana.json&style=for-the-badge)](https://qodana.cloud/projects/0WLa5/)

***

# Wills of Words Application

This project, **WillsOfWords**, is a Python-based application designed to programmatically generate word search puzzle
books, complete with educational "facts" and professional PDF formatting.

The application takes a structured word list (in JSON format) and automates the entire process of creating a puzzle
book:

* **Puzzle Generation:** It calculates grid layouts and places words within a grid.
* **Content Enrichment:** It supports adding "short facts" and "long facts" (educational snippets) to each puzzle
  category.
* **Safety Filtering:** It includes a profanity filter (found in `backend/assets/`) to ensure generated grids don't
  accidentally contain offensive strings in the random filler characters.
* **PDF Export:** It renders the puzzles, word lists, and facts into a multipage PDF document suitable for printing.

There are two primary services involved in the application:

* **Backend:** A RESTful API that handles the data model and logic for puzzle generation.
* **Frontend:** A Vue.js application that handles the user interface and PDF export.

The Backend has three main modules:

* **API:** **FastAPI** and **Pydantic** exposing and access and control layer for the application.
* **Puzzle Generation:** The core business logic processes the input wordlist and creates the puzzle data structures.
* **PDF Generation:** Heavily reling on **Pillow (PIL)** for the low-level rendering of grids, text, and solution lines,
  this model produces a cover pdf and manuscript pdf suitable for printing.

The Frontend is currently vapourware, but will be:

* **GUI:** A **Vue.js** / **Vite** / **TypeScript** setup for creating wordlists, managing the application including
  profanity lists, and controlling the conversion in to puzzles and PDFs.
* **AI Integration:** Using **Ollama**, and some model yet to be identified, this module will allow the generation of
  the wordlist and acts for the planned book.

## Current State

The project is in active development.

- The backend is fully functional and can be used to generate word lists and puzzles.
- The backend needs a solid controller mechanism.
- The back end API to facilitate the frontend is not yet complete.
- The frontend is currently vapourware.
- The AI integration is planned. A couple of experiments have been run, but nothing solid yet.
- The whole system needs wrapping up in docker for easy deployment.

## In a nutshell

Wordsworth is a **factory for word search books**. You provide the words and themes, and it handles the algorithmic
placement of words, the visual design of the pages, and the generation of a print-ready PDF.

***

## Installation

### Requirements

* Docker >= 29.1.3

## Usage
the description goes here for how to run the application using docker compose, what it does, and how to access the front end.

### Configuration
the description goes here for how to configure the application.

### GUI
the description of the GUI and screenshots of the pages goes here.

## Development

### Requirements

* Docker >= 29.1.3
* Python >= 3.12
* Node >= 25.2.1
* npm >= 11.6.2

A machine that can handle the heavy lifting of generating the puzzles and running the LLM is recommended.

##### Check out the code

```shell
$ git clone git@github.com:<<Repo>>
$ cd <<folder>>
```

### Backend

#### Prepare

It is strongly recommended that you use a separate python environment for this work. These instructions assume the use
of venv
on linux, other envs and OSes are available, and if you prefer them, then please amend the instructions as required:

##### Prepare the venv

```shell
$ python -m venv venv
$ source venv/bin/activate
(venv) $ pip install -U pip
```
##### Compile the requirements
A requirements-dev.txt is committed with this repo and can be used, but it is recommended to recompile the
requirements-dev.txt file from
the pyproject.toml – especially if developing on Windows (you monster).

```shell
(venv) $ pip install pip-tools
(venv) $ pip-compile --extra dev --strip-extras -q -o requirements-dev.txt pyproject.toml 
```

##### Install the requirements

```shell
(venv) $ pip install -r requirements-dev.txt
```

##### Install pre-commit hooks

```shell
(venv) $ pre-commit install
```

The pre-commit hooks:

* `black` (using rules in `pyproject.toml`)
* `flake8` (using the rules in `.flake8`)
* `bandit` (using the rules in `.pyproject.toml`)

##### Run the tests

`pytest` settings are in `pyproject.toml`

```shell
(venv) $ pytest
```

### Frontend

#### Prepare

Ensure you are using the correct versions of `node` and `npm`.  `nvm` is recommended for this.

```shell
$ nvm use v25.2.1
```

#### Install dependencies

```shell
(venv) $ cd frontend
(venv) $ npm install
```

#### Run the frontend

```shell
(venv) $ cd frontend
(venv) $ npm run dev
```
### AI Integration

Instructions to follow.
