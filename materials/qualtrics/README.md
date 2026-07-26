# Qualtrics survey definitions

## Status

| File | Status |
|---|---|
| `delayed_posttest.qsf` | Present — the 72-hour delayed retest |
| `main_survey.qsf` | **Missing — action required** |
| `main_survey.pdf` | **Missing — action required** |
| `delayed_posttest.pdf` | **Missing — action required** |

The main survey definition does not exist anywhere on disk, in the thesis tree or in
the `thesis-rct` repository. It exists only inside your Qualtrics account. Nobody but
you can export it, and the replication package is incomplete without it.

---

## Action 1 — export the `.qsf` files

The `.qsf` is Qualtrics' own JSON survey format. Another researcher imports it and
gets your blocks, randomiser, embedded-data fields, display logic and question-level
JavaScript exactly as you built them.

In Qualtrics, for **each** survey:

1. Open the survey → **Tools** → **Import/Export** → **Export Survey**
2. Save the downloaded file here, named:
   - `main_survey.qsf` — the main study (consent → Mini-VLAT → practice → post-test)
   - `delayed_posttest.qsf` — already present; re-export if it has changed since
     2026-07-14

**Check before committing:** open the `.qsf` in a text editor and search for `sk-`,
`Bearer`, `api`, and `token`. Question-level JavaScript is exported verbatim, so if a
key was ever pasted into a JS panel it will be in the file. The architecture here puts
keys in the Cloudflare Worker specifically to avoid this, but verify rather than assume.

## Action 2 — export human-readable versions

A `.qsf` is minified JSON; no examiner will read it. Provide a printable version too.

For each survey: **Tools** → **Print Survey** → save as PDF here, named
`main_survey.pdf` and `delayed_posttest.pdf`.

This is also what belongs in the thesis appendix as the instrument of record.

Caveat: the print view renders the *survey*, so the iframed experimental app appears
as an empty block. That is expected — layer 3 in `../README.md` covers it. Consider
adding a screenshot of the live interface alongside.

## Action 3 — note the deviation, if any

If the Qualtrics survey was edited *during* data collection (e.g. the recruitment
batches used slightly different versions), the exported `.qsf` is the **final** state,
not necessarily the state every participant saw. If that happened, say so in
`../../preregistration/deviations.md`.

---

## Note on the delayed retest

`delayed_posttest.qsf` was built as a standalone one-off Prolific project rather than
a second wave of the main longitudinal study, because Prolific does not allow adding a
wave to an already-published longitudinal project. Access was gated to Wave-1
completers via a participant group. This is a fielding detail, not a design change,
but it explains why the delayed wave is a separate survey and a separate export.
