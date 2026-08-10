# Contributing to lvlspy

Thank you for your interest in improving `lvlspy`. Contributions from
researchers, students, and other users are welcome.

## Before you begin

For bug reports and feature proposals, first search the
[issue tracker](https://github.com/jaadt7/lvlspy/issues) for an existing
discussion. When reporting a bug, include:

- a small example that reproduces the problem;
- the behavior you expected and what happened instead;
- your Python and `lvlspy` versions; and
- any relevant input data, traceback, or warning.

For a substantial new feature or a change to the scientific model,
please open an issue before investing in an implementation. This gives
the maintainers and contributors an opportunity to agree on scope,
interfaces, and validation.

## Development setup

`lvlspy` supports Python 3.9 and newer. Clone your fork, create and
activate a virtual environment, and install the package and test
dependencies:

```console
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[test]"
python -m pip install black pylint
```

On Windows, activate the environment with
`.venv\Scripts\activate` instead.

## Tests and code quality

Run the local test suite from the repository root:

```console
python -m pytest -v tests
```

Check formatting and linting with the same settings used by the
project:

```console
python -m black --check --line-length=79 lvlspy
python -m pylint --extension-pkg-whitelist=lxml.etree \
    --fail-under=9.9 lvlspy
```

The additional integration tests used in continuous integration
download public example data and therefore require network access:

```console
python -m pytest -v .github/workflows/lvlspy_test.py
```

New behavior should include focused tests. Changes to numerical or
scientific results should also explain the physical basis, cite
relevant references where appropriate, and include validation against
an analytical result or trusted data.

## Documentation

Update docstrings and user documentation when public behavior changes.
To build the Sphinx documentation locally:

```console
python -m pip install -r doc/requirements.txt
python -m sphinx -M html doc/source doc/_build
```

Open `doc/_build/html/index.html` to review the result.

## Pull requests

Keep each pull request focused on one change. In its description:

- explain the problem and the chosen solution;
- link related issues;
- summarize the tests you ran; and
- call out compatibility considerations or changes to scientific
  results.

Please avoid committing generated build artifacts, virtual
environments, or unrelated formatting changes. By contributing, you
agree that your contribution will be distributed under the repository's
[GNU General Public License v3 or later](LICENSE).
