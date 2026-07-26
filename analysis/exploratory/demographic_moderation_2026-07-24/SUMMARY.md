# Exploratory demographic moderation analysis — immediate wave (2026-07-24)

> **EXPLORATORY, NON-PRE-REGISTERED, HYPOTHESIS-GENERATING ONLY.**
> Nothing here is confirmatory, and nothing here bears on, overrides, or re-litigates the
> trial's pre-registered (SAP) conclusions. Effect sizes and CIs are the intended output;
> p-values are screening devices.

## Bottom line

**No demographic characteristic detectably moderates the arm effect on immediate unaided
accuracy.** Across seven moderators (age, sex, first-language English, employment status,
ethnicity, IT/data occupation, Prolific platform experience), every arm×moderator
interaction is small relative to its uncertainty, and nothing approaches survival of
BH-FDR correction (all q ≥ .44). The unrestricted-arm deficit looks like a broadly
*uniform* effect: the U−G point estimate is negative in essentially every subgroup
examined (−1.9 to −5.6 pp), never significantly so within a subgroup, and never
significantly different between subgroups.

One suggestive-but-fragile pattern (age × Socratic) and one weak whisper (English-L1 ×
abstention) are described below with their fragility evidence.

## Data decisions

- **Outcomes/covariates from the SAP pipeline's own frames** (`analysis_frames_2026-07-21/`,
  written by `rct_data_literacy_analysis_4_FINAL_2026-07-21.ipynb`), merged to the
  `demo__*` columns of `merged_immediate_demographics_2026-07-20.csv` by `PROLIFIC_PID`.
  This reuses the trial's exact analysable-set filter, answer-key scoring (16 immediate
  items), the *key-scored* Mini-VLAT (the survey's `minivlat_score` column is an attempts
  count — known bug), and the AIUse (Q71) covariate. Validation anchors reproduced exactly:
  n=218 (69/72/77), immediate ANCOVA U−G −5.01 pp (one-sided p=.034), IDK rates G 4.3% /
  U 8.7%.
- **Merge gap:** 168/218 analysable participants have usable demographics (54 G / 55 S /
  59 U; match rate 76–78% in every arm, χ² p=.96). The gap is *administrative*: every
  matched participant started on **2026-07-17**; the unmatched are exactly the July-16 and
  July-20 batches — the Prolific demographic export simply doesn't cover those batches.
  One further participant is consent-revoked (all demographics blanked). Handling:
  **complete-case per moderator**, because (a) missingness is export-coverage-driven, not
  behaviour-driven; (b) imputing the *moderator* in a moderation-discovery analysis would
  manufacture the quantity under study. Representativeness checks: matched vs unmatched
  differ by ≤0.19 SMD on accuracy / Mini-VLAT / AIUse (all Welch p>.22), and the arm effect
  does not differ detectably between matched and unmatched (joint interaction p=.45).
- **Important context:** within the matched subset the baseline adjusted arm effects are
  U−G **−3.70 pp [−9.97, +2.57]** and S−G **+1.78 pp [−4.35, +7.91]** (n=168) — the U−G
  harm estimate is attenuated relative to the full sample's −5.01 pp and is not itself
  significant here. All subgroup effects must be read against that weaker baseline.
- **Data quality:** Prolific bot-authenticity check is "high" for every non-missing case —
  nobody flagged, so no bot-driven exclusions are possible and the flag cannot moderate.
  2 of 168 are "AWAITING REVIEW" (rest APPROVED); excluding them changes nothing.

## Models and multiplicity

Per moderator M: OLS on the 16-item proportion correct,
`acc ~ soc + unr + M + soc:M + unr:M + minivlat_c + aiuse_c`, HC3 robust SEs.
Moderation = joint robust Wald F on the two interaction terms. Continuous moderators
centred (age per +10 y; approvals per log10 unit). Families: 7 omnibus tests on accuracy
(primary), 7 on IDK-abstention (secondary); BH-FDR within family. Freedman–Lane
residual-permutation p (B=2000, seed 2026) for anything with omnibus p<.10. Sensitivity
specs: unadjusted; APPROVED-only; suggestive results re-fit with the other six moderators'
main effects.

## Results — accuracy (primary exploratory family, n=165–168)

| Moderator | U−G × M (pp) [95% CI] | S−G × M (pp) [95% CI] | omnibus p | BH q | MDES80 (U×M) |
|---|---|---|---|---|---|
| Age (per +10 y) | −0.1 [−8.5, +8.2] | **+6.8 [−0.3, +13.9]** | .062 | .44 | 11.9 pp |
| Sex (F vs M) | −3.2 [−16.1, +9.6] | +2.3 [−9.6, +14.2] | .72 | .99 | 18.4 pp |
| English L1 | −0.3 [−12.5, +11.8] | −0.9 [−13.0, +11.2] | .99 | .99 | 17.3 pp |
| Part- vs full-time | +1.8 [−10.8, +14.4] | −2.6 [−16.2, +11.0] | .85 | .99 | 18.0 pp |
| Non-White vs White | +2.4 [−13.7, +18.6] | −3.5 [−18.6, +11.5] | .80 | .99 | 23.1 pp |
| IT/data occupation | +0.8 [−16.5, +18.2] | −7.5 [−22.5, +7.5] | .53 | .99 | 24.8 pp |
| Prolific approvals (log10, aux.) | +4.0 [−8.3, +16.4] | +8.3 [−4.5, +21.0] | .43 | .99 | 17.6 pp |

