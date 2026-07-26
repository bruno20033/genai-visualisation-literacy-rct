# Findings summary — answer-level adoption analysis (2026-07-20)

Exploratory, post-hoc, associational; not pre-registered (post-commencement — author
sign-off required before thesis use). No p is adjusted and none is confirmatory;
verdicts rest on sign-consistency, magnitudes, and intervals. Self-selection pushes
"harm"-signed estimates toward harm, so nulls here are the more informative outcomes.
Resolution: |rho|>=.34 detectable at n=66; behaviour-share regressions have full-range
MDES of roughly 30-60 pp (CI widths in the log) — only large effects were detectable.

## Phase 0 (enabling result, itself a finding)
376 engaged cells, all coded blind to key/submission/correctness. Regex draft
auto-accepted 36; a blind re-read of ALL 36 agreed 36/36 (100%). Manual confidence:
362 high / 13 med / 1 low (3.7% non-high). QA: CONCEPT_SUPPORT -> no_answer 6/6;
FULL_OUTSOURCING committed-answer rate 279/351.
**The assistant rarely answered in the item's answer space:** only 19.1% of engaged
cells got a clean option letter; 76.6% got a descriptive answer (143 trivially
mappable, 80 requiring genuine translation, 65 matching NO listed option — the last
concentrated on the two eval items, where the assistant's spontaneous answer
"overplotting/clutter" is not among the options and its committed-answer accuracy
collapses to 58%/44% vs 92-100% elsewhere; overall committed accuracy 93.9%).
Caveat: single automated coder (me); the coder had incidental knowledge of the answer
key from pipeline QA earlier in the session — extraction rules were content-mechanical
and every cell carries a quoted excerpt, but a human spot-check is recommended before
any thesis use (evidence files + audit_cells.csv make this fast).

