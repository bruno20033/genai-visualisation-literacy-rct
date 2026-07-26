#!/usr/bin/env python
"""
Figure: outsourcing dose vs. unaided post-test accuracy (exploratory, U arm).

House style per generated/results/make_results_figures.py: serif/Times,
Okabe-Ito ARM colours/markers, no in-figure titles beyond short panel heads,
vector PDF with pdf.fonttype=42, and a VERIFY block that recomputes every
plotted/quoted statistic and prints PASS/FAIL against the draft prose.

Run in the `course` env:
    ~/opt/anaconda3/envs/course/bin/python make_fig_outsourcing_dose_response.py

Input : ~/Downloads/analysis_frames_immediate/{imm,items_train,items_unassisted}.pkl
        ~/Downloads/transcript_coding_unrestricted_2026-07-18/
            unrestricted_outsourcing_codes_2026-07-18.csv
Output: fig_outsourcing_dose_response.pdf/.png (THIS directory - deliberately
        distinct from the prior session's fig_outsourcing_posttest*)
"""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

RNG = np.random.default_rng(2026)          # jitter seed (D8 SEED convention)
OUT = Path(__file__).resolve().parent
FRAMES = Path("~/Downloads/analysis_frames_immediate").expanduser()
CODES = Path("~/Downloads/transcript_coding_unrestricted_2026-07-18/"
             "unrestricted_outsourcing_codes_2026-07-18.csv").expanduser()

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "STIXGeneral", "DejaVu Serif"],
    "mathtext.fontset": "stix",
    "font.size": 10, "axes.labelsize": 11, "axes.titlesize": 11,
    "xtick.labelsize": 9.5, "ytick.labelsize": 9.5, "legend.fontsize": 9,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": 0.7, "lines.linewidth": 1.3,
    "figure.dpi": 150, "savefig.dpi": 300, "savefig.bbox": "tight",
    "pdf.fonttype": 42,
})
ARM = {
    "google":       dict(label="Google (control)", c="#0072B2", m="o", ls="-"),
    "socratic":     dict(label="Socratic",         c="#009E73", m="s", ls="--"),
    "unrestricted": dict(label="Unrestricted",     c="#D55E00", m="^", ls="-."),
}
GREY = "#6e6e6e"

# ---------------------------------------------------------------- rebuild frames
imm    = pd.read_pickle(FRAMES / "imm.pkl")
itrain = pd.read_pickle(FRAMES / "items_train.pkl")
unass  = pd.read_pickle(FRAMES / "items_unassisted.pkl")
codes  = pd.read_csv(CODES)

per = codes.pivot_table(index="participant_id", columns="code", aggfunc="size",
                        fill_value=0).reset_index().rename(
                        columns={"participant_id": "pid"})
for c in ["FULL_OUTSOURCING", "NO_INTERACTION"]:
    if c not in per:
        per[c] = 0
per["n_fo"] = per["FULL_OUTSOURCING"]
per["engaged_n"] = 8 - per["NO_INTERACTION"]
per["frac_fo"] = per["n_fo"] / 8
per["frac_fo_eng"] = np.where(per["engaged_n"] > 0,
                              per["n_fo"] / per["engaged_n"], np.nan)
u = imm[imm.arm == "unrestricted"].merge(
        per[["pid", "n_fo", "engaged_n", "frac_fo", "frac_fo_eng"]],
        on="pid", validate="1:1")

it = itrain.dropna(subset=["adopt_delta_s"])
it = it[it["adopt_delta_s"] >= 0].copy()
it["logd"] = np.log(it["adopt_delta_s"].clip(lower=1e-3))
lat = (it.groupby(["pid", "arm"], observed=True)
         .agg(mean_logd=("logd", "mean")).reset_index())
u = u.merge(lat[lat.arm == "unrestricted"][["pid", "mean_logd"]],
            on="pid", how="left", validate="1:1")
lat_all = imm.merge(lat, on=["pid", "arm"], validate="1:1")

