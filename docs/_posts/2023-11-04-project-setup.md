# Project setup

Description for Mac OS. Setup for other systems may differ.

## Shell

For now I stick with zsh because I don't like creating accounts and requiring internet 
connection every time I open a terminal (looking at you, [warp](www.warp.dev).

## Poetry

### Why you need it
Environment synching. Typically requirement files do not get updated after a package is installed.
If packages are added through `poetry add` it is more likely that changes are propagated to others.

### How to get it
- First, make sure to get an up to date [python version](https://www.python.org/downloads/macos/) and 
get the SSL certificates.
- Then follow the [poetry install instructions](https://python-poetry.org/docs/#installation).
- Make sure that you update `PATH` so poetry gets found.

### Start of a project
Set the flag whether to initialize environments locally or centrally:
`poetry config virtualenvs.in-project = [true|false]`.

Likely you will want to use [poetry init](https://python-poetry.org/docs/basic-usage/#initialising-a-pre-existing-project)
in an existing directory (e.g. cloned, empty git repo) to actually create the environment.

## Pre-Commit

- Add Pre-Commit to the environment and linters you need: `poetry add pre-commit ruff pylint`
- Install pre-commit: `pre-commit install`
- Add a file `.pre-commit-config.yaml` to the root directory

``` 
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    # Ruff version.
    rev: v0.1.5
    hooks:
      # Run the linter.
      - id: ruff
      # Run the formatter.
      - id: ruff-format
  - repo: local
    hooks:
      - id: pylint
        name: pylint
        entry: pylint
        language: system
        types: [ python ]
        args:
          [
            "-rn", # Only display messages
            "-sn", # Don't display the score
          ]
fail_fast: false
```

### Pre-Commit options

[Ruff](https://github.com/astral-sh/ruff) appears to do the job of most linters. 
Pylint, however, has useful rules (W0613, C0103, C0104 and likely more) ruff does not appear to implement (under the pylint heading).
Since pylint sometimes fails in situations that may be syntactically correct but semantically
wrong, I will likely keep it in most situations.
If you are concerned about speed, you can set fail_fast to true so pylint is only run if 
all the other checks have passed.

Extend `pyproject.toml` with all the linting you want to do (exclude sub-codes where needed) like so:

``` 
[tool.ruff]
[tool.ruff.lint]
select = [
    "E4", 
    "E7", 
    "E9",
    "F", # Flake8
    "I", # isort
    "N", # pep8-naming
    "D", # pydocstyle
    "PL" # pylint
    # Consider also: "ARG", "PTH", "ERA", "PD", "PGH", "TCH", "TID", "SIM", "RET", "RSE", "Q", "PT", "PYI"
]
ignore = ["D211", "D213"]  # There are mutually exclusive codes where you should pick one.
```

## CI

A simple CI setup includes

- A configuration file in `.github/workflows/<some_filename>.yml`
- Requiring a successful status for the branch in question (github repo -> settings -> 
Branches -> Branch protection rules –> Require status checks to pass before merging -> 
select status)

Some points to note in the below example file:
- Python version is hard coded and is not automatically in synch with the one in poetry
- Note that the system on which tests are run may differ from tho local development 
environment. While poetry is platform agnostic there may potentially still be subtle
  (or not so subtle) differences.

```
name: check-code-quality
run-name: ${{ github.actor }} is checking code quality
on: [ pull_request ]
jobs:
  check-code:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '^3.12'
          architecture: 'x64'
      - name: Install poetry
        run: |
          curl -sSL https://install.python-poetry.org | python3 -
          export PATH=$PATH:$HOME/.local/bin
      - name: Install requirements
        run: poetry install
      - name: Ruff check
        run: poetry run ruff check src
      - name: Pylint check
        run: poetry run pylint src
```

