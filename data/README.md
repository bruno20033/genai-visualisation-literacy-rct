# Data

## What is published

**These are the exact Qualtrics exports** — every row, every remaining column, every
cell value, in the original column order, three-row Qualtrics header intact — with
exactly two kinds of change, both confined to identifiers:

1. **Seven columns are removed outright**, not anonymised: `IPAddress`,
   `RecipientFirstName`, `RecipientLastName`, `RecipientEmail`, `ExternalReference`,
   `LocationLatitude`, `LocationLongitude`.
2. **Five identifier columns keep their place but not their values** —
   `PROLIFIC_PID`, `Participant_ID`, `ResponseId`, `SESSION_ID`, `STUDY_ID` (plus the
   per-block session-id columns) are replaced with anonymous pseudonyms/tokens. See
   *What was changed* below for exactly how.

Nothing else is touched: every survey answer, every timestamp, every interaction
transcript is unmodified. `public/` is not a reduced analysis extract — it is the
complete export, so these are still genuine Qualtrics exports and the notebooks read
them unchanged.

| File | Rows | Columns | Contents |
|---|---|---|---|
| `public/immediate_wave.csv` | 247 | 433 (from 440) | Main study: consent, Mini-VLAT baseline, aided practice block, immediate unaided post-test, cognitive-load and manipulation-check items, full interaction transcripts |
| `public/delayed_wave.csv` | 175 | 61 (from 68) | 72-hour delayed unaided retest |

Join the waves on `PROLIFIC_PID`. All 175 delayed responses match an immediate one.

Row counts are pre-exclusion: they include non-consenting, unfinished and duplicate
responses. The analysis applies the pre-registered exclusions itself, arriving at 218
analysable immediate responses (google 69 / socratic 72 / unrestricted 77) and 174
delayed. See `codebook.md` for how to identify the arms — it needs two columns, which
is a common source of error.

## Why the raw files are not here

Consent item 8 reads:

> I agree to my **anonymised** data being used in future research and shared with
> other researchers via public data repositories.

The raw exports are not anonymous. They contain 240 IP addresses, geolocation
coordinates, Qualtrics recipient name/email fields, and Prolific IDs. Publishing them
would exceed what participants agreed to.

So `raw/` is gitignored and stays on the author's machine. What *is* published is the
transformation: `analysis/scripts/deidentify.py` turns raw into public, and it is in
the repository. Anyone can audit exactly what was removed and how, even though they
cannot see the input.

## What was changed

**Removed outright** (7 columns, none used by any analysis):

`IPAddress` · `RecipientFirstName` · `RecipientLastName` · `RecipientEmail` ·
`ExternalReference` · `LocationLatitude` · `LocationLongitude`

**Replaced with pseudonyms:**

- `PROLIFIC_PID` → `P001`, `P002`, … Assigned in order of first appearance in the
  immediate wave and reused for the delayed wave, so the two still join. The mapping
  back to real Prolific IDs exists only in `raw/participant_crosswalk.csv`, which is
  gitignored and never leaves the author's machine. Without it the renumbering is
  irreversible.
- `ResponseId`, `Participant_ID`, `SESSION_ID`, `STUDY_ID` and the per-block session
  ids → opaque salted-hash tokens. These are internal Qualtrics/Prolific identifiers
  with no analytic meaning, but they are lookup keys, so they are not left intact.
  `STUDY_ID` is tokenised rather than dropped because its distinct values mark the
  recruitment batches.

**Left intact:** everything else, including the free-text interaction transcripts.
Those were audited before publication — 1,267 participant-typed prompts and queries
were scanned for emails, phone numbers, self-identification and embedded Prolific
IDs. Nothing was found; participants were instructed under consent item 4 not to
enter personal information and appear to have complied.

## Residual disclosure risk

Two things are deliberately kept that a strict reading might question:

1. **Timestamps and durations** (`StartDate`, `EndDate`, `RecordedDate`, response
   latencies). These are quasi-identifiers in principle — someone with Prolific's own
   records could match on submission time. They are retained because the analysis
   requires them: the success-time outcome, the adoption-latency manipulation check
   and the wave-interval check are all built on them. With the Prolific ID removed,
   re-identification would require privileged access to Prolific's side.

2. **Demographics** (in `analysis/exploratory/demographic_moderation_2026-07-24/`).
   Age, sex, ethnicity, employment and job role are individually coarse but jointly
   more distinguishing. They cover 168 of 218 participants. Standard practice for a
   Prolific sample of this size, but worth stating plainly rather than leaving
   implicit.

Neither is a breach of consent item 8; both are judgement calls, recorded here so
they are reviewable.

## Regenerating

```bash
# audit the raw files without writing anything
python analysis/scripts/deidentify.py --check

# regenerate public/ and rewrite ids in derived exploratory outputs
python analysis/scripts/deidentify.py --derived

# repo-wide safety net — run before every commit
python analysis/scripts/check_no_pii.py
```

`deidentify.py` verifies its own output: it re-scans for emails, IPs and Prolific-style
IDs, confirms no identifier column survived, confirms row counts are unchanged, and
confirms the wave join still works. It exits non-zero if any check fails.

## Provenance

| | |
|---|---|
| Immediate wave | `RCT_DataLiteracy_DL_BK_July 20, 2026_10.55.csv` |
| Delayed wave | `RCT_DelayedRetest_PCP (rebuilt)_July 21, 2026_05.55.csv` |
| Anonymised | 2026-07-26 |

These are the exports the reported results were produced from. If a later export
supersedes them, replace the files in `raw/`, update `FILES` in `deidentify.py`, re-run
it, and re-run the analysis — do not edit `public/` by hand.
