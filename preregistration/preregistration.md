# Pre-registration — GenAI and the acquisition of visualisation-literacy skills

**A three-arm, active-control, post-test-only randomised controlled trial**

> **STATUS: DRAFT — not yet fielded.** This document is **aligned to the live Statistical Analysis Plan** (`sections/SAP_04_07.tex`, implementing decisions D1–D9) and **supersedes the pre‑2026‑07‑04 draft**, which described a now‑abandoned *co‑primary / α = 0.025‑split / wave‑averaged* plan.
> **Registry:** OSF Registries — `[OSF REGISTRATION LINK — created at registration]`.
> **CUREC reference:** `3366042` (approved; approval covers the concealment‑by‑omission + debrief of §5.1).
> **Recruitment window:** 15 July 2026 onward, rolling until N = 200 is reached (no fixed end date) — **not yet launched**.
> **Frozen analysis code + materials:** archived with the registration — `[CODE / OSF STORAGE LINK — TBD]`.
> Bracketed pointers, e.g. *(methods.tex §Randomisation)*, cite the authoritative thesis source. The authoritative analysis plan is `sections/SAP_04_07.tex` (\label{sec:sap}); this section is a faithful human‑readable summary of it.

---

## 1. Research questions

- **RQ1.** How does GenAI use affect the acquisition of visualisation‑literacy skills by knowledge workers?
- **RQ2.** Do the effects of LLM access on skill acquisition differ between lower‑ and higher‑order visualisation‑literacy skills?
- **RQ3.** Is there a trade‑off between the short‑term productivity LLM access provides and the long‑term skill acquisition it may impair?

## 2. Hypotheses

Each hypothesis is stated for **both outcomes** — accuracy (subscript *a*, indexing schema **construction**) and time‑to‑success (subscript *b*, indexing schema **automation**). **Accuracy is the sole primary outcome; success time is a key secondary outcome** (see §6). The three theoretical frameworks converge on one ordinal prediction for **unaided** performance — **Unrestricted < Control ≤ Socratic** — with the ordering inverted during **assisted** practice. *(theory.tex §Hypothesis Development.)*

The strict inequality is a **superiority** claim; the weak inequality (Socratic ≥ Control) is a **non‑inferiority** claim, tested only on accuracy against a pre‑specified margin.

| # | Accuracy (*a*) | Time‑to‑success (*b*) | Confirmatory status |
|---|---|---|---|
| **H1** — Outsourcing impairs acquisition | Unrestricted **<** Control on the immediate unaided post‑test (superiority, directional) | Unrestricted needs **more** time per correct response than Control (immediate) | **H1a = PRIMARY (confirmatory).** H1b = key‑secondary |
| **H2** — Scaffolding is not harmful | Socratic **non‑inferior** to Control within margin **Δ = 8.5 pp**; supporting contrast Socratic **>** Unrestricted | Socratic **faster** than Unrestricted (superiority supporting contrast **only — no NI claim on time**) | **H2a = PRIMARY (confirmatory, non‑inferiority).** H2b = key‑secondary supporting |
| **H3** — Performance and learning dissociate | Unrestricted **superior** to Control **during the assisted block** (crossover vs. the unaided deficit) | Unrestricted **faster** than Control during the assisted block | Converging/supporting only (FDR‑controlled), **not confirmatory** |
| **H4** — Deficit concentrates in higher‑order tasks | Negative arm×Bloom‑order interaction (Unrestricted–Control deficit larger for higher‑order items), immediate wave | Order‑specific version | **H4a = secondary confirmatory (Holm family).** **H4b = exploratory** |
| **H5** — Deficit persists | The H1a deficit is still present at the 72‑h delayed post‑test | The H1b fluency deficit persists at 72 h | **H5a = secondary confirmatory (Holm family).** **H5b = exploratory** |

*(Full theoretical motivation: theory.tex §H1–§H5. H2b was recast to superiority‑only and H4b/H5b tagged exploratory per D1/D4.)*

## 3. Design

Three‑arm, between‑subjects, **active‑control**, **content‑matched post‑test‑only** superiority RCT; **1:1:1** allocation via the **Qualtrics randomisation engine**. Arms:

