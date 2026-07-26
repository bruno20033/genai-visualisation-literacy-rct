# Unrestricted-arm transcript coding — outsourcing vs. own reasoning (2026-07-18)

**Source data:** `RCT_DataLiteracy_DL_BK_July 17, 2026_15.46.csv` (full immediate-wave export, n=208
records), field `vlat_train_responses` (the `pcp_consolidate.js` per-item interaction log for the
aided 8-item PCP practice block). Arm filter: `arm == "unrestricted"` → **66 participants × 8 items
= 528 coded units** (474 user turns). Item question texts and option lists for the
question-reproduction check were taken from `Code/thesis-rct/pcp_items_data.js`.

**Files**
- `unrestricted_outsourcing_codes_2026-07-18.json` — array of 66 objects, each matching the
  requested schema exactly (`participant_id` = PROLIFIC_PID; `items` in the participant's
  presentation order; `overall_confidence`; `summary_note`).
- `unrestricted_outsourcing_codes_2026-07-18.csv` — flat file (one row per participant×item) with
  `plabel` (P01–P66 in CSV row order), item position, code, turn count, rationale.

## Codebook (as specified)
`FULL_OUTSOURCING` / `VERIFICATION_ONLY` / `CONCEPT_SUPPORT` / `NO_INTERACTION`; multi-turn items
coded by strongest evidence, any FULL_OUTSOURCING turn dominates unless a later turn shows explicit
decline-plus-own-reasoning (that rescue case never occurred in this corpus).

## Results

| Code | n | % of 528 | % of 376 engaged |
|---|---|---|---|
| FULL_OUTSOURCING | 351 | 66.5% | **93.4%** |
| VERIFICATION_ONLY | 19 | 3.6% | 5.1% |
| CONCEPT_SUPPORT | 6 | 1.1% | 1.6% |
| NO_INTERACTION | 152 | 28.8% | — |

**Participant profiles (n=66):** 51 pure outsourcers (every engaged item FULL_OUTSOURCING);
9 mixed (outsourcing plus verification and/or concept items — P19, P28, P30, P41, P44, P45, P50,
P53, P66); 1 pure concept-support user (P34: only definitional questions, answered all items
themselves); 5 never messaged the assistant (P33, P35, P40, P59, P65). 60/66 participants
outsourced at least one item.

**Confidence:** high for 60 participants, medium for 5 (P03, P12, P44, P45, P53 — see conventions),
low for 1 (P60, a single ambiguous "can you please help me with this chart" with no follow-up).

## Coding conventions applied (interpretive calls, for audit)
1. **Generic delegation prompts** ("can u help me", "what are your thoughts?", bare "?"/"/",
   "answer") were coded FULL_OUTSOURCING: the practice item is auto-shared with the assistant, so a
   contentless nudge invites the assistant's own solution of the item; no concept is asked and no
   candidate offered. Where a same-participant follow-up made intent explicit ("which one is
   correct?"), that is cited in the rationale.
2. **Candidate-first prompts** were coded VERIFICATION_ONLY even when the item question was also
   reproduced, per the codebook's "no sign of an own candidate" carve-out (e.g. P19 "…Maybe C?",
   P28 "what is wrong… i think the colour legend is not properly labeled", P41's option recital
   with "I think color legend is wrong").
3. **Bare option letters** as the sole prompt ("c", "a" — P44, P53) were read as presenting the
   participant's own tentative pick for reaction → VERIFICATION_ONLY (the assistant treated them
   exactly that way). Flagged medium confidence.
4. **Deictic checks** ("is it right?" ×5, P45) reference an already-formed but unstated selection →
   VERIFICATION_ONLY; the same participant's "what do you think?" prompts (no candidate, no
   referent) were coded FULL_OUTSOURCING.
