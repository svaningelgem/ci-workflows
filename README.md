# ci-workflows

Shared GitHub Actions workflows. Change them here once instead of in every repo.

## Python

`ruff format --check` + `ruff check --no-fix` (latest ruff via `uvx`, or a locked one with `ruff-group`), optional pylint and ty, and `pytest` after `uv sync --locked`, with patch coverage merged across the matrix.

### Minimal

```yaml
name: Python

on:
  push:
    branches: [master]
  pull_request:

permissions:
  contents: read
  pull-requests: write  # patch-coverage PR comment

jobs:
  python:
    uses: svaningelgem/ci-workflows/.github/workflows/python.yml@v1
```

### Exhaustive

Every input set; the values are examples.

```yaml
name: Python

on:
  push:
    branches: [master]
  pull_request:

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}

permissions:
  contents: read
  pull-requests: write  # patch-coverage PR comment

jobs:
  python:
    uses: svaningelgem/ci-workflows/.github/workflows/python.yml@v1
    with:
      runner: ubuntu-24.04
      windows: true
      macos: true
      python-versions: '["3.12", "3.14"]'
      working-directory: backend
      setup: echo PYTHONPATH=src >> "$GITHUB_ENV"
      sync-args: --all-extras
      ruff-group: lint
      pylint: src/ --fail-under=10
      ty: true
      pytest: true
      pytest-args: -n auto
      patch-coverage: 90
      total-coverage: 80
    secrets:
      CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}
      GIT_TOKEN: ${{ secrets.PRIVATE_DEPS_PAT }}
```

ruff, pylint, ty, the pytest matrix and (on pull requests) a Conventional Commits check of the PR title run in parallel; `coverage` follows pytest, and `result` fails if any job failed, so make `result` the required status check. The merged `coverage.xml` is uploaded as the `merged-coverage` artifact for later jobs, e.g. a Sonar scan with `needs: python`.

| Input | Default | |
|---|---|---|
| `runner` | `vars.RUNNER_LABEL \|\| 'ubuntu-latest'` | Runner for the Linux jobs; `RUNNER_LABEL` is read from the calling repo |
| `windows` / `macos` | `false` | Extra pytest legs on GitHub-hosted runners |
| `python-versions` | `[""]` | JSON list; `""` uses the project's own Python pin. `pylint`/`ty` use the first |
| `working-directory` | `.` | |
| `setup` | | Bash run before `uv sync` in the pytest and lint jobs (system packages, `echo VAR=x >> "$GITHUB_ENV"`) |
| `sync-args` | | Appended to `uv sync --locked` |
| `ruff-group` | | Dependency group with a locked ruff; empty = latest ruff via `uvx` |
| `pylint` | `false` | `true` = `pylint --recursive=y .`; any other string replaces the `.`, and a later `--recursive` overrides the default. Its venv lives in the runner's temp directory, so it's never linted. Locked pylint if any, else the latest |
| `ty` | `false` | `true` = `ty check`; any other string is appended as its arguments. Locked ty if any, else the latest |
| `pytest` | `true` | `false` for repos without tests |
| `pytest-args` | | |
| `patch-coverage` | `100` | Minimum coverage of what a PR changes, merged across the matrix; `0` only reports. A changed line counts once and each branch on it once more, so a half-taken `if` costs half a point. Posted as a PR comment when the caller grants `pull-requests: write` and no `CODECOV_TOKEN` is passed (Codecov comments itself) |
| `total-coverage` | `0` | Minimum total % of the merged coverage; `0` leaves it to the project's `[tool.coverage.report] fail_under` |

Secrets (passed explicitly, `secrets: inherit` doesn't cross owners): `CODECOV_TOKEN` uploads the merged coverage, `GIT_TOKEN` clones private GitHub dependencies.

Releases: tag `vX.Y.Z` and move `v1` along.
