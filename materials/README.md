# Materials — reconstructing the study

## Why a `.qsf` alone is not enough

The usual answer to "how do I share my Qualtrics survey" is: export the `.qsf` and be
done. That is not sufficient here, and it is worth being explicit about why.

The Qualtrics survey in this study is a **thin shell**. It handles consent, the
baseline covariate, randomisation, the questionnaires and the embedded-data plumbing —
but the actual intervention is an externally hosted web application that Qualtrics
loads in an `<iframe>`:

```
https://bruno20033.github.io/thesis-rct/embed-pcp.html?condition=…&arm=…&pid=…
```

That app holds the chart stimuli, the item bank, the chat and search panes, the two
arm system prompts, and the event logging that produces most of the analysis
variables. It in turn calls a Cloudflare Worker that proxies the LLM, the search API
and the fidelity judge.

So a complete reconstruction needs **four** layers, not one:

| Layer | What it is | Where it lives |
|---|---|---|
| 1. Survey definition | Blocks, randomiser, embedded data, display logic, question JS | `qualtrics/*.qsf` |
| 2. Human-readable instrument | What a participant actually saw, in order | `qualtrics/*.pdf` *(to export)* |
| 3. Intervention interface | The iframed app: stimuli, items, prompts, logging | `interface/` |
| 4. Backend | LLM / search / judge proxy | `interface/worker.js` |

Miss layer 3 and you have a survey that renders an empty frame. Miss layer 1 and you
have an app with no randomisation or consent around it.

---

## What is here

### `qualtrics/`

- `delayed_posttest.qsf` — the 72-hour delayed retest, complete.
- **The main survey `.qsf` is missing and only you can produce it.** See
  `qualtrics/README.md` for the export steps.

### `interface/`

A verbatim snapshot of [`bruno20033/thesis-rct`](https://github.com/bruno20033/thesis-rct)
at commit `c1438217`, the state as fielded. Provenance and verification steps are in
`interface/SNAPSHOT.md`.

The upstream repository is still live and still serves GitHub Pages, so it may move
on; this snapshot does not. When describing what participants saw, cite the commit,
not `main`.

Key files inside it:

| File | Role |
|---|---|
| `embed-pcp.html` | The experimental app participants loaded |
| `pcp_items_data.js` | PCP item bank (stems, options, chart references) |
| `pcp_scoring.js` | Answer key (`PCP_KEY`) and abstention options (`PCP_OMIT`) |
| `pcp_consolidate.js` | Builds the consolidated event log written back to Qualtrics |
| `worker.js` | Cloudflare Worker proxying LLM, search and judge calls |
| `charts/` | The 62 chart stimulus images |

### `instruments/`

Copies of the item banks and scoring key, lifted out of the snapshot so they can be
read without digging through the app. These are duplicates — the snapshot copies are
authoritative.

### `prompts/`

- `rct_arm_prompts.md` — the Socratic and Unrestricted system prompts. **This is the
  manipulation.** The difference between these two files is the independent variable.
- `rct_judge_prompts.md` — the LLM-as-judge fidelity rubric.

Model as fielded: `openai/gpt-5.4`, via OpenRouter. Participant-facing chat used the
provider default temperature.

### `ethics/`

- `consent_form.pdf` — CUREC reference `3366042`.

Item 8 of the consent form is what makes this repository possible: participants
agreed to their **anonymised** data being shared via public repositories. It is also
the binding constraint — see `../data/README.md`.

---

## Rebuilding the study from scratch

1. Deploy `interface/` to any static host (it was GitHub Pages). Note the URL.
2. Deploy `interface/worker.js` to Cloudflare Workers and set the API-key secrets it
   expects. Point the interface at the Worker.
3. Import the `.qsf` files into Qualtrics.
4. Update the iframe `src` in the survey's HTML questions to your host from step 1 —
   they currently point at `bruno20033.github.io`.
5. Re-check the embedded-data field names match what `pcp_consolidate.js` writes;
   the analysis reads those names.

Steps 4 and 5 are the ones that silently break. A survey that imports cleanly can
still record nothing if the iframe URL or the embedded-data names are stale.
