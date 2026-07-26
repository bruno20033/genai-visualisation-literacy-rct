#!/usr/bin/env python3
"""
Repo-wide safety net: fail if anything committable contains personal data.

deidentify.py guarantees data/public/ is clean. This checks *everything else* --
executed notebook outputs, exploratory analysis bundles, coding spreadsheets, logs --
because those were produced from the raw data and routinely embed Prolific IDs in
printed dataframes, per-participant filenames and JSON dumps.

Run before every commit:

    python analysis/scripts/check_no_pii.py

Exits non-zero and lists offending files if anything is found. Paths matched by
.gitignore are skipped, since they are never committed.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

PATTERNS = {
    "Prolific-style 24-hex ID": re.compile(r"(?<![0-9a-fA-F])[0-9a-f]{24}(?![0-9a-fA-F])"),
    "email address": re.compile(r"[\w.+-]+@[\w-]+\.[A-Za-z]{2,}"),
    "IPv4 address": re.compile(r"(?<!\d)(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.){3}(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(?!\d)"),
    "Qualtrics response id": re.compile(r"\bR_[A-Za-z0-9]{15,17}\b"),
}

# Text that legitimately matches a pattern and is not participant data. Each entry
# was checked against the file it fires on -- do not widen these without doing the same.
ALLOW = re.compile(
    r"""
    noreply@|example\.com|@example|
    \.png|\.jpg|\.svg|                       # asset filenames
    (?:0|127)\.0\.0\.[01]|                   # localhost / null route
    ^\d{2,3}\.0\.0\.0$|                      # browser version in a User-Agent string
    firat@nottingham                         # BTPL instrument author's published contact
    """,
    re.VERBOSE | re.I,
)

BINARY_SUFFIXES = {".pdf", ".png", ".jpg", ".jpeg", ".gif", ".pkl", ".zip", ".xlsx",
                   ".woff", ".woff2", ".ttf", ".ico", ".pyc", ".parquet"}


def tracked_files() -> list[Path]:
    """Files git would actually commit: tracked + untracked, minus ignored."""
    out = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=REPO, capture_output=True, text=True,
    )
    if out.returncode != 0:  # not a git repo yet -- fall back to walking the tree
        return [p for p in REPO.rglob("*") if p.is_file() and ".git" not in p.parts]
    return [REPO / line for line in out.stdout.splitlines() if line]


def scan_file(path: Path) -> dict[str, set[str]]:
    if path.suffix.lower() in BINARY_SUFFIXES:
        return {}
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except (OSError, UnicodeDecodeError):
        return {}
    found: dict[str, set[str]] = {}
    for label, pattern in PATTERNS.items():
        hits = {m for m in pattern.findall(text) if not ALLOW.search(m)}
        if hits:
            found[label] = hits
    return found


def main() -> int:
    files = [p for p in tracked_files() if p.is_file()]
    print(f"Scanning {len(files)} committable files for personal data\n")

    offenders: list[tuple[Path, dict[str, set[str]]]] = []
    for path in files:
        hits = scan_file(path)
        if hits:
            offenders.append((path, hits))

    if not offenders:
        print("PASS -- no Prolific IDs, emails, IP addresses or Qualtrics response ids found.")
        return 0

    print(f"FAIL -- personal data found in {len(offenders)} file(s):\n")
    for path, hits in sorted(offenders, key=lambda x: str(x[0])):
        rel = path.relative_to(REPO)
        print(f"  {rel}")
        for label, values in hits.items():
            sample = sorted(values)[:2]
            print(f"      {label}: {len(values)} distinct, e.g. {', '.join(sample)}")
    print("\nFix by de-identifying the file, clearing notebook outputs, or gitignoring it.")
    print("Clear notebook outputs with:")
    print("  jupyter nbconvert --clear-output --inplace <notebook>.ipynb")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
