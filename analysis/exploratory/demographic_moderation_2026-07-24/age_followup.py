#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Follow-up robustness probes for the one suggestive result (age x Socratic).
EXPLORATORY ONLY. Run after demographic_moderation_analysis.py.
Run:  ~/opt/anaconda3/envs/course/bin/python age_followup.py
"""
import numpy as np, pandas as pd, statsmodels.api as sm, scipy.stats as st

d = pd.read_csv("analysis_dataset.csv")
mm = d[d.matched == 1].dropna(subset=["age", "acc", "minivlat_c", "aiuse_c"]).copy()
mm["age_c10"] = (mm.age - mm.age.mean()) / 10

def fit(sub, quad=False):
    X = pd.DataFrame({"const": 1.0, "soc": sub.soc, "unr": sub.unr, "m": sub.age_c10,
                      "soc_m": sub.soc * sub.age_c10, "unr_m": sub.unr * sub.age_c10,
                      "mv": sub.minivlat_c, "ai": sub.aiuse_c})
    if quad:
        X["m2"] = sub.age_c10 ** 2
        X["soc_m2"] = sub.soc * X.m2
        X["unr_m2"] = sub.unr * X.m2
    return X, sm.OLS(sub.acc.to_numpy(float), X).fit(cov_type="HC3")

X, r = fit(mm); ci = r.conf_int()
print("full (n=%d): S x age %+.1f pp/decade [%.1f, %.1f] p=%.4f | U x age %+.1f [%.1f, %.1f]" % (
    len(mm), r.params.soc_m*100, ci.loc['soc_m',0]*100, ci.loc['soc_m',1]*100, r.pvalues.soc_m,
    r.params.unr_m*100, ci.loc['unr_m',0]*100, ci.loc['unr_m',1]*100))

t = mm[mm.age <= 55]; X2, r2 = fit(t); ci2 = r2.conf_int()
print("age<=55 (n=%d, drops %d): S x age %+.1f [%.1f, %.1f] p=%.4f  <- collapses" % (
    len(t), len(mm)-len(t), r2.params.soc_m*100, ci2.loc['soc_m',0]*100, ci2.loc['soc_m',1]*100, r2.pvalues.soc_m))

mm["age_rank"] = st.rankdata(mm.age)
mm["age_rank"] = (mm.age_rank - mm.age_rank.mean()) / mm.age_rank.std()
Xr = pd.DataFrame({"const": 1.0, "soc": mm.soc, "unr": mm.unr, "m": mm.age_rank,
                   "soc_m": mm.soc*mm.age_rank, "unr_m": mm.unr*mm.age_rank,
                   "mv": mm.minivlat_c, "ai": mm.aiuse_c})
rr = sm.OLS(mm.acc.to_numpy(float), Xr).fit(cov_type="HC3")
print("rank-age (per SD): S x age %+.1f pp p=%.4f  <- collapses" % (rr.params.soc_m*100, rr.pvalues.soc_m))

Xq, rq = fit(mm, quad=True)
Rq = np.zeros((2, Xq.shape[1]))
Rq[0, list(Xq.columns).index("soc_m2")] = 1
Rq[1, list(Xq.columns).index("unr_m2")] = 1
print("quadratic arm x age^2 joint p=%.3f (no curvature evidence)" % float(rq.wald_test(Rq, use_f=True, scalar=True).pvalue))

mm["band"] = pd.cut(mm.age, [24, 31, 41, 64], labels=["25-31", "32-41", "42-63"])
piv = mm.groupby(["band", "arm"], observed=True).acc.agg(["mean", "count"])
piv["mean"] = (piv["mean"]*100).round(1)
print("\nunadjusted accuracy % by arm x age band (pattern rests on the 11-person 42-63 socratic cell):")
print(piv.to_string())

print("\nper-arm covariate-adjusted age slopes (pp/decade):")
for a in ["google", "socratic", "unrestricted"]:
    s = mm[mm.arm == a]
    Xs = pd.DataFrame({"const": 1.0, "m": s.age_c10, "mv": s.minivlat_c, "ai": s.aiuse_c})
    rs = sm.OLS(s.acc.to_numpy(float), Xs).fit(cov_type="HC3")
    cis = rs.conf_int()
    print("  %-12s %+.1f [%.1f, %.1f] p=%.3f" % (a, rs.params.m*100, cis.loc['m',0]*100, cis.loc['m',1]*100, rs.pvalues.m))
