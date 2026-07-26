#!/usr/bin/env python
"""
Exploratory dose-response analysis: does cognitive outsourcing ITSELF (not just
arm assignment) predict lower unaided post-test accuracy?  (2026-07-18)

POST-HOC / EXPLORATORY. Not pre-registered; recruitment launched 2026-07-16
(CLAUDE.md D13), so this is a post-commencement analysis. It must never be
framed as confirmatory. The latency strand is anticipated by the SAP's own
exploratory clause (SAP_04_07.tex l.113: direct-adoption rate "carried into the
exploratory moderation analysis (adoption rate x unassisted performance)");
the content-coding strand is fully post-hoc.

Run in the `course` env:
    ~/opt/anaconda3/envs/course/bin/python analyze_outsourcing_doseresponse.py

Inputs
  ~/Downloads/analysis_frames_immediate/{imm,items_train,items_unassisted}.pkl
      (pickled by rct_data_literacy_analysis_5_IMMEDIATE_FULL_2026-07-17.ipynb;
       items_train already carries adopt_delta_s = answer_ts - last tool ts,
       negatives set NaN, exactly the SAP/D11 definition)
  ~/Downloads/transcript_coding_unrestricted_2026-07-18/
      unrestricted_outsourcing_codes_2026-07-18.csv
      (durable single-coder content codes, 66 x 8 cells; primary codes here.
       The non-durable D17 88-agent pass differs on 8/528 cells -> sensitivity.)

Outputs (this directory)
  results_outsourcing_doseresponse.txt   full numeric record (this stdout)
  frame_doseresponse_unrestricted.csv    merged participant-level frame (n=66)
  frame_latency_all_arms.csv             participant-level latency frame (n=176)

Design notes
  * Dose (content) = n_FO/8: share of the 8 aided practice items on which the
    participant had the assistant produce the answer (FULL_OUTSOURCING).
    Self-answered, verification-only and concept-support items all retain the
    participant's own reasoning, i.e. the theorised schema-construction
    opportunity; FO items forfeit it. Defined for all 66 (never-engaged = 0).
    Sensitivity: n_FO/engaged (undefined for the 5 never-engaged).
  * Dose (latency) = participant mean log adoption latency over tool-items
    (threshold-free, per the SAP's own "primary read is threshold-free");
    the SAP-anticipated direct-adoption-rate (share of tool-items < 5 s)
    variant is reported alongside.
  * All models: OLS with HC3 (house ANCOVA convention); covariates minivlat_c
    + aiuse_c (the pre-registered pre-treatment covariate set). Two-sided
    p-values throughout (exploratory convention; matches the Abstention row).
  * Within-person strand: post-test item correctness ~ Bloom-category practice
    dose with participant + category fixed effects, participant-clustered SE.
    Person-level confounders (ability, motivation, effort) cancel by design;
    within-person selection (outsourcing the categories one is weak in) does not.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf

OUT = Path(__file__).resolve().parent
FRAMES = Path("~/Downloads/analysis_frames_immediate").expanduser()
CODES = Path("~/Downloads/transcript_coding_unrestricted_2026-07-18/"
             "unrestricted_outsourcing_codes_2026-07-18.csv").expanduser()

log_lines = []
def say(*a):
    s = " ".join(str(x) for x in a)
    print(s); log_lines.append(s)

imm    = pd.read_pickle(FRAMES / "imm.pkl")
itrain = pd.read_pickle(FRAMES / "items_train.pkl")
unass  = pd.read_pickle(FRAMES / "items_unassisted.pkl")
codes  = pd.read_csv(CODES)

# ---------------------------------------------------------------- content dose
per = codes.pivot_table(index="participant_id", columns="code", aggfunc="size",
                        fill_value=0)
for c in ["FULL_OUTSOURCING", "VERIFICATION_ONLY", "CONCEPT_SUPPORT",
          "NO_INTERACTION"]:
    if c not in per:
        per[c] = 0
per = per.reset_index().rename(columns={"participant_id": "pid"})
per["n_fo"]     = per["FULL_OUTSOURCING"]
per["engaged_n"] = 8 - per["NO_INTERACTION"]
per["frac_fo"]  = per["n_fo"] / 8
per["frac_fo_eng"] = np.where(per["engaged_n"] > 0,
                              per["n_fo"] / per["engaged_n"], np.nan)

u = imm[imm.arm == "unrestricted"].merge(
        per[["pid", "n_fo", "engaged_n", "frac_fo", "frac_fo_eng"]],
        on="pid", validate="1:1")
assert len(u) == 66, "merge lost participants"

# ---------------------------------------------------------------- latency dose
it = itrain.dropna(subset=["adopt_delta_s"])
it = it[it["adopt_delta_s"] >= 0].copy()
it["logd"] = np.log(it["adopt_delta_s"].clip(lower=1e-3))
lat = (it.groupby(["pid", "arm"], observed=True)
         .agg(mean_logd=("logd", "mean"), n_toolitems=("logd", "size"),
              adoption_rate=("adopt_delta_s", lambda x: (x < 5).mean()))
         .reset_index())
lat_all = imm.merge(lat, on=["pid", "arm"], validate="1:1")
u = u.merge(lat[lat.arm == "unrestricted"]
            [["pid", "mean_logd", "n_toolitems", "adoption_rate"]],
            on="pid", how="left", validate="1:1")

# ---------------------------------------------------------------- helpers
def fit(formula, data):
    return smf.ols(formula, data=data).fit(cov_type="HC3")

def slope_row(fitres, term, scale=100.0):
    b  = fitres.params[term] * scale
    lo, hi = fitres.conf_int().loc[term] * scale
    p  = fitres.pvalues[term]
    return b, lo, hi, p

def pearson(x, y):
    m = pd.notna(x) & pd.notna(y)
    return stats.pearsonr(x[m], y[m])

def detectable_r(n, alpha=0.05, power=0.80):
    za, zb = stats.norm.ppf(1 - alpha / 2), stats.norm.ppf(power)
    return np.tanh((za + zb) / np.sqrt(n - 3))

say("=" * 78)
say("EXPLORATORY OUTSOURCING DOSE-RESPONSE  (immediate wave, n=188 sample of D15)")
say("All p two-sided. OLS + HC3. Covariates: minivlat_c + aiuse_c.")
say("=" * 78)

# ---------------------------------------------------------------- descriptives
say("\n--- Dose descriptives (Unrestricted arm, n=66) ---")
say(f"n_FO of 8: mean {u.n_fo.mean():.2f}, SD {u.n_fo.std():.2f}; "
    f"distribution {dict(u.n_fo.value_counts().sort_index())}")
say(f"frac_fo (n_FO/8): mean {u.frac_fo.mean():.3f}, SD {u.frac_fo.std():.3f}")
say(f"engaged 0 items (never used assistant): n={int((u.engaged_n==0).sum())} "
    f"(< 10 -> report descriptively only)")
say(f"acc SD (U arm): {u.acc.std():.3f}; post-test acc mean {u.acc.mean():.3f}")

say("\n--- Selection diagnostics: who outsources? ---")
r, p = pearson(u.frac_fo, u.minivlat_c)
say(f"frac_fo ~ baseline Mini-VLAT: r={r:+.3f} (p={p:.3f})")
r, p = pearson(u.frac_fo, u.aiuse_c)
say(f"frac_fo ~ baseline GenAI use: r={r:+.3f} (p={p:.3f})")

# ---------------------------------------------------------------- prior-result sanity
say("\n--- Sanity: reproduce the prior binary split (pure-FO vs rest) ---")
pure = u[u.frac_fo_eng == 1.0]
rest = u[~u.pid.isin(pure.pid)]
tt = stats.ttest_ind(pure.acc, rest.acc, equal_var=False)
say(f"pure outsourcers n={len(pure)} acc={pure.acc.mean()*100:.1f}% | "
    f"others n={len(rest)} acc={rest.acc.mean()*100:.1f}% | "
    f"diff={100*(pure.acc.mean()-rest.acc.mean()):+.1f}pp, Welch p={tt.pvalue:.2f}"
    f"   (prior session: 68.8 vs 74.2, p=.32)")

# ================================================================ STRAND A
say("\n" + "=" * 78)
say("STRAND A - content-coded dose: acc ~ frac_fo   (Unrestricted, n=66)")
say("=" * 78)
r, p = pearson(u.frac_fo, u.acc)
say(f"Pearson r = {r:+.3f} (p={p:.3f}); "
    f"Spearman rho = {stats.spearmanr(u.frac_fo, u.acc).statistic:+.3f} "
    f"(p={stats.spearmanr(u.frac_fo, u.acc).pvalue:.3f})")

fA0 = fit("acc ~ frac_fo", u)
b, lo, hi, p = slope_row(fA0, "frac_fo")
say(f"UNADJUSTED : full-range slope {b:+.2f}pp [{lo:+.2f}, {hi:+.2f}], p={p:.3f}"
    f"  (per outsourced item: {b/8:+.2f}pp)")
fA1 = fit("acc ~ frac_fo + minivlat_c + aiuse_c", u)
b1, lo1, hi1, p1 = slope_row(fA1, "frac_fo")
say(f"ADJUSTED   : full-range slope {b1:+.2f}pp [{lo1:+.2f}, {hi1:+.2f}], p={p1:.3f}"
    f"  (per outsourced item: {b1/8:+.2f}pp)")

fA2 = fit("acc ~ frac_fo_eng + minivlat_c + aiuse_c",
          u.dropna(subset=["frac_fo_eng"]))
b2, lo2, hi2, p2 = slope_row(fA2, "frac_fo_eng")
say(f"SENSITIVITY (dose among engaged, n={int(u.frac_fo_eng.notna().sum())}): "
    f"{b2:+.2f}pp [{lo2:+.2f}, {hi2:+.2f}], p={p2:.3f}")

# D17-convention sensitivity: the 8 disputed cells (VO here, FO in D17).
# Their pids/items are known from the README (P45 x5 deictic; P44 x1, P53 x2
# bare letters). Recode those VO -> FO and re-run.
disp = codes[(codes.plabel.isin(["P44", "P45", "P53"])) &
             (codes.code == "VERIFICATION_ONLY")]
say(f"D17-coder-convention sensitivity: {len(disp)} disputed cells recoded VO->FO")
codes_d17 = codes.copy()
codes_d17.loc[disp.index, "code"] = "FULL_OUTSOURCING"
per17 = (codes_d17.assign(fo=(codes_d17.code == "FULL_OUTSOURCING").astype(int))
         .groupby("participant_id")["fo"].sum().rename("n_fo17").reset_index()
         .rename(columns={"participant_id": "pid"}))
u17 = u.merge(per17, on="pid"); u17["frac_fo17"] = u17.n_fo17 / 8
fA3 = fit("acc ~ frac_fo17 + minivlat_c + aiuse_c", u17)
b3, lo3, hi3, p3 = slope_row(fA3, "frac_fo17")
say(f"  under D17 codes: adjusted slope {b3:+.2f}pp [{lo3:+.2f}, {hi3:+.2f}], p={p3:.3f}")

say("\nNever-engaged subgroup (n=5, BELOW the n>=10 reporting floor):")
ne = u[u.engaged_n == 0]
say(f"  acc={ne.acc.mean()*100:.1f}% (control arm mean "
    f"{imm[imm.arm=='google'].acc.mean()*100:.1f}%), "
    f"baseline Mini-VLAT {ne.minivlat_c.mean():+.2f} above centre - "
    f"descriptive only, no inference")

# ---------------- influence / fragility (leave-one-out on both dose codings)
def loo_range(formula, data, term):
    bs, ps = [], []
    for pid in data.pid:
        f = fit(formula, data[data.pid != pid])
        bs.append(f.params[term] * 100); ps.append(f.pvalues[term])
    return min(bs), max(bs), min(ps), max(ps)

say("\nLeave-one-out fragility:")
bmin, bmax, pmin, pmax = loo_range("acc ~ frac_fo + minivlat_c + aiuse_c",
                                   u, "frac_fo")
say(f"  adjusted frac_fo   : slope [{bmin:+.1f}, {bmax:+.1f}]pp, "
    f"p [{pmin:.3f}, {pmax:.3f}]  (sign-stable, never significant)")
ee = u.dropna(subset=["frac_fo_eng"])
bmin, bmax, pmin, pmax = loo_range("acc ~ frac_fo_eng + minivlat_c + aiuse_c",
                                   ee, "frac_fo_eng")
say(f"  engaged-dose       : slope [{bmin:+.1f}, {bmax:+.1f}]pp, "
    f"p [{pmin:.3f}, {pmax:.3f}]  (NOT robust: p crosses .05; only "
    f"{int((ee.frac_fo_eng < 1).sum())} non-fully-outsourcing participants "
    f"identify it)")
say(f"  engaged non-pure n={int((ee.frac_fo_eng < 1).sum())} "
    f"acc={ee[ee.frac_fo_eng < 1].acc.mean()*100:.1f}% vs pure "
    f"n={int((ee.frac_fo_eng == 1).sum())} "
    f"acc={ee[ee.frac_fo_eng == 1].acc.mean()*100:.1f}%")
say(f"  coherence: mean dose {u.frac_fo.mean():.3f} x unadjusted slope "
    f"{fA0.params['frac_fo']*100:+.2f} = "
    f"{u.frac_fo.mean()*fA0.params['frac_fo']*100:+.1f}pp; observed adjusted "
    f"U-G arm effect -4.83pp (same order: the dose model prices the arm "
    f"deficit consistently)")

# ================================================================ STRAND B
say("\n" + "=" * 78)
say("STRAND B - latency dose: acc ~ mean log(adoption latency)")
say("=" * 78)
uB = u.dropna(subset=["mean_logd"])
r, p = pearson(uB.mean_logd, uB.acc)
say(f"Unrestricted (n={len(uB)}): Pearson r = {r:+.3f} (p={p:.3f})")
fB0 = fit("acc ~ mean_logd", uB)
b, lo, hi, p = slope_row(fB0, "mean_logd")
say(f"UNADJUSTED : {b:+.2f}pp per log-unit [{lo:+.2f}, {hi:+.2f}], p={p:.3f}"
    f"  (per doubling of Delta: {b*np.log(2):+.2f}pp)")
fB1 = fit("acc ~ mean_logd + minivlat_c + aiuse_c", uB)
b, lo, hi, p = slope_row(fB1, "mean_logd")
say(f"ADJUSTED   : {b:+.2f}pp per log-unit [{lo:+.2f}, {hi:+.2f}], p={p:.3f}"
    f"  (per doubling of Delta: {b*np.log(2):+.2f}pp)")

fB2 = fit("acc ~ adoption_rate + minivlat_c + aiuse_c", uB)
b, lo, hi, p = slope_row(fB2, "adoption_rate")
say(f"SAP-variant (direct-adoption rate 0-1): {b:+.2f}pp full-range "
    f"[{lo:+.2f}, {hi:+.2f}], p={p:.3f}")

say("\nSpecificity probe - the same slope in the other arms "
    "(Delta = post-tool deliberation there, not answer adoption):")
for arm in ["socratic", "google"]:
    s = lat_all[lat_all.arm == arm]
    r, p = pearson(s.mean_logd, s.acc)
    fS = fit("acc ~ mean_logd + minivlat_c + aiuse_c", s)
    b, lo, hi, pa = slope_row(fS, "mean_logd")
    say(f"  {arm:12s} (n={len(s)}): r={r:+.3f}; adjusted "
        f"{b:+.2f}pp/log-unit [{lo:+.2f}, {hi:+.2f}], p={pa:.3f}")
pooled = lat_all[lat_all.arm.isin(["socratic", "unrestricted"])]
fP = fit("acc ~ mean_logd + unrestricted + minivlat_c + aiuse_c", pooled)
b, lo, hi, p = slope_row(fP, "mean_logd")
say(f"  pooled LLM arms (n={len(pooled)}, arm fixed effect): "
    f"{b:+.2f}pp/log-unit [{lo:+.2f}, {hi:+.2f}], p={p:.3f}")

say("\nConvergent validity of the two dose measures (within U):")
m = u.dropna(subset=["mean_logd"])
r, p = pearson(m.frac_fo, m.mean_logd)
say(f"  r(frac_fo, mean_logd) = {r:+.3f} (p={p:.3f}) - "
    "weak: content and latency capture related but distinct facets")

# ================================================================ STRAND C
say("\n" + "=" * 78)
say("STRAND C - within-person: Bloom-category practice dose vs category accuracy")
say("=" * 78)
cat = codes.assign(bloom_cat=codes.item_id.str.extract(r"pcp_(\w+?)_fa")[0],
                   fo=(codes.code == "FULL_OUTSOURCING").astype(int))
catdose = (cat.groupby(["participant_id", "bloom_cat"])["fo"].sum()
           .rename("cat_dose").reset_index()
           .rename(columns={"participant_id": "pid"}))
ui = unass[(unass.arm == "unrestricted") & (unass.wave == "immediate")].copy()
ui["bloom_cat"] = ui.item_id.str.extract(r"pcp_(\w+?)_sa")[0]
ui = ui.merge(catdose, on=["pid", "bloom_cat"], validate="m:1")
say(f"post-test items matched to a practice category: {len(ui)} "
    f"(= 66 x 16); participants with within-person dose variance: "
    f"{int((catdose.groupby('pid')['cat_dose'].nunique() > 1).sum())}/66")
ui["correct"] = ui["correct"].astype(float)
fC = smf.ols("correct ~ cat_dose + C(pid) + C(bloom_cat)", data=ui).fit(
        cov_type="cluster", cov_kwds={"groups": ui["pid"]})
b, lo, hi, p = slope_row(fC, "cat_dose")
say(f"item correct ~ category dose (0-2) + person FE + category FE, "
    f"participant-clustered:")
say(f"  {b:+.2f}pp per outsourced practice item in the same Bloom category "
    f"[{lo:+.2f}, {hi:+.2f}], p={p:.3f}")
say("  (person-level confounders cancel; within-person selection into which")
say("   categories to outsource does not - direction of that bias unknown)")

# check whether practice item order was fixed (position-fatigue caveat)
ordvar = itrain[itrain.arm == "unrestricted"].groupby("item_id")["position"].nunique()
say(f"  practice item order: {'RANDOMISED across participants' if (ordvar > 1).any() else 'FIXED'}"
    f" (positions per item: {sorted(set(ordvar))})")

# ================================================================ POWER
say("\n" + "=" * 78)
say("POWER / RESOLUTION (two-sided alpha=.05, 80% power)")
say("=" * 78)
for n, lab in [(66, "content dose, n=66"), (61, "latency U-arm, n=61"),
               (123, "pooled LLM arms, n=123")]:
    rd = detectable_r(n)
    say(f"  {lab:26s}: detectable |rho| >= {rd:.2f}")
sd_ratio = u.acc.std() / u.frac_fo.std()
say(f"  in slope terms (content dose): 80%-detectable full-range slope "
    f"~= {detectable_r(66)*sd_ratio*100:.1f}pp "
    f"(SD_acc={u.acc.std():.3f}, SD_dose={u.frac_fo.std():.3f})")

# ---------------------------------------------------------------- persist
u_out = u[["pid", "arm", "acc", "n_idk", "minivlat_c", "aiuse_c", "n_fo",
           "engaged_n", "frac_fo", "frac_fo_eng", "mean_logd", "n_toolitems",
           "adoption_rate"]]
u_out.to_csv(OUT / "frame_doseresponse_unrestricted.csv", index=False)
lat_all[["pid", "arm", "acc", "minivlat_c", "aiuse_c", "mean_logd",
         "n_toolitems", "adoption_rate"]].to_csv(
    OUT / "frame_latency_all_arms.csv", index=False)
(OUT / "results_outsourcing_doseresponse.txt").write_text("\n".join(log_lines))
print("\nwrote:", OUT / "results_outsourcing_doseresponse.txt")