- **A — Google Search (active control):** replicated web‑search tool; the AI‑overview feature is disabled to avoid capability overlap.
- **B — Socratic LLM (offloading):** GPT‑5.5 via the OpenRouter API, guardrailed to give only conceptual guidance and probing questions, never the answer.
- **C — Unrestricted LLM (outsourcing):** the **same** model and interface, system prompt matched to B in length and tone but with **no constraint** against producing complete solutions — so the arms differ only in the outsourcing affordance.

Two unaided measurement waves per participant (**immediate**; **~72 h delayed**). Outcome scoring is automated against a pre‑registered key and is therefore **blind to arm**. Participants are not blinded to their own tool (interfaces differ visibly) and are not told which tools the other arms receive (to limit Hawthorne effects). *(methods.tex §Research Design, §Experimental Conditions; Figure "Study flow diagram".)*

## 4. Sampling and eligibility

- **Platform:** Prolific; UK/EU residents. **Target N = 200 (66 per arm)**, fixed a priori.
- **Power (a priori).** N = 200 is powered against the **sole primary contrast** — Unrestricted‑vs‑Google accuracy on the immediate unaided post‑test — at one‑sided α = 0.05, covariate‑adjusted (ANCOVA R² ≈ 0.30): **80 % power at d = 0.36 ≈ 7.6 pp**, comfortably below the ≈17 pp comprehension gap of Shen et al. (2026), which is detected with power > 0.99. The **non‑inferiority test (H2a)** is powered ≈ 0.80 against the **8.5 pp** margin. The delayed‑wave persistence contrast (H5a) stays adequately powered under attrition up to 30 %; the Bloom interaction (H4a) is powered only for a large concentration and is reported with its minimum detectable effect. *(methods.tex §Sample size; Appendix `app:power`.)*
- **Inclusion:** age ≥ 25; **current employment in a white‑collar role**; self‑reported English sufficient to read a chart caption and answer options; able to complete on a **desktop/laptop** device.
- **Exclusion / stop:** did not confirm consent, or failed the modified Müller‑Lyer **AI‑agent screen** (Affonso et al. 2026). Excluded participants are compensated per Prolific guidelines.
- **Compensation:** fixed fee **+ a completion‑based bonus (conditional on completing both sessions, NOT on performance)** — see §6 note on incentives.

## 5. Procedure (participant flow)

**Phase 1 —** consent → AI‑agent screen → baseline covariates: **Mini‑VLAT** (Pandey & Rall 2023; 12 items, 25 s/item) and a **behaviourally‑anchored GenAI‑usage frequency item** (never … several times a day). Demographics (gender, age) via the Prolific API.
**Phase 2 —** randomisation → **task‑primer video** (identical across arms except the tool explanation) → **8 aided practice items** with the assigned tool available (no time limit) → **Leppink (2013) differentiated cognitive‑load questionnaire**.
**Phase 3 —** **16 unaided items** (immediate) → **~72 h delay** → **16 parallel‑form unaided items** (delayed) → demographics + **external‑tool‑use disclosure item** + **debrief**.

### 5.1 REGISTERED: concealment of the assessment (incidental‑learning framing)

To instantiate the workplace **by‑product** configuration (learning incidental to doing a task) rather than the education **purpose** configuration (learning as the explicit goal), the assessment nature of the study is **concealed by omission**:

1. The session is presented as a **chart‑reading task**, not a learning‑and‑test study; the Phase‑2 video is a brief **task primer**, not a lesson; the Phase‑2 block is not called a "learning phase".
2. Participants are **not told a scored test follows**. The Phase‑3 unaided blocks are presented as continued task items with the tool withdrawn; the second session is **"part 2 of the task,"** not a retention test. (The *existence* of a second session is disclosed at recruitment, as it must be; only its test‑nature is withheld.)
3. Researcher‑facing terms ("post‑test," "primary outcome," "practice phase") are **analysis labels**, never shown to participants.
4. **Debrief.** An end‑of‑study debrief discloses the assessment purpose and the delayed‑measurement design. This concealment‑by‑omission + debrief procedure is covered by CUREC approval, reference `3366042`.

