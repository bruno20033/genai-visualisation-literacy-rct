#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Answer-level adoption analyses, Themes 1-7. Exploratory/associational only.
Seed 2026; B=10,000 permutations. Estimates in pp with 95% CI, two-sided p, n, subgroup."""
import json
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats

SEED, B = 2026, 10_000
rng = np.random.default_rng(SEED)
HOME = Path.home()
OUT = HOME / 'Downloads' / 'outsourcing_adoption_analysis_2026-07-20'
FRAMES = HOME / 'Downloads' / 'analysis_frames_immediate'
PRIOR = HOME / 'Downloads' / 'outsourcing_doseresponse_verification_2026-07-20'
ITEMS_JS = (HOME / 'Library' / 'Mobile Documents' / 'com~apple~CloudDocs'
            / 'gymnasium steglitz' / 'B.SC Frankfurt School' / 'Oxford' / 'Thesis'
            / 'Code' / 'thesis-rct' / 'pcp_items_data.js')

af = pd.read_csv(OUT / 'adoption_frame.csv')
imm = pd.read_pickle(FRAMES / 'imm.pkl')
it_un = pd.read_pickle(FRAMES / 'items_unassisted.pkl')
prior = pd.read_csv(PRIOR / 'participant_level_unrestricted.csv')
panel_prior = pd.read_csv(PRIOR / 'participant_category_panel.csv')
txt = ITEMS_JS.read_text()
items = json.loads(txt[txt.index('['): txt.rindex(']') + 1])
OPT = {it['id']: {o['label']: o['text'] for o in it['options']} for it in items}

U = imm[imm.arm == 'unrestricted'].copy()
un = it_un[it_un.arm == 'unrestricted'].copy()
un['cat'] = un.item_id.str.extract(r'pcp_(\w+?)_sa')[0]

results = []


def rep(theme, label, est, lo, hi, p, n, ident):
    results.append(dict(theme=theme, label=label, est_pp=round(est, 2), lo95=round(lo, 2),
                        hi95=round(hi, 2), p=(None if p is None else round(p, 4)),
                        n=n, identified_off=ident))
    ps = 'NA' if p is None else f'{p:.4f}'
    print(f'  {label}: {est:+7.2f} pp [95% CI {lo:+7.2f}, {hi:+7.2f}] p={ps} n={n} | {ident}')


def ols_line(res, term, scale=100.0):
    ci = res.conf_int().loc[term]
    return (res.params[term] * scale, ci[0] * scale, ci[1] * scale, res.pvalues[term])


def crate(df, col, label, theme, ident):
    d = df[df[col].notna()]
    r = smf.ols(f'{col} ~ 1', data=d).fit(cov_type='cluster', cov_kwds={'groups': d.pid})
    rep(theme, label, *ols_line(r, 'Intercept'), n=len(d), ident=ident)


def loo_range(df, formula, term, idcol='pid'):
    est, ps = [], []
    for i in df[idcol]:
        r = smf.ols(formula, data=df[df[idcol] != i]).fit(cov_type='HC3')
        est.append(r.params[term] * 100)
        ps.append(r.pvalues[term])
    return (min(est), max(est), min(ps), max(ps))


def fl_perm(df, ycol, xcol, covs, B=B):
    d = df.dropna(subset=[ycol, xcol] + covs)
    y = d[ycol].to_numpy(float)
    X = np.column_stack([np.ones(len(d)), d[xcol], d[covs[0]], d[covs[1]]])
    Xr = X[:, [0, 2, 3]]
    br = np.linalg.lstsq(Xr, y, rcond=None)[0]
    fit_r, e_r = Xr @ br, y - Xr @ br
    XtXi = np.linalg.inv(X.T @ X)
    A = XtXi @ X.T
    h = np.einsum('ij,ji->i', X, A)

    def t_of(yv):
        b = A @ yv
        u = (yv - X @ b) / (1 - h)
        V = XtXi @ (X * (u ** 2)[:, None]).T @ X @ XtXi
        return b[1] / math.sqrt(V[1, 1])

    t0 = t_of(y)
    hits = sum(abs(t_of(fit_r + e_r[rng.permutation(len(y))])) >= abs(t0) - 1e-12
               for _ in range(B))
    return (1 + hits) / (B + 1)


def fe_within(panel, ycol, xcol, label, theme, scale=100.0, perm=True):
    d = panel.dropna(subset=[ycol, xcol]).copy()
    contrib = int((d.groupby('pid')[xcol].nunique() > 1).sum())
    r = smf.ols(f'{ycol} ~ {xcol} + C(pid) + C(cat)', data=d).fit(
        cov_type='cluster', cov_kwds={'groups': d.pid})
    e = ols_line(r, xcol, scale)
    ptxt = ''
    if perm:
        cats = sorted(d['cat'].unique())
        Y = d.pivot(index='pid', columns='cat', values=ycol).reindex(columns=cats)
        X0 = d.pivot(index='pid', columns='cat', values=xcol).reindex(columns=cats)

        def beta_of(Xm):
            dd = pd.DataFrame({'y': Y.stack(), 'x': Xm.stack()}).dropna().reset_index()
            dd.columns = ['pid', 'cat', 'y', 'x']
            Z = pd.get_dummies(dd['cat'], drop_first=True).astype(float)
            M = pd.concat([dd[['x']], Z], axis=1)
            Mg = M.groupby(dd.pid.to_numpy()).transform('mean')
            yg = dd.groupby('pid')['y'].transform('mean')
            b = np.linalg.lstsq((M - Mg).to_numpy(), (dd.y - yg).to_numpy(), rcond=None)[0]
            return b[0]

        b0 = beta_of(X0)
        assert abs(b0 - r.params[xcol]) < 1e-6, (b0, r.params[xcol])
        hits = 0
        Xv = X0.to_numpy()
        for _ in range(B):
            Xp = Xv.copy()
            for i in range(Xp.shape[0]):
                obs = ~np.isnan(Xp[i])
                if obs.sum() > 1:
                    v = Xp[i, obs]
                    Xp[i, obs] = v[rng.permutation(len(v))]
            if abs(beta_of(pd.DataFrame(Xp, index=X0.index, columns=X0.columns))) >= abs(b0) - 1e-12:
                hits += 1
        ptxt = f'; within-person perm p={(1 + hits) / (B + 1):.4f}'
    rep(theme, label, *e, n=len(d),
        ident=f'{contrib} participants with within-person exposure variation{ptxt}')


print('=' * 78 + '\nPARTICIPANT-LEVEL EXPOSURES\n' + '=' * 78)
af['mapfail'] = af.mapping_difficulty.isin(['nontrivial', 'unmappable'])
af['blind5'] = (af.adopted == 1) & (af.adopt_delta_s < 5)
af['blind10'] = (af.adopted == 1) & (af.adopt_delta_s < 10)
g = af.groupby('pid')
pp = pd.DataFrame(dict(
    n_engaged=g.size(), n_committed=g.llm_committed.sum(),
    adoption_rate=g.adopted.mean(), n_llmwrong=g.apply(lambda x: (x.llm_correct == 0).sum()),
    n_rescue=g.apply(lambda x: ((x.llm_correct == 0) & (x.adopted == 0)).sum()),
    mapfail_share=g.mapfail.mean(),
    blind5_share=g.apply(lambda x: x.blind5.sum() / max(x.llm_committed.sum(), 1)),
    blind10_share=g.apply(lambda x: x.blind10.sum() / max(x.llm_committed.sum(), 1)),
    idk_after_answer=g.apply(lambda x: (x.idk & x.llm_committed).sum()),
    reasoning_any=g.asked_reasoning.any(), bare_any=g.bare_answer_demand.any(),
    paste_share=g.verbatim_paste.mean(), prompt_chars=g.prompt_chars.sum(),
    med_delta_comm=g.apply(lambda x: x.loc[x.llm_committed, 'adopt_delta_s'].median()),
)).reset_index()
plab = af.groupby('pid').plabel.first().reset_index()
P = U.merge(pp, on='pid', how='left').merge(plab, on='pid', how='left').merge(
    prior[['pid', 'fo_share']], on='pid')
P['idk_share'] = P.n_idk / 16
P['acc_att'] = P.n_correct / (16 - P.n_idk)
for c in ['n_engaged', 'n_committed']:
    P[c] = P[c].fillna(0)
print(f'n=66; engaged>=1: {(P.n_engaged>0).sum()}; committed>=2: {(P.n_committed>=2).sum()}; '
      f'llm-wrong>=1: {(P.n_llmwrong>=1).sum()} participants '
      f'({int(P.n_llmwrong.sum())} llm-wrong committed cells)')
print(f'adoption_rate: mean {P.adoption_rate.mean():.3f} SD {P.adoption_rate.std():.3f}; '
      f'mapfail_share: mean {P.mapfail_share.mean():.3f} SD {P.mapfail_share.std():.3f}; '
      f'blind5_share: mean {P.blind5_share.mean():.3f} SD {P.blind5_share.std():.3f}')
za, zb = stats.norm.ppf(.975), stats.norm.ppf(.80)
print(f'Resolution: detectable |rho| ~ {math.tanh((za+zb)/math.sqrt(66-3)):.3f} at n=66 '
      f'(80% power, two-sided .05); subgroup models smaller n -> larger floor')

print('\n' + '=' * 78 + '\nTHEME 1: ADOPTION & DISCORDANCE\n' + '=' * 78)
com = af[af.llm_committed].copy()
crate(com, 'adopted', 'T1 adoption rate P(adopted) overall', 'T1',
      f'{len(com)} committed cells, {com.pid.nunique()} participants (cluster-robust)')
com['disc'] = 1 - com.adopted
crate(com, 'disc', 'T1 discordance rate (=1-adoption)', 'T1', 'same cells')
crate(com, 'llm_correct', 'T1 LLM correctness base rate (committed)', 'T1',
      'committed cells; per-item table in phase0_merge log')
for code, d in com.groupby('code'):
    r = smf.ols('adopted ~ 1', data=d).fit(cov_type='cluster', cov_kwds={'groups': d.pid})
    rep('T1', f'T1 adoption rate | {code}', *ols_line(r, 'Intercept'), n=len(d),
        ident=f'{d.pid.nunique()} participants')
print('\nanswer_form shares of ENGAGED cells (n=376): '
      f'{(af.answer_form.value_counts(normalize=True)*100).round(1).to_dict()}')
print('mapping burden (nontrivial+unmappable descriptive): '
      f'{af.mapfail.mean()*100:.1f}% of engaged cells')

print('\n2x2x2 taxonomy (committed cells):')
tax = com.groupby([com.llm_correct.astype(int), com.adopted.astype(int),
                   com.correct.astype(int)]).size()
tax.index.names = ['llm_correct', 'adopted', 'participant_correct']
print(tax.to_frame('cells'))
lc_na = com[(com.llm_correct == 1) & (com.adopted == 0)]
lw_ad = com[(com.llm_correct == 0) & (com.adopted == 1)]
lw_na = com[(com.llm_correct == 0) & (com.adopted == 0)]
lc_ad = com[(com.llm_correct == 1) & (com.adopted == 1)]
print(f'\npassive success (LLM right, adopted): {len(lc_ad)} cells, {lc_ad.pid.nunique()} participants')
print(f'threw away a correct answer: {len(lc_na)} cells, {lc_na.pid.nunique()} participants '
      f'-> then IDK: {int(lc_na.idk.sum())}, wrong option: {int((~lc_na.idk & (lc_na.correct==0)).sum())}')
print(f'inherited the error (LLM wrong, adopted): {len(lw_ad)} cells, {lw_ad.pid.nunique()} participants')
print(f'rescued (LLM wrong, overridden): {len(lw_na)} cells, {lw_na.pid.nunique()} participants '
      f'-> then correct: {int(lw_na.correct.sum())}, IDK: {int(lw_na.idk.sum())}')

print('\nanswer_form -> non-adoption (committed cells only):')
com['m3'] = np.select([com.answer_form == 'clean_option',
                       com.mapping_difficulty == 'trivial',
                       com.mapping_difficulty == 'nontrivial'],
                      ['clean', 'desc_trivial', 'desc_nontrivial'], default='other')
r = smf.ols('adopted ~ C(m3, Treatment("clean"))', data=com).fit(
    cov_type='cluster', cov_kwds={'groups': com.pid})
for lab, term in [('desc_trivial - clean', 'C(m3, Treatment("clean"))[T.desc_trivial]'),
                  ('desc_nontrivial - clean', 'C(m3, Treatment("clean"))[T.desc_nontrivial]')]:
    rep('T1', f'T1 adoption diff: {lab}', *ols_line(r, term), n=len(com),
        ident='cluster-robust LPM, clean_option reference')
tab = pd.crosstab(com.m3 == 'desc_nontrivial', com.adopted)
odds, pf = stats.fisher_exact(tab)
print(f'  Fisher (nontrivial vs rest x adopted): OR={odds:.2f} p={pf:.4f} (ignores clustering)')
print('  adoption by form:')
print(com.groupby('m3').adopted.agg(['mean', 'count']).round(3))

print('\n' + '=' * 78 + '\nTHEME 2: BEHAVIOUR -> POST-TEST ACCURACY\n' + '=' * 78)
COVS = ['minivlat_c', 'aiuse_c']
specs = [('adoption_rate', 'n_committed>=2', 'T2 adoption rate (0->1)'),
         ('mapfail_share', 'n_engaged>=2', 'T2 mapping-failure exposure (0->1)'),
         ('blind5_share', 'n_committed>=2', 'T2 blind-copy share (<5s, 0->1)'),
         ('blind10_share', 'n_committed>=2', 'T2 blind-copy share (<10s, sens)')]
for xcol, cond, lab in specs:
    d = P.query(cond).dropna(subset=[xcol])
    r1 = smf.ols(f'acc ~ {xcol} + minivlat_c + aiuse_c', data=d).fit(cov_type='HC3')
    rep('T2', f'{lab}, adjusted', *ols_line(r1, xcol), n=len(d), ident=cond)
    r2 = smf.ols(f'acc ~ {xcol} + fo_share + minivlat_c + aiuse_c', data=d).fit(cov_type='HC3')
    rep('T2', f'{lab}, + fo_share (over-and-above dose)', *ols_line(r2, xcol),
        n=len(d), ident=f'fo_share coef {r2.params.fo_share*100:+.1f}pp p={r2.pvalues.fo_share:.3f}')
    if r1.pvalues[xcol] < 0.10:
        lo, hi, pmin, pmax = loo_range(d, f'acc ~ {xcol} + minivlat_c + aiuse_c', xcol)
        print(f'    LOO: est [{lo:+.1f},{hi:+.1f}] pp, p [{pmin:.3f},{pmax:.3f}]')
    pfl = fl_perm(d, 'acc', xcol, COVS)
    print(f'    Freedman-Lane permutation p = {pfl:.4f}')
print(f'\nrescue: only {(P.n_llmwrong>=1).sum()} participants ever received a wrong committed '
      'answer; rescue-rate regression skipped (counts in Theme 3 instead)')

d = P.query('n_engaged>=2').dropna(subset=['mapfail_share'])
gl = smf.glm('acc ~ mapfail_share + minivlat_c + aiuse_c', data=d,
             family=sm.families.Binomial()).fit(cov_type='HC3')
d1, d0 = d.copy(), d.copy()
d1['mapfail_share'], d0['mapfail_share'] = 1.0, 0.0
print(f'  frac-logit check (mapfail): AME full-range {100*(gl.predict(d1)-gl.predict(d0)).mean():+.2f} pp '
      f'(coef p={gl.pvalues.mapfail_share:.3f}) vs LPM above')

print('\nWithin-person (participant x Bloom category; removes stable traits, NOT within-person targeting):')
adopt_pc = af[af.llm_committed].groupby(['pid', 'cat']).adopted.mean().rename('adopt_pc')
mapf_pc = af.groupby(['pid', 'cat']).mapfail.mean().rename('mapfail_pc')
llmw_pc = af.groupby(['pid', 'cat']).apply(lambda x: float((x.llm_correct == 0).any())).rename('llmwrong_pc')
idk_pc = un.groupby(['pid', 'cat']).idk.mean().rename('idk_pc')
pan = (panel_prior.set_index(['pid', 'cat'])
       .join(adopt_pc).join(mapf_pc).join(llmw_pc).join(idk_pc).reset_index())
fe_within(pan, 'acc_pc', 'adopt_pc', 'T2 FE: category adoption share -> category accuracy', 'T2')
fe_within(pan, 'acc_pc', 'mapfail_pc', 'T2 FE: category mapping-failure share -> category accuracy', 'T2')

print('\n' + '=' * 78 + '\nTHEME 3: LLM-ERROR PROPAGATION\n' + '=' * 78)
lw = af[af.llm_correct == 0]
print(f'LLM-wrong committed cells: {len(lw)} across {lw.pid.nunique()} participants; by item:')
print(lw.groupby('item_id').size())
print('\ncase table (practice cell -> that participant\'s category post-test):')
for _, r0 in lw.iterrows():
    sub = un[(un.pid == r0.pid) & (un['cat'] == r0['cat'])]
    wrong = sub[(sub.correct == 0)]
    wtxt = '; '.join(f"{w.item_id.split('_')[-2]}_{w.item_id.split('_')[-1]}:{w.answer}"
                     + ('(IDK)' if w.idk else '') for _, w in wrong.iterrows())
    opt_t = OPT[r0.item_id].get(r0.llm_answer, '?')[:38]
    print(f"  {r0.plabel} {r0.item_id} llm={r0.llm_answer}({opt_t}) "
          f"submitted={r0.answer} adopted={r0.adopted} "
          f"-> cat acc {sub.correct.mean():.2f}, wrong: {wtxt or 'none'}")
fe_within(pan, 'acc_pc', 'llmwrong_pc',
          'T3 FE: received wrong LLM answer in category -> category accuracy', 'T3')
expo_eval = set(lw[lw['cat'] == 'eval'].pid)
ev = un[un['cat'] == 'eval'].copy()
ev['exposed'] = ev.pid.isin(expo_eval)
print(f'\neval post-test option shares, exposed-to-wrong-eval-answer (n={len(expo_eval)}) vs rest:')
for iid, d in ev.groupby('item_id'):
    t = d.groupby('exposed').answer.value_counts(normalize=True).unstack(fill_value=0).round(2)
    print(f'  {iid} (key={d.key.iloc[0]}):')
    print(t.to_string())

print('\n' + '=' * 78 + '\nTHEME 4: ABSTENTION / LETTER-MAPPING\n' + '=' * 78)
prac_idk = af[af.idk]
print(f'practice-block IDK submissions: {len(prac_idk)} cells, {prac_idk.pid.nunique()} participants')
print('  after a COMMITTED llm answer:', int(prac_idk.llm_committed.sum()),
      '| on mapfail cells:', int(prac_idk.mapfail.sum()),
      '| after clean_option:', int((prac_idk.answer_form == "clean_option").sum()),
      '| on no_answer/hedged cells:', int(prac_idk.answer_form.isin(['no_answer', 'hedged_multiple']).sum()))
eng2 = af.copy()
eng2['idk_f'] = eng2.idk.astype(float)
eng2['mapfail_f'] = eng2.mapfail.astype(float)
r = smf.ols('idk_f ~ mapfail_f', data=eng2).fit(cov_type='cluster', cov_kwds={'groups': eng2.pid})
rep('T4', 'T4 practice IDK: mapfail cells vs other engaged cells', *ols_line(r, 'mapfail_f'),
    n=len(eng2), ident='cluster-robust LPM over 376 engaged cells')
tabm = pd.crosstab(eng2.mapfail, eng2.idk)
odds, pf = stats.fisher_exact(tabm)
print(f'  Fisher: OR={odds:.2f} p={pf:.4f} (ignores clustering)')
for ycol, lab in [('idk_share', 'post-test IDK share'), ('acc_att', 'attempted-only accuracy')]:
    d = P.query('n_engaged>=2')
    r1 = smf.ols(f'{ycol} ~ mapfail_share + minivlat_c + aiuse_c', data=d).fit(cov_type='HC3')
    rep('T4', f'T4 mapfail exposure -> {lab}, adjusted', *ols_line(r1, 'mapfail_share'),
        n=len(d), ident='n_engaged>=2')
    if r1.pvalues['mapfail_share'] < 0.10:
        lo, hi, pmin, pmax = loo_range(d, f'{ycol} ~ mapfail_share + minivlat_c + aiuse_c',
                                       'mapfail_share')
        print(f'    LOO: est [{lo:+.1f},{hi:+.1f}] pp, p [{pmin:.3f},{pmax:.3f}]')
fe_within(pan, 'idk_pc', 'fo_pc',
          'T4 FE: category outsourcing dose (per practice item, 0-2) -> category post-test IDK share', 'T4')
fe_within(pan, 'idk_pc', 'mapfail_pc',
          'T4 FE: category mapping-failure share -> category post-test IDK share', 'T4')

print('\n' + '=' * 78 + '\nTHEME 5: PROMPT QUALITY (n_regen all 0, n_queries all 0, '
      'judge_fidelities empty -> dropped)\n' + '=' * 78)
print(f'cells with reasoning-request language: {int(af.asked_reasoning.sum())} '
      f'({af.asked_reasoning.mean()*100:.1f}%), participants ever: {int(P.reasoning_any.sum())}')
print(f'cells with bare-answer-demand language: {int(af.bare_answer_demand.sum())}, '
      f'participants ever: {int(P.bare_any.sum())}')
print(f'verbatim question-paste cells: {int(af.verbatim_paste.sum())} '
      f'({af.verbatim_paste.mean()*100:.1f}%)')
print(f'prompt length per engaged cell: median {af.prompt_chars.median():.0f} chars, '
      f'p90 {af.prompt_chars.quantile(.9):.0f}')
nr = int(P.reasoning_any.sum())
if nr >= 8:
    d = P.query('n_engaged>=2').copy()
    d['reasoning_f'] = d.reasoning_any.astype(float)
    r1 = smf.ols('acc ~ reasoning_f + fo_share + minivlat_c + aiuse_c', data=d).fit(cov_type='HC3')
    rep('T5', 'T5 ever-asked-reasoning vs not (adjusted + fo_share)', *ols_line(r1, 'reasoning_f'),
        n=len(d), ident=f'{int(d.reasoning_f.sum())} reasoning-askers vs rest')
else:
    print(f'  -> only {nr} participants ever asked for reasoning: regression skipped (counts only)')
d = P.dropna(subset=['med_delta_comm']).query('n_committed>=2').copy()
d['log_med'] = np.log(d.med_delta_comm)
r1 = smf.ols('acc ~ log_med + fo_share + minivlat_c + aiuse_c', data=d).fit(cov_type='HC3')
rep('T5', 'T5 slower adoption (per log-unit median Delta, committed cells), + fo_share',
    *ols_line(r1, 'log_med'), n=len(d),
    ident='NB prior pass: latency gradient NOT outsourcing-specific (Google slope >= this)')

print('\n' + '=' * 78 + '\nTHEME 6: COGNITIVE LOAD (4-outcome family; suggestive only)\n' + '=' * 78)
print('  NOTE: tlx is all-NaN in imm.pkl -> skipped (routed around, not fabricated)')
for ycol in ['GL_ave', 'EL_ave', 'IL_ave']:
    d = P.dropna(subset=[ycol])
    r1 = smf.ols(f'{ycol} ~ fo_share + minivlat_c + aiuse_c', data=d).fit(cov_type='HC3')
    rep('T6', f'T6 fo_share -> {ycol} (RAW scale units, not pp)', *ols_line(r1, 'fo_share', 1.0),
        n=len(d), ident=f'outcome SD={d[ycol].std():.2f}')
d = P.query('n_committed>=2').dropna(subset=['GL_ave'])
r1 = smf.ols('GL_ave ~ blind5_share + minivlat_c + aiuse_c', data=d).fit(cov_type='HC3')
rep('T6', 'T6 blind-copy share -> GL_ave (RAW units)', *ols_line(r1, 'blind5_share', 1.0),
    n=len(d), ident='germane load; committed>=2')
r_a = smf.ols('acc ~ fo_share + minivlat_c + aiuse_c', data=P).fit(cov_type='HC3')
r_b = smf.ols('acc ~ fo_share + GL_ave + minivlat_c + aiuse_c', data=P).fit(cov_type='HC3')
print(f'  mediation sketch (Baron-Kenny style, NO causal ordering): fo_share coef '
      f'{r_a.params.fo_share*100:+.1f} pp -> {r_b.params.fo_share*100:+.1f} pp when GL_ave added; '
      f'GL_ave coef {r_b.params.GL_ave*100:+.2f} pp/unit (p={r_b.pvalues.GL_ave:.3f})')

print('\n' + '=' * 78 + '\nTHEME 7: MODERATION (underpowered, hypothesis-generating)\n' + '=' * 78)
for mod in ['minivlat_c', 'aiuse_c']:
    sd = P[mod].std()
    P[f'{mod}_z'] = P[mod] / sd
    other = 'aiuse_c' if mod == 'minivlat_c' else 'minivlat_c'
    r1 = smf.ols(f'acc ~ fo_share*{mod}_z + {other}', data=P).fit(cov_type='HC3')
    term = f'fo_share:{mod}_z'
    rep('T7', f'T7 fo_share x {mod} (pp per full dose per +1 SD moderator)',
        *ols_line(r1, term), n=66, ident=f'moderator SD={sd:.2f}; n=66 cannot resolve interactions')
mdes_int = 2.8 * smf.ols('acc ~ fo_share*minivlat_c_z + aiuse_c', data=P
                         ).fit(cov_type='HC3').bse['fo_share:minivlat_c_z'] * 100
print(f'  MDES for the literacy interaction ~ {mdes_int:.0f} pp per SD (2.8 x SE) -> underpowered as stated')

P.drop(columns=[c for c in P.columns if c.endswith('_z')]).to_csv(
    OUT / 'participant_behaviour_frame.csv', index=False)
pan.to_csv(OUT / 'participant_category_adoption_panel.csv', index=False)
pd.DataFrame(results).to_csv(OUT / 'results_summary.csv', index=False)
print('\nwrote participant_behaviour_frame.csv, participant_category_adoption_panel.csv, '
      'results_summary.csv | seed', SEED, '| B =', B)
