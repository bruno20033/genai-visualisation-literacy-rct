# OSF Preregistration — [Working title, AUTHOR TO CONFIRM: "Does Cognitive Outsourcing to Generative AI Impair Skill Acquisition? A Three-Arm Randomised Controlled Trial of LLM Scaffolding in Visualisation Literacy"]

> Template: **OSF Preregistration** (the 26-question "OSF Prereg" form).
> Source of truth: `sections/theory.tex` (hypotheses), `sections/methods.tex` (design),
> `sections/SAP_04_07.tex` + `sections/SAP_appendix_04_07.tex` (analysis plan, decisions D1–D11),
> `sections/appendix_power.tex` (power). Drafted 2026-07-12, AFTER the SAP audit of the same date.
> All `[⚠ …]` items must be resolved before clicking "Register".

---

## METADATA

### 1. Title
[⚠ AUTHOR] Proposed: *Does Cognitive Outsourcing to Generative AI Impair Skill Acquisition? A Three-Arm Randomised Controlled Trial of LLM Scaffolding in Visualisation Literacy.* (`main.tex` still carries the placeholder `THESIS-TITLE`.)

### 2. Description
Large language models (LLMs) can complete knowledge-work tasks on a learner's behalf. Cognitive Load Theory predicts that such *cognitive outsourcing* raises assisted performance while preventing the schema construction and automation that constitute skill acquisition, whereas a *Socratic* LLM that withholds answers but scaffolds reasoning should leave learning intact. We will conduct a pre-registered, three-arm, parallel-group randomised controlled trial (N = 200; 1:1:1) with an active web-search control, in which employed adults learn to read parallel-coordinates plots (PCPs) during a tool-assisted practice block and are then tested **without any tool** immediately and again ≈72 hours later. The sole primary outcome is accuracy on the immediate unaided post-test; success time (time to a correct answer, right-censored) is a key secondary outcome. The confirmatory architecture is a fixed-sequence gatekeeper at one-sided α = 0.05: (1) Unrestricted-LLM inferiority vs. search (superiority test of harm), (2) Socratic non-inferiority vs. search within a pre-specified 8.5-percentage-point preservation margin (ITT ∧ per-protocol), (3) Socratic superiority over Unrestricted. Secondary confirmatory tests (Bloom-level concentration; 72-h persistence) form a Holm family. The full analysis code is written and simulation-validated against known ground truth before registration.

### 3. Contributors
Bruno Kneffel (Frankfurt School of Finance & Management, in collaboration with the University of Oxford); supervisor: Fabian Stephany [⚠ email/affiliation line to add].

### 4. License
[⚠ AUTHOR] Recommended: CC-By Attribution 4.0 International (OSF default).

### 5. Subject
Social and Behavioral Sciences → Psychology / Educational Psychology; secondary: Human–Computer Interaction.

---

## STUDY INFORMATION

### 6. Hypotheses
Numbering follows the thesis (H1–H5); subscript *a* = accuracy, *b* = time-to-success. Predicted ordinal pattern for **unaided** performance: Unrestricted < Control ≤ Socratic; for **assisted** performance the ordering inverts. Status labels (confirmatory / supporting / exploratory) are binding.

**H1 — Cognitive outsourcing impairs acquisition.**
- **H1a (accuracy; PRIMARY, confirmatory).** On the immediate unaided post-test, the Unrestricted arm achieves a lower proportion correct than the search control. Directional; one-sided.
- **H1b (time-to-success; key secondary, supporting).** On the immediate unaided post-test, the Unrestricted arm requires more time per correct response than the search control (hazard ratio of correct-answer production < 1).

**H2 — Scaffolding is not harmful to learning.**
- **H2a (accuracy; confirmatory, non-inferiority).** On the immediate unaided post-test, the Socratic arm's proportion correct is not lower than the search control's by more than the pre-specified margin **Δ = 8.5 percentage points** (50% preservation of the ≈17-pp reference deficit anchoring H1; Shen et al. 2026). Supporting contrast: the Socratic arm's proportion correct exceeds the Unrestricted arm's.
- **H2b (time-to-success; supporting, superiority only).** The Socratic arm's time per correct response is less than the Unrestricted arm's. No non-inferiority claim is made on the time scale.

