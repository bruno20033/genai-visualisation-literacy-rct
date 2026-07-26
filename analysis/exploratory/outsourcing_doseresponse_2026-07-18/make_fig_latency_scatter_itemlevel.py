#!/usr/bin/env python
"""
ITEM-LEVEL scatterplots: raw per-item answer-adoption latency (Delta) vs
immediate post-test accuracy.
  (1) Unrestricted + Socratic together
  (2) Unrestricted only
Requested by the author 2026-07-18 (raw-item version of the participant-mean
figures in this directory). Exploratory / post-hoc.

Every AIDED tool-item is one point at its raw adopt_delta_s (X, log scale).
Y = the participant's immediate unaided post-test accuracy (%), which is
measured on a DIFFERENT item set and so is necessarily participant-level:
each participant therefore appears as a horizontal row of points. Because
items within a participant are not independent AND share the same Y, inference
is a PARTICIPANT-CLUSTERED OLS (cluster-robust SEs); the naive item-level
Pearson r is shown for description only and is anticonservative.

House style per generated/results/make_results_figures.py: serif/Times,
Okabe-Ito ARM colours+markers, no in-figure title, vector PDF pdf.fonttype=42,
VERIFY block PASS/FAIL. Run in `course` env:
    ~/opt/anaconda3/envs/course/bin/python make_fig_latency_scatter_itemlevel.py
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

OUT = Path(__file__).resolve().parent
FRAMES = Path("~/Downloads/analysis_frames_immediate").expanduser()

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

# ---------------------------------------------------------------- build frame
imm    = pd.read_pickle(FRAMES / "imm.pkl")[["pid", "arm", "acc"]]
itrain = pd.read_pickle(FRAMES / "items_train.pkl")
it = itrain.dropna(subset=["adopt_delta_s"]).copy()
it = it[it["adopt_delta_s"] >= 0]
it["logd"] = np.log(it["adopt_delta_s"].clip(lower=1e-3))
it = it.merge(imm.drop(columns="arm"), on="pid", validate="m:1")   # bring post-test acc

def fit_arm(sub):
    # participant-clustered OLS; point estimate == plain OLS, SEs cluster-robust
    f = smf.ols("acc ~ logd", data=sub).fit(
            cov_type="cluster", cov_kwds={"groups": sub["pid"]})
    b = f.params["logd"] * 100
    p = f.pvalues["logd"]
    r = stats.pearsonr(sub.logd, sub.acc).statistic     # item-level, descriptive
    return f, b, p, r

fits = {a: fit_arm(it[it.arm == a]) for a in ("unrestricted", "socratic")}

def band(f, sub, npts=60):
    """Mean prediction +/- 1.96*cluster-robust SE, computed manually so the
    band reflects the clustered covariance (not the naive homoskedastic one)."""
    xs = np.linspace(sub.logd.min(), sub.logd.max(), npts)
    X = np.column_stack([np.ones_like(xs), xs])          # [1, logd]
    V = f.cov_params().values                            # 2x2 cluster-robust cov
    mean = X @ f.params.values
    se = np.sqrt(np.einsum("ij,jk,ik->i", X, V, X))
    return np.exp(xs), mean * 100, (mean - 1.96 * se) * 100, (mean + 1.96 * se) * 100

# ---------------------------------------------------------------- VERIFY
def ck(name, got, want, tol=0.02):
    ok = abs(got - want) <= tol
    print(f"  [{'PASS' if ok else 'FAIL'}] {name:30s} got {got:+8.3f}  want {want:+8.3f}")
    return ok

print("VERIFY (item-level, participant-clustered):")
nU = int((it.arm == "unrestricted").sum()); nS = int((it.arm == "socratic").sum())
ck("U tool-items", nU, 376, tol=0)     # 61 U participants, mean 6.16 items
ck("S tool-items", nS, 195, tol=0)     # 61 S participants, mean 3.20 items
ck("U participants", it[it.arm == "unrestricted"].pid.nunique(), 61, tol=0)
ck("S participants", it[it.arm == "socratic"].pid.nunique(), 61, tol=0)
for a in ("unrestricted", "socratic"):
    f, b, p, r = fits[a]
    sub = it[it.arm == a]
    print(f"    {a:12s} n_items={len(sub)}  item-r={r:+.3f}  "
          f"clustered slope={b:+.2f}pp/log-unit  p={p:.3f}  "
          f"median raw Delta={sub.adopt_delta_s.median():.1f}s  "
          f"n_clusters={sub.pid.nunique()}")
# cross-check: clustered point slope equals plain-OLS point slope (SE differs only)
_plainU = smf.ols("acc ~ logd", data=it[it.arm == "unrestricted"]).fit().params["logd"] * 100
ck("U slope clustered==plain (pt)", fits["unrestricted"][1], _plainU, tol=0.001)

# ---------------------------------------------------------------- draw
def draw(ax, arms):
    for a in arms:
        sub = it[it.arm == a]; s = ARM[a]
        ax.scatter(sub.adopt_delta_s, sub.acc * 100, s=14, marker=s["m"],
                   color=s["c"], alpha=0.28, edgecolors="none", zorder=3,
                   label=f"{s['label']}  ($n={len(sub)}$ items)")
        gx, gm, glo, ghi = band(fits[a][0], sub)
        ax.plot(gx, gm, color=s["c"], ls=s["ls"], lw=1.8, zorder=4)
        ax.fill_between(gx, glo, ghi, color=s["c"], alpha=0.14, linewidth=0, zorder=2)
    ax.axvline(5, color="#b2182b", lw=1.0, ls=(0, (5, 3)), zorder=1)
    ax.text(5, 105, "direct adoption\n($\\Delta<5\\,$s)", color="#b2182b",
            fontsize=7.6, ha="center", va="bottom")
    ax.set_xscale("log")
    ax.set_xticks([1, 5, 10, 30, 100, 300])
    ax.set_xticklabels(["1", "5", "10", "30", "100", "300"])
    ax.set_xlim(0.4, 500)
    ax.set_ylim(-4, 108); ax.yaxis.set_major_locator(MultipleLocator(20))
    ax.set_xlabel("Answer-adoption latency $\\Delta$ per item (s, log scale)")
    ax.set_ylabel("Immediate unaided post-test accuracy (%)")
    ax.grid(axis="both", ls=":", lw=0.6, alpha=0.5); ax.set_axisbelow(True)

# FIG 1 - U + S
fig, ax = plt.subplots(figsize=(5.8, 4.3))
draw(ax, ["unrestricted", "socratic"])
for a, yoff in (("unrestricted", 0.115), ("socratic", 0.05)):
    _, b, p, r = fits[a]
    ax.annotate(f"{ARM[a]['label'].split(' ')[0]}: ${b:+.1f}$ pp/log-unit, "
                f"$p={p:.2f}$ (clustered)",
                xy=(0.03, yoff), xycoords="axes fraction",
                fontsize=8.3, color=ARM[a]["c"], va="bottom")
ax.legend(frameon=False, loc="lower right", handletextpad=0.3)
fig.savefig(OUT / "fig_latency_scatter_itemlevel_llm_arms.pdf")
fig.savefig(OUT / "fig_latency_scatter_itemlevel_llm_arms.png")
plt.close(fig)

# FIG 2 - U only
fig, ax = plt.subplots(figsize=(5.8, 4.3))
draw(ax, ["unrestricted"])
_, b, p, r = fits["unrestricted"]
ax.annotate(f"${b:+.1f}$ pp/log-unit, $p={p:.2f}$ (participant-clustered; "
            f"$n={nU}$ items, 61 participants)",
            xy=(0.03, 0.05), xycoords="axes fraction",
            fontsize=8.3, color=ARM["unrestricted"]["c"], va="bottom")
fig.savefig(OUT / "fig_latency_scatter_itemlevel_unrestricted.pdf")
fig.savefig(OUT / "fig_latency_scatter_itemlevel_unrestricted.png")
plt.close(fig)

print("\nwrote 2 item-level figures (pdf+png) to", OUT)
