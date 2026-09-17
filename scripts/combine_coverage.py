# /// script
# dependencies = ["coverage[toml]"]
# ///
"""Combine the pytest legs' coverage data into coverage.xml."""

from pathlib import Path

import coverage


def main() -> None:
    # A single downloaded artifact isn't put in its own directory.
    legs = [root.parent for root in Path(".coverage-legs").rglob("coverage-root")]
    roots = [leg.joinpath("coverage-root").read_text().strip() for leg in legs]
    cov = coverage.Coverage()
    cov.set_option("paths", {"legs": [".", *roots]})
    cov.combine([str(leg) for leg in legs], strict=True)
    cov.xml_report(outfile="coverage.xml")


if __name__ == "__main__":
    main()
