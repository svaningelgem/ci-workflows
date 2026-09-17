"""Run pytest under coverage like `coverage run -m pytest`, without needing coverage config from the caller.

Coverage starts before pytest is imported, so module-level code of pytest plugins is measured.
Subprocesses such as pytest-xdist workers are measured too, and pytest-cov is switched off so it
can't take over the tracer.
"""

import importlib.util
import os
import sys

import coverage


def main() -> int:
    # The coverage job maps each leg's checkout path onto its own.
    with open("coverage-root", "w") as f:
        print(os.getcwd(), file=f)

    cov = coverage.Coverage()
    cov.set_option("run:branch", True)
    cov.set_option("run:parallel", True)
    cov.set_option("run:relative_files", False)
    cov.set_option("run:disable_warnings", ["no-data-collected"])
    # What `[run] patch = ["subprocess"]` does: subprocesses start coverage with this config.
    os.environ["COVERAGE_PROCESS_CONFIG"] = cov.config.serialize()
    cov.start()

    import pytest  # imported only once coverage runs

    no_cov = ["--no-cov"] if importlib.util.find_spec("pytest_cov") else []
    exit_code = pytest.main(sys.argv[1:] + no_cov)
    cov.stop()
    cov.save()
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