**H3 — Performance and learning dissociate (assisted block).**
- **H3a (accuracy; supporting, FDR-controlled).** During the assisted practice block, the Unrestricted arm's accuracy exceeds the control's.
- **H3b (time-to-success; supporting, FDR-controlled).** During the assisted practice block, the Unrestricted arm produces correct answers faster than the control.

**H4 — The deficit concentrates in higher-order tasks.**
- **H4a (accuracy; secondary confirmatory).** The Unrestricted-vs-control accuracy deficit is larger for higher-order (Analyze, Evaluate) than for lower-order (Remember, Understand) items — a negative arm × Bloom-order interaction.
- **H4b (time-to-success; EXPLORATORY).** The analogous time-based moderation, reported as order-specific hazard ratios with confidence intervals, no significance verdict (underpowered by design: 4 items/level).

**H5 — The deficit persists.**
- **H5a (accuracy; secondary confirmatory).** The Unrestricted-vs-control accuracy deficit is still present at the ≈72-hour delayed unaided post-test (delayed-wave simple effect < 0). The wave interaction itself is reported as the decay estimate with CI, not tested as the persistence claim.
- **H5b (time-to-success; EXPLORATORY).** The delayed-wave fluency contrasts, read from arm × wave terms of the success-time model as estimates with CIs, no verdict.

---

## DESIGN PLAN

### 7. Study Type
**Experiment** — a randomised controlled trial: participants are randomly assigned to one of three tool conditions by the survey software.

### 8. Blinding
- Participants cannot be blinded to their **own** tool (interfaces differ visibly) but are **not informed that other conditions exist** (no cross-arm awareness; Hawthorne mitigation).
- Participants are blind to the study's purpose: the session is framed as a chart-reading task; the unaided blocks are presented as continued task items, not as tests (concealment by omission per CUREC protocol; end-of-study debrief discloses the assessment purpose).
- **Outcome scoring is fully automated against a pre-registered answer key** and therefore blind to arm.
- No experimenter interacts with participants (fully online); the analyst runs pre-written, simulation-validated code (see §20), which constrains analyst degrees of freedom.

### 9. Additional blinding
The delayed session is framed as "part 2 of the task", not a retention test. The analysis code (notebook + estimator module) was written and validated on simulated and pipeline-test data only, before any participant outcome data exist.

### 10. Study design
Three-arm, parallel-group, between-subjects RCT with 1:1:1 allocation and an active control:
- **Arm A — Google-Search control:** replicated web-search tool (no AI-overview; LLM sites blocked as far as possible).
- **Arm B — Socratic LLM:** chat assistant constrained to conceptual guidance and probing questions; never reveals answers (judge-enforced).
- **Arm C — Unrestricted LLM:** same model/interface with a default helpful-assistant prompt matched in length and tone to Arm B; may produce complete solutions.

Session 1: consent → AI-agent screen → baseline covariates (Mini-VLAT; GenAI-usage item) → randomisation → tool-specific instructional video → **assisted practice block** (8 PCP items, assigned tool available, untimed) → cognitive-load questionnaire (Leppink) → **immediate unaided post-test** (16 PCP items, no tool; PRIMARY outcome block). Session 2 (≈72 h later): **delayed unaided post-test** (16 parallel-form PCP items, no tool) → demographics & external-tool-use disclosure → debrief.

Within-subject factors: test wave (immediate/delayed) and item Bloom level (Remember, Understand, Analyze, Evaluate; 2 items/level in training, 4/level per post-test), enabling the arm × wave (H5) and arm × order (H4) analyses. Item content is drawn from the same instrument bank across blocks (content-matched, near-transfer outcome); all participants receive the same items in the same order within each block.

