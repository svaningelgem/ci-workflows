# /// script
# dependencies = ["coverage[toml]"]
# ///
"""Combine the coverage data of every pytest leg into coverage.xml."""

from pathlib import Path

import coverage


def main() -> None:
    # download-artifact extracts a lone artifact straight into .coverage-legs, several get a directory each.
    legs = [root.parent for root in Path(".coverage-legs").rglob("coverage-root")]
    roots = [leg.joinpath("coverage-root").read_text().strip() for leg in legs]
    cov = coverage.Coverage()
    # Map each leg's checkout path onto this one.
    cov.set_option("paths", {"legs": [".", *roots]})
    cov.combine([str(leg) for leg in legs], strict=True)
    cov.xml_report(outfile="coverage.xml")


if __name__ == "__main__":
    main()