# ---------------------------------------------------------------- models
fitA0 = smf.ols("acc ~ frac_fo", data=u).fit(cov_type="HC3")
fitA1 = smf.ols("acc ~ frac_fo + minivlat_c + aiuse_c", data=u).fit(cov_type="HC3")
e = u.dropna(subset=["frac_fo_eng"])
fitAe = smf.ols("acc ~ frac_fo_eng + minivlat_c + aiuse_c", data=e).fit(cov_type="HC3")
uB = u.dropna(subset=["mean_logd"])
fitB0 = smf.ols("acc ~ mean_logd", data=uB).fit(cov_type="HC3")
fitB1 = smf.ols("acc ~ mean_logd + minivlat_c + aiuse_c", data=uB).fit(cov_type="HC3")
g = lat_all[lat_all.arm == "google"]
fitG = smf.ols("acc ~ mean_logd + minivlat_c + aiuse_c", data=g).fit(cov_type="HC3")

# strand C: within-person Bloom-category dose
cat = codes.assign(bloom_cat=codes.item_id.str.extract(r"pcp_(\w+?)_fa")[0],
                   fo=(codes.code == "FULL_OUTSOURCING").astype(int))
catdose = (cat.groupby(["participant_id", "bloom_cat"])["fo"].sum()
           .rename("cat_dose").reset_index().rename(columns={"participant_id": "pid"}))
ui = unass[(unass.arm == "unrestricted") & (unass.wave == "immediate")].copy()
ui["bloom_cat"] = ui.item_id.str.extract(r"pcp_(\w+?)_sa")[0]
ui = ui.merge(catdose, on=["pid", "bloom_cat"], validate="m:1")
ui["correct"] = ui["correct"].astype(float)
fitC = smf.ols("correct ~ cat_dose + C(pid) + C(bloom_cat)", data=ui).fit(
        cov_type="cluster", cov_kwds={"groups": ui["pid"]})

def sl(f, t):
    lo, hi = f.conf_int().loc[t]
    return f.params[t] * 100, lo * 100, hi * 100, f.pvalues[t]

# ---------------------------------------------------------------- VERIFY
def ck(name, got, want, tol=0.15):
    ok = abs(got - want) <= tol
    print(f"  [{'PASS' if ok else 'FAIL'}] {name:34s} got {got:+8.2f}  prose {want:+8.2f}")
    return ok

print("VERIFY against the draft prose / results txt (pp unless noted):")
A0 = sl(fitA0, "frac_fo"); A1 = sl(fitA1, "frac_fo"); Ae = sl(fitAe, "frac_fo_eng")
B0 = sl(fitB0, "mean_logd"); B1 = sl(fitB1, "mean_logd")
G  = sl(fitG, "mean_logd"); C = sl(fitC, "cat_dose")
r_pear = stats.pearsonr(u.frac_fo, u.acc)
ck("Pearson r (x100)", r_pear.statistic * 100, -20.0, tol=0.5)
ck("A unadj slope", A0[0], -10.41); ck("A unadj p (x100)", A0[3] * 100, 16.7, tol=0.5)
ck("A adj slope", A1[0], -9.49); ck("A adj CI lo", A1[1], -24.27); ck("A adj CI hi", A1[2], 5.30)
ck("A adj p (x100)", A1[3] * 100, 20.8, tol=0.5)
ck("A per-item slope", A1[0] / 8, -1.19, tol=0.05)
ck("A engaged slope", Ae[0], -17.27); ck("A engaged p (x100)", Ae[3] * 100, 1.6, tol=0.3)
ck("B unadj /doubling", B0[0] * np.log(2), 2.83, tol=0.05)
ck("B adj /doubling", B1[0] * np.log(2), 3.31, tol=0.05)
ck("B adj p (x100)", B1[3] * 100, 25.5, tol=0.6)
ck("google adj slope/log-unit", G[0], 7.49); ck("google p (x1000)", G[3] * 1000, 1.0, tol=0.9)
ck("C within-person slope", C[0], -5.51); ck("C p (x100)", C[3] * 100, 7.4, tol=0.5)
ck("dose mean (x100)", u.frac_fo.mean() * 100, 66.5, tol=0.5)
pure = u[u.frac_fo_eng == 1.0]; rest = u[~u.pid.isin(pure.pid)]
ck("prior pure acc (%)", pure.acc.mean() * 100, 68.8, tol=0.3)
ck("prior other acc (%)", rest.acc.mean() * 100, 74.2, tol=0.3)
ck("never-engaged acc (%)", u[u.engaged_n == 0].acc.mean() * 100, 66.2, tol=0.3)
ck("coherence dose x slope", u.frac_fo.mean() * A0[0], -6.9, tol=0.3)

