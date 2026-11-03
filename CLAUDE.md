# mazini (Python)

## Releasing

Every release gets a GitHub Release with a description; the JS package
([forzagreen/mazini-js](https://github.com/forzagreen/mazini-js)) is released alongside it with the same
version when the API changes.

1. Bump `version` in `pyproject.toml` and `__version__` in `src/mazini/__init__.py`, run `uv lock`. Open a
   "Release X.Y.Z" PR and merge it once CI is green.
2. Run the **Release** workflow (`.github/workflows/release.yml`, `workflow_dispatch`) with `notes` set to
   the description. It creates tag `vX.Y.Z` and the GitHub Release, then runs `publish.yml` on the tag,
   which publishes to PyPI.
3. Notes follow the earlier releases: what is new, what stayed unchanged, `pip install mazini==X.Y.Z`, and
   a Full Changelog compare link from the previous tag.
4. Check `https://pypi.org/pypi/mazini/json`.