### Randomisation (template asks under Design)
Simple randomisation, 1:1:1, executed by the **Qualtrics randomisation engine** at the start of Phase 2 (evenly-present option). No stratification or blocking. Allocation concealment is structural: assignment happens after consent, screening, and baseline measurement, so neither participant nor researcher can influence it.

---

## SAMPLING PLAN

### 11. Existing data
**Registration prior to creation of data.** Recruitment has not begun; no participant outcome data exist.

### 12. Explanation of existing data
The only data touched to date are (a) ~6 author-generated pipeline-test rows on a **superseded** instrument (different outcome construct, no answer keys — unusable for the registered analyses) used to test the export/parsing code, and (b) simulated data used to Monte-Carlo-validate the analysis code (63 checks against known ground truth; archived with the registration). Neither contains information about the registered hypotheses.

### 13. Data collection procedures
Participants are recruited via **Prolific** and routed to a Qualtrics survey (Prolific PID auto-captured). **Inclusion:** age ≥ 25; resident in the UK or EU; currently employed in a white-collar occupation; self-reported English proficiency sufficient for chart captions; desktop/laptop completion. **Exclusion at intake:** declined consent; failed the AI-agent screen (modified Müller-Lyer illusion; Affonso et al. 2026). Two sessions ≈72 h apart (72 h ± 24 h invitation window), total ≈ 1 hour. Compensation: £6 per hour base payment plus a £2 completion-conditional (not performance-conditional) bonus for completing both sessions; performance bonuses are avoided because they raise differential cheating incentives across arms. Recruitment window: 15 July 2026 onward, rolling until N = 200 is reached (no fixed end date). Ethics: approved by CUREC, reference 3366042; informed consent before randomisation.

### 14. Sample size
**N = 200 randomised (≈66 per arm).** Analysed units: 200 participants; ≈32 unaided item responses per participant (≈6,400 item-level observations) for the item-level analyses. Expected delayed-wave sample under up to 30% attrition: ≥140.

### 15. Sample size rationale
An a-priori power analysis (script `power_analysis_v2.py`, archived; full write-up in thesis Appendix `app:power`) fixed N against the **sole primary contrast** (H1a: Unrestricted vs. Google, immediate accuracy), one-sided α = 0.05, covariate adjustment R² ≈ 0.30 (Mini-VLAT + GenAI-usage):
- **H1a:** 80% power for a minimum detectable deficit of **7.6 pp (d = 0.36)** — far below the ≈17-pp comprehension gap reported by Shen et al. (2026), which is detected with power ≈ 1.00.
- **H2a (non-inferiority):** power **≈ 0.87** at a true Socratic–Google difference of zero against Δ = 8.5 pp (90%-CI decision rule; rises to ≈0.98 if Socratic is truly ≈+3 pp).
- **H5a (persistence):** power ≥ 0.78 for a persisting deficit of ≥ 8 pp under 30% attrition.
- **H4a (interaction):** adequately powered only for a large concentration (≈11 pp extra higher-order deficit for 80% under the screening statistic; the confirmatory clustered-GEE estimator is somewhat less efficient) — H4a is therefore secondary and will be reported with its minimum detectable effect.
- **Success time:** minimum detectable HR ≈ 1.26–1.35 at 80% (clustering-adjusted simulation).
Sensitivity sweeps over attrition {10/20/30%}, wave correlation ρ {0.3/0.5/0.7}, and R² {0–0.40} are in the archived outputs. SD assumptions (control accuracy ≈ 0.60, KR-20 ≈ 0.70 → SD ≈ 0.21) are literature/derivation-based and flagged as such; the primary MDES is stated on the d-scale and is SD-agnostic.

### 16. Stopping rule
Fixed-N design: recruit on Prolific until **200 participants complete Session 1 with valid data** (consent passed, agent screen passed, practice + immediate blocks submitted); then close intake. All Session-1 completers are invited to Session 2; Session 2 closes [⚠ e.g. 96 h] after each participant's Session 1. **No interim analyses and no data-dependent stopping.** Participants who drop out are not replaced beyond the fixed intake target.

---

## VARIABLES