MDES80 = interaction size detectable with 80% power at the realised SE — 12–25 pp, i.e.
2–5× the main effect itself. **This analysis can only rule out enormous moderation.**
Expected false positives at raw p<.05 across 7 tests: ~0.35.

### The one suggestive pattern: age × Socratic — fragile, lean noise

Socratic-vs-Google grows with age (+6.8 pp/decade [−0.3, +13.9]; S−G −2.8 pp at age ~29
vs +6.0 pp at age ~42; per-arm adjusted age slopes: socratic +4.7 [+0.9, +8.5] vs google
−2.1, unrestricted −2.5). Omnibus p=.062 (FL permutation p=.057; stable to APPROVED-only
p=.059 and to adding the other moderators' main effects p=.053). **But it is fragile in
exactly the ways that matter:** trimming the 10 participants aged >55 → p=.30 (+4.1
[−3.7, +11.9]); rank-transforming age → p=.15; unadjusted spec → p=.15; and the band means
show the pattern rests on an **11-person socratic 42–63 cell scoring 83.5%**. Verdict:
not robust; at most a hypothesis ("older adults may benefit more from Socratic
scaffolding — consistent with them being less fluent AI self-directed users") for a future,
larger sample. Note the U×age interaction is ~0 — the *harm* arm shows no age gradient.

### Results — IDK abstention (secondary family)

Nothing significant (all omnibus p ≥ .14, q ≥ .63). Weak whisper: the unrestricted-arm
abstention excess appears concentrated among **native English speakers** (U×English-L1
+7.1 pp [−0.1, +14.3], omnibus p=.14, q=.63) and there is a directionally positive age
gradient (U×age +3.3 pp/decade [−1.6, +8.2], p=.18). Both are noise-compatible; recorded
only because abstention is mechanistically central to the thesis (D15/D20 side-finding).

### Curiosity (main effect, not moderation)

Non-native English speakers scored ~5–7 pp *higher* than native speakers in **every** arm
(a main effect with no interaction). Most plausibly Prolific pool composition (the
non-native pool here is largely continental-EU professionals), not a treatment phenomenon;
it does not affect the moderation conclusions.

## Not tested, and why

- **Student status** — only 20 students (~5–9/arm); interaction MDES would be astronomically
  large. Descriptive means only (students numerically lower everywhere).
- **Country of residence (UK vs non-UK)** — φ=0.86 with first-language English; testing both
  double-counts one construct and pads the family. Descriptive only.
- **Country of birth / Nationality** — 33 countries, high-cardinality, redundant with
  residence/language.
- **Fluent languages (multilingualism)** — collinear with first-language English;
  heterogeneous combinations.
- **Full job-role taxonomy** — 88 distinct roles at n=168; only the explicit 13-role
  IT/software/data collapse was testable. Black-vs-White specifically (n=34, 15/10/9 per
  arm) was left descriptive: means are directionally lower for Black participants in the
  two LLM arms, but cells of 9–15 cannot support an interaction claim.
- **Authenticity check: Bots** — zero variance (all "high").
- **Submission metadata** (ids, timestamps, time-taken, status, completion code) — tracking
  noise, not demographics. Prolific status used only as a sensitivity filter.
- **Delayed-wave outcomes and success-time** — out of scope for this immediate-wave file;
  success-time moderation via Cox interactions at ~55/arm would be hopeless for power and
  was not attempted.

## Caveats (read before quoting anything above)

1. Exploratory; nothing pre-registered; report only as hypothesis-generating.
2. Power: MDES for interactions is 12–25 pp vs a ~5 pp main effect — absence of evidence
   here is very much not evidence of absence.
3. The matched subset's own U−G estimate (−3.7 pp, ns) is weaker than the full-sample
   −5.0 pp; subgroup "effects" partition an already-fragile main effect.
4. Chance arm×composition imbalances within the matched subset (socratic 69% male vs
   google 49%; unrestricted 42% part-time vs google 22%) — these widen interaction CIs and
   make unadjusted subgroup means treacherous; the models handle them, eyeballs won't.
5. Demographics cover only the July-17 batch (77% of the sample) — representativeness
   checks pass, but the coverage is batch-defined, not random.
6. Sex has 1 "prefer not to say", ethnicity 3 (excluded case-wise); ethnicity binary is a
   crude heterogeneous collapse.

## Files

| File | What |
|---|---|
| `demographic_moderation_analysis.py` | Main analysis (build, validate, triage, models, sensitivities) |
| `age_followup.py` (+ `age_followup_output.txt`) | Robustness probes for the age×Socratic pattern |
| `make_figures.py` | Figure generator (self-verifying, 5/5 PASS) |
| `full_output.txt` | Complete printed output of the main script |
| `analysis_dataset.csv` | Participant-level merged dataset (218 rows, matched flag) |
| `triage_decisions.csv` | Variable-by-variable test/skip decisions |
| `moderation_results_accuracy.csv` / `moderation_results_idk.csv` | Tidy interaction results incl. unadjusted-spec p |
| `subgroup_effects_accuracy.csv` / `subgroup_effects_idk.csv` | Simple effects per subgroup level |
| `fig_interaction_forest.(png/pdf)` | Interaction forest, both contrasts, BH q annotated |
| `fig_subgroup_effects.(png/pdf)` | U−G and S−G within every subgroup |
| `fig_age_accuracy.(png/pdf)` | Age×arm scatter + fits, fragility annotated |

Environment: `~/opt/anaconda3/envs/course/bin/python` (pandas/statsmodels). Seed 2026.
