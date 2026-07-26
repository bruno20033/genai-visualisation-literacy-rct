# Answer-level adoption analysis — plan (written before any analysis was run)

**Date:** 2026-07-20. **Status:** exploratory / post-hoc / associational; recruitment launched
2026-07-16, so everything here is post-commencement, needs author sign-off before any thesis
use, and nothing may be read causally. Builds on (does not redo) the dose–response pass in
`~/Downloads/outsourcing_doseresponse_verification_2026-07-20/`.

## Phase 0 — the adoption frame (enabling step)

One row per unrestricted practice cell with assistant interaction (expected 376 = 528 − 152
NO_INTERACTION; cross-checked against `n_turns>0`). Fields: `llm_answer` (option letter in
the item's own label space), `answer_form` ∈ {clean_option, descriptive, hedged_multiple,
no_answer}, `mapping_difficulty` for descriptive answers ('trivial' when the assistant states
an option's text near-verbatim — e.g. "Yes" on the is-this-a-PCP items — vs 'nontrivial' when
the participant must genuinely translate, e.g. "the second scatterplot" → B; the Theme-4
mapping-burden exposure uses the nontrivial variant, with all-descriptive as sensitivity),
`llm_correct` (= llm_answer vs `key`; for descriptive, semantic match to the keyed option's
text), `adopted` (participant's submitted `answer` == llm_answer; NaN when no committed
recommendation), `participant_correct`, `participant_idk`, `extract_confidence`
(high/med/low), and a quoted `excerpt` of the operative phrase for audit. Committal rule:
"I can't see the chart, but if I had to pick, B" counts as a committed recommendation
(clean_option); hedged_multiple is reserved for genuinely uncommitted replies (several
options kept alive, or refusal to pick); no_answer covers concept-only replies and pure
requests for the image. Two wrinkles known before analysis, from read-only source
inspection: (1) the assistant cannot see the stimulus charts (items are auto-shared as
text), so "I'd need to see the chart" replies and blind guesses are expected and
substantively interesting (the LLM's own correctness ceiling on chart-reading items);
(2) per `pcp_consolidate.js`, the judge layer exists only in the Socratic arm (judge:null
in Unrestricted), so `judge_fidelities` is expected unusable and `n_regen` likely
degenerate in this arm — verified in Phase 0a and dropped with a note if so.

**Extraction protocol (integrity-relevant).** A regex battery over the assistant turns
(final turn prioritised; "answer is X", "correct answer: X", bold/bare option statements,
option-text verbatim hits displayed as evidence) produces a DRAFT code for every cell. Cells
where the draft is unambiguous (single letter, no cross-turn conflict, letter in the item's
label set) are auto-accepted at confidence 'high'. Every other cell — no letter found,
conflicting letters, changed answers across turns, letter outside the label set, Yes/No
items answered semantically, all VERIFICATION_ONLY and CONCEPT_SUPPORT cells — is
**read and coded by me directly** from an evidence block containing the question, the
option list, and the full assistant text, **blind to the key, the participant's submission,
and correctness** (those merge in afterwards, so extraction cannot be steered by outcomes).
A stratified random audit sample (~60) of the auto-accepted cells is read the same blind way
and the disagreement rate reported. This is still a single automated coder overall — same
caveat class as the existing content coding; a human check is recommended before thesis use
and the per-cell excerpts make that audit fast. QA: cross-tab llm-answer availability
against the 4-way content codes (FULL_OUTSOURCING should nearly always have a committed
answer; CONCEPT_SUPPORT should be no_answer; mismatches listed).

## Analyses by theme (tests fixed in advance)

- **T1 Adoption/discordance.** Clustered-by-participant intercept-only LPMs for all rates
  (adoption, discordance = 1 − adoption, answer_form shares, LLM correctness base rate —
  overall, by content code, by Bloom, by item). The 2×2×2 {llm_correct}×{adopted}×
  {participant_correct} table with the named cells (passive success / threw away a correct
  answer, split IDK vs wrong option / inherited error / rescue). Association answer_form →
  non-adoption: LPM `adopted ~ descriptive` with CRVE(pid), Fisher exact as a small-sample
  check (noting it ignores clustering).
- **T2 Behaviour → learning.** Participant-level: `acc ~ X + minivlat_c + aiuse_c` (HC3),
  then `+ fo_share` ("over and above dose"), one predictor at a time to avoid a collinear
  soup: adoption rate, mapping-failure exposure (share of engaged cells with a nontrivial
  descriptive answer), blind-copy share (adopted & Δ<5 s — the D11 threshold; 10 s
  sensitivity), rescue rate only if enough participants have llm-wrong cells (else counts).
  Denominator rule: participants need ≥2 cells in the relevant denominator; n reported per
  model. Within-person: participant×Bloom-category panels (exposure = category share of
  adopted / nontrivial-descriptive cells among engaged; outcome = 4-item category accuracy),
  two-way FE via FWL demeaning, CRVE(pid), within-person permutation (B=10,000, seed 2026,
  shuffling exposure across each person's non-missing categories). States plainly: removes
  stable person confounding, does NOT remove within-person targeting; exposure self-selected.
- **T3 LLM-error propagation.** Count llm-wrong practice cells; within-person FE of category
  accuracy on "received a wrong LLM answer in this category"; distractor tracing done
  case-by-case (the item bank's option texts define distractor families, e.g. legend-blaming
  vs nothing-wrong on eval items) — reported as counts + excerpts, honestly labelled
  qualitative if cells are as thin as expected.
- **T4 Abstention/mapping.** Practice-side: P(participant IDK | committed answer) by
  answer_form (Fisher + clustered LPM). Participant-level: mapping exposure → post-test IDK
  share and → attempted-only accuracy (decomposition mirroring the dose pass). Within-person:
  post-test category IDK share on category outsourcing dose (FE + permutation).
- **T5 Prompt quality.** Prompt length, verbatim-paste rate (fuzzy match ≥25-char shingle of
  the item's questionText), asked-for-reasoning flag, bare-answer-demand flag, n_turns,
  n_regen, Δ. If explanation-askers are as rare as the content-coding README suggests,
  report counts and skip regressions (stated, not forced).
- **T6 Cognitive load.** `GL_ave/EL_ave/IL_ave/tlx ~ fo_share + covariates` (4 models,
  flagged as a family); blind-copy → GL; a Baron–Kenny-style decomposition of
  dose→GL→acc reported as *suggestive only* (single wave, n=66, no causal ordering).
- **T7 Moderation.** `acc ~ fo_share×minivlat_c + aiuse_c` and `acc ~ fo_share×aiuse_c +
  minivlat_c`, interactions scaled per SD of the moderator; explicit statement that n=66
  cannot resolve interactions (MDES reported) — hypothesis-generating only.

## Self-selection, multiplicity, robustness

All exposures (adoption, discordance, mapping failure, prompt style) are self-chosen;
the dominant confound direction (weaker/less-motivated participants both behave "worse" and
score lower) pushes estimates toward harm, so negative associations are upper bounds in
magnitude and robust nulls are the more informative outcome. No p is adjusted and none is
confirmatory: estimation-first triangulation, conclusions from sign-consistency and CIs
across strands, every number reported regardless of significance. Standards: CRVE(pid) for
all item-level models; permutation inference for the within-person tests; LOO influence on
any participant-level result with p<.10; fractional-logit check where a headline pp estimate
comes from an LPM; detectable-effect floors restated (|ρ|≈.34 at n=66, larger for
subgroups); any result carried by <10 participants flagged. Contingencies: analyses whose
cells are too thin are reported as counts, not forced through models.
