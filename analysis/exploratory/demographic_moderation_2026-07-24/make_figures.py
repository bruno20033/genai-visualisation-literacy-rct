#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Figures for the EXPLORATORY demographic moderation analysis (2026-07-24).

Self-verifying: recomputes key plotted statistics from the analysis dataset and
compares them against the saved results CSVs (PASS/FAIL printed at the end).

Palette: Okabe-Ito subset (#0072B2 / #009E73 / #D55E00), validated CVD-safe
(dataviz six-checks: all PASS, worst adjacent deutan dE 11.0). Identity is never
color-alone: distinct markers and linestyles throughout.

Run:  ~/opt/anaconda3/envs/course/bin/python make_figures.py
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = "/Users/brunokneffel/Downloads/demographic_moderation_2026-07-24"

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
    "font.size": 10, "axes.titlesize": 11, "axes.labelsize": 10,
    "pdf.fonttype": 42, "ps.fonttype": 42,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": False,
})

C = {"google": "#0072B2", "socratic": "#009E73", "unrestricted": "#D55E00"}
MK = {"google": "o", "socratic": "s", "unrestricted": "^"}
LS = {"google": "-", "socratic": "--", "unrestricted": "-."}
GREY = "#6b6b6b"

R = pd.read_csv(f"{OUT}/moderation_results_accuracy.csv")
S = pd.read_csv(f"{OUT}/subgroup_effects_accuracy.csv")
d = pd.read_csv(f"{OUT}/analysis_dataset.csv")
mm = d[d.matched == 1]

FOOT = ("Exploratory, non-pre-registered; hypothesis-generating only. OLS on 16-item "
        "proportion correct, Mini-VLAT + AI-use adjusted, HC3 95% CIs.")

# ---------------------------------------------------------------- fig 1: forest
fig, ax = plt.subplots(figsize=(9.2, 5.2))
rows = R.iloc[::-1].reset_index(drop=True)   # first moderator on top
y = np.arange(len(rows))
off = 0.17
ax.axvline(0, color="#9a9a9a", lw=1, zorder=1)
ax.axvspan(-5, 5, color="#000000", alpha=0.05, zorder=0)
for i, r in rows.iterrows():
    ax.plot([r.ci_lo, r.ci_hi], [i + off] * 2, color=C["unrestricted"], lw=1.8,
            solid_capstyle="round", zorder=3)
    ax.plot(r.int_UxM_pp, i + off, MK["unrestricted"], color=C["unrestricted"],
            ms=6.5, zorder=4)
    ax.plot([r.s_ci_lo, r.s_ci_hi], [i - off] * 2, color=C["socratic"], lw=1.8,
            solid_capstyle="round", zorder=3)
    ax.plot(r.int_SxM_pp, i - off, MK["socratic"], color=C["socratic"], ms=6,
            mfc="white", mew=1.6, zorder=4)
    ax.text(27.5, i, f"q={r.bh_q:.2f}", va="center", ha="left", fontsize=8.5,
            color=GREY)
ax.set_yticks(y)
ax.set_yticklabels([f"{r.moderator}\n(n={r.n})" for _, r in rows.iterrows()],
                   fontsize=9)
ax.set_xlim(-27, 33)
ax.set_xlabel("Interaction: difference in arm effect on immediate accuracy "
              "(percentage points)")
ax.set_title("No demographic moderator of the arm effect survives correction",
             loc="left", fontweight="bold", pad=24)
ax.text(0, 1.02, "Arm x moderator interactions with 95% CIs; shaded band = "
        "size of the full-sample main effect (~5 pp); q = BH-FDR",
        transform=ax.transAxes, fontsize=9, color=GREY, va="bottom")
h1, = ax.plot([], [], MK["unrestricted"], color=C["unrestricted"], ls="none",
              label="Unrestricted-vs-Google x moderator")
h2, = ax.plot([], [], MK["socratic"], color=C["socratic"], mfc="white", mew=1.6,
              ls="none", label="Socratic-vs-Google x moderator")
