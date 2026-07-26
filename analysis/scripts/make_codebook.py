#!/usr/bin/env python3
"""
Generate data/codebook.md from the published CSVs.

Generated rather than hand-written so it cannot drift from the data. Re-run after
any change to data/public/:

    python analysis/scripts/make_codebook.py

The interpretive text (what each variable family means, which are live and which are
legacy) is maintained in FAMILIES below; the per-column listing is read from the
files themselves.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

csv.field_size_limit(10**9)

REPO = Path(__file__).resolve().parents[2]
PUBLIC = REPO / "data" / "public"
OUT = REPO / "data" / "codebook.md"

# (prefix test, family name, description). Order matters -- first match wins.
FAMILIES: list[tuple[str, str, str]] = [
    ("pcp_", "PCP outcome items",
     "The primary outcome. Bloom-tagged parallel-coordinates-plot literacy items from the "
     "BTPL bank. Item ids encode the Bloom level (`rem`/`und`/`app`/`anal`/`eval`) and the "
     "block (`fa` = aided practice, `sa` = unaided post-test). Scored against `PCP_KEY` in "
     "`materials/instruments/pcp_scoring.js`."),
    ("vlat_", "Practice-block event log",
     "Per-item interaction records from the aided practice block: prompts, responses, search "
     "queries, clicks and timestamps. `vlat_` is legacy naming for the chart-image item "
     "format -- these are PCP items, not Mini-VLAT items. `vlat_train_responses` holds the "
     "full JSON transcript and is the source for adoption latency and the outsourcing coding."),
    ("minivlat", "Mini-VLAT baseline covariate",
     "Twelve-item visualisation-literacy pre-test, the pre-specified covariate in every "
     "adjusted model. Note `minivlat_score` as exported by Qualtrics is an attempts count, "
     "not a score; the analysis re-scores it against the key (`minivlat_recomputed`)."),
    ("judge_", "LLM-as-judge fidelity",
     "Automated manipulation-fidelity ratings of each assistant turn, used to verify the "
     "Socratic arm did not simply hand over answers. See `materials/prompts/rct_judge_prompts.md`."),
    ("cr_", "LEGACY -- critical-reasoning instrument",
     "**Not used in any reported analysis.** Columns from a superseded critical-reasoning "
     "instrument carried along in the Qualtrics form. The live construct is visualisation "
     "literacy. Retained only so the export matches what Qualtrics actually produced."),
    ("post_test", "Post-test block state", "Interface state for the unaided post-test block."),
    ("delayed", "Delayed-wave block state", "Interface state for the 72-hour delayed retest."),
    ("search_", "Search-arm event log", "Queries, clicks and dwell times for the Google-search control arm."),
    ("llm_", "LLM-arm event log", "Chat turns for the two LLM arms."),
]

CLT_RE = re.compile(r"^(IL|EL|GL) ?\d", re.I)

NAMED: dict[str, str] = {
    "Condition": "Randomised branch as assigned by Qualtrics. `SEARCH` = Google-search control arm; `LLM` = either LLM arm.",
    "arm": "Which LLM arm: `socratic` or `unrestricted`. **Blank for the control arm** -- control is identified by `Condition == 'SEARCH'`, not by this column.",
    "PROLIFIC_PID": "Participant pseudonym (`P001`...). Replaces the Prolific ID. **The key joining the immediate and delayed waves.**",
    "Q71": "GenAI usage frequency, the behaviourally-anchored single item (`AIUse`). Second pre-specified covariate.",
    "Finished": "Whether the response was completed. The analysis sample is finished, consenting responses.",
    "Duration (in seconds)": "Total time in the survey.",
    "consent_choice": "Consent outcome; non-consenting responses are excluded before analysis.",
    "excluded": "Exclusion flag set during data collection.",
    "attention_check_1": "Attention check item.",
    "attention_check_2": "Attention check item.",
    "timing_flag": "Speeding flag; the pre-registered rule is a median item response time below 1,000 ms.",
    "Model_Used": "Generator model serving the LLM arms (`openai/gpt-5.4` as fielded).",
    "STUDY_ID": "Prolific study, tokenised. Distinct values correspond to recruitment batches.",
    "SESSION_ID": "Session token, tokenised.",
    "ResponseId": "Qualtrics response token, tokenised.",
    "Participant_ID": "Qualtrics response token, tokenised. Despite the name this is **not** a participant identifier -- use `PROLIFIC_PID`.",
}


def family_of(col: str) -> tuple[str, str] | None:
    for prefix, name, desc in FAMILIES:
        if col.lower().startswith(prefix):
            return name, desc
    if CLT_RE.match(col):
        return ("Cognitive load subscales",
                "Self-reported cognitive load: `IL` intrinsic, `EL` extraneous, `GL` germane "
                "(three items each). Manipulation check MC1.")
    return None


def read_header(path: Path) -> tuple[list[str], list[str]]:
    rows = list(csv.reader(path.open(encoding="utf-8")))
    return rows[0], rows[1]


def main() -> None:
    lines: list[str] = []
    add = lines.append

    add("# Codebook")
    add("")
    add("Generated by `analysis/scripts/make_codebook.py` -- edit that script, not this file.")
    add("")
    add("Both published files keep the **three-row Qualtrics header**: row 1 column names, "
        "row 2 question text, row 3 Qualtrics import ids. Read them with:")
    add("")
    add("```python")
    add("df = pd.read_csv('data/public/immediate_wave.csv', skiprows=[1, 2], low_memory=False)")
    add("```")
    add("")

    add("## Identifying the arms")
    add("")
    add("Arm membership needs two columns, which trips people up:")
    add("")
    add("```python")
    add("google       = df['Condition'] == 'SEARCH'   # control; df['arm'] is blank here")
    add("socratic     = df['arm'] == 'socratic'")
    add("unrestricted = df['arm'] == 'unrestricted'")
    add("```")
    add("")

    add("## Variable families")
    add("")
    seen: set[str] = set()
    for path in sorted(PUBLIC.glob("*.csv")):
        for col in read_header(path)[0]:
            fam = family_of(col)
            if fam and fam[0] not in seen:
                seen.add(fam[0])
                add(f"### {fam[0]}")
                add("")
                add(fam[1])
                add("")

    add("## Key individual variables")
    add("")
    add("| Column | Meaning |")
    add("|---|---|")
    for col, desc in NAMED.items():
        add(f"| `{col}` | {desc} |")
    add("")

    add("## Full column listing")
    add("")
    for path in sorted(PUBLIC.glob("*.csv")):
        names, text = read_header(path)
        rows = sum(1 for _ in path.open(encoding="utf-8")) - 3
        add(f"### `{path.name}`")
        add("")
        add(f"{len(names)} columns, {rows} rows.")
        add("")
        add("<details><summary>Expand column list</summary>")
        add("")
        add("| # | Column | Family | Question text (row 2) |")
        add("|---|---|---|---|")
        for i, (col, txt) in enumerate(zip(names, text), start=1):
            fam = family_of(col)
            label = fam[0] if fam else ""
            clean = (txt or "").replace("|", "\\|").replace("\n", " ").strip()
            if len(clean) > 80:
                clean = clean[:77] + "..."
            add(f"| {i} | `{col}` | {label} | {clean} |")
        add("")
        add("</details>")
        add("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT.relative_to(REPO)} ({len(lines)} lines)")


if __name__ == "__main__":
    main()