*Rationale.* Under a levels‑of‑processing account, incidental encoding under deep processing yields learning comparable to intentional encoding (Craik & Lockhart 1972; Hyde & Jenkins 1973); the CLT mechanism under test (outsourcing suppresses germane processing → weaker schema construction) is a property of the processing the task demands, not of the intent to learn.

## 6. Outcomes and measures

**Pre‑specified outcome hierarchy** *(D3 — replaces the earlier co‑primary framing):*

1. **Accuracy — PRIMARY.** Proportion of correct responses on each 16‑item unaided block (0–1).
2. **Success time — KEY SECONDARY.** Per‑item time from item onset to submission of a **correct** answer; items answered incorrectly, answered "I do not know", or left unanswered are **right‑censored** at their recorded response time (censoring is required because correctness is post‑treatment). Analysed and reported with full rigour, but **does not gate the confirmatory decision.**

Aided‑block versions of both index **productivity** (RQ3/H3). **Bloom level** is recorded per item: **lower‑order** = Remember, Understand; **higher‑order** = Analyze, Evaluate. The Apply and Create levels (chart *construction*) are outside the consumption construct and **not administered**. Items are drawn from the **BTPL** bank (4 per level per post‑test; 2 per level for training); multiple‑choice with an explicit **"I do not know"** counted as incorrect. **Covariates:** Mini‑VLAT and the GenAI‑usage item (`AIUse`), both mean‑centred. *(methods.tex §Measurement, §Task Stimuli.)*

> **Note (incentives).** A performance‑contingent bonus would be the more *ecologically valid* instantiation of workplace stakes but is deliberately **not** used: it would give the Unrestricted arm the strongest incentive to covertly re‑consult an LLM on the withdrawn‑tool blocks, inflating that arm on the primary outcome and biasing **against** H1; the forgone motivational gain is small (Cala et al. 2026). Completion‑based pay and the concealed test are mutually reinforcing. **Stakes are the one workplace feature the design does not instantiate** (see §10).

## 7. Analysis plan (summary; authoritative version = `sections/SAP_04_07.tex`)

**Estimand & identification.** **Intent‑to‑treat**: the effect of *assignment*, all randomised participants with outcome data analysed as assigned. Intercurrent events (external‑tool use during training/post‑test, disclosed via the end‑item; minimal engagement) are handled under a **treatment‑policy** strategy. Because H2a is a **non‑inferiority** claim (for which ITT is not conservative), the non‑inferiority conclusion is **additionally required to hold in the per‑protocol population** (CONSORT NI extension; Piaggio et al. 2012).

**Primary outcome — accuracy (linear mixed model, REML).** Both unaided waves, covariate‑adjusted, one fit (SAP Eq. `primary-acc`):

> `Y_iw = β0 + β1·Socratic + β2·Unrestricted + δ·Wave + β4·(Socratic×Wave) + β5·(Unrestricted×Wave) + γ1·MiniVLATᶜ + γ2·AIUseᶜ + u_i + ε_iw`

with **Google the reference** and **Wave a 0/1 dummy (immediate = 0)**, so **every arm coefficient is anchored at the immediate post‑test — the primary estimand** *(D2, replacing the old effect‑coded, wave‑averaged specification).*

- **H1a (superiority):** β2 (immediate Unrestricted–Google) — reject `H0: β2 ≥ 0` if one‑sided *p* < .05.
- **H2a (non‑inferiority):** β1 (immediate Socratic–Google) — declare NI if the **90 % CI lower bound for β1 exceeds −Δ**, Δ = **8.5 pp** (TOST; Schuirmann 1987; Lakens 2017/2018). Must hold in **ITT ∧ per‑protocol**; the 90 % CI is reported whatever the verdict.
- **Supporting contrast:** β1 − β2 > 0 (Socratic superior to Unrestricted).
- **H5a (persistence):** adjudicated by the **delayed‑wave simple effect β2 + β5** — reject `H0: β2 + β5 ≥ 0` if one‑sided *p* < .05. The interaction **β5** is the **decay estimate**, reported with its CI, **not** itself the persistence test *(D9 Refinement 1).*