fig.text(0.01, 0.008, FOOT, fontsize=7.5, color=GREY)
fig.tight_layout(rect=(0, 0.03, 1, 0.94))
fig.legend(handles=[h1, h2], loc="upper right", bbox_to_anchor=(0.995, 1.0),
           frameon=False, fontsize=8.8)
for ext in ("png", "pdf"):
    fig.savefig(f"{OUT}/fig_interaction_forest.{ext}", dpi=200)
plt.close(fig)

# ------------------------------------------- fig 2: subgroup simple effects
fig, axes = plt.subplots(1, 2, figsize=(9.6, 6.0), sharey=True)
Ss = S.copy()
NICE = {
    ("Sex (female vs male)", "no"): "Sex - men",
    ("Sex (female vs male)", "yes"): "Sex - women",
    ("First language English (vs other)", "no"): "First language - other",
    ("First language English (vs other)", "yes"): "First language - English",
    ("Employment (part-time vs full-time)", "no"): "Employment - full-time",
    ("Employment (part-time vs full-time)", "yes"): "Employment - part-time",
    ("Ethnicity (non-White vs White, crude)", "no"): "Ethnicity - White",
    ("Ethnicity (non-White vs White, crude)", "yes"): "Ethnicity - non-White",
    ("IT/software/data occupation (vs other)", "no"): "Occupation - other",
    ("IT/software/data occupation (vs other)", "yes"): "Occupation - IT/software/data",
    ("Age (per +10 years)", "age~29"): "Age - ~29 (Q1)",
    ("Age (per +10 years)", "age~42"): "Age - ~42 (Q3)",
    ("Prolific approvals (per log10 unit, aux.)", "log10appr~2.16"): "Prolific approvals - ~145 (Q1)",
    ("Prolific approvals (per log10 unit, aux.)", "log10appr~2.76"): "Prolific approvals - ~575 (Q3)",
}
Ss["row"] = [NICE.get((m, str(l)), f"{m} | {l}") for m, l in zip(Ss.moderator, Ss.level)]
order = Ss.row.drop_duplicates().tolist()[::-1]
ypos = {r: i for i, r in enumerate(order)}
for ax, con, arm in [(axes[0], "U-G", "unrestricted"), (axes[1], "S-G", "socratic")]:
    sub = Ss[Ss.contrast == con]
    ax.axvline(0, color="#9a9a9a", lw=1, zorder=1)
    for _, r in sub.iterrows():
        i = ypos[r.row]
        ax.plot([r.ci_lo, r.ci_hi], [i] * 2, color=C[arm], lw=1.8,
                solid_capstyle="round", zorder=3)
        ax.plot(r.est_pp, i, MK[arm], color=C[arm], ms=5.5, zorder=4,
                mfc="white" if arm == "socratic" else C[arm], mew=1.4)
    ax.set_title(("Unrestricted - Google" if con == "U-G" else "Socratic - Google"),
                 color=C[arm], loc="left", fontsize=10.5, fontweight="bold")
    ax.set_xlim(-22, 22)
    ax.set_xlabel("Arm effect within subgroup (pp)")
axes[0].set_yticks(range(len(order)))
axes[0].set_yticklabels(order, fontsize=8.6)
fig.suptitle("Arm effects within demographic subgroups (all CIs overlap; exploratory)",
             x=0.01, ha="left", fontweight="bold", fontsize=11.5)
fig.text(0.01, 0.008, FOOT + " Levels for continuous moderators are the 25th/75th "
         "percentiles.", fontsize=7.5, color=GREY)
fig.tight_layout(rect=(0, 0.03, 1, 0.96))
for ext in ("png", "pdf"):
    fig.savefig(f"{OUT}/fig_subgroup_effects.{ext}", dpi=200)
plt.close(fig)

