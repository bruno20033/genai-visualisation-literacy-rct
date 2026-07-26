#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Phase 0a+0b(draft): structure check, regex DRAFT extraction, blind evidence files.
Blind: evidence blocks contain question+options+prompts+assistant text ONLY (no key,
no participant answer, no correctness, no idk). Audit blocks also hide drafts.
Seed 2026. 2026-07-20."""
import json
import re
from pathlib import Path
import numpy as np
import pandas as pd

SEED = 2026
rng = np.random.default_rng(SEED)
HOME = Path.home()
FRAMES = HOME / 'Downloads' / 'analysis_frames_immediate'
CODES_CSV = (HOME / 'Downloads' / 'transcript_coding_unrestricted_2026-07-18'
             / 'unrestricted_outsourcing_codes_2026-07-18.csv')
ITEMS_JS = (HOME / 'Library' / 'Mobile Documents' / 'com~apple~CloudDocs'
            / 'gymnasium steglitz' / 'B.SC Frankfurt School' / 'Oxford' / 'Thesis'
            / 'Code' / 'thesis-rct' / 'pcp_items_data.js')
OUT = HOME / 'Downloads' / 'outsourcing_adoption_analysis_2026-07-20'

it_tr = pd.read_pickle(FRAMES / 'items_train.pkl')
codes = pd.read_csv(CODES_CSV)

print('=' * 78 + '\n0a. STRUCTURE VERIFICATION\n' + '=' * 78)
u = it_tr[it_tr.arm == 'unrestricted'].copy()
print('unrestricted train rows:', len(u))
for c in ['answer', 'key', 'correct', 'idk', 'prompts', 'responses', 'queries',
          'judge_fidelities', 'n_regen', 'n_turns', 'adopt_delta_s', 'bloom']:
    print(f'  {c}: dtype={u[c].dtype}')
print('answer values:', sorted(u.answer.dropna().astype(str).unique()))
print('key values:', sorted(u.key.dropna().astype(str).unique()))
print('idk values:', u.idk.value_counts(dropna=False).to_dict())
print('n_regen values:', u.n_regen.value_counts(dropna=False).to_dict())
print('n_queries>0 cells:', int((u.n_queries > 0).sum()))
jf = u.judge_fidelities.apply(lambda x: 'empty' if (x is None or isinstance(x, float)
                              or (hasattr(x, '__len__') and len(x) == 0)) else 'nonempty')
print('judge_fidelities:', jf.value_counts().to_dict())
ex = u[u.n_turns > 0].iloc[0]
print('example prompts type:', type(ex.prompts).__name__,
      '| responses type:', type(ex.responses).__name__)

def to_turns(x):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return []
    if isinstance(x, str):
        try:
            v = json.loads(x)
            return [('' if t is None else str(t)) for t in v] if isinstance(v, list) else [x]
        except Exception:
            return [x]
    if isinstance(x, (list, tuple, np.ndarray)):
        return [('' if t is None else str(t)) for t in list(x)]
    return [str(x)]

u['p_turns'] = u.prompts.apply(to_turns)
u['r_turns'] = u.responses.apply(to_turns)
print('example prompt turn:', repr(ex.prompts)[:200])
print('example response turn (first 300 chars):', to_turns(ex.responses)[0][:300])
print('n_turns vs len(r_turns) mismatches:',
      int((u.n_turns != u.r_turns.apply(len)).sum()))

txt = ITEMS_JS.read_text()
arr = txt[txt.index('['): txt.rindex(']') + 1]
items = json.loads(arr)
OPT = {it['id']: {o['label']: o['text'] for o in it['options']} for it in items}
QTXT = {it['id']: it['questionText'] for it in items}
print('item bank parsed:', len(items), 'items;',
      'practice ids ok:', set(u.item_id) <= set(OPT))

m = u.merge(codes[['participant_id', 'plabel', 'item_id', 'code']],
            left_on=['pid', 'item_id'], right_on=['participant_id', 'item_id'],
            how='left', validate='1:1')
assert m.code.notna().all()
eng = m[m.code != 'NO_INTERACTION'].copy().reset_index(drop=True)
print('engaged cells (code != NO_INTERACTION):', len(eng),
      '| n_turns>0 cells:', int((m.n_turns > 0).sum()),
      '| disagreement:', int(((m.code != 'NO_INTERACTION') != (m.n_turns > 0)).sum()))

PATTERNS = [
    ('ans_is', r'(?:correct\s+answer|answer|it)\s*(?:is|:|=|would\s+be|should\s+be|remains)\s*'
               r'(?:option\s*|choice\s*|letter\s*)?[\'"]?\(?([A-Ga-g])\)?[\'"]?(?![A-Za-z0-9])'),
    ('ans_dash', r'\banswer\s*[:\-]\s*\(?([A-Ga-g])\)?(?![A-Za-z0-9])'),
    ('option_x', r'\b(?:option|choice|letter)\s+\(?([A-Ga-g])\)?(?![A-Za-z0-9])'),
    ('x_correct', r'\(?\b([A-Ga-g])\)?\s+is\s+(?:the\s+)?(?:correct|right)'),
    ('go_with', r'\b(?:go\s+with|choose|pick|select)\s+\(?([A-Ga-g])\)?(?![A-Za-z0-9])'),
    ('its_x', r"\bit'?s\s+\(?([A-Ga-g])\)?(?![A-Za-z0-9])"),
    ('line_start', r'^\s*\(?([A-Ga-g])\)?\s*[\.\):,-]\s'),
    ('bare_line', r'^\s*\(?([A-Ga-g])\)?\s*[\.!]?\s*$'),
]
CANT_SEE = re.compile(r"can'?t\s+(?:actually\s+)?see|cannot\s+see|unable\s+to\s+(?:see|view)|"
                      r"need\s+(?:to\s+see|the\s+(?:image|chart|screenshot))|share\s+(?:the|a)\s+"
                      r"(?:chart|image|screenshot)|don'?t\s+have\s+(?:access|the\s+image)", re.I)

def clean(t):
    return re.sub(r'[*_`]+', '', t)

def letter_hits(text):
    hits = []
    for name, pat in PATTERNS:
        for mm in re.finditer(pat, clean(text), re.I | re.M):
            raw = mm.group(1)
            L = raw.upper()
            if raw == 'a':
                tail = clean(text)[mm.end(1):mm.end(1) + 3]
                if re.match(r'\s*[A-Za-z]', tail):
                    continue
            hits.append((name, L, mm.group(0).strip()[:80]))
    return hits

rows = []
for i, r in eng.iterrows():
    labels = set(OPT[r.item_id])
    all_hits = [h for t in r.r_turns for h in letter_hits(t)]
    letters = {h[1] for h in all_hits if h[1] in labels}
    bad_letters = {h[1] for h in all_hits if h[1] not in labels}
    draft = letters.pop() if len(letters) == 1 and not bad_letters else None
    group = 'A' if (draft and r.code == 'FULL_OUTSOURCING') else 'B'
    rows.append(dict(cell=i, pid=r.pid, plabel=r.plabel, item_id=r.item_id, code=r.code,
                     n_turns=int(r.n_turns), draft_letter=draft, group=group,
                     n_letter_hits=len(all_hits),
                     distinct_letters='|'.join(sorted({h[1] for h in all_hits})),
                     last_excerpt=(all_hits[-1][2] if all_hits else ''),
                     cant_see=bool(CANT_SEE.search(' '.join(r.r_turns))),
                     resp_chars=sum(len(t) for t in r.r_turns)))

d = pd.DataFrame(rows)
print()
print('DRAFT groups:', d.group.value_counts().to_dict())
print('by code x group:')
print(pd.crosstab(d.code, d.group))
print("cells with 'cannot see the chart' language:", int(d.cant_see.sum()))
print('response length: median', int(d.resp_chars.median()), 'p90',
      int(d.resp_chars.quantile(.9)), 'max', int(d.resp_chars.max()))
d.to_csv(OUT / 'draft_cells.csv', index=False)

def block(i, r, show_draft):
    lab = OPT[r.item_id]
    opts = ' | '.join(f'{k}) {v}' for k, v in lab.items())
    dr = d.loc[d.cell == i].iloc[0]
    lines = [f'### CELL {i:03d} | {r.plabel} | {r.item_id} | code={r.code} | turns={int(r.n_turns)}',
             f'Q: {QTXT[r.item_id]}', f'OPTS: {opts}']
    if show_draft:
        lines.append(f'REGEX-EVIDENCE: letters={dr.distinct_letters or "none"} '
                     f'hits={dr.n_letter_hits} last_excerpt="{dr.last_excerpt}"')
    for k in range(max(len(r.p_turns), len(r.r_turns))):
        if k < len(r.p_turns):
            p = r.p_turns[k]
            lines.append(f'-- USER T{k+1}: {p[:400]}' + (' [...]' if len(p) > 400 else ''))
        if k < len(r.r_turns):
            t = r.r_turns[k]
            if len(t) > 1600:
                t = t[:900] + f' [...ELIDED {len(t)-1500} chars...] ' + t[-600:]
            lines.append(f'-- ASSISTANT T{k+1}: {t}')
    return '\n'.join(lines) + '\n\n'

gb = d[d.group == 'B']
with open(OUT / 'evidence_groupB.txt', 'w') as f:
    for i in gb.cell:
        f.write(block(i, eng.loc[i], show_draft=True))
ga = d[d.group == 'A']
audit_n = min(60, len(ga))
audit_cells = rng.choice(ga.cell.to_numpy(), size=audit_n, replace=False)
audit_cells.sort()
with open(OUT / 'evidence_audit.txt', 'w') as f:
    for i in audit_cells:
        f.write(block(i, eng.loc[i], show_draft=False))
pd.Series(audit_cells, name='cell').to_csv(OUT / 'audit_cells.csv', index=False)
print()
print(f'wrote evidence_groupB.txt ({len(gb)} cells), evidence_audit.txt '
      f'({audit_n} cells, drafts hidden), draft_cells.csv, audit_cells.csv')
print('groupB KB:', round((OUT / 'evidence_groupB.txt').stat().st_size / 1024),
      '| audit KB:', round((OUT / 'evidence_audit.txt').stat().st_size / 1024))
