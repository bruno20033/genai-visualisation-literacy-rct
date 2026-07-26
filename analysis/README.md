# Analysis

## Setup

```bash
conda env create -f analysis/environment.yml
conda activate genai-vizlit
jupyter lab
```

Versions are pinned to what produced the reported results. `lifelines` and
`statsmodels` in particular are version-sensitive here — the Cox model's
cluster-robust covariance and the mixed-model optimiser fallback chain both depend on
internals that have changed across releases.

## What runs what

| File | Role |
|---|---|
| `sap_estimators.py` | **Single source of truth for every estimator.** All notebooks import it. Fix a model here, not in a notebook. |
| `01_main_analysis.ipynb` | The pre-registered SAP, both waves. This is the analysis of record. |
| `02_sap_validation_montecarlo.ipynb` | Monte-Carlo validation of the estimators against known truth (~7,500 fits). Run before trusting a change to `sap_estimators.py`. |
| `exploratory/immediate_wave_only.ipynb` | Immediate-wave-only reduction, used while the delayed wave was still collecting. Superseded by `01_` but kept — its ANCOVA reduction is an exact special case of the two-wave model and a useful cross-check. |
| `exploratory/` (bundles) | Post-hoc analyses: demographic moderation, outsourcing coding, dose-response, adoption. Each is self-contained with its own `SUMMARY.md`. |
| `scripts/` | Utilities — see below. |

## Scripts

```bash
python analysis/scripts/deidentify.py --check      # audit raw exports, write nothing
python analysis/scripts/deidentify.py --derived    # regenerate data/public/ + rewrite ids in exploratory outputs
python analysis/scripts/check_no_pii.py            # repo-wide scan; run before every commit
python analysis/scripts/make_codebook.py           # regenerate data/codebook.md
python analysis/scripts/make_results_figures.py    # regenerate the thesis figures
```

`make_results_figures.py` is self-verifying: it recomputes every plotted statistic and
prints PASS/FAIL against the values reported in the thesis.

## Confirmatory design

The details are in `../preregistration/`; the short version, because it determines how
the notebook output should be read:

- **Primary outcome: accuracy only.** Success-time is a key secondary, not co-primary.
- **Primary estimand: the immediate wave.** `Wave` is coded 0/1 with immediate = 0, so
  the arm coefficients are the immediate-wave effects.
- **Full α = 0.05 under a fixed-sequence gatekeeper**, not a split or a flat Holm:
  H1a (Unrestricted vs Google superiority) → H2a (Socratic vs Google non-inferiority,
  margin 8.5 pp) → supporting contrast. If the first gate closes, the later claims are
  forfeit even if their own tests pass.
- **Persistence (H5a) is the delayed-wave simple effect**, not the interaction term.
  The interaction is reported as a decay estimate with a CI.

## Known issues

Carried forward so they are not rediscovered:

- **The primary p-value drifts as the delayed wave fills.** The SAP's primary model is
  a joint two-wave mixed model, so adding delayed responses moves the immediate-wave
  estimate's standard error. H1a has crossed the α = 0.05 boundary in both directions
  across successive runs. Treat any verdict as provisional until the delayed wave is
  final, and report the fragility rather than the point verdict.
- **CONSORT completion table (`01_`, attrition cell).** Builds its participant key
  from `Participant_ID`/`ResponseId` while the rest of the analysis keys on
  `PROLIFIC_PID`. The two do not overlap, so completion-by-arm prints zeros and the
  dropout model raises. Completion figures in the thesis were computed by hand.
- **Standalone early ANCOVA cell (`01_`)** prints a wrong-tailed one-sided p. Cosmetic;
  the authoritative primary is the gatekeeper cell.
- **`exploratory/immediate_wave_only.ipynb` monitoring cell** prints hard-coded pilot
  prose around live numbers, and the prose now contradicts the numbers it surrounds.
  Read the table, not the sentences.

## Reproducing

The notebooks read `../data/public/*.csv` — the anonymised exports, which are complete.
You do not need the raw data.

Set the input paths in the `CONFIG` cell near the top of `01_main_analysis.ipynb`, then
run top to bottom. Runtime is roughly 20 minutes at 2,000 permutations and 50 MICE
imputations.

One caveat: the bootstrap and permutation cells are BLAS-heavy. Running two notebooks
at once causes thread oversubscription and can blow the cell timeouts.