**Key‑secondary outcome — success time (Cox PH).** Wave‑stratified, **with arm×wave interaction terms**, participant‑clustered robust SEs (SAP Eq. `primary-st`); event = correct submission; incorrect/"I don't know"/unanswered censored at recorded time (no administrative cap; extreme values are handled by the speeder-exclusion sensitivity check, R8). θ2 = immediate Unrestricted–Google log‑HR (**H1b**); θ1 − θ2 = Socratic‑faster‑than‑Unrestricted supporting contrast (**H2b**); delayed combinations θ1+θ3, θ2+θ4 = **exploratory H5b** (CIs only). **No non‑inferiority claim on the time scale** *(D1/D9 Refinement 2).*

**Hypothesis testing & multiplicity.** All confirmatory tests are **one‑sided at α = 0.05**; 95 % CIs accompany every estimate.

- **Primary family (accuracy only) — fixed‑sequence gatekeeper** *(D3/D8, replacing the old two‑family α = 0.025 split and flat Holm):* **(1) H1a → (2) H2a → (3) supporting contrast**, each tested at **full α**, stopping at the first non‑rejection. Strong FWER control without taxing the primary contrast (Maurer/Bauer 1995; Dmitrienko 2013). If H1a fails, H2a is not formally tested (accepted structural cost).
- **Secondary confirmatory family = {H4a, H5a}** — Holm step‑down, one‑sided, familywise α = 0.05.
- **Key‑secondary success‑time contrasts** — a separate Holm family, **supporting evidence only**, never a substitute for the primary conclusion.
- **Productivity (H3a/H3b)** — Benjamini–Hochberg **FDR**, converging non‑confirmatory indicators.

**Secondary I — Bloom concentration (H4a).** Item‑level logistic mixed model with crossed participant/item random intercepts (SAP Eq. `bloom`); focal directional quantity = arm×order interaction **β5** for the Unrestricted–Search contrast (`H0: β5 ≥ 0` vs `β5 < 0` on the log‑odds scale); tested inside the secondary Holm family. The four‑level trend and the **lower‑order sparing equivalence test (bound = 6.25 pp)** are exploratory.

**Secondary II — productivity (H3).** Aided block: OLS with HC3 SEs (accuracy) + Cox restricted to the training block (time); β2 / θ2 evaluate H3 (`H0: ≤ 0` vs `> 0`: tool access raises assisted performance); FDR‑controlled; doubles as the affordance manipulation check.

**Compliance / contamination.** Per‑protocol estimate (excluding participants who disclosed external LLM/AI‑overview use during training) — **the pre‑specified NI co‑analysis**; complier‑average causal effect via 2SLS with assignment as the instrument; compliance rates reported per arm.