### 17. Manipulated variables
**Tool condition** (single between-subjects factor, 3 levels), operative only during the assisted practice block:
1. **Google-Search control:** replicated search tool (Serper API); free querying; AI-overview disabled; LLM providers blocked as far as possible.
2. **Socratic LLM:** GPT-5.5 via OpenRouter, temperature 0.1, embedded chat widget; system prompt (archived in appendix) restricts the model to conceptual guidance and probing questions; a judge model triggers regeneration on answer disclosure (fidelity telemetry logged).
3. **Unrestricted LLM:** same model, API, widget, temperature (0.1); default helpful-assistant system prompt matched to Arm B in length and tone, with no constraint against complete solutions.
All arms receive the same instructional video except tool-specific segments, the same 8 practice items in the same order, and identical test blocks.

### 18. Measured variables
**Primary outcome:** immediate unaided post-test **accuracy** — proportion correct on the 16-item PCP block (0–1); correctness scored automatically against the pre-registered key; "I do not know" (offered on every item) and timeouts score incorrect.
**Key secondary outcome:** **success time** — per item, time from item onset to submission of a **correct** answer; items answered incorrectly / "I do not know" / unanswered are right-censored at their recorded response time. Recorded at both waves and in the practice block.
**Other measured variables:** delayed-wave accuracy (persistence estimand); aided-block accuracy and time (H3); per-item response, response time, Bloom level; tool-interaction logs (chat turns, prompts/responses, judge fidelity + regenerations; search queries + clicks); answer-adoption latency Δ (final assistant message → answer submission; shared wall clock); cognitive load (Leppink et al. 2013: intrinsic 3, extraneous 3, germane 4 items; 0–10); **covariates:** Mini-VLAT (12 items, 25-s/item) and a behaviourally anchored GenAI-usage frequency item ("How often do you use AI chatbots or large language models?", *never* → *several times a day*, scored 0–5); demographics (Prolific: age, gender; survey: education, job field, English L1); end-of-study external-tool-use disclosure; embedded attention check; MAILS (descriptive baseline table ONLY — not a model covariate); KR-20 per 16-item block (descriptive).

### 19. Indices
- **Block accuracy** = mean item correctness per participant × block (16 items unaided; 8 aided).
- **Bloom order** = binary partition: lower (Remember, Understand) vs higher (Analyze, Evaluate); the four-level version is used only in the exploratory trend.
- **Leppink subscale scores** = item means per subscale (IL, EL, GL).
- **Rate correct score (RCS)** = aided-block correct answers ÷ minutes, analysed as log(RCS).
- **Direct-adoption rate** = share of aided items with Δ < 5 s (threshold locked from pilot Δ distribution; default 5 s).
- **Per-protocol set** (for H2a co-analysis) = randomised participants who did **not** disclose external LLM / AI-overview use during training.
- **Complier definition (CACE)** = ≥1 logged interaction with the *assigned* tool during practice (one-sided noncompliance: the control arm has no access to the assigned LLM).

---

## ANALYSIS PLAN

### 20. Statistical models
*(Identical to the thesis SAP, `sections/SAP_04_07.tex`; all code pre-written in `rct_data_literacy_analysis_3.ipynb` + `sap_estimators.py`, Monte-Carlo-validated — see §Other.)*

**Estimand:** intent-to-treat (treatment-policy for intercurrent events); all randomised participants providing outcome data, analysed as randomised.

**Primary (accuracy), eq. (1):** participant-level linear mixed model (REML), participant random intercept u_i:

Y_iw = β0 + β1·Socratic_i + β2·Unrestricted_i + δ·Wave_w + β4·(Socratic×Wave) + β5·(Unrestricted×Wave) + γ1·MiniVLAT^c_i + γ2·AIUse^c_i + u_i + ε_iw

Wave is a 0/1 dummy (immediate = 0), so arm coefficients are the **immediate-wave** effects. Mapping: **β2 → H1a** (H1: β2 < 0); **β1 → H2a** (H0: β1 ≤ −Δ vs H1: β1 > −Δ, Δ = 0.085); **β1−β2 → supporting contrast** (H1: > 0); **β2+β5 → H5a** (delayed simple effect; H1: < 0); β5 = decay estimate, CI only.

