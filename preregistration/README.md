# Pre-registration

## Contents

| File | What it is |
|---|---|
| `preregistration.md` | The human-readable pre-registration: research questions, hypotheses, design, exclusions, analysis plan |
| `osf_registration_form.md` | The OSF registration form as submitted, question by question |
| `statistical_analysis_plan.pdf` | The SAP as a standalone document — the version circulated for review |
| `sap_source_main.tex` | SAP source as it appears in the thesis methods chapter |
| `sap_source_appendix.tex` | Extended SAP justification from the thesis appendix |
| `deviations_appendix.tex` | Registered plan vs. what was actually done |

`sap_source_*.tex` are the authoritative statements — the PDF and the markdown are
renderings of them.

## Registration

- **OSF:** https://osf.io/yw3nm
- **Ethics:** CUREC reference `3366042`
- **Recruitment:** launched 2026-07-16; the design was registered before launch.

## The confirmatory architecture in brief

| | |
|---|---|
| Design | Three-arm parallel RCT, 1:1:1 — Google-search control, Socratic LLM, Unrestricted LLM |
| Primary outcome | Accuracy on the unaided post-test. **Sole** primary — success-time is a key secondary |
| Primary estimand | The **immediate** wave |
| Primary contrast | H1a: Unrestricted < Google (superiority, one-sided) |
| Multiplicity | Full α = 0.05, **fixed-sequence gatekeeper**: H1a → H2a → supporting contrast |
| Non-inferiority | H2a: Socratic vs Google, margin **Δ = 8.5 pp**, TOST with a 90% CI, required to hold under **both** ITT and per-protocol |
| Persistence | H5a: the **delayed-wave simple effect**, not the interaction |

Two consequences of the gatekeeper worth stating explicitly, because they are easy to
misread:

1. The margin of 8.5 pp is a **preservation-of-effect** margin — 50% of the 17 pp
   effect H1 anchors on. It was chosen on substantive grounds. Non-inferiority margins
   may not be widened to buy power, and this one was not.
2. The sequence is **strict and linear**. If H1a fails, the H2a non-inferiority claim
   is forfeit *even if its own test passes*. This was a recorded, deliberate choice;
   the alternative (graphical α-recycling, which would let H2a stand alone) was
   considered and not adopted, on the grounds that H1a is the headline predicted
   effect.

## Reading the deviations

`deviations_appendix.tex` is the file to read before treating any result as
confirmatory. Several analyses reported in the thesis are **exploratory and
post-commencement** — notably the outsourcing content coding, the demographic
moderation, the abstention analysis and the answer-adoption work. They are labelled as
such in the results and should not be read as pre-registered.