**Missing data & attrition.** Attrition is expected mainly at 72 h; the LMM uses all available data and is valid under **MAR**. Sensitivity: **MICE, m = 50** (Rubin's rules) and **Lee (2009) worst‑case bounds** on the delayed contrast. Unanswered items are scored incorrect (accuracy) / censored (time).

**Manipulation & implementation checks** (interpretation only — **never trigger participant exclusion**): differentiated **cognitive‑load** subscales (germane load predicted lowest in Unrestricted; Jonckheere–Terpstra against the ordered alternative); engagement logs; **answer‑adoption latency** (direct‑adoption rate = share of aided items with latency < `[ADOPTION-THRESHOLD]` s); **Socratic fidelity** (double‑code a random `[SAMPLE]%` of assistant turns; Cohen's κ ≥ 0.80). KR‑20 of each 16‑item block reported descriptively.

**Robustness.** Randomisation inference (10,000 permutations of arm labels), fractional‑logit and item‑level logistic re‑fits, per‑wave Lin (2013) estimator, log‑normal AFT fallback — per SAP Appendix `app:robustness`.

**Software.** Python `3.11`, pinned environment, fixed seed; `statsmodels`, `lifelines`, `scipy`/`numpy`, `pingouin`. **Analysis code is written against this pre‑registration before unblinding of outcome data** and archived with the registration.

**Exploratory (no error‑rate claim):** arm×Mini‑VLAT moderation of the immediate accuracy deficit; H4b and H5b (success‑time moderation and persistence); four‑level Bloom trend; per‑protocol / CACE; lower‑order equivalence.

## 8. Confirmatory architecture (at a glance)

- **Primary:** accuracy, **immediate** wave — Unrestricted‑vs‑Google **superiority** (H1a); Socratic‑vs‑Google **non‑inferiority** within Δ = 8.5 pp (H2a); supporting Socratic‑vs‑Unrestricted. **Fixed‑sequence gatekeeper at full α = 0.05.**
- **Key secondary:** success time (all superiority/supporting contrasts; **no NI claim**).
- **Secondary confirmatory:** Bloom concentration on accuracy, immediate (H4a); accuracy persistence = delayed‑wave simple effect (H5a). **{H4a, H5a} = Holm family, one‑sided α = 0.05.**
- **Exploratory:** success‑time Bloom moderation (H4b) and persistence (H5b), aided‑block productivity (H3), four‑level Bloom trend, complier/per‑protocol effects, arm×Mini‑VLAT moderation, lower‑order equivalence.

## 9. REGISTERED: construct‑validity scope condition

The education/workplace distinction has two separable components — **population** and **learning configuration** (by‑product vs. purpose) — with **stakes** as a third. This design **captures** the population (employed white‑collar knowledge workers); **instantiates** the by‑product configuration via the §5.1 concealment; **argues** task‑content authenticity (visualisation literacy is a core knowledge‑work skill; the parallel‑coordinates plot is a controlled instrument chosen for measurement properties, not a claim of everyday frequency); and **does not instantiate** workplace stakes (§6 note). Inferences that travel are the **mechanism/direction** (theory‑testing generalisation; Mook 1983); effect **magnitude** and spontaneous on‑the‑job occurrence do not, and are bounded by near‑transfer confinement (Barnett & Ceci 2002) and left to future field work.

## 10. REGISTERED: higher‑order floor contingency (no pilot)

No pilot is run. Incidental conditions may depress higher‑order (Analyze/Evaluate) accuracy toward the floor, threatening the H4a test. Pre‑specified management: (i) the task primer still seeds baseline skill (concealment ≠ no instruction); (ii) the **key‑secondary success‑time outcome** and the CI‑over‑significance posture in the Bloom analysis carry the signal where accuracy cells are thin; (iii) if higher‑order accuracy floors, **H4a is reported from point estimates and intervals as a bounded result, not asserted as a null**; (iv) the pre‑registered level‑ordering / difficulty check detects a floor and doubles as a parallel‑form check. Session‑scale learnability evidence (Peng et al. 2022; Srinivas et al. 2025; Firat et al. 2022) is treated as a partial, *intentional‑learning* substitute for a pilot and flagged as such.

## 11. Deviations log

Any change after registration is recorded here with date and rationale. *(none yet)*

---

### Open placeholders to LOCK before filing

| Item | Status |
|---|---|
| CUREC reference number | **LOCKED = `3366042`** ✅ — filled 2026-07-14 across preregistration.md (×2), sections/methods.tex, drafts/OSF_preregistration_2026-07-12.md (§13, §26), and the live OSF draft registration. |
| OSF registration URL + code/materials archive link | created at registration |
| Non‑inferiority margin Δ (accuracy) | **LOCKED = 8.5 pp** ✅ |
| Sample size N | **LOCKED = 200 (66/arm)** ✅ |
| Covariate symbol | **LOCKED = `AIUse`** ✅ |
| `[SESOI-LO]` lower‑order sparing equivalence bound | **LOCKED = 6.25 pp** ✅ (exploratory test) |
| Response‑time censoring cap | **LOCKED = none** ✅ — no administrative cap; extreme values handled by the speeder‑exclusion sensitivity check (R8) |
| `[ADOPTION-THRESHOLD]` direct‑adoption latency (s) | **OPEN** (default 5 s pending pilot Δ distribution per D11) |
| Socratic‑arm model temperature; Python version | **LOCKED = 0.1 (temperature); Python 3.11** ✅ |
| Manipulation‑check double‑coding `[SAMPLE]%` (draft: 20 %) | **OPEN** |
| Bonus amount; recruitment window dates | **LOCKED** ✅ — £6/hr + £2 completion bonus; recruitment opens 2026‑07‑15, rolling until N=200 |
| Confirm participant‑facing Qualtrics copy implements §5.1 | **OPEN** |
