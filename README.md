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
    with:
      runner: ${{ vars.RUNNER_LABEL || 'ubuntu-latest' }}  # private orgs only; public repos leave this out
    secrets:
      CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}
```

| Input | Default | |
|---|---|---|
| `runner` | `ubuntu-latest` | Runner for the Linux jobs |
| `windows` / `macos` | `false` | Extra pytest legs on GitHub-hosted runners |
| `ruff-group` | | Dependency group with a locked ruff; empty = latest ruff via `uvx` |
| `python-versions` | `[""]` | JSON list; `""` uses the project's own Python pin |
| `working-directory` | `.` | |
| `setup` | | Bash run before `uv sync` in the pytest job (system packages, `echo VAR=x >> "$GITHUB_ENV"`) |
| `sync-args` | | Appended to `uv sync --locked` |
| `pytest` | `true` | `false` for repos without tests |
| `pytest-args` | | |
| `patch-coverage` | `100` | Minimum % of changed lines and branches covered, merged across the matrix; `0` only reports. Posted as a PR comment when the caller grants `pull-requests: write` |

Secrets (passed explicitly, `secrets: inherit` doesn't cross owners): `CODECOV_TOKEN` uploads the merged coverage, `GIT_TOKEN` clones private GitHub dependencies.

Releases: tag `vX.Y.Z` and move `v1` along.
