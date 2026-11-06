# Contributing

## Developer install

```bash
git clone https://github.com/fusion-energy/paramak.git
cd paramak
python -m pip install -e .[tests]
pre-commit install  # optional, runs black and whitespace fixes on commit
```

## Tests and linting

```bash
pytest -v
ruff check .
```

The transport tests need OpenMC and cad_to_dagmc. OpenMC wheels are not on PyPI:

```bash
python -m pip install --extra-index-url https://shimwell.github.io/wheels -e .[tests,transport]
pytest -v -k transport
```

## Docs

```bash
python -m pip install -e .[docs]
sphinx-build docs _build
```

CI builds the docs against the CadQuery main branch until a CadQuery release
includes CadQuery/cadquery#2124 (see `.github/workflows/documentation_update.yml`).

Docs are built on every PR. Pushes to main deploy to `/dev`, tags deploy to
`/<tag>` and `/stable`.

## Releasing

1. Add the new version to `docs/version_switcher.json`, below `stable`, and
   merge to main.
2. Create a GitHub release from main with a new tag of the same version, e.g.
   `0.12.0`. The version comes from the tag (setuptools_scm), nothing else
   needs bumping.
3. The tag push builds and deploys the docs. Publishing the release runs
   `python-publish.yml`, which checks the tag is in `docs/version_switcher.json`
   and then uploads to PyPI.

Until the docs deploy, the new dropdown entry links to a page that does not
exist yet. This takes a few minutes.

If the PyPI job fails because step 1 was missed, merge the switcher entry,
delete the release and tag, and recreate them from main.