## T1 Adoption & discordance — SUPPORTED (descriptively strong)
Adoption 90.2% [86.9, 93.5] of 295 committed cells; discordance 9.8%.
Discordance is a MAPPING phenomenon, not disagreement: adoption is 94.4% on clean
letters and 97.9% on trivially-mappable descriptions but 72.5% on
nontrivial descriptions (-21.9 pp vs clean [-32.7, -11.2], p=.0001 cluster-robust;
Fisher p<.0001). 2x2x2: passive success 252 cells; "threw away a correct answer"
25 cells / 22 participants (21 then chose a wrong option, 4 IDK — i.e. mostly failed
translation of a correct descriptive answer, the P61-style letter-mapping failure);
inherited error 14; rescue 4 (of 18 wrong answers received, 78% were adopted; only 1
override ended correct). Verification-only cells: 16/16 endorsed answers adopted
(tautology caveat: the endorsed option usually WAS the participant's own candidate).

## T2 Behaviour -> learning — FAIL TO SUPPORT (informative null battery)
Nothing about HOW participants used the answers predicts post-test accuracy over and
above HOW MUCH they outsourced: adoption rate +12.8 pp [-28.6, +54.2] p=.54; mapping-
failure exposure -2.3 [-25.9, +21.4] p=.85; blind-copy(<5s) -1.3 [-27.3, +24.7] p=.92
(<10s: -9.7 [-29.1, +9.7] p=.33); all Freedman-Lane permutation p's agree; fractional
logit agrees. Within-person FE: adoption share -2.4 pp p=.86 (perm .81); mapping
failure +1.0 p=.89 (perm .84). In every "+fo_share" model the DOSE coefficient stays
at -14 to -17 pp — the dose gradient is not explained away by answer handling. With
these CI widths only ~40+ pp effects were detectable, so moderate effects are not
ruled out; but the consistent near-zero point estimates across five operationalisations
argue against answer-handling style as a major learning channel at this n.

## T3 LLM-error propagation — TOO THIN TO SUPPORT (counts + one case)
18 wrong committed answers (14 participants), concentrated on eval (10) and the
chart-choice ana items (7) — nearly all arose when participants pushed the assistant
to commit to letters/options it could not see (sycophantic confirmations of wrong
candidates: P19, P30, P44; user-steered option picks: P02 "slopes", P13/P20/P57
"nothing wrong", P27/P47/P25 "titles missing"; one letter-mislabel of its own correct
content, P13 und_fa_2). 14/18 were adopted (inherited). Within-person FE of category
accuracy on wrong-answer exposure: +1.3 pp [-14.9, +17.5] p=.87 (13 contributors) —
no detectable propagation. Distractor tracing: with 9 exposed participants the eval
option-share tables show no systematic clustering; the single clean qualitative case
is P57 (adopted "nothing wrong" at practice, chose "nothing wrong" at post-test
eval_sa_6). Verdict: error INHERITANCE at practice is real and near-total; onward
propagation to the post-test is not demonstrable at these cell counts.

## T4 Abstention / letter-mapping — SUPPORTED at practice; dose-linked at post-test
Practice block: 19 IDK submissions; 15 sit on mapping-failure cells. IDK rate is
+8.6 pp higher on mapping-failure cells than other engaged cells ([+3.2, +14.1],
p=.002 cluster-robust; Fisher OR 6.6) — the letter-mapping mechanism is visible in
behaviour, not just in the README anecdotes. Post-test: mapping exposure does NOT
predict IDK share (+3.4 pp p=.64) or attempted-only accuracy (-0.1 pp p=.99); but the
within-person link runs through DOSE: categories a participant outsourced more show
+4.5 pp post-test IDK per outsourced practice item [+0.4, +8.7], p=.033, within-person
permutation p=.043 (36 contributors) — the one significant within-person result, and
it survives its permutation test. Reading (hedged): practice abstention tracks the
immediate mapping burden; post-test abstention tracks where outsourcing displaced
learning, not residual mapping difficulty. Self-selection caveat applies (participants
may outsource categories they'd abstain on anyway; person FE do not remove targeting).

## T5 Prompt quality — CANNOT TEST (near-zero variance), descriptives only
Reasoning-request language: 5 cells, 4 participants (regression skipped as
pre-committed); bare-answer demands (regex, conservative): 5 cells / 2 participants;
verbatim question-paste: 48.7% of engaged cells; median prompt 49 chars. n_regen
all-zero and judge_fidelities empty in this arm (judge exists only in Socratic);
n_queries all-zero — dropped, not fabricated. Slower adoption: +2.9 pp per log-unit
[-5.3, +11.2] p=.49 (and the prior pass showed latency gradients are not
outsourcing-specific). Verdict: "quality of use" barely exists in this arm to test —
itself a finding echoing the near-universal bluntness of the prompts.

## T6 Cognitive load — FAIL TO SUPPORT
fo_share -> germane load +0.26 units [-1.33, +1.85] p=.75; extraneous -0.90 p=.29;
intrinsic +0.96 p=.19; blind-copy -> GL -0.79 p=.59. tlx all-NaN in imm.pkl (skipped).
Mediation sketch: adding GL to the dose model leaves the dose coefficient unchanged
(-9.5 -> -10.0 pp); GL's own slope +2.1 pp/unit p=.069. No within-arm evidence that
self-reported load tracks outsourcing or mediates the deficit (arm-LEVEL contrasts in
D15 are a different, randomised comparison and are untouched by this).

## T7 Moderation — UNRESOLVABLE at n=66 (as pre-stated)
fo_share x baseline literacy +5.2 pp per SD [-15.3, +25.7] p=.62; x AI-use -6.0
[-30.2, +18.2] p=.63. MDES ~29 pp per SD. Hypothesis-generating only; no direction
claimed.

## Overall
The answer-level layer shows WHERE the interaction went wrong (descriptive answers
that participants had to translate; near-total adoption; no verification; errors
inherited when the assistant was pushed to commit blind) but does NOT show that these
micro-behaviours explain the learning deficit beyond the outsourcing dose itself.
The one post-test signal that survives its permutation test is dose-linked abstention
concentration (T4). Everything here is associational; the self-selected exposures and
n=66 floors mean nulls bound large effects only, and nothing supports causal language.