**Key secondary (success time), eq. (2):** item-level Cox proportional-hazards model, **stratified by wave** (wave-specific baseline hazards), with arm × wave interaction terms and the two centred covariates; event = correct submission; incorrect/IDK/unanswered right-censored; Efron ties; **participant-clustered robust (Lin–Wei) standard errors, with contrasts formed from the full reconstructed cluster-robust covariance matrix**. Mapping: θ2 → H1b (H1: θ2 < 0); θ1−θ2 → H2b-supporting (H1: > 0); θ1+θ3, θ2+θ4 → H5b (estimates + CIs only). Proportional hazards checked by scaled Schoenfeld residuals (Grambsch–Therneau); pre-specified fallback: log-normal accelerated-failure-time model reporting time ratios.

**Secondary I (Bloom, H4a), eq. (3):** item-level logistic model of correctness on the immediate wave with arm, order (higher = 1), arm × order, and the two covariates. **Confirmatory estimator: participant-clustered logistic GEE (exchangeable working correlation)**; focal term = Unrestricted × higher-order (H1: β5 < 0, log-odds). The crossed-random-effects Bayesian GLMM is reported as corroboration only (its variational posterior SDs are anticonservative — demonstrated in the archived validation), and the interaction is additionally expressed as an average marginal interaction contrast on the probability scale.

**Secondary II (productivity, H3):** aided accuracy, log time-per-item, log RCS by OLS with HC3 errors on arm + covariates; aided success time by the Cox model restricted to the practice block (no wave terms). One-sided tests of the tool arms vs control.

**Compliance/complier analyses (supplementary):** descriptive per-protocol estimate; CACE by Wald/2SLS with random assignment instrumenting assigned-tool engagement (one-sided noncompliance; first stage = treated-arm engagement rate), exclusion + monotonicity stated, compliance rates per arm.

**Robustness (pre-specified, all reported):** (R1) unadjusted difference-in-means + unadjusted Cox; (R2) Lin (2013) fully interacted estimator per wave, HC3; (R3) fractional logit (Papke–Wooldridge QMLE) per wave, average marginal effects; (R4) item-level accuracy model with participant clustering; (R5) randomisation inference — 10,000 permutations of arm labels re-running the full pipeline for the primary accuracy and success-time contrasts; (R6) "I do not know" rescoring (incorrect vs excluded); (R7) participant-level median time-to-correct and log-RCS in the linear framework; (R8) exclusion of speeders (median item RT < 1,000 ms) and attention-check failures, applied symmetrically. Additionally: unstructured-covariance sensitivity fit for eq. (1), reported in place of the compound-symmetric fit if a likelihood-ratio test rejects the equal-variance restriction.