5. **Post-answer pushback** that only negotiates a valid option letter (P13 "you're wrong. answer
   a b or c", P36 "thats not true", P57 "your answer is not one of the multiple choice answers.
   Maybe there is nothing wrong…?") does NOT trigger the decline-and-reason exception — the
   adjudication stays with the assistant throughout.
6. **Late candidates after an outsourcing opener** (P17, P28-eval_fa_11, P30-eval_fa_11, P57) do
   not rescue the item: the edge rule keeps FULL_OUTSOURCING.

## Side observations relevant to the thesis (not part of the codes)
- **Question-forwarding is literal:** several participants pasted survey UI chrome ("Next question →
  You can change your selection…") or the wrong item's text (P37, P47, P49, P61) — mechanical
  copy-paste of the item into the chat.
- **Answer received ≠ answer adopted:** discordant submissions against the assistant's stated answer
  occurred (P04, P16, P54, and P66 on three items), and several participants submitted "I don't
  know" right after receiving an answer (P08, P20, P25, P38, P39 ×2, P46, P53, P55, P61 ×2) — often
  a **letter-mapping failure** (assistant answered descriptively, e.g. "the 2nd scatterplot", and the
  participant could not map it to an option letter; clearest in P61). This connects to the D15
  abstention side-finding (unaided IDK rate highest in this arm).
- **The one concept-support user (P34)** asked only general definitional questions and then answered
  both "is this a PCP?" items **incorrectly** (submitted No) — concept support without adoption did
  not guarantee accuracy.
- P29 explicitly refused learning content ("i need just the correct answer no explanation");
  P52 is the lone case of answer-first-then-ask-how ("Please explain how I could have determined
  this answer?").

## Cross-validation against the D17 workflow run (same day, earlier session)
An independent 88-agent Workflow classification of the same transcripts (CLAUDE.md **D17**; its
per-item artifacts were scratchpad-only and are unrecoverable) reported: FO **95.5%**, VO 2.9%
(=11), CS 1.6% (=6) of the same 376 engaged items, and is already written into
`sections/results.tex` (exploratory tool-use classification paragraph). Reconciliation:

- **Agreement: 520/528 cells (98.5%).** The concept-support sets are identical (6), and D17's 11
  verification items correspond exactly to this pass's 11 *explicit*-candidate verification items
  (P19, P28, P30 ×5, P41, P50 ×3).
- **All 8 disagreements are the implicit-candidate prompts** (P45's five deictic "is it right?" and
  the three bare option letters of P44/P53): coded VERIFICATION_ONLY here (own pick implied),
  FULL_OUTSOURCING by D17 (no candidate stated in text). Both readings are defensible under the
  codebook's "presents the participant's own tentative answer" wording; the headline moves
  95.5% ↔ 93.4% with that single convention. (Cell-level attribution is inferred from the exact
  count alignment, since D17's per-cell output no longer exists.)
- **The rendered convergence numbers are robust to the convention:** recomputed under this pass's
  codes, self-answered aided accuracy is 67.8% (identical — the NO_INTERACTION sets agree),
  full-outsourcing aided accuracy 76.4% (vs 75.8%), median adoption latency on outsourced items
  12.1 s (vs 11.8 s; arm-wide MC4 11.7 s). Bonus sharpening: VERIFICATION_ONLY items score 68.4%
  (n=19) — at the self-answered level, not the copied level, consistent with verification being
  genuine own-reasoning use.
- This full-corpus dual-coding is a stronger reliability statement than D17's 22-participant
  κ=1.00 subsample — and it locates the one convention boundary that κ could not see.
- **Author decision needed** (flagged in a comment above the results.tex paragraph; rendered text
  untouched): keep 95.5%, adopt the stricter-verification 93.4%, or cite the range. The substantive
  claim ("genuine scaffolded use was nearly absent") holds under every variant.

## Caveats
- **Post-hoc, non-pre-registered** analysis of collected data (recruitment launched 2026-07-16, D13):
  if used in the thesis it must be labelled exploratory and needs author sign-off, per the
  post-commencement rule in CLAUDE.md.
- **Single-coder (LLM) coding.** Before use as primary evidence, a human second coder should
  double-code a random subsample (e.g. 15–20 participants) and report inter-rater agreement
  (Cohen's κ); the per-item rationales quote the operative prompt phrase to make that audit fast.
- The 3 non-consent/unfinished exclusions of the D15 analysis set are irrelevant here: all 66
  randomised unrestricted participants had a practice-block log and all were coded.
