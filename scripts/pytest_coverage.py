"""`coverage run -m pytest` that also measures subprocesses and needs no coverage config."""

import importlib.util
import os
import sys

import coverage


def main() -> int:
    with open("coverage-root", "w") as f:
        print(os.getcwd(), file=f)

    cov = coverage.Coverage()
    cov.set_option("run:branch", True)
    cov.set_option("run:parallel", True)
    cov.set_option("run:relative_files", False)
    cov.set_option("run:disable_warnings", ["no-data-collected"])
    if hasattr(cov.config, "serialize"):  # missing before coverage 7.10
        os.environ["COVERAGE_PROCESS_CONFIG"] = cov.config.serialize()
    cov.start()

    import pytest  # after cov.start(), so plugin imports are measured

    no_cov = ["--no-cov"] if importlib.util.find_spec("pytest_cov") else []
    exit_code = pytest.main(sys.argv[1:] + no_cov)
    cov.stop()
    cov.save()
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
