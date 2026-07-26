# Does GenAI use impair the acquisition of visualisation literacy?

Replication package for a pre-registered, three-arm randomised controlled trial on
whether generative-AI assistance during practice impairs the *learning* of
parallel-coordinates-plot literacy — as distinct from performance while the
assistance is available.

> **Status: private working repository.** Intended to be made public at thesis
> submission, at which point it should be archived for a DOI. Nothing here is final
> until then; see [Before going public](#before-going-public).

---

## The study in one paragraph

Knowledge workers (N = 232 randomised, 218 analysed) were randomised 1:1:1 to complete
a chart-interpretation practice block with one of three tools: **Google search**
(active control), a **Socratic LLM** constrained not to give answers, or an
**unrestricted LLM**. They were then tested twice *without any tool*: immediately, and
again after 72 hours. The question is whether the arm that could outsource the task
learned less from doing it.

| | |
|---|---|
| Design | Three-arm parallel RCT, 1:1:1 allocation |
| Primary outcome | Unaided post-test accuracy, **immediate** wave |
| Secondary | Time-to-success, Bloom-level moderation, 72-hour persistence |
| Registration | [osf.io/yw3nm](https://osf.io/yw3nm) — registered before recruitment |
| Ethics | CUREC `3366042` |
| Recruitment | Prolific, from 2026-07-16 |

---

## Repository layout

```
preregistration/   registration, SAP, and the deviations record
materials/         everything needed to re-run the study
  qualtrics/         survey definitions (.qsf)
  interface/         the iframed experimental app, snapshotted as fielded
  instruments/       item banks and scoring key
  prompts/           the arm system prompts — this is the manipulation
  ethics/            consent form
data/
  raw/               identifiable exports — GITIGNORED, never committed
  public/            the same exports, anonymised — what everything runs on
  codebook.md        generated column reference
analysis/
  sap_estimators.py  single source of truth for every estimator
  01_main_analysis.ipynb        the pre-registered analysis
  02_sap_validation_montecarlo.ipynb
  exploratory/       post-hoc analyses, each self-contained
  scripts/           de-identification, PII scanning, codebook, figures
outputs/           generated figures and tables
```

Each directory has its own README with the detail. Start with
[`materials/README.md`](materials/README.md) to understand the apparatus and
[`data/README.md`](data/README.md) to understand what was published and why.

---

## Reproducing the analysis

```bash
conda env create -f analysis/environment.yml
conda activate genai-vizlit
jupyter lab analysis/01_main_analysis.ipynb
```

Runs against `data/public/` — the anonymised exports, which are complete. The raw data
is not needed. Roughly 20 minutes end to end.

---

## Data protection

The raw Qualtrics exports contain IP addresses, geolocation, recipient name/email
fields and Prolific IDs. Consent item 8 permits sharing **anonymised** data only, so
the raw files are gitignored and stay on the author's machine.

What is published is the *complete export with identifiers removed* — all 433 columns,
all 247 rows, three-row Qualtrics header intact — plus the script that produced it, so
the transformation is auditable even though its input is not shared.

Two guards, both runnable:

```bash
python analysis/scripts/deidentify.py --check   # audit the raw files
python analysis/scripts/check_no_pii.py         # scan everything committable
```

`check_no_pii.py` scans every file git would commit for Prolific IDs, emails, IP
addresses and Qualtrics response tokens. **Run it before every commit.** It caught 17
files on the first pass, including 219 Prolific IDs sitting in the main notebook's
saved outputs — the kind of leak that is invisible until someone looks.

Full detail, including the residual risks that were deliberately accepted, in
[`data/README.md`](data/README.md).

---

## Before going public

- [ ] Export `main_survey.qsf` from Qualtrics — **the package is incomplete without
      it** (see [`materials/qualtrics/README.md`](materials/qualtrics/README.md))
- [ ] Export printable PDFs of both surveys
- [ ] Run `check_no_pii.py` one final time
- [ ] Confirm no API keys in the exported `.qsf` question JavaScript
- [ ] Fill in the citation details in `CITATION.cff`
- [ ] Link the thesis PDF (or its DOI) from this README
- [ ] Archive for a DOI (Zenodo, or an OSF component linked to the registration)
- [ ] Add the repository URL to the OSF registration

---

## Related

- **Experiment interface, upstream:** [github.com/bruno20033/thesis-rct](https://github.com/bruno20033/thesis-rct) —
  still live and still serving GitHub Pages. `materials/interface/` pins the fielded
  commit `c1438217`; cite that, not `main`.
- **Registration:** [osf.io/yw3nm](https://osf.io/yw3nm)

## Licence

Code MIT; data, materials and text CC BY 4.0. See [`LICENSE`](LICENSE).

The PCP item bank derives from the BTPL instrument and the Mini-VLAT from its
published source; both remain under their original authors' terms, and the CC BY grant
here does not extend to them.
