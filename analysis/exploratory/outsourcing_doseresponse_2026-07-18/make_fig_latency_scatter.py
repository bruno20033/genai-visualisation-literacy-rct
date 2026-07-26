#!/usr/bin/env python
"""
Scatterplots: answer-adoption latency (Delta) vs immediate post-test accuracy.
  (1) Unrestricted + Socratic together
  (2) Unrestricted only
Requested by the author 2026-07-18. Exploratory / post-hoc (same status as the
dose-response pass in this directory).

House style per generated/results/make_results_figures.py: serif/Times,
Okabe-Ito ARM colours+markers, no in-figure title, vector PDF pdf.fonttype=42,
plus a VERIFY block that recomputes every plotted statistic PASS/FAIL.

Run in `course` env:
    ~/opt/anaconda3/envs/course/bin/python make_fig_latency_scatter.py

X = participant mean log adoption latency, shown as geometric-mean Delta on a
log axis (Delta = answer_ts - last tool-interaction ts, per item, averaged in
log space -- the SAP log-Delta convention). Y = immediate unaided accuracy (%).
Regression lines are unadjusted OLS with 95% CI band, fitted per arm.
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
imm    = pd.read_pickle(FRAMES / "imm.pkl")
itrain = pd.read_pickle(FRAMES / "items_train.pkl")
it = itrain.dropna(subset=["adopt_delta_s"])
it = it[it["adopt_delta_s"] >= 0].copy()
it["logd"] = np.log(it["adopt_delta_s"].clip(lower=1e-3))
lat = (it.groupby(["pid", "arm"], observed=True)
         .agg(mean_logd=("logd", "mean"), n_toolitems=("logd", "size"))
         .reset_index())
d = imm.merge(lat, on=["pid", "arm"], validate="1:1")
d["gm_delta"] = np.exp(d["mean_logd"])          # geometric-mean Delta (s)

def fit_arm(sub):
    f = smf.ols("acc ~ mean_logd", data=sub).fit(cov_type="HC3")
    b = f.params["mean_logd"] * 100
    p = f.pvalues["mean_logd"]
    r = stats.pearsonr(sub.mean_logd, sub.acc).statistic
    return f, b, p, r

fits = {a: fit_arm(d[d.arm == a]) for a in ("unrestricted", "socratic")}

# ---------------------------------------------------------------- VERIFY
def ck(name, got, want, tol=0.02):
    ok = abs(got - want) <= tol
    print(f"  [{'PASS' if ok else 'FAIL'}] {name:26s} got {got:+7.3f}  want {want:+7.3f}")
    return ok

print("VERIFY (per-arm latency-accuracy association):")
ck("U n", len(d[d.arm == 'unrestricted']), 61, tol=0)
ck("S n", len(d[d.arm == 'socratic']), 61, tol=0)
ck("U pearson r", fits["unrestricted"][3], 0.138, tol=0.003)
ck("S pearson r", fits["socratic"][3], 0.081, tol=0.003)
ck("U slope pp/log-unit", fits["unrestricted"][1], 4.08, tol=0.05)
for a in ("unrestricted", "socratic"):
    _, b, p, r = fits[a]
    print(f"    {a:12s} n={len(d[d.arm==a])}  r={r:+.3f}  "
          f"slope={b:+.2f}pp/log-unit  p={p:.3f}  "
          f"median Delta={d[d.arm==a].gm_delta.median():.1f}s")

def draw(ax, arms, band=True):
    for a in arms:
        sub = d[d.arm == a]; s = ARM[a]
        ax.scatter(sub.gm_delta, sub.acc * 100, s=30, marker=s["m"],
                   color=s["c"], alpha=0.55, edgecolors="white",
                   linewidths=0.5, zorder=3, label=s["label"])
        f = fits[a][0]
        grid = pd.DataFrame({"mean_logd":
                             np.linspace(sub.mean_logd.min(), sub.mean_logd.max(), 60)})
        pr = f.get_prediction(grid).summary_frame(alpha=0.05)
        ax.plot(np.exp(grid.mean_logd), pr["mean"] * 100,
                color=s["c"], ls=s["ls"], lw=1.6, zorder=2)
        if band:
            ax.fill_between(np.exp(grid.mean_logd), pr["mean_ci_lower"] * 100,
                            pr["mean_ci_upper"] * 100, color=s["c"],
                            alpha=0.12, linewidth=0, zorder=1)
    ax.set_xscale("log")
    ax.set_xticks([2, 5, 10, 30, 100]); ax.set_xticklabels(["2", "5", "10", "30", "100"])
    ax.set_xlim(1.5, 160)
    ax.set_ylim(15, 104); ax.yaxis.set_major_locator(MultipleLocator(20))
    ax.set_xlabel("Mean answer-adoption latency $\\Delta$ (s, log scale)")
    ax.set_ylabel("Immediate unaided post-test accuracy (%)")
    ax.grid(axis="both", ls=":", lw=0.6, alpha=0.5); ax.set_axisbelow(True)

# ---------------------------------------------------------------- FIG 1: U + S
fig, ax = plt.subplots(figsize=(5.6, 4.2))
draw(ax, ["unrestricted", "socratic"])
for a, yoff in (("unrestricted", 0.11), ("socratic", 0.045)):
    _, b, p, r = fits[a]
    ax.annotate(f"{ARM[a]['label'].split(' ')[0]}: $r={r:+.2f}$, "
                f"${b:+.1f}$ pp/log-unit, $p={p:.2f}$",
                xy=(0.03, yoff), xycoords="axes fraction",
                fontsize=8.4, color=ARM[a]["c"], va="bottom")
ax.legend(frameon=False, loc="lower right")
fig.savefig(OUT / "fig_latency_scatter_llm_arms.pdf")
fig.savefig(OUT / "fig_latency_scatter_llm_arms.png")
plt.close(fig)

# ---------------------------------------------------------------- FIG 2: U only
fig, ax = plt.subplots(figsize=(5.6, 4.2))
draw(ax, ["unrestricted"])
_, b, p, r = fits["unrestricted"]
ax.annotate(f"$r={r:+.2f}$, ${b:+.1f}$ pp/log-unit, $p={p:.2f}$  ($n=61$)",
            xy=(0.03, 0.045), xycoords="axes fraction",
            fontsize=8.6, color=ARM["unrestricted"]["c"], va="bottom")
fig.savefig(OUT / "fig_latency_scatter_unrestricted.pdf")
fig.savefig(OUT / "fig_latency_scatter_unrestricted.png")
plt.close(fig)

print("\nwrote 2 figures (pdf+png) to", OUT)
