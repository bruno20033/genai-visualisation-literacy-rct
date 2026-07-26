# Answer-level adoption analysis — Unrestricted arm (2026-07-20)

Exploratory / post-hoc / associational; NOT pre-registered (recruitment launched
2026-07-16 → post-commencement: author sign-off required before any thesis use).
Question: what did the LLM recommend, what did participants submit, was either
correct, and did any of it predict unaided post-test learning — beyond the
outsourcing dose already analysed in
`~/Downloads/outsourcing_doseresponse_verification_2026-07-20/` (built on, not redone).

## Pipeline (run order)
1. `phase0_build.py` → structure verification (0a), regex DRAFT extraction, blind
   evidence files (`phase0_log.txt`).
2. Manual blind coding by the analyst-LLM: `manual_codes.jsonl` (all 340 group-B
   cells) + `audit_codes.jsonl` (blind re-read of ALL 36 regex-accepted cells;
   36/36 agreement). Blind = no key, no submission, no correctness in evidence.
3. `phase0_merge.py` → `adoption_frame.csv` + QA (`phase0_merge_log.txt`).
4. `analysis.py` (seed 2026, B=10,000 permutations) → `results_log.txt`,
   `results_summary.csv`, `participant_behaviour_frame.csv`,
   `participant_category_adoption_panel.csv`.

## Key outputs
- `adoption_frame.csv` — 376 engaged cells: llm_answer, answer_form
  (clean/descriptive/hedged/no_answer), mapping_difficulty
  (trivial/nontrivial/unmappable), llm_correct, adopted, confidence, audit excerpt.
- `findings_summary.md` — per-theme verdicts. `exploratory_paragraph.tex` — drop-in
  paragraph (NOT wired into the thesis). `plain_english_answer.md`.
- Evidence/audit trail: `evidence_groupB.txt`, `evidence_audit.txt`,
  `draft_cells.csv`, `audit_cells.csv`.

## Headlines
19.1% of engaged cells got a clean option letter; 76.6% descriptive (65 cells
matched NO option — eval items; LLM committed-accuracy 58%/44% there vs 92–100%
elsewhere, 93.9% overall). Adoption 90.2%; discordance concentrates on
hard-to-map descriptive answers (−21.9 pp vs clean letters, p=.0001). Of 18 wrong
recommendations, 14 adopted; 1 successful override. Practice IDK sits on
mapping-failure cells (+8.6 pp, p=.002). NOTHING about answer handling predicts
post-test accuracy beyond fo_share (all null; dose coef stays −14…−17 pp).
Within-person dose→post-test IDK +4.5 pp/item (perm p=.043) is the one surviving
post-test signal.

## Integrity caveats
- Single automated coder (the analyst LLM). The 36-cell audit was blind and the
  extraction rules content-mechanical, but the coder had incidental answer-key
  knowledge from earlier pipeline QA in the same session — a HUMAN spot-check of
  `adoption_frame.csv` against `evidence_groupB.txt` is recommended before thesis
  use (excerpts quote the operative phrase; ~30 min for a 40-cell sample).
- 3.7% of cells coded below high confidence (13 med, 1 low) — flagged in-frame.
- `tlx` all-NaN in imm.pkl; `n_regen`/`n_queries` all-zero; `judge_fidelities`
  empty in this arm (judge = Socratic-only) → dropped, not imputed.
- All exposures self-selected; n=66 resolves only |rho|≥.34 (behaviour-share
  models: full-range MDES ≈30–60 pp). Nothing causal.
