# ci-workflows

Shared GitHub Actions workflows. Change them here once instead of in every repo.

## Python

`ruff format --check` + `ruff check` (latest ruff via `uvx`) and `pytest` after `uv sync --locked`.

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
| `python-versions` | `[""]` | JSON list; `""` uses the project's own Python pin |
| `working-directory` | `.` | |
| `sync-args` | | Appended to `uv sync --locked` |
| `pytest` | `true` | `false` for repos without tests |
| `pytest-args` | | |
| `patch-coverage` | `false` | PRs must cover 100% of changed lines; needs `--cov --cov-report=xml` |

Secrets (passed explicitly, `secrets: inherit` doesn't cross owners): `CODECOV_TOKEN` uploads `coverage.xml` when present, `GIT_TOKEN` clones private GitHub dependencies.

Releases: tag `vX.Y.Z` and move `v1` along.