**Manipulation/implementation checks (never trigger outcome-based exclusion):** Leppink subscale arm contrasts (predictions: germane lowest in Unrestricted; extraneous highest in control) + Jonckheere–Terpstra ordered-alternative test where a monotone ordering is pre-specified; engagement summaries; answer-adoption latency (log-Δ mixed model, Unrestricted < Socratic predicted; direct-adoption rate at the 5-s threshold; three-arm parallel including the search-arm analogue); Socratic fidelity (judge-regeneration rate; [20]% double-coded sample for answer disclosure, Cohen's κ ≥ 0.80 adequacy); KR-20 per block; contamination screen of search queries.

**Software:** Python 3.11, pinned environment, fixed seed. statsmodels (MixedLM REML with pre-specified optimiser fallback chain lbfgs→bfgs→powell→cg; GEE; MICE; HC3), lifelines (Cox with cluster-robust covariance; PH test; AFT), scipy/numpy (permutation inference; Jonckheere–Terpstra), statsmodels.stats.multitest (Holm, BH). Analysis code is archived **with this registration** and was validated by Monte Carlo before registration.

### 21. Transformations
Baseline covariates mean-centred. Wave coded 0 = immediate, 1 = delayed. Arm coded as two dummies (Google = reference). GenAI-usage mapped to an ordinal 0–5 score. Bloom levels collapsed to the binary lower/higher partition for the confirmatory H4a test. Response times converted to seconds (floored at 50 ms); no administrative cap (extreme values are handled by the speeder-exclusion sensitivity check, R8). Log transforms: RCS, time-per-item, adoption latency Δ. "I do not know" = incorrect (accuracy) / censored (success time). No other recoding.

### 22. Inference criteria
All confirmatory tests **one-sided at α = 0.05**; two-sided 95% CIs accompany every estimate.
- **Primary family — fixed-sequence gatekeeper** (strong FWER control at 0.05, each step at full α, ordered a priori, testing stops at the first non-rejection; order never rearranged): (1) H1a: reject if one-sided p < .05; (2) H2a: non-inferiority declared iff the lower bound of the two-sided 90% CI for β1 exceeds −8.5 pp **in both the ITT and the per-protocol population** (TOST logic; the 90% CI is reported whatever the verdict); (3) supporting contrast: reject if one-sided p < .05. Quantities beyond a closed gate are reported as estimates with CIs, without confirmatory claims.
- **Secondary confirmatory family {H4a, H5a}:** one-sided Holm at familywise α = 0.05.
- **Key-secondary success-time family {H1b, H2b-supporting}:** one-sided Holm; interpreted as supporting evidence only — never a substitute for the primary conclusion. The Socratic–Google hazard ratio is an estimate with CI (no directional hypothesis).
- **Productivity indicators (H3):** Benjamini–Hochberg FDR at q = 0.05; converging indicators, not confirmatory claims.
- Everything else: estimates + CIs, no error-rate claim. No claim will be promoted across tiers after seeing data.

### 23. Data exclusion
- **Pre-randomisation screening (not exclusions from analysis):** declined consent; failed AI-agent check; duplicate Prolific IDs (first complete record kept).
- **Analysis set (ITT):** all randomised participants with ≥1 immediate-wave item. **No outcome-based or compliance-based exclusions from the primary analysis.**
- **Data-quality sensitivity only (R8):** speeders (median unaided item RT < 1,000 ms) and attention-check failures excluded symmetrically; reported alongside, never replacing, the primary result.
- **Per-protocol population (H2a co-analysis + descriptive PP):** excludes participants disclosing external LLM / AI-overview use during training (end-of-study item).
- Item-level: records with neither answer nor response time (block not administered) are dropped as non-administered.

### 24. Missing data
Attrition is expected mainly at the 72-h wave; the primary contrasts are same-session and essentially complete-data by design. (a) The primary mixed model uses all available observations and is valid under missing-at-random given the modelled variables. (b) Differential attrition: wave-2 return rates by arm; logit of return on arm; baseline-covariate × arm dropout screen. (c) **Sensitivity:** multiple imputation by chained equations, m = 50, imputation model containing arm, both baseline covariates, and wave-1 outcomes, Rubin-pooled. [⚠ AUTHOR before freezing: the archived validation found this MICE configuration biased toward zero under MAR (−0.060 vs −0.080 truth) while the primary mixed model was unbiased; either reconfigure (e.g., impute within arm / add arm-interaction terms) or pre-commit to interpreting MMRM-vs-MICE discrepancies in favour of the MMRM with this diagnostic cited.] (d) **Worst-case (MNAR):** Lee (2009) trimming bounds on the delayed-wave contrast (trimming the lower-attrition arm). (e) Within completed blocks: unanswered items scored per the pre-registered key (incorrect / censored) — not imputed.

### 25. Exploratory analysis
Reported as estimates with 95% CIs, no verdicts: H4b; H5b; four-level Bloom trend (arm × linear polynomial; Jonckheere–Terpstra); lower-order *sparing* equivalence test against a 6.25 pp bound (distinct from Δ); arm × Mini-VLAT moderation of the immediate deficit (expertise-reversal probe); direct-adoption-rate × unassisted-performance moderation; CACE and per-protocol estimates (supplementary); productivity–learning frontier plot; wave-extended Bloom model (arm × order × wave).

---

## OTHER

### 26. Other
**Theoretical anchors:** Cognitive Load Theory (Sweller et al.); Script Theory of Guidance (Fischer et al. 2013, minimal-scripting principle); desirable difficulties (Bjork & Bjork 2011); soderstrom2015 performance-vs-learning distinction. Reference effect for the margin: Shen et al. (2026) ≈17-pp comprehension gap.
**Reporting:** CONSORT 2025 + CONSORT-AI, supplementary CONSORT-SPI and TIDieR items.
**Code availability & analytic pre-commitment:** the complete analysis pipeline (`rct_data_literacy_analysis_3.ipynb`, `sap_estimators.py`) and its 63-check Monte-Carlo validation notebook (type-I error, power recovery, CI coverage, gatekeeper FWER, NI operating characteristics, missing-data behaviour) are attached to this registration and were finalised before recruitment. Confirmatory numbers will come from this code with only the data path, answer key, and column mappings changed ([⚠ set `AIUSE_ITEM`, answer key, delayed-wave column at fielding]).
**Deviations policy:** any deviation from this plan will be reported in a labelled "Deviations from pre-registration" section with rationale and, where possible, both per-plan and as-deviated results.
**Ethics:** CUREC approval, reference 3366042; concealment-by-omission design with end-of-study debrief; completion-conditional (not performance-conditional) incentives.
**Related work by the authors:** none on this dataset; the trial is the author's M.Sc. thesis (Frankfurt School of Finance & Management, in collaboration with the University of Oxford).

---

## PRE-SUBMISSION CHECKLIST (internal — delete before registering)
1. [x] Title (draft) + CUREC ref (3366042) + compensation (GBP 6/hr + GBP 2 completion bonus) + search API (Serper) + Socratic/Unrestricted temperature (0.1) + Python version (3.11) + supervisor name (Fabian Stephany) + recruitment window (15 July 2026, rolling until N=200) filled 2026-07-14. [ ] Still open: supervisor email/affiliation line; whether Fabian Stephany is added as a formal OSF contributor (needs his OSF account/email — not yet done, see chat note).
2. [x] RT cap = none, SESOI-LO = 6.25 pp, adoption-latency = 5 s, speeder rule 1,000 ms all locked 2026-07-14. Synced 2026-07-14 into `sections/SAP_04_07.tex` + `sections/SAP_appendix_04_07.tex` (live) and `drafts/sap_main.tex` + `drafts/sap_appendix.tex` (review copies) — `[THRESHOLD]` placeholder cleared everywhere except the unrelated, older answer-adoption-latency `[THRESHOLD]` at `drafts/sap_main.tex` line ~114 (superseded by the D11 rewrite, left as historical draft text).
3. [x] MICE decision (§24) resolved 2026-07-14; SAP text updated to match — ported into `sections/SAP_04_07.tex`'s "Missing data and attrition" paragraph and `drafts/sap_main.tex`'s equivalent paragraph (CLAUDE.md D10).
4. [ ] Notebook config flipped for real run: `SIMULATE_DELAYED=False`, `GENERATE_DUMMY_KEY=False`, `N_MICE=50`, `N_PERMUTATIONS=10000`, `AIUSE_ITEM` set, answer key final.
5. [ ] Adoption-latency logging deployed (`pcp_consolidate.NEW.js` promoted) & verified on one session — else drop the Δ check from §18/§20 before registering.
6. [ ] Missing notebook pieces added (Jonckheere–Terpstra; R7; unstructured-covariance LR sensitivity; CACE SE) so §20 promises = code.
7. [ ] `tab:clt-patterns` created in the thesis (referenced by the manipulation-check logic).
8. [x] methods.tex:151 already reads 0.87 — confirmed fixed (verified 2026-07-13).
9. [ ] Attach: power script + outputs, system prompts, answer key (private component if items must stay concealed), analysis notebook + estimator module + validation notebook, pinned environment file.
