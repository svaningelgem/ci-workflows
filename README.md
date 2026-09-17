# ci-workflows

Shared GitHub Actions workflows. Change them here once instead of in every repo.

## Python

`ruff format --check` + `ruff check --no-fix` (latest ruff via `uvx`, or a locked one with `ruff-group`) and `pytest` after `uv sync --locked`.

```yaml
name: Python

on:
  push:
    branches: [master]
  pull_request:

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}

jobs:
  python:
    uses: svaningelgem/ci-workflows/.github/workflows/python.yml@v1
    secrets:
      CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}
```

| Input | Default | |
|---|---|---|
| `runner` | `vars.RUNNER_LABEL \|\| 'ubuntu-latest'` | Runner for the Linux jobs; `RUNNER_LABEL` is read from the calling repo |
| `windows` / `macos` | `false` | Extra pytest legs on GitHub-hosted runners |
| `ruff-group` | | Dependency group with a locked ruff; empty = latest ruff via `uvx` |
| `pylint` | | Arguments for the project's `pylint` (`src/ --fail-under=10`); empty = skipped |
| `ty` | | Arguments for the project's `ty check` (`src/`); empty = skipped |
| `python-versions` | `[""]` | JSON list; `""` uses the project's own Python pin. `pylint`/`ty` use the first |
| `working-directory` | `.` | |
| `setup` | | Bash run before `uv sync` in the pytest and lint jobs (system packages, `echo VAR=x >> "$GITHUB_ENV"`) |
| `sync-args` | | Appended to `uv sync --locked` |
| `pytest` | `true` | `false` for repos without tests |
| `pytest-args` | | |
| `patch-coverage` | `100` | Minimum % of changed lines and branches covered, merged across the matrix; `0` only reports. Posted as a PR comment when the caller grants `pull-requests: write` |

Secrets (passed explicitly, `secrets: inherit` doesn't cross owners): `CODECOV_TOKEN` uploads the merged coverage, `GIT_TOKEN` clones private GitHub dependencies.

Releases: tag `vX.Y.Z` and move `v1` along.
