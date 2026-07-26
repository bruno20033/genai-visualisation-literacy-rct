#!/usr/bin/env python3
"""
De-identify the raw Qualtrics exports so they can be published.

Consent item 8 permits sharing *anonymised* data via public repositories. The raw
exports are not anonymous: they carry IP address, recipient name/email, geolocation
and the Prolific ID. This script converts a raw export into a publishable one while
preserving everything the analysis needs.

What it does
------------
1. DROPS direct identifiers outright (IP, name, email, external reference, lat/long).
2. PSEUDONYMISES the participant key. PROLIFIC_PID -> P001, P002, ... The mapping is
   assigned once, from the immediate-wave file, and reused for the delayed wave, so
   the two waves still join. The crosswalk is written to data/raw/ and is gitignored.
3. PSEUDONYMISES Qualtrics/session tokens (ResponseId, SESSION_ID, ...) to short
   opaque tokens, keeping any joins that rely on them.
4. KEEPS everything else byte-for-byte, including the three-row Qualtrics header, so
   the output is still a genuine Qualtrics export the notebooks can read unchanged.

Deliberately kept (documented residual risk, see data/README.md): response
timestamps and durations. They are quasi-identifiers in principle but are required
by the analysis (wave timing, success-time outcome), and with the Prolific ID gone
they are not linkable to a person by anyone outside the study team.

Usage
-----
    python deidentify.py --check     # audit the raw files, write nothing
    python deidentify.py             # write data/public/*.csv + crosswalk

The script verifies its own output and exits non-zero if any check fails.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sys
from pathlib import Path

csv.field_size_limit(10**9)

REPO = Path(__file__).resolve().parents[2]
RAW = REPO / "data" / "raw"
PUBLIC = REPO / "data" / "public"

# Which raw file becomes which published file. The immediate wave is listed first:
# it is the file the participant numbering is assigned from.
FILES = [
    ("immediate", "RCT_DataLiteracy_DL_BK_July 20, 2026_10.55.csv", "immediate_wave.csv"),
    ("delayed", "RCT_DelayedRetest_PCP (rebuilt)_July 21, 2026_05.55.csv", "delayed_wave.csv"),
]

# Removed entirely. Nothing in the analysis reads these.
DROP_COLUMNS = {
    "IPAddress",
    "RecipientLastName",
    "RecipientFirstName",
    "RecipientEmail",
    "ExternalReference",
    "LocationLatitude",
    "LocationLongitude",
}

# Replaced with P001, P002, ... The same participant gets the same number in both waves.
# PROLIFIC_PID only. Despite the name, Participant_ID is a Qualtrics response token
# (R_ followed by 16 characters), not a Prolific ID -- the two sets do not overlap, and
# the analysis keys on PROLIFIC_PID. Treating both as participant keys doubles the
# namespace and breaks the immediate/delayed join.
PARTICIPANT_COLUMNS = {"PROLIFIC_PID"}

# Replaced with short opaque tokens (prefix + 10 hex chars), consistently within a run.
# STUDY_ID is the Prolific study identifier: not personal, but tokenising it removes a
# route back to the live study listing while preserving batch distinctness (3 values in
# the immediate wave, 2 in the delayed one -- the recruitment batches).
TOKEN_COLUMNS = {
    "ResponseId",
    "ResponseID",
    "Participant_ID",
    "participant_id",
    "SESSION_ID",
    "STUDY_ID",
    "posttest_session_id",
    "delayed_session_id",
    "vlat_train_session_id",
}

# Salt for token hashing. Not a secret: tokens are internal Qualtrics identifiers with
# no external meaning. The participant key is NOT hashed at all -- it is renumbered,
# which is irreversible without the gitignored crosswalk.
TOKEN_SALT = "genai-vizlit-rct"

QUALTRICS_HEADER_ROWS = 3

# Patterns the published output must not contain.
FORBIDDEN = {
    "email address": re.compile(r"[\w.+-]+@[\w-]+\.[A-Za-z]{2,}"),
    "IPv4 address": re.compile(r"(?<!\d)(?:\d{1,3}\.){3}\d{1,3}(?!\d)"),
    "Prolific-style 24-hex ID": re.compile(r"(?<![0-9a-fA-F])[0-9a-f]{24}(?![0-9a-fA-F])"),
}


def token(value: str, prefix: str) -> str:
    """Stable opaque token for an internal identifier."""
    if not value:
        return value
    digest = hashlib.sha256((TOKEN_SALT + value).encode("utf-8")).hexdigest()[:10]
    return f"{prefix}{digest}"


def read_export(path: Path) -> tuple[list[list[str]], list[list[str]]]:
    rows = list(csv.reader(path.open(encoding="utf-8")))
    if len(rows) < QUALTRICS_HEADER_ROWS:
        raise SystemExit(f"{path.name}: too short to be a Qualtrics export")
    return rows[:QUALTRICS_HEADER_ROWS], rows[QUALTRICS_HEADER_ROWS:]


def build_crosswalk(paths: list[Path]) -> dict[str, str]:
    """Assign P001... in order of first appearance, immediate wave first."""
    seen: list[str] = []
    for path in paths:
        header, data = read_export(path)
        names = header[0]
        idx = [i for i, c in enumerate(names) if c in PARTICIPANT_COLUMNS]
        for row in data:
            for i in idx:
                if i < len(row) and row[i] and row[i] not in seen:
                    seen.append(row[i])
    width = max(3, len(str(len(seen))))
    return {pid: f"P{str(n).zfill(width)}" for n, pid in enumerate(seen, start=1)}


def deidentify(path: Path, out: Path, crosswalk: dict[str, str]) -> dict:
    header, data = read_export(path)
    names = header[0]
    keep = [i for i, c in enumerate(names) if c not in DROP_COLUMNS]
    dropped = sorted(names[i] for i in range(len(names)) if i not in set(keep))

    part_idx = {i for i, c in enumerate(names) if c in PARTICIPANT_COLUMNS}
    tok_idx = {i for i, c in enumerate(names) if c in TOKEN_COLUMNS}
    unmapped = 0

    def clean(row: list[str]) -> list[str]:
        nonlocal unmapped
        row = row + [""] * (len(names) - len(row))
        out_row = []
        for i in keep:
            value = row[i]
            if i in part_idx and value:
                if value not in crosswalk:
                    unmapped += 1
                value = crosswalk.get(value, "UNMAPPED")
            elif i in tok_idx and value:
                value = token(value, "R")
            out_row.append(value)
        return out_row

    with out.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        for hrow in header:  # keep all three Qualtrics header rows, minus dropped cols
            padded = hrow + [""] * (len(names) - len(hrow))
            writer.writerow([padded[i] for i in keep])
        for row in data:
            writer.writerow(clean(row))

    return {
        "rows": len(data),
        "cols_in": len(names),
        "cols_out": len(keep),
        "dropped": dropped,
        "unmapped": unmapped,
    }


def scan(path: Path) -> dict[str, list[str]]:
    """Look for anything that must not survive into a published file."""
    text = path.read_text(encoding="utf-8")
    found: dict[str, list[str]] = {}
    for label, pattern in FORBIDDEN.items():
        hits = sorted(set(pattern.findall(text)))
        if hits:
            found[label] = hits
    return found


def check_join(paths: list[Path]) -> tuple[int, int]:
    """How many participants appear in both published files, keyed on PROLIFIC_PID."""
    sets = []
    for path in paths:
        header, data = read_export(path)
        names = header[0]
        if "PROLIFIC_PID" not in names:
            raise SystemExit(f"{path.name}: PROLIFIC_PID column missing, cannot verify the join")
        idx = names.index("PROLIFIC_PID")
        sets.append({row[idx] for row in data if idx < len(row) and row[idx]})
    return len(sets[0] & sets[1]), len(sets[1])


DERIVED_ROOT = REPO / "analysis"
DERIVED_SUFFIXES = {".csv", ".json", ".md", ".txt", ".tsv", ".ipynb"}


def pseudonymise_derived(crosswalk: dict[str, str]) -> None:
    """Apply the crosswalk to derived analysis outputs.

    Two kinds of file are affected. The exploratory bundles (transcript coding,
    dose-response frames, adoption analysis) carry Prolific IDs in their rows. The
    executed notebooks carry them in printed dataframes inside saved cell outputs.

    Both are worth publishing, so rewrite the IDs in place rather than dropping the
    files or clearing the outputs -- clearing would discard the executed evidence.
    Substitution is plain text, which is safe here: notebooks are JSON and the
    frames are flat tables, so the ID always appears as a literal value.
    """
    if not DERIVED_ROOT.exists():
        return
    print("\nPseudonymising derived exploratory outputs")
    touched = 0
    for path in sorted(DERIVED_ROOT.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in DERIVED_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        replaced = 0
        for pid, pseudonym in crosswalk.items():
            if pid in text:
                text = text.replace(pid, pseudonym)
                replaced += 1

        # Sweep up any residual Prolific-style token the crosswalk does not cover.
        # The Prolific demographics export carries a second identifier per person
        # ("Submission id") alongside the participant id, and it is just as linkable.
        residual = set(re.findall(r"(?<![0-9a-fA-F])[0-9a-f]{24}(?![0-9a-fA-F])", text))
        for value in residual:
            text = text.replace(value, token(value, "X"))

        if replaced or residual:
            path.write_text(text, encoding="utf-8")
            note = f"{replaced} participant ids"
            if residual:
                note += f", {len(residual)} residual prolific tokens"
            print(f"  {path.relative_to(REPO)}: {note} replaced")
            touched += 1
    print(f"  {touched} file(s) rewritten" if touched else "  nothing to rewrite")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="audit raw files only, write nothing")
    ap.add_argument("--derived", action="store_true",
                    help="also rewrite Prolific ids in analysis/exploratory/ outputs")
    args = ap.parse_args()

    raw_paths = []
    for _, raw_name, _ in FILES:
        p = RAW / raw_name
        if not p.exists():
            print(f"MISSING: data/raw/{raw_name}", file=sys.stderr)
            print("\nRaw exports are gitignored. See data/raw/README.md.", file=sys.stderr)
            return 2
        raw_paths.append(p)

    if args.check:
        print("Auditing RAW exports (these are the files that must NOT be committed)\n")
        for path in raw_paths:
            hits = scan(path)
            print(f"  {path.name}")
            for label, values in hits.items():
                print(f"    {label}: {len(values)} distinct")
        return 0

    PUBLIC.mkdir(parents=True, exist_ok=True)
    crosswalk = build_crosswalk(raw_paths)
    print(f"Assigned pseudonyms to {len(crosswalk)} unique participants\n")

    out_paths = []
    for (wave, raw_name, out_name), raw_path in zip(FILES, raw_paths):
        out_path = PUBLIC / out_name
        stats = deidentify(raw_path, out_path, crosswalk)
        out_paths.append(out_path)
        print(f"  {wave:<10} {raw_name}")
        print(f"    -> data/public/{out_name}")
        print(f"       {stats['rows']} rows, {stats['cols_in']} -> {stats['cols_out']} columns")
        print(f"       dropped: {', '.join(stats['dropped'])}")
        if stats["unmapped"]:
            print(f"       WARNING: {stats['unmapped']} unmapped participant values")

    if args.derived:
        pseudonymise_derived(crosswalk)

    crosswalk_path = RAW / "participant_crosswalk.csv"
    with crosswalk_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["prolific_pid", "participant"])
        writer.writerows(crosswalk.items())
    print(f"\n  crosswalk -> data/raw/{crosswalk_path.name}  (GITIGNORED - never commit)")

    # ---- verification -----------------------------------------------------
    print("\nVerifying published output")
    failures = []

    for path in out_paths:
        hits = scan(path)
        if hits:
            for label, values in hits.items():
                failures.append(f"{path.name}: {label} still present ({len(values)} distinct, e.g. {values[0]})")
        else:
            print(f"  PASS  {path.name}: no emails, IPs, or Prolific-style IDs")

    for path in out_paths:
        names = read_export(path)[0][0]
        leaked = sorted(set(names) & DROP_COLUMNS)
        if leaked:
            failures.append(f"{path.name}: dropped column(s) still present: {leaked}")
    if not failures:
        print("  PASS  no identifier columns survive")

    for (_, raw_name, out_name), raw_path in zip(FILES, out_paths and raw_paths):
        raw_rows = len(read_export(raw_path)[1])
        out_rows = len(read_export(PUBLIC / out_name)[1])
        if raw_rows != out_rows:
            failures.append(f"{out_name}: row count changed {raw_rows} -> {out_rows}")
    if not any("row count" in f for f in failures):
        print("  PASS  row counts preserved (no participants silently lost)")

    matched, delayed_total = check_join(out_paths)
    if matched == 0:
        failures.append("immediate/delayed join is broken: 0 participants match")
    else:
        print(f"  PASS  wave join intact: {matched}/{delayed_total} delayed responses match an immediate one")

    if failures:
        print("\nFAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1

    print("\nAll checks passed. data/public/ is safe to commit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
