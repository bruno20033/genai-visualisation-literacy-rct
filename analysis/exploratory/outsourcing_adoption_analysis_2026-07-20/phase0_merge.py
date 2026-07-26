#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Merge manual+audit codes with the item frame -> adoption_frame.csv + QA.
The coder was blind to key/answer/correct/idk; those merge in HERE."""
import json, re
from pathlib import Path
import numpy as np
import pandas as pd

HOME = Path.home()
OUT = HOME / 'Downloads' / 'outsourcing_adoption_analysis_2026-07-20'
FRAMES = HOME / 'Downloads' / 'analysis_frames_immediate'
CODES_CSV = (HOME / 'Downloads' / 'transcript_coding_unrestricted_2026-07-18'
             / 'unrestricted_outsourcing_codes_2026-07-18.csv')
ITEMS_JS = (HOME / 'Library' / 'Mobile Documents' / 'com~apple~CloudDocs'
            / 'gymnasium steglitz' / 'B.SC Frankfurt School' / 'Oxford' / 'Thesis'
            / 'Code' / 'thesis-rct' / 'pcp_items_data.js')

it_tr = pd.read_pickle(FRAMES / 'items_train.pkl')
codes = pd.read_csv(CODES_CSV)
u = it_tr[it_tr.arm == 'unrestricted'].copy()

def to_turns(x):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return []
    if isinstance(x, (list, tuple, np.ndarray)):
        return [('' if t is None else str(t)) for t in list(x)]
    return [str(x)]

u['p_turns'] = u.prompts.apply(to_turns)
m = u.merge(codes[['participant_id', 'plabel', 'item_id', 'code']],
            left_on=['pid', 'item_id'], right_on=['participant_id', 'item_id'],
            how='left', validate='1:1')
eng = m[m.code != 'NO_INTERACTION'].copy().reset_index(drop=True)

txt = ITEMS_JS.read_text()
items = json.loads(txt[txt.index('['): txt.rindex(']') + 1])
QTXT = {it['id']: it['questionText'] for it in items}

manual = pd.DataFrame([json.loads(l) for l in open(OUT / 'manual_codes.jsonl')])
audit = pd.DataFrame([json.loads(l) for l in open(OUT / 'audit_codes.jsonl')])
draft = pd.read_csv(OUT / 'draft_cells.csv')

# audit vs regex-draft agreement (group A only; audit covered ALL 36 A cells)
ga = draft[draft.group == 'A'].set_index('cell')
au = audit.set_index('cell')
agree = (ga.draft_letter == au.llm).sum()
print(f'AUDIT: regex draft vs blind re-read on all {len(ga)} group-A cells: '
      f'{agree}/{len(ga)} agree ({agree/len(ga):.1%})')
dis = ga[ga.draft_letter != au.llm]
if len(dis):
    print(dis[['plabel', 'item_id', 'draft_letter']].join(au[['llm', 'ex']]))

final = pd.concat([manual, audit]).set_index('cell').sort_index()
assert len(final) == len(eng) == 376, (len(final), len(eng))

af = eng[['pid', 'plabel', 'item_id', 'bloom', 'position', 'code', 'n_turns',
          'answer', 'key', 'correct', 'idk', 'adopt_delta_s']].copy()
af['llm_answer'] = final.llm.values
af['answer_form'] = final.form.values
af['mapping_difficulty'] = final['map'].values
af['extract_confidence'] = final.conf.values
af['excerpt'] = final.ex.values
af['cat'] = af.item_id.str.extract(r'pcp_(\w+?)_fa')[0]
af['llm_committed'] = af.llm_answer.notna()
af['llm_correct'] = np.where(af.llm_committed, (af.llm_answer == af.key).astype(float), np.nan)
af['adopted'] = np.where(af.llm_committed, (af.answer == af.llm_answer).astype(float), np.nan)

# prompt features (Theme 5)
def feats(row):
    turns = row.p_turns
    joined = ' '.join(turns).lower()
    q = QTXT[row.item_id].lower()
    shingles = {q[i:i + 25] for i in range(0, max(1, len(q) - 25), 5)} if len(q) >= 25 else {q}
    paste = any(s in joined for s in shingles)
    reasoning = bool(re.search(r'\bwhy\b|explain|how (?:could|do|can|would) i|walk me|reason|understand', joined))
    bare = bool(re.search(r'just (?:give|the|need)|no explanation|only the answer|answer only', joined))
    return pd.Series(dict(prompt_chars=sum(len(t) for t in turns),
                          verbatim_paste=paste, asked_reasoning=reasoning,
                          bare_answer_demand=bare))

af = pd.concat([af.reset_index(drop=True),
                eng.apply(feats, axis=1).reset_index(drop=True)], axis=1)
af.to_csv(OUT / 'adoption_frame.csv', index=False)

print('\n=== QA: llm-answer availability x content code ===')
print(pd.crosstab(af.code, af.llm_committed, margins=True))
print('\n=== answer_form distribution ===')
print(af.answer_form.value_counts())
print('\nmapping_difficulty (descriptive cells):')
print(af[af.answer_form == 'descriptive'].mapping_difficulty.value_counts())
print('\nextract_confidence:', af.extract_confidence.value_counts().to_dict())
print('\nFlag check: FULL_OUTSOURCING cells WITHOUT a committed llm answer:',
      int(((af.code == 'FULL_OUTSOURCING') & ~af.llm_committed).sum()))
print('CONCEPT_SUPPORT cells coded no_answer:',
      int(((af.code == 'CONCEPT_SUPPORT') & (af.answer_form == 'no_answer')).sum()), 'of',
      int((af.code == 'CONCEPT_SUPPORT').sum()))
print('\nLLM correctness base rate (committed cells):',
      round(af.llm_correct.mean(), 3), 'n =', int(af.llm_committed.sum()))
print('by item:')
print(af[af.llm_committed].groupby('item_id').llm_correct.agg(['mean', 'count']).round(2))
print('\nAdoption rate (committed cells):', round(af.adopted.mean(), 3))
print('\nwrote adoption_frame.csv:', len(af), 'rows')