# ---------------------------------------------------------- fig 3: age x arm
fig, ax = plt.subplots(figsize=(8.0, 5.2))
rng = np.random.default_rng(2026)
slopes = {}
for arm in ["google", "socratic", "unrestricted"]:
    g = mm[(mm.arm == arm) & mm.age.notna()]
    jit = rng.uniform(-0.012, 0.012, len(g))
    yj = np.clip(g.acc * 100 + jit * 100, 0.5, 100.0)
    ax.plot(g.age, yj, MK[arm], color=C[arm], ms=4.5,
            alpha=0.45, ls="none", mew=0.8,
            mfc="white" if arm == "socratic" else None)
    X = sm.add_constant(g.age)
    f = sm.OLS(g.acc * 100, X).fit()
    xs = np.linspace(g.age.min(), g.age.max(), 50)
    ax.plot(xs, f.params.iloc[0] + f.params.iloc[1] * xs, LS[arm], color=C[arm],
            lw=2.2, label=f"{arm.capitalize()}  ({f.params.iloc[1]*10:+.1f} pp/decade)")
    slopes[arm] = f.params.iloc[1] * 10
ax.axvspan(55, 64, color="#000000", alpha=0.05)
ax.text(59.5, 22, "ages >55:\nn=10 total", ha="center", fontsize=8, color=GREY)
ax.set_xlabel("Age (years)")
ax.set_ylabel("Immediate unaided accuracy (%)")
ax.set_ylim(15, 104)
ax.set_title("The one suggestive pattern - Socratic advantage grows with age - "
             "is fragile", loc="left", fontweight="bold", pad=24)
ax.text(0, 1.02, "Unadjusted per-arm fits; interaction omnibus p=.06, BH q=.44; "
        "collapses when ages >55 are trimmed (p=.30) or age is rank-transformed (p=.15)",
        transform=ax.transAxes, fontsize=8.7, color=GREY, va="bottom")
ax.legend(loc="lower left", frameon=False, fontsize=9)
fig.text(0.01, 0.008, "Exploratory, non-pre-registered. Points jittered vertically "
         "(<1.5 pp) for visibility; lines are unadjusted OLS fits.",
         fontsize=7.5, color=GREY)
fig.tight_layout(rect=(0, 0.03, 1, 1))
for ext in ("png", "pdf"):
    fig.savefig(f"{OUT}/fig_age_accuracy.{ext}", dpi=200)
plt.close(fig)

# ------------------------------------------------------------------ VERIFY
print("VERIFY block (plotted vs saved/recomputed):")
ok = True

def check(name, a, b, tol):
    global ok
    good = abs(a - b) <= tol
    ok &= good
    print(f"  [{'PASS' if good else 'FAIL'}] {name}: {a:.3f} vs {b:.3f}")

age_row = R[R.key == "age"].iloc[0]
mm2 = mm.dropna(subset=["age", "acc", "minivlat_c", "aiuse_c"]).copy()
mm2["age_c10"] = (mm2.age - d.age.mean()) / 10
X = pd.DataFrame({"const": 1.0, "soc": mm2.soc, "unr": mm2.unr, "m": mm2.age_c10,
                  "soc_m": mm2.soc * mm2.age_c10, "unr_m": mm2.unr * mm2.age_c10,
                  "mv": mm2.minivlat_c, "ai": mm2.aiuse_c})
r = sm.OLS(mm2.acc.to_numpy(float), X).fit(cov_type="HC3")
check("age SxM interaction (pp)", r.params.soc_m * 100, age_row.int_SxM_pp, 0.05)
check("age UxM interaction (pp)", r.params.unr_m * 100, age_row.int_UxM_pp, 0.05)
check("n moderators plotted", len(R), 7, 0)
check("all BH q >= 0.44", R.bh_q.min(), 0.44, 0.01)
g = mm[(mm.arm == "socratic") & mm.age.notna()]
f = sm.OLS(g.acc * 100, sm.add_constant(g.age)).fit()
check("socratic unadjusted slope pp/decade (fig3)", slopes["socratic"], f.params.iloc[1] * 10, 0.01)
print("ALL PASS" if ok else "*** SOME CHECKS FAILED ***")
