# /// script
# requires-python = ">=3.11"
# ///
"""Report and gate coverage of the lines a pull request changes."""

import argparse
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

BAR_WIDTH = 24
HUNK = re.compile(r"^@@ -\S+ \+(\d+)(?:,(\d+))? @@")
CONDITIONS = re.compile(r"\((\d+)/(\d+)\)")


@dataclass
class FileStats:
    lines: int = 0
    lines_missed: int = 0
    conditions: int = 0
    conditions_missed: int = 0
    missed_lines: list[int] = field(default_factory=list)
    partial_lines: list[int] = field(default_factory=list)

    @property
    def covered(self) -> int:
        return (self.lines - self.lines_missed) + (
            self.conditions - self.conditions_missed
        )

    @property
    def total(self) -> int:
        return self.lines + self.conditions

    @property
    def percent(self) -> float:
        return 100.0 if not self.total else 100.0 * self.covered / self.total


def changed_lines(base: str) -> dict[str, set[int]]:
    diff = subprocess.run(
        ["git", "diff", "-U0", "--diff-filter=d", f"{base}...HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    changed: dict[str, set[int]] = {}
    path = ""
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            path = line[6:]
        elif (m := HUNK.match(line)) and path:
            start, count = int(m[1]), int(m[2] or 1)
            changed.setdefault(path, set()).update(range(start, start + count))
    return changed


def coverage_by_file(xml_path: Path, root: Path) -> dict[str, dict[int, ET.Element]]:
    tree = ET.parse(xml_path)
    sources = [
        Path(s.text.strip()) for s in tree.findall("sources/source") if s.text
    ] or [root]
    measured: dict[str, dict[int, ET.Element]] = {}
    for clazz in tree.iter("class"):
        name = clazz.get("filename", "")
        for source in sources:
            candidate = (source / name).resolve()
            if candidate.is_file():
                rel = os.path.relpath(candidate, root).replace(os.sep, "/")
                lines = measured.setdefault(rel, {})
                lines.update(
                    {
                        int(line.get("number", 0)): line
                        for line in clazz.findall("lines/line")
                    }
                )
                break
    return measured


def collect(base: str, xml_path: Path, root: Path) -> dict[str, FileStats]:
    measured = coverage_by_file(xml_path, root)
    stats: dict[str, FileStats] = {}
    for path, lines in changed_lines(base).items():
        for number in sorted(lines & measured.get(path, {}).keys()):
            line = measured[path][number]
            stat = stats.setdefault(path, FileStats())
            stat.lines += 1
            if line.get("hits") == "0":
                stat.lines_missed += 1
                stat.missed_lines.append(number)
            if line.get("branch") == "true" and (
                m := CONDITIONS.search(line.get("condition-coverage", ""))
            ):
                covered, total = int(m[1]), int(m[2])
                stat.conditions += total
                stat.conditions_missed += total - covered
                if covered < total:
                    stat.partial_lines.append(number)
    return stats


def bar(percent: float, width: int = BAR_WIDTH) -> str:
    filled = round(width * percent / 100)
    return f"`{'█' * filled}{'░' * (width - filled)}`"


def numbers(missed: int, total: int) -> str:
    return f"{missed}/{total}" if total else "—"


def render(stats: dict[str, FileStats], minimum: float) -> tuple[str, float]:
    covered = sum(s.covered for s in stats.values())
    total = sum(s.total for s in stats.values())
    percent = 100.0 if not total else 100.0 * covered / total
    if not total:
        return (
            "### Patch coverage\n\nNo changed lines are measured by the coverage report.\n",
            percent,
        )

    lines = sum(s.lines for s in stats.values())
    lines_missed = sum(s.lines_missed for s in stats.values())
    conditions = sum(s.conditions for s in stats.values())
    conditions_missed = sum(s.conditions_missed for s in stats.values())
    out = [
        "### Patch coverage",
        "",
        f"{bar(percent)} **{percent:.0f}%**  ·  lines {lines - lines_missed}/{lines}  ·  branches {conditions - conditions_missed}/{conditions}",
        "",
        "| File | Coverage | Lines missed | Branches missed |",
        "|:--|:--|--:|--:|",
    ]
    for path, stat in sorted(stats.items(), key=lambda kv: (kv[1].percent, kv[0])):
        out.append(
            f"| `{path}` | {bar(stat.percent, 20)} {stat.percent:.0f}% "
            f"| {numbers(stat.lines_missed, stat.lines)} | {numbers(stat.conditions_missed, stat.conditions)} |"
        )
    details = [
        f"- `{path}`: "
        + ", ".join(
            [f"line {n}" for n in stat.missed_lines]
            + [f"branch on {n}" for n in stat.partial_lines]
        )
        for path, stat in sorted(stats.items())
        if stat.missed_lines or stat.partial_lines
    ]
    if details:
        out += [
            "",
            "<details><summary>Which lines</summary>",
            "",
            *details,
            "",
            "</details>",
        ]
    if percent + 0.5 < minimum:
        out += ["", "> [!WARNING]", f"> The gate needs {minimum:g}%."]
    return "\n".join(out) + "\n", percent


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--xml", type=Path, default=Path("coverage.xml"))
    parser.add_argument("--min", type=float, default=0.0)
    parser.add_argument("--out", type=Path, default=Path("patch-coverage.md"))
    args = parser.parse_args()

    root = Path(
        subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    )
    report, percent = render(collect(args.base, args.xml, root), args.min)
    args.out.write_text(report, encoding="utf8")
    print(report)
    return 1 if percent + 0.5 < args.min else 0


if __name__ == "__main__":
    sys.exit(main())
