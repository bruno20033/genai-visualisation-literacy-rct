#!/usr/bin/env python
"""
Reliance-discrimination statistic for the Results CONSORT-19 paragraph.
Added 2026-07-26. SELF-VERIFYING: asserts every value that appears in
sections/results.tex. Run it; if it prints ALL PASS, the chapter is consistent.

PROVENANCE
----------
This statistic is DERIVED, 2026-07-26, from the 2x2 cross-tab already produced by
the 2026-07-20 run (analysis.py, seed 2026) and printed in results_log.txt under
"THEME 3 / T1". It is NOT itself an output of that run. The four input counts are
the only new-number dependency:

    results_log.txt:
      passive success (LLM right, adopted):            252 cells
      threw away a correct answer (right, discarded):   25 cells
      inherited the error (LLM wrong, adopted):         14 cells
      rescued (LLM wrong, overridden):                   4 cells
                                                    -------
                                        committed total   295

WHY IT EXISTS
-------------
"Overreliance" is a calibration claim: it requires showing that adoption failed to
track the assistant's correctness. Reporting only "14 of 18 errors adopted" invites
that reading without testing it. This computes the discrimination directly, and the
answer is a hedge -- directionally present, not statistically resolved at 18 cells.
Interpretation belongs in the Discussion; Results reports the numbers.

CORPUS: n=66 Unrestricted arm (same as app:outsourcing-coding). Arm is now n=77;
the 11 newer participants are uncoded. Refresh this together with the appendix.
EXPLORATORY / post-commencement; single automated coder. Author sign-off pending.
"""
from scipy import stats

# --- inputs: the T1 2x2, verbatim from results_log.txt ------------------------
ADOPT_RIGHT, DISC_RIGHT = 252, 25   # assistant's recommendation was correct
ADOPT_WRONG, DISC_WRONG = 14, 4     # assistant's recommendation was incorrect

n_right = ADOPT_RIGHT + DISC_RIGHT
n_wrong = ADOPT_WRONG + DISC_WRONG
n_committed = n_right + n_wrong

p_right = ADOPT_RIGHT / n_right          # adoption | correct
p_wrong = ADOPT_WRONG / n_wrong          # adoption | incorrect
gap_pp = 100 * (p_right - p_wrong)       # discrimination
llm_acc = n_right / n_committed          # assistant's committed accuracy

lo, hi = stats.binomtest(ADOPT_WRONG, n_wrong).proportion_ci(method="wilson")
odds, fisher_p = stats.fisher_exact([[ADOPT_RIGHT, DISC_RIGHT],
                                    [ADOPT_WRONG, DISC_WRONG]])

print(f"committed cells                 : {n_committed}")
print(f"erroneous recommendations       : {n_wrong}  (adopted {ADOPT_WRONG})")
print(f"adoption | assistant CORRECT    : {p_right:.3%}")
print(f"adoption | assistant INCORRECT  : {p_wrong:.3%}")
print(f"discrimination                  : {gap_pp:+.1f} pp")
print(f"Wilson 95% CI on adoption|wrong : [{lo:.1%}, {hi:.1%}]")
print(f"Fisher exact                    : OR={odds:.2f}, p={fisher_p:.3f}")
print(f"assistant committed accuracy    : {llm_acc:.1%}")

# --- assertions: these are the values rendered in the chapter -----------------
CHECKS = [
    ("n committed = 295",              n_committed == 295),
    ("n erroneous = 18",               n_wrong == 18),
    ("adopted erroneous = 14",         ADOPT_WRONG == 14),
    ("overrides = 4",                  DISC_WRONG == 4),
    ("adoption|correct = 91.0%",       round(100 * p_right, 1) == 91.0),
    ("adoption|incorrect = 77.8%",     round(100 * p_wrong, 1) == 77.8),
    ("discrimination = 13.2 pp",       round(gap_pp, 1) == 13.2),
    ("Fisher p = .087",                round(fisher_p, 3) == 0.087),
    ("assistant accuracy = 93.9%",     round(100 * llm_acc, 1) == 93.9),
    ("CI includes correct-rate",       lo <= p_right <= hi),
    ("discrimination not sig at .05",  fisher_p >= 0.05),
]
print()
for label, ok in CHECKS:
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
n_pass = sum(ok for _, ok in CHECKS)
print(f"\n{n_pass}/{len(CHECKS)} " + ("ALL PASS" if n_pass == len(CHECKS) else "*** FAILURES ***"))