# ---------------------------------------------------------------- figure
fig, (aL, aR) = plt.subplots(1, 2, figsize=(7.2, 3.5), sharey=True,
                             gridspec_kw=dict(wspace=0.10))
d = ARM["unrestricted"]

# panel L - content dose
jx = RNG.uniform(-0.18, 0.18, len(u))
aL.scatter(u.n_fo + jx, u.acc * 100, s=26, marker=d["m"], color=d["c"],
           alpha=0.55, edgecolors="white", linewidths=0.5, zorder=3)
grid = pd.DataFrame({"frac_fo": np.linspace(0, 1, 60)})
pr = fitA0.get_prediction(grid).summary_frame(alpha=0.05)
aL.plot(grid.frac_fo * 8, pr["mean"] * 100, color=d["c"], lw=1.5, zorder=2)
aL.fill_between(grid.frac_fo * 8, pr["mean_ci_lower"] * 100,
                pr["mean_ci_upper"] * 100, color=d["c"], alpha=0.14,
                linewidth=0, zorder=1)
aL.annotate(f"${A0[0]:+.1f}$ pp per full dose\n$[{A0[1]:+.1f}, {A0[2]:+.1f}]$, $p={A0[3]:.2f}$",
            xy=(0.03, 0.045), xycoords="axes fraction", fontsize=8.6,
            color=d["c"], va="bottom")
aL.set_xlabel("Practice items outsourced (of 8)")
aL.set_ylabel("Immediate unaided post-test accuracy (%)")
aL.set_xticks(range(0, 9)); aL.set_xlim(-0.55, 8.55)
aL.set_title("Content-coded dose", fontsize=10.5, pad=5)

# panel R - latency dose (geometric-mean Delta, log axis)
gm = np.exp(uB.mean_logd)
aR.scatter(gm, uB.acc * 100, s=26, marker=d["m"], color=d["c"],
           alpha=0.55, edgecolors="white", linewidths=0.5, zorder=3)
lg = pd.DataFrame({"mean_logd": np.linspace(uB.mean_logd.min(),
                                            uB.mean_logd.max(), 60)})
prB = fitB0.get_prediction(lg).summary_frame(alpha=0.05)
aR.plot(np.exp(lg.mean_logd), prB["mean"] * 100, color=d["c"], lw=1.5, zorder=2)
aR.fill_between(np.exp(lg.mean_logd), prB["mean_ci_lower"] * 100,
                prB["mean_ci_upper"] * 100, color=d["c"], alpha=0.14,
                linewidth=0, zorder=1)
# NB: no 5-s direct-adoption line here -- that threshold is defined per item
# (fig_adoption_latency), whereas this axis is the participant MEAN Delta.
aR.annotate(f"${B0[0]*np.log(2):+.1f}$ pp per doubling of $\\Delta$\n$p={B0[3]:.2f}$",
            xy=(0.03, 0.045), xycoords="axes fraction", fontsize=8.6,
            color=d["c"], va="bottom")
aR.set_xscale("log")
aR.set_xticks([2, 5, 10, 30, 100])
aR.set_xticklabels(["2", "5", "10", "30", "100"])
aR.set_xlabel("Mean answer-adoption latency $\\Delta$ (s, log scale)")
aR.set_title("Timing dose", fontsize=10.5, pad=5)

for a in (aL, aR):
    a.set_ylim(15, 104)
    a.yaxis.set_major_locator(MultipleLocator(20))
    a.grid(axis="y", ls=":", lw=0.6, alpha=0.5)
    a.set_axisbelow(True)

fig.savefig(OUT / "fig_outsourcing_dose_response.pdf")
fig.savefig(OUT / "fig_outsourcing_dose_response.png")
plt.close(fig)
print("\nwrote fig_outsourcing_dose_response.pdf/.png to", OUT)
