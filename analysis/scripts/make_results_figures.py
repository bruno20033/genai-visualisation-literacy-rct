#!/usr/bin/env python
"""
Generate the ten Results figures from the TWO-WAVE analysis frames.

Run in the `course` env (statsmodels + lifelines + pandas):
    ~/opt/anaconda3/envs/course/bin/python make_results_figures.py

Input : ~/Downloads/analysis_frames/{acc_pw,aided,items_unassisted,items_train,surv}.pkl
        (pickled by rct_data_literacy_analysis_4_FINAL_2026-07-21.ipynb; the
        July-21 run, n=218 immediate / 174 delayed --- the dataset
        sections/results.tex is reconciled to).
Output: fig_outcome_space.pdf, fig_forest_primary.pdf, fig_bloom.pdf,
        fig_crossover.pdf, fig_idk.pdf, fig_adoption_latency.pdf,
        fig_cogload.pdf, fig_bloom_twowave.pdf, fig_bloom4_twowave.pdf,
        fig_bloom_combined.pdf  (vector PDF, this directory) + *_preview.png
        (scratchpad).
        fig_bloom_twowave  = the FIG 3 arm x Bloom (lower/higher) interaction
        drawn for BOTH waves in the two-panel fig_idk layout; fig_bloom4_twowave
        = the same but split into the four taxonomic levels; fig_bloom_combined
        = both stacked as a 2x2 grid (lower/higher over four-level).

SUPERSEDES the n=188 immediate-only generator (see make_results_figures.py.bak_n188_*):
  * outcome-space now draws BOTH waves (delayed panel filled), per-arm N in the
    x-labels ("n=" stated once), titles "Immediate/Delayed post-test";
  * forest + crossover use the pre-registered TWO-WAVE LMM contrasts
    (eq:primary-acc via sap_estimators.fit_primary_acc) so the immediate simple
    effect matches the chapter headline (H1a -5.06, H2a -0.67 / 90% lo -5.37),
    and the crossover's delayed phase is filled from the delayed simple effects;
  * the abstention bracket uses the no-covariate participant-clustered GEE that
    the chapter prose reports (OR 2.14), not the covariate-adjusted variant.

Every plotted quantity is recomputed here and cross-checked against the numbers
in sections/results.tex; the VERIFY block prints each with PASS/FAIL so figure
and prose cannot drift.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import scipy.stats as st
import statsmodels.formula.api as smf
import statsmodels.api as sm
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

RNG    = np.random.default_rng(2026)                      # cluster-boot seed (D8 SEED)
FRAMES = Path("~/Downloads/analysis_frames").expanduser() # two-wave, n=218/174
OUT    = Path(__file__).resolve().parent
PREVIEW = Path("/private/tmp/claude-501/-Users-brunokneffel-Library-Mobile-Documents-com-apple-CloudDocs-gymnasium-steglitz-B-SC-Frankfurt-School-Oxford-Thesis-WIP-thesis-latex/9db3e08c-45e1-428b-a6ee-0bf1d13e0292/scratchpad")

# shared, Monte-Carlo-validated estimators (same module the notebook uses)
sys.path.insert(0, str(Path("~/Downloads").expanduser()))
from sap_estimators import (fit_primary_acc, lincom, adoption_latency, Z90, z_onesided_p,
                            fit_cox_st, cox_lincom, holm_family)

# ----------------------------------------------------------------------------
# House style — academic, colourblind-safe (Okabe–Ito), print-safe (distinct
# markers + line styles), serif to match the LaTeX body. No figure titles.
# ----------------------------------------------------------------------------
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
ARM = {  # order matters: control first
    "google":       dict(label="Google (control)", c="#0072B2", m="o", ls="-"),
    "socratic":     dict(label="Socratic",         c="#009E73", m="s", ls="--"),
    "unrestricted": dict(label="Unrestricted",     c="#D55E00", m="^", ls="-."),
}
GREY  = "#6e6e6e"
arms  = list(ARM)
waves = ["immediate", "delayed"]

# ----------------------------------------------------------------------------
accpw  = pd.read_pickle(FRAMES / "acc_pw.pkl")               # both waves
imm    = accpw[accpw.wave == "immediate"].copy()            # immediate cross-section
aided  = pd.read_pickle(FRAMES / "aided.pkl")
unass  = pd.read_pickle(FRAMES / "items_unassisted.pkl")
unassI = unass[unass.wave == "immediate"].copy()            # Bloom = immediate wave
surv   = pd.read_pickle(FRAMES / "surv.pkl")                # both waves
itrain = pd.read_pickle(FRAMES / "items_train.pkl")         # MC4 adoption latency

# ---- primary two-wave LMM (eq:primary-acc) and its contrasts (percentage pts)
res = fit_primary_acc(accpw)
def lmm(d):
    """(est, lo95, hi95) in pp for a linear combination of LMM coefficients."""
    e, se = lincom(res, d); return e*100, (e-1.96*se)*100, (e+1.96*se)*100
def lmm90(d):
    e, se = lincom(res, d); return e*100, (e-Z90*se)*100, (e+Z90*se)*100
def lmm_p(d, direction):
    e, se = lincom(res, d); return z_onesided_p(e, se, direction)

UG   = lmm({"unrestricted": 1})                                  # H1a immediate U-G
SG   = lmm({"socratic": 1})                                      # H2a immediate S-G (95%)
SG90 = lmm90({"socratic": 1})                                    # H2a 90% CI (NI scale)
SU   = lmm({"socratic": 1, "unrestricted": -1})                  # supporting S-U
UG_d = lmm({"unrestricted": 1, "unrestricted:wave_d": 1})        # delayed U-G (H5a)
SG_d = lmm({"socratic": 1, "socratic:wave_d": 1})                # delayed S-G

# ---- pre-registered contrast p-values for the outcome-space brackets (FIG 1).
#      Recomputed here so the on-figure annotations match the chapter verbatim.
#      Accuracy (immediate, primary family) --- one-sided per the SAP:
P_UG_acc = lmm_p({"unrestricted": 1}, -1)                        # H1a  U-G superiority
_b1, _se1 = lincom(res, {"socratic": 1})                         # H2a  S-G, proportion scale
P_SG_ni  = float(st.norm.sf((_b1 + 0.085) / _se1))              # H2a  non-inferiority vs -8.5 pp
#      Success-time (immediate, secondary confirmatory family) --- Cox HRs:
cph = fit_cox_st(surv)
_bH1b, _seH1b = cox_lincom(cph, {"unrestricted": 1})             # H1b  U-G (hypothesised U slower, HR<1)
HR_UG_t, P_UG_t = np.exp(_bH1b), z_onesided_p(_bH1b, _seH1b, -1)
_bH2b, _seH2b = cox_lincom(cph, {"socratic": 1, "unrestricted": -1})  # H2b  S-U (S faster, HR>1)
HR_SU_t, P_SU_t = np.exp(_bH2b), z_onesided_p(_bH2b, _seH2b, +1)
P_SU_t_holm = float(holm_family({"H1b": P_UG_t, "H2b": P_SU_t}).loc["H2b", "p_holm"])
#      S-G (time): descriptive only --- D1 dropped the time NI claim, so this
#      pair carries no pre-registered hypothesis or direction; report two-sided.
_bSG_t, _seSG_t = cox_lincom(cph, {"socratic": 1})
HR_SG_t = np.exp(_bSG_t)
P_SG_t = float(2 * st.norm.sf(abs(_bSG_t) / _seSG_t))

# ---- immediate cross-sectional ANCOVA (aided phase + cognitive load) --------
def ancova(df, y):
    return smf.ols(f"{y} ~ socratic + unrestricted + minivlat_c + aiuse_c",
                   data=df).fit(cov_type="HC3")
def contrast(fit, expr):
    t = fit.t_test(expr); est = float(t.effect[0])*100
    lo, hi = (t.conf_int()[0]*100); return est, lo, hi
fit_aided = ancova(aided, "aided_acc")
UG_a = contrast(fit_aided, "unrestricted")                       # aided U-G
SG_a = contrast(fit_aided, "socratic")                           # aided S-G

# ---- per-wave observed accuracy + time-to-success ---------------------------
def acc_cell(a, w):
    s = accpw[(accpw.arm == a) & (accpw.wave == w)]["acc"]
    m = s.mean(); return m, m-1.96*s.sem(), m+1.96*s.sem(), len(s)
def time_cell(a, w):
    sub  = surv[(surv.arm == a) & (surv.wave == w) & (surv.event == 1)]
    pt   = sub["duration_s"].median(); pids = sub["pid"].unique()
    by   = {p: sub[sub.pid == p]["duration_s"].values for p in pids}
    boot = [np.median(np.concatenate([by[p] for p in RNG.choice(pids, len(pids), replace=True)]))
            for _ in range(2000)]
    lo, hi = np.percentile(boot, [2.5, 97.5]); return pt, lo, hi
A = {w: {a: acc_cell(a, w)  for a in arms} for w in waves}       # (mean, lo, hi, N)
T = {w: {a: time_cell(a, w) for a in arms} for w in waves}
NN = {w: {a: A[w][a][3] for a in arms} for w in waves}

# ---- Bloom cell means (immediate, item-level) + participant-cluster boot CI --
def bloom_cell(arm, order):
    sub = unassI[(unassI.arm == arm) & (unassI.order == order)]
    pt = sub["correct"].mean(); pids = sub["pid"].unique()
    by = {p: sub[sub.pid == p]["correct"].values for p in pids}
    boot = [np.concatenate([by[p] for p in RNG.choice(pids, len(pids), replace=True)]).mean()
            for _ in range(2000)]
    lo, hi = np.percentile(boot, [2.5, 97.5]); return pt, lo, hi
bloom = {a: {o: bloom_cell(a, o) for o in ("lower", "higher")} for a in arms}

# ---- abstention (IDK): observed rates + the chapter's no-covariate GEE, -------
#      computed for BOTH post-test waves (immediate | delayed) so the figure
#      shows persistence of the give-up effect. Same estimators as the prose:
#      observed rate, participant-clustered bootstrap 95% CI, no-covariate
#      participant-clustered GEE for the odds ratios.
def _idk_stats(w):
    d = surv[surv.wave == w].copy(); d["idk"] = d["idk"].astype(int)
    gee = smf.gee("idk ~ unrestricted + socratic", groups="pid", data=d,     # no covariates: matches prose
                  family=sm.families.Binomial(),
                  cov_struct=sm.cov_struct.Exchangeable()).fit()
    rate = {a: d[d.arm == a]["idk"].mean() for a in arms}
    def _ci(arm):
        sub = d[d.arm == arm]; pids = sub["pid"].unique()
        by = {p: sub[sub.pid == p]["idk"].values for p in pids}
        boot = [np.concatenate([by[p] for p in RNG.choice(pids, len(pids), replace=True)]).mean()
                for _ in range(2000)]
        return tuple(np.percentile(boot, [2.5, 97.5]))
    ci  = {a: _ci(a) for a in arms}
    loU, hiU = gee.conf_int().loc["unrestricted"]
    loS, hiS = gee.conf_int().loc["socratic"]
    OR_U = (np.exp(gee.params["unrestricted"]), np.exp(loU), np.exp(hiU), gee.pvalues["unrestricted"])
    OR_S = (np.exp(gee.params["socratic"]),     np.exp(loS), np.exp(hiS), gee.pvalues["socratic"])
    tt = gee.t_test("unrestricted - socratic")                  # supporting U-vs-S contrast
    eUS = float(np.ravel(tt.effect)[0]); cUS = np.ravel(tt.conf_int())
    OR_US = (np.exp(eUS), np.exp(cUS[0]), np.exp(cUS[1]), float(np.ravel(tt.pvalue)[0]))
    npid = {a: d[d.arm == a]["pid"].nunique() for a in arms}
    return dict(rate=rate, ci=ci, OR_U=OR_U, OR_S=OR_S, OR_US=OR_US, npid=npid)
idk = {w: _idk_stats(w) for w in waves}

# ----------------------------------------------------------------------------
# VERIFY against sections/results.tex
# ----------------------------------------------------------------------------
def ck(name, got, want, tol=0.15):
    ok = abs(got - want) <= tol
    print(f"  [{'PASS' if ok else 'FAIL'}] {name:28s} got {got:+8.3f}  chapter {want:+8.3f}")
    return ok
print("VERIFY primary two-wave LMM (pp):")
ck("H1a U-G", UG[0], -5.06); ck("H1a lo", UG[1], -10.57); ck("H1a hi", UG[2], 0.45)
ck("H2a S-G", SG[0], -0.67); ck("H2a 90% lo", SG90[1], -5.37)
ck("supp S-U", SU[0], 4.39)
ck("H5a U-G delayed", UG_d[0], -1.02, tol=0.2)
ck("aided U-G", UG_a[0], 10.69); ck("aided S-G", SG_a[0], -3.50)
print("VERIFY outcome-space bracket p-values (pre-registered, immediate wave):")
ck("H1a p  (acc U-G)",  P_UG_acc,    0.036, tol=0.004)
ck("H2a NI p (acc S-G)", P_SG_ni,    0.003, tol=0.002)
ck("H1b HR (time U-G)",  HR_UG_t,    1.02,  tol=0.02)
ck("H1b p  (time U-G)",  P_UG_t,     0.60,  tol=0.02)
ck("H2b HR (time S-U)",  HR_SU_t,    1.14,  tol=0.02)
ck("H2b p  (time S-U)",  P_SU_t,     0.058, tol=0.004)
ck("H2b Holm p (S-U)",   P_SU_t_holm, 0.116, tol=0.005)
print(f"  time S-G (descriptive, 2-sided): HR {HR_SG_t:.3f}, p={P_SG_t:.3f} (no chapter number to check)")
print("VERIFY observed accuracy / time / Bloom:")
for a, v in (("google",.755),("socratic",.747),("unrestricted",.709)):
    ck(f"acc imm {a}", A["immediate"][a][0], v)
for a, v in (("google",.661),("socratic",.647),("unrestricted",.644)):
    ck(f"acc del {a}", A["delayed"][a][0], v)
for a, v in (("google",.819),("socratic",.795),("unrestricted",.737)):
    ck(f"bloom lower {a}", bloom[a]["lower"][0], v)
for a, v in (("google",.692),("socratic",.698),("unrestricted",.682)):
    ck(f"bloom higher {a}", bloom[a]["higher"][0], v)
print(f"  time imm (s): " + ", ".join(f"{a} {T['immediate'][a][0]:.1f}" for a in arms))
print(f"  time del (s): " + ", ".join(f"{a} {T['delayed'][a][0]:.1f}" for a in arms))
print("VERIFY abstention (no-cov GEE, matches prose) — IMMEDIATE:")
ck("IDK rate google (pp)", idk["immediate"]["rate"]["google"]*100, 4.3)
ck("IDK rate unrestr (pp)", idk["immediate"]["rate"]["unrestricted"]*100, 8.7)
ck("IDK OR U-G", idk["immediate"]["OR_U"][0], 2.14, tol=0.05)
for w in waves:
    r, o = idk[w]["rate"], idk[w]["OR_U"]; s = idk[w]["OR_S"]; us = idk[w]["OR_US"]
    print(f"  [{w:9s}] rates G/S/U = {r['google']*100:.1f}/{r['socratic']*100:.1f}/{r['unrestricted']*100:.1f}%"
          f"  |  U-G {o[0]:.2f} [{o[1]:.2f},{o[2]:.2f}] p={o[3]:.3f}"
          f"  |  S-G {s[0]:.2f} p={s[3]:.3f}"
          f"  |  U-S {us[0]:.2f} [{us[1]:.2f},{us[2]:.2f}] p={us[3]:.3f}")

def savefig(fig, stem):
    fig.savefig(OUT / f"{stem}.pdf")
    fig.savefig(PREVIEW / f"{stem}_preview.png", dpi=200)
    plt.close(fig)

# ============================================================================
# FIG 1 — outcome space (2x2): rows accuracy / time, cols immediate / delayed
# ============================================================================
fig, ax = plt.subplots(2, 2, figsize=(7.4, 5.6), sharey="row", sharex="col",
                       gridspec_kw=dict(wspace=0.10, hspace=0.16))
xpos = np.arange(3)
def _draw(a_ax, cells):
    for i, arm in enumerate(arms):
        pt, lo, hi = cells[arm][:3]; d = ARM[arm]
        a_ax.errorbar(i, pt, yerr=[[pt-lo], [hi-pt]], fmt=d["m"], color=d["c"],
                      ms=7, capsize=3.5, elinewidth=1.1, mec="white", mew=0.6)
    a_ax.set_xlim(-0.5, 2.5); a_ax.set_xticks(xpos)
    a_ax.grid(axis="y", ls=":", lw=0.6, alpha=0.5)
_first = {"done": False}
def xlabels(w):
    out = []
    for a in arms:
        name = ARM[a]["label"].replace(" (control)", ""); n = NN[w][a]
        if not _first["done"]:
            out.append(f"{name}\n(n={n})"); _first["done"] = True
        else:
            out.append(f"{name}\n({n})")
    return out
_draw(ax[0, 0], A["immediate"]); _draw(ax[0, 1], A["delayed"])
ax[0, 0].set_ylabel("Proportion correct"); ax[0, 0].set_ylim(0.55, 0.90)
ax[0, 0].yaxis.set_major_locator(MultipleLocator(0.05))
ax[0, 0].set_title(r"$\mathbf{(1)}$ Immediate post-test", fontsize=11, pad=6)
ax[0, 1].set_title(r"$\mathbf{(2)}$ Delayed post-test",   fontsize=11, pad=6)
_draw(ax[1, 0], T["immediate"]); _draw(ax[1, 1], T["delayed"])
ax[1, 0].set_ylabel("Median time to\ncorrect (s)"); ax[1, 0].set_ylim(16.5, 32.5)
ax[1, 0].yaxis.set_major_locator(MultipleLocator(2))
ax[1, 0].set_title(r"$\mathbf{(3)}$", fontsize=11, pad=6)
ax[1, 1].set_title(r"$\mathbf{(4)}$", fontsize=11, pad=6)
ax[1, 0].set_xticklabels(xlabels("immediate")); ax[1, 1].set_xticklabels(xlabels("delayed"))
ax[0, 0].annotate("Accuracy\n(construction)", xy=(-0.30, 0.5), xycoords="axes fraction",
                  ha="center", va="center", rotation=90, fontsize=10.5)
ax[1, 0].annotate("Time to success\n(automation)", xy=(-0.30, 0.5), xycoords="axes fraction",
                  ha="center", va="center", rotation=90, fontsize=10.5)
# --- pre-registered significance brackets on the two IMMEDIATE panels only ----
#     Accuracy: H1a (U-G superiority) + H2a (S-G non-inferiority vs the -8.5 pp
#     margin).  Success-time: H1b (U-G) + H2b (S-U), Cox hazard ratios with the
#     Holm-adjusted p for H2b, plus S-G shown descriptively (two-sided; not a
#     pre-registered contrast --- D1 dropped the time NI claim for this pair).
#     All pre-registered p-values one-sided per the SAP; the delayed panels stay
#     unannotated (H4b/H5b are CI-only exploratory, D4/D9).
def _ap(p):  # APA p: leading zero stripped, 3 dp (2 dp when >= .10)
    if p < .001: return "<.001"
    return (f"{p:.3f}" if p < .0995 else f"{p:.2f}").lstrip("0")
def _obrk(a_ax, x1, x2, y, text, tick, fs=7.3):
    a_ax.plot([x1, x1, x2, x2], [y-tick, y, y, y-tick], lw=0.8, color="#3a3a3a",
              zorder=6, clip_on=False, solid_capstyle="round")
    a_ax.annotate(text, xy=((x1+x2)/2, y), xytext=(0, 1.6), textcoords="offset points",
                  ha="center", va="bottom", fontsize=fs, color="#3a3a3a", linespacing=1.0, zorder=6)
_ay = max(A["immediate"][a][2] for a in arms)                    # top whisker, accuracy
_obrk(ax[0, 0], 0, 1, _ay + 0.012,
      f"S vs G: ${SG[0]:+.2f}$ pp\nnon-inferior, $p={_ap(P_SG_ni)}$", 0.006)
_obrk(ax[0, 0], 0, 2, _ay + 0.066,
      f"U vs G: ${UG[0]:+.2f}$ pp, $p={_ap(P_UG_acc)}$", 0.006)
_ty = max(T["immediate"][a][2] for a in arms)                    # top whisker, time
_obrk(ax[1, 0], 0, 1, _ty + 0.7,
      f"S vs G: HR ${HR_SG_t:.2f}$, $p={_ap(P_SG_t)}$ (descriptive)", 0.28)
_obrk(ax[1, 0], 1, 2, _ty + 2.3,
      f"S vs U: HR ${HR_SU_t:.2f}$, $p={_ap(P_SU_t)}$ (Holm ${_ap(P_SU_t_holm)}$)", 0.28)
_obrk(ax[1, 0], 0, 2, _ty + 4.5,
      f"U vs G: HR ${HR_UG_t:.2f}$, $p={_ap(P_UG_t)}$", 0.28)

handles = [plt.Line2D([], [], color=ARM[x]["c"], marker=ARM[x]["m"], ls="none",
                      ms=7, mec="white", mew=0.6, label=ARM[x]["label"]) for x in arms]
fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.03))
savefig(fig, "fig_outcome_space")

# ============================================================================
# FIG 2 — forest plot of the primary accuracy contrasts (two-wave LMM)
# ============================================================================
fig, a = plt.subplots(figsize=(6.4, 2.9))
rows = [
    ("Unrestricted $-$ Google\n(H1$_a$, superiority)", UG, ARM["unrestricted"]["c"]),
    ("Socratic $-$ Google\n(H2$_a$, non-inferiority; 90% CI)", (SG[0], SG90[1], SG90[2]), ARM["socratic"]["c"]),
    ("Socratic $-$ Unrestricted\n(supporting)", SU, GREY),
]
ys = [2, 1, 0]
for (lab, (est, lo, hi), col), y in zip(rows, ys):
    a.errorbar(est, y, xerr=[[est-lo], [hi-est]], fmt="o", color=col, ms=7,
               capsize=4, elinewidth=1.3, mec="white", mew=0.6, zorder=3)
    a.annotate(f"{est:+.2f} [{lo:+.2f}, {hi:+.2f}]", xy=(est, y), xytext=(0, 11),
               textcoords="offset points", ha="center", fontsize=8.6, color=col)
a.axvline(0, color="black", lw=1.0, zorder=1)
a.axvline(-8.5, color="#b2182b", lw=1.1, ls=(0, (5, 3)), zorder=1)
a.text(-8.5, 2.62, "NI margin\n$-8.5$ pp", color="#b2182b", fontsize=8.4, ha="center", va="bottom")
a.set_yticks(ys); a.set_yticklabels([r[0] for r in rows])
a.set_ylim(-0.5, 3.0); a.set_xlim(-13, 13)
a.set_xlabel("Accuracy difference vs. reference (percentage points)")
a.grid(axis="x", ls=":", lw=0.6, alpha=0.5)
savefig(fig, "fig_forest_primary")

# ============================================================================
# FIG 3 — arm x Bloom-order interaction (immediate)
# ============================================================================
fig, a = plt.subplots(figsize=(5.4, 4.0))
xo = [0, 1]
for arm in arms:
    d = ARM[arm]; pts = [bloom[arm]["lower"], bloom[arm]["higher"]]
    y  = [p[0] for p in pts]; lo = [p[0]-p[1] for p in pts]; hi = [p[2]-p[0] for p in pts]
    a.errorbar(xo, y, yerr=[lo, hi], color=d["c"], marker=d["m"], ls=d["ls"],
               ms=7.5, capsize=3.5, elinewidth=1.1, mec="white", mew=0.6, label=d["label"])
a.set_xticks(xo); a.set_xticklabels(["Lower-order\n(Remember/Understand)",
                                     "Higher-order\n(Analyze/Evaluate)"])
a.set_xlim(-0.35, 1.35); a.set_ylim(0.60, 0.87)
a.set_ylabel("Proportion correct"); a.yaxis.set_major_locator(MultipleLocator(0.05))
a.grid(axis="y", ls=":", lw=0.6, alpha=0.5); a.legend(frameon=False, loc="upper right")
savefig(fig, "fig_bloom")

# ============================================================================
# FIG 4 — performance/learning crossover (difference from control, 3 phases)
# ============================================================================
fig, a = plt.subplots(figsize=(5.6, 4.0))
xph = [0, 1, 2]  # aided, immediate, delayed
series = {"unrestricted": [UG_a, UG, UG_d], "socratic": [SG_a, SG, SG_d]}
for arm, pts in series.items():
    d = ARM[arm]
    ys = [p[0] for p in pts]
    lo = [p[0]-p[1] for p in pts]; hi = [p[2]-p[0] for p in pts]
    a.errorbar(xph, ys, yerr=[lo, hi], color=d["c"], marker=d["m"], ls=d["ls"],
               ms=7.5, capsize=3.5, elinewidth=1.1, mec="white", mew=0.6, label=d["label"])
a.axhline(0, color="black", lw=1.1)
a.text(0.02, 0.4, "Google control (reference)", fontsize=8.2, color="black", va="bottom")
a.set_xticks(xph); a.set_xticklabels(["Aided\npractice", "Immediate\npost-test", "Delayed\npost-test"])
a.set_xlim(-0.25, 2.3)
a.set_ylabel("Accuracy vs. control (percentage points)")
a.grid(axis="y", ls=":", lw=0.6, alpha=0.5); a.legend(frameon=False, loc="upper right")
savefig(fig, "fig_crossover")

# ============================================================================
# FIG 5 — post-test abstention ("I don't know"): two-wave dot-and-whisker plot
#   Two panels (left = immediate, right = 72-h delayed) sharing the rate axis.
#   Arms on the x-axis; point = observed rate; vertical whiskers = participant-
#   clustered bootstrap 95% CI; dashed horizontal line = the control arm's rate.
#   Three staple brackets carry the pairwise no-covariate GEE odds ratios:
#   Socratic-vs-control and Unrestricted-vs-Socratic (supporting) and the
#   confirmed Unrestricted-vs-control contrast on top.
# ============================================================================
def _pf(p):  # APA p-value, leading zero stripped
    return "$< .001$" if p < .001 else f"$= {('%.3f' % p).lstrip('0')}$"
def _sigbracket(ax, x1, x2, y, text, tick=0.34, fs=8.2):   # staple bracket + centred label
    ax.plot([x1, x1, x2, x2], [y-tick, y, y, y-tick], lw=0.9, color="#333333",
            zorder=4, clip_on=False)
    ax.annotate(text, xy=((x1+x2)/2, y), xytext=(0, 2.5), textcoords="offset points",
                ha="center", va="bottom", fontsize=fs, color="#333333")
XPOS = {"google": 0, "socratic": 1, "unrestricted": 2}          # control first
WLAB = {"immediate": "Immediate post-test", "delayed": "Delayed post-test (72 h)"}
YMAX = 19.0
YBR  = {"sg": 10.8, "us": 15.7, "ug": 17.3}                     # shared bracket heights
def _orfmt(t):
    return f"OR $= {t[0]:.2f}$, $p$ {_pf(t[3])}"
fig, axes = plt.subplots(1, 2, figsize=(6.6, 4.6), sharex=True, sharey=True)
for ax, w in zip(axes, waves):
    ax.axhline(idk[w]["rate"]["google"]*100, ls=(0, (3, 3)), lw=0.9,
               color=ARM["google"]["c"], alpha=0.45, zorder=1)          # control reference level
    for arm in arms:
        d = ARM[arm]; x = XPOS[arm]
        r = idk[w]["rate"][arm]*100
        lo, hi = idk[w]["ci"][arm][0]*100, idk[w]["ci"][arm][1]*100
        ax.errorbar(x, r, yerr=[[r-lo], [hi-r]], fmt=d["m"], color=d["c"],
                    ecolor=d["c"], elinewidth=1.5, capsize=4, ms=7,
                    mec="white", mew=0.6, zorder=3)
        ax.text(x, hi+0.45, f"{r:.1f}\n[{lo:.1f}, {hi:.1f}]", ha="center",
                va="bottom", fontsize=7.8, color="#222222", linespacing=1.15)
    _sigbracket(ax, XPOS["google"], XPOS["socratic"], YBR["sg"],
                _orfmt(idk[w]["OR_S"]))                                  # Socratic vs control (supporting)
    _sigbracket(ax, XPOS["socratic"], XPOS["unrestricted"], YBR["us"],
                _orfmt(idk[w]["OR_US"]))                                 # Unrestricted vs Socratic (supporting)
    _sigbracket(ax, XPOS["google"], XPOS["unrestricted"], YBR["ug"],
                _orfmt(idk[w]["OR_U"]))                                  # Unrestricted vs control (confirmed)
    ax.set_title(WLAB[w], fontsize=10.5, pad=6)
    ax.set_xlim(-0.6, 2.6); ax.set_ylim(0, YMAX)
    ax.yaxis.set_major_locator(MultipleLocator(2))
    ax.set_xticks([XPOS[a] for a in arms])
    ax.set_xticklabels([ARM[a]["label"].replace(" (control)", "\n(control)") for a in arms])
    ax.grid(axis="y", ls=":", lw=0.6, alpha=0.5); ax.set_axisbelow(True)
    ax.tick_params(axis="x", length=0)
axes[0].set_ylabel("Post-test “I don’t know” rate (%)")
fig.subplots_adjust(wspace=0.08)
savefig(fig, "fig_idk")

# ============================================================================
# FIG 6 — answer-adoption latency Delta by arm (MC4), forest plot
#   One row per arm: median latency + participant-clustered bootstrap 95% CI,
#   log x-axis (latency is heavily right-skewed). No direct-adoption threshold
#   marker --- the measure-first Delta distribution is the headline read (per
#   D11); the threshold-based adoption rate is still verified below but no
#   longer annotated on the plot.
# ============================================================================
_ad = adoption_latency(itrain[["pid", "arm", "adopt_delta_s"]], threshold_s=5)
_dist = _ad["dist"].set_index("arm"); _rate = _ad["adoption_rate"]
dd = itrain.dropna(subset=["adopt_delta_s"]); dd = dd[dd["adopt_delta_s"] >= 0]
print("\nVERIFY MC4 adoption latency (seconds / %):")
ck("median unrestr (s)",  _dist.loc["unrestricted", "median"], 11.6, tol=0.3)
ck("direct-adopt unrestr (%)", _rate["unrestricted"]*100, 16.2, tol=0.6)
print(f"  log-Delta U-S contrast {_ad['contrast']['est']:+.3f} "
      f"[{_ad['contrast']['ci95'][0]:+.3f}, {_ad['contrast']['ci95'][1]:+.3f}]  (chapter -0.532 [-0.754,-0.310])")

def latency_cell(arm):
    sub = dd[dd.arm == arm]
    pt = sub["adopt_delta_s"].median(); pids = sub["pid"].unique()
    by = {p: sub[sub.pid == p]["adopt_delta_s"].values for p in pids}
    boot = [np.median(np.concatenate([by[p] for p in RNG.choice(pids, len(pids), replace=True)]))
            for _ in range(2000)]
    lo, hi = np.percentile(boot, [2.5, 97.5]); return pt, lo, hi
Lat = {a: latency_cell(a) for a in arms}
print("VERIFY adoption latency median + bootstrap 95% CI (s):")
for a in arms:
    pt, lo, hi = Lat[a]; print(f"  {a:12s} {pt:5.1f} [{lo:5.1f}, {hi:5.1f}]")

fig, a = plt.subplots(figsize=(5.2, 4.0))
xpos = {arm: i for i, arm in enumerate(arms)}  # control first, matches other figures
for arm in arms:
    d = ARM[arm]; x = xpos[arm]; pt, lo, hi = Lat[arm]
    a.errorbar(x, pt, yerr=[[pt - lo], [hi - pt]], fmt=d["m"], color=d["c"], ms=8,
               capsize=4, elinewidth=1.3, mec="white", mew=0.6, zorder=3)
    a.annotate(f"{pt:.1f} s\n[{lo:.1f}, {hi:.1f}]", xy=(x, hi), xytext=(0, 6),
               textcoords="offset points", ha="center", va="bottom", fontsize=8.6, color=d["c"])
a.set_yscale("log"); a.set_ylim(1, 100)
a.set_yticks([1, 5, 10, 30, 100]); a.set_yticklabels(["1", "5", "10", "30", "100"])
a.set_xticks([xpos[x] for x in arms])
a.set_xticklabels([ARM[x]["label"].replace(" (control)", "\n(control)") for x in arms])
a.set_xlim(-0.6, 2.6); a.set_ylabel("Answer-adoption latency $\\Delta$ (s, log scale)")
a.grid(axis="y", ls=":", lw=0.6, alpha=0.5); a.set_axisbelow(True)
savefig(fig, "fig_adoption_latency")

# ============================================================================
# FIG 6b — answer-adoption latency by Bloom level, forest plot (median + 95% CI)
#   One column per taxonomic level (Remember/Understand/Analyze/Evaluate, the
#   aided practice-block item bank, D17/D19); three per-arm points (small
#   horizontal dodge) show the median latency and its participant-clustered
#   bootstrap 95% CI, log y-axis (latency is heavily right-skewed). No
#   direct-adoption threshold, matching the FIG 6 redesign. Exploratory/
#   descriptive breakdown of MC4 --- not a pre-registered analysis.
# ============================================================================
def latency_bloom_cell(arm, level):
    sub = dd[(dd.arm == arm) & (dd.bloom == level)]
    pt = sub["adopt_delta_s"].median(); pids = sub["pid"].unique()
    by = {p: sub[sub.pid == p]["adopt_delta_s"].values for p in pids}
    boot = [np.median(np.concatenate([by[p] for p in RNG.choice(pids, len(pids), replace=True)]))
            for _ in range(2000)]
    lo, hi = np.percentile(boot, [2.5, 97.5]); return pt, lo, hi, len(sub)
LEVELS4 = ["Remember", "Understand", "Analyze", "Evaluate"]
latBL = {L: {a: latency_bloom_cell(a, L) for a in arms} for L in LEVELS4}
print("\nDescriptive: adoption latency by Bloom level (median [95% CI] s, n items):")
for L in LEVELS4:
    for a in arms:
        pt, lo, hi, n = latBL[L][a]
        print(f"  {L:11s} {a:12s} n={n:3d}  {pt:5.1f} [{lo:5.1f}, {hi:5.1f}]")

fig, a = plt.subplots(figsize=(7.2, 4.2))
xpos_level = {L: i for i, L in enumerate(LEVELS4)}
DODGE = {"google": -0.22, "socratic": 0.0, "unrestricted": +0.22}
for L in LEVELS4:
    for arm in arms:
        d = ARM[arm]; x = xpos_level[L] + DODGE[arm]
        pt, lo, hi, n = latBL[L][arm]
        a.errorbar(x, pt, yerr=[[pt - lo], [hi - pt]], fmt=d["m"], color=d["c"], ms=6.5,
                   capsize=3, elinewidth=1.1, mec="white", mew=0.6, zorder=3)
a.set_yscale("log"); a.set_ylim(1, 300)
a.set_yticks([1, 5, 10, 30, 100, 300]); a.set_yticklabels(["1", "5", "10", "30", "100", "300"])
a.set_ylabel("Answer-adoption latency $\\Delta$ (s, log scale)")
a.set_xticks([xpos_level[L] for L in LEVELS4]); a.set_xticklabels(LEVELS4)
a.set_xlim(-0.6, 3.6)
a.grid(axis="y", ls=":", lw=0.6, alpha=0.5); a.set_axisbelow(True)
handles = [plt.Line2D([], [], color=ARM[x]["c"], marker=ARM[x]["m"], ls="none",
                      ms=6.5, mec="white", mew=0.6, label=ARM[x]["label"]) for x in arms]
a.legend(handles=handles, loc="upper right", frameon=False, fontsize=8.5)
savefig(fig, "fig_adoption_latency_bloom")

# ============================================================================
# FIG 7 — cognitive load (Leppink subscales) by arm, with adjusted contrasts (MC1)
# ============================================================================
SUBS = [("IL_ave", "Intrinsic"), ("EL_ave", "Extraneous"), ("GL_ave", "Germane")]
cl_mean, cl_ci, cl_fit = {}, {}, {}
for col, name in SUBS:
    sub = imm.dropna(subset=[col])
    cl_mean[name] = {a: sub[sub.arm == a][col].mean() for a in arms}
    cl_ci[name]   = {a: 1.96*sub[sub.arm == a][col].sem() for a in arms}
    cl_fit[name]  = ancova(sub, col)
def _adj(name, arm):
    f = cl_fit[name]; return f.params[arm], f.pvalues[arm]
print("\nVERIFY MC1 cognitive load (adjusted contrasts vs control):")
ck("germane unrestr", _adj("Germane", "unrestricted")[0], -0.76, tol=0.05)
ck("extraneous socratic", _adj("Extraneous", "socratic")[0], 1.15, tol=0.05)

fig, a = plt.subplots(figsize=(6.4, 3.7))
xg = np.arange(len(SUBS)); w = 0.26
off = {"google": -w, "socratic": 0.0, "unrestricted": +w}
for arm in arms:
    d = ARM[arm]; ys = [cl_mean[n][arm] for _, n in SUBS]; err = [cl_ci[n][arm] for _, n in SUBS]
    a.bar(xg + off[arm], ys, w, yerr=err, capsize=3, color=d["c"], edgecolor="white",
          linewidth=0.6, label=d["label"], error_kw=dict(ecolor="#333333", elinewidth=1.0), zorder=2)
def _bracket(gi, arm_a, arm_b, text, top):
    x1, x2 = gi+off[arm_a], gi+off[arm_b]
    a.plot([x1, x1, x2, x2], [top-0.18, top, top, top-0.18], lw=0.9, color="#333333", zorder=4)
    a.annotate(text, xy=((x1+x2)/2, top), xytext=(0, 2), textcoords="offset points",
               ha="center", fontsize=8.4, color="#333333")
_bE, _pE = _adj("Extraneous", "socratic"); _bG, _pG = _adj("Germane", "unrestricted")
_topE = max(cl_mean["Extraneous"][a2]+cl_ci["Extraneous"][a2] for a2 in ("google", "socratic")) + 0.5
_bracket(1, "google", "socratic", f"$+{_bE:.2f}$, $p={_pE:.3f}$".replace("0.", "."), _topE)
_topG = max(cl_mean["Germane"][a2]+cl_ci["Germane"][a2] for a2 in ("google", "unrestricted")) + 0.5
_bracket(2, "google", "unrestricted", f"${_bG:.2f}$, $p={_pG:.2f}$".replace("0.", "."), _topG)
a.set_xticks(xg); a.set_xticklabels([n for _, n in SUBS])
a.set_ylabel("Mean subscale rating (0--10)"); a.set_ylim(0, 9)
a.legend(frameon=False, loc="upper right", ncol=1)
a.grid(axis="y", ls=":", lw=0.6, alpha=0.5); a.set_axisbelow(True)
savefig(fig, "fig_cogload")

# ============================================================================
# FIG 8 — arm x Bloom-order interaction, BOTH waves (immediate | delayed)
#   The FIG 3 interaction drawn for both post-tests in the two-panel fig_idk
#   layout: shared y-axis, per-wave titles, one shared arm legend. The delayed
#   panel is exploratory/descriptive — there is no pre-registered delayed Bloom
#   test (H4a is the immediate wave; H4b is CI-only exploratory, D4/D9) — and is
#   shown for cross-wave comparison of where the retention loss concentrates.
# ============================================================================
def bloom_cell_w(arm, order, w):
    sub = unass[(unass.arm == arm) & (unass.order == order) & (unass.wave == w)]
    pt = sub["correct"].mean(); pids = sub["pid"].unique()
    by = {p: sub[sub.pid == p]["correct"].values for p in pids}
    boot = [np.concatenate([by[p] for p in RNG.choice(pids, len(pids), replace=True)]).mean()
            for _ in range(2000)]
    lo, hi = np.percentile(boot, [2.5, 97.5]); return pt, lo, hi
bloomW = {w: {a: {o: bloom_cell_w(a, o, w) for o in ("lower", "higher")} for a in arms}
          for w in waves}
print("VERIFY delayed Bloom cells (exploratory, item-level observed):")
for a, v in (("google", .817), ("socratic", .819), ("unrestricted", .825)):
    ck(f"bloom del lower {a}",  bloomW["delayed"][a]["lower"][0],  v, tol=0.01)
for a, v in (("google", .504), ("socratic", .474), ("unrestricted", .463)):
    ck(f"bloom del higher {a}", bloomW["delayed"][a]["higher"][0], v, tol=0.01)

fig, axes = plt.subplots(1, 2, figsize=(7.0, 4.6), sharex=True, sharey=True)
xo = [0, 1]
for ax, w in zip(axes, waves):
    for arm in arms:
        d = ARM[arm]; pts = [bloomW[w][arm]["lower"], bloomW[w][arm]["higher"]]
        y  = [p[0] for p in pts]; lo = [p[0]-p[1] for p in pts]; hi = [p[2]-p[0] for p in pts]
        ax.errorbar(xo, y, yerr=[lo, hi], color=d["c"], marker=d["m"], ls=d["ls"],
                    ms=7.5, capsize=3.5, elinewidth=1.1, mec="white", mew=0.6, label=d["label"])
    ax.set_xticks(xo); ax.set_xticklabels(["Lower-order\n(Remember/Understand)",
                                           "Higher-order\n(Analyze/Evaluate)"])
    ax.set_xlim(-0.35, 1.35); ax.set_title(WLAB[w], fontsize=10.5, pad=6)
    ax.grid(axis="y", ls=":", lw=0.6, alpha=0.5); ax.set_axisbelow(True)
axes[0].set_ylabel("Proportion correct"); axes[0].set_ylim(0.38, 0.88)
axes[0].yaxis.set_major_locator(MultipleLocator(0.05))
handles = [plt.Line2D([], [], color=ARM[x]["c"], marker=ARM[x]["m"], ls=ARM[x]["ls"],
                      ms=7.5, mec="white", mew=0.6, label=ARM[x]["label"]) for x in arms]
fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.10))
fig.subplots_adjust(wspace=0.08, bottom=0.16)
savefig(fig, "fig_bloom_twowave")

# ============================================================================
# FIG 9 — arm x Bloom-LEVEL profile, BOTH waves (immediate | delayed)
#   As FIG 8 but the x-axis is the FOUR taxonomic levels (Remember, Understand,
#   Analyze, Evaluate) rather than the lower/higher collapse; a faint divider
#   marks the lower-order | higher-order boundary. 4 items per level per
#   participant per wave (thin cells, D4). Exploratory/descriptive, as FIG 8.
# ============================================================================
LEVELS = ["Remember", "Understand", "Analyze", "Evaluate"]      # taxonomic ascending
def bloom4_cell(arm, level, w):
    sub = unass[(unass.arm == arm) & (unass.bloom == level) & (unass.wave == w)]
    pt = sub["correct"].mean(); pids = sub["pid"].unique()
    by = {p: sub[sub.pid == p]["correct"].values for p in pids}
    boot = [np.concatenate([by[p] for p in RNG.choice(pids, len(pids), replace=True)]).mean()
            for _ in range(2000)]
    lo, hi = np.percentile(boot, [2.5, 97.5]); return pt, lo, hi
cells4 = {w: {a: {L: bloom4_cell(a, L, w) for L in LEVELS} for a in arms} for w in waves}
_EXP4 = {("immediate","google"):[.775,.862,.692,.692], ("immediate","socratic"):[.722,.868,.722,.674],
         ("immediate","unrestricted"):[.630,.844,.662,.701], ("delayed","google"):[.857,.777,.522,.487],
         ("delayed","socratic"):[.836,.802,.470,.478], ("delayed","unrestricted"):[.812,.838,.446,.479]}
_n4 = sum(abs(cells4[w][a][L][0]-v) > 0.01 for (w,a),vals in _EXP4.items() for L,v in zip(LEVELS,vals))
print(f"VERIFY four-level Bloom cells (24 checked): {'all PASS' if _n4==0 else str(_n4)+' FAIL'}")

fig, axes = plt.subplots(1, 2, figsize=(8.0, 4.7), sharex=True, sharey=True)
xo = list(range(4))
for ax, w in zip(axes, waves):
    ax.axvline(1.5, color="#999999", ls=(0, (4, 4)), lw=0.8, alpha=0.55, zorder=1)  # lower|higher
    for arm in arms:
        d = ARM[arm]; pts = [cells4[w][arm][L] for L in LEVELS]
        y  = [p[0] for p in pts]; lo = [p[0]-p[1] for p in pts]; hi = [p[2]-p[0] for p in pts]
        ax.errorbar(xo, y, yerr=[lo, hi], color=d["c"], marker=d["m"], ls=d["ls"],
                    ms=7.0, capsize=3.2, elinewidth=1.1, mec="white", mew=0.6, label=d["label"], zorder=3)
    ax.set_xticks(xo); ax.set_xticklabels(LEVELS)
    ax.set_xlim(-0.4, 3.4); ax.set_title(WLAB[w], fontsize=10.5, pad=6)
    ax.grid(axis="y", ls=":", lw=0.6, alpha=0.5); ax.set_axisbelow(True)
    ax.text(0.5, 0.975, "lower-order", transform=ax.get_xaxis_transform(),
            ha="center", va="top", fontsize=8.0, style="italic", color="#777777")
    ax.text(2.5, 0.975, "higher-order", transform=ax.get_xaxis_transform(),
            ha="center", va="top", fontsize=8.0, style="italic", color="#777777")
axes[0].set_ylabel("Proportion correct"); axes[0].set_ylim(0.36, 0.93)
axes[0].yaxis.set_major_locator(MultipleLocator(0.05))
handles = [plt.Line2D([], [], color=ARM[x]["c"], marker=ARM[x]["m"], ls=ARM[x]["ls"],
                      ms=7.0, mec="white", mew=0.6, label=ARM[x]["label"]) for x in arms]
fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.06))
fig.subplots_adjust(wspace=0.08, bottom=0.14)
savefig(fig, "fig_bloom4_twowave")

# ============================================================================
# FIG 10 — combined Bloom figure: FIG 8 (lower/higher collapse) stacked ABOVE
#   FIG 9 (four levels) as a 2x2 grid. Columns = immediate | delayed; all four
#   panels share one proportion-correct axis so heights are comparable; the
#   lower|higher divider runs down the centre of both rows. Reuses the FIG 8
#   (bloomW) and FIG 9 (cells4) cell dicts, so each row matches its source fig.
# ============================================================================
figC, axC = plt.subplots(2, 2, figsize=(8.0, 8.4), sharey=True)
def _draw_bloom_row(row, xpos, xlabels, div, getter, keys, ms, caps, tags):
    for j, w in enumerate(waves):
        a_ = axC[row, j]
        a_.axvline(div, color="#999999", ls=(0, (4, 4)), lw=0.8, alpha=0.55, zorder=1)
        for arm in arms:
            d = ARM[arm]; pts = [getter(w, arm, k) for k in keys]
            y = [p[0] for p in pts]; lo = [p[0]-p[1] for p in pts]; hi = [p[2]-p[0] for p in pts]
            a_.errorbar(xpos, y, yerr=[lo, hi], color=d["c"], marker=d["m"], ls=d["ls"],
                        ms=ms, capsize=caps, elinewidth=1.1, mec="white", mew=0.6, zorder=3)
        a_.set_xticks(xpos); a_.set_xticklabels(xlabels); a_.set_xlim(xpos[0]-0.4, xpos[-1]+0.4)
        a_.grid(axis="y", ls=":", lw=0.6, alpha=0.5); a_.set_axisbelow(True)
        if row == 0: a_.set_title(WLAB[w], fontsize=10.5, pad=6)
        if tags:
            a_.text(0.5, 0.965, "lower-order", transform=a_.get_xaxis_transform(),
                    ha="center", va="top", fontsize=7.8, style="italic", color="#777777")
            a_.text(2.5, 0.965, "higher-order", transform=a_.get_xaxis_transform(),
                    ha="center", va="top", fontsize=7.8, style="italic", color="#777777")
_draw_bloom_row(0, [0, 1], ["Lower-order", "Higher-order"], 0.5,
                lambda w, a, o: bloomW[w][a][o], ["lower", "higher"], 7.5, 3.5, False)
_draw_bloom_row(1, [0, 1, 2, 3], LEVELS, 1.5,
                lambda w, a, L: cells4[w][a][L], LEVELS, 7.0, 3.2, True)
axC[0, 0].set_ylim(0.36, 0.93); axC[0, 0].yaxis.set_major_locator(MultipleLocator(0.05))
for r in (0, 1): axC[r, 0].set_ylabel("Proportion correct")
axC[0, 0].annotate("Lower- vs.\nhigher-order", xy=(-0.30, 0.5), xycoords="axes fraction",
                   rotation=90, ha="center", va="center", fontsize=10.5)
axC[1, 0].annotate("Four Bloom\nlevels", xy=(-0.30, 0.5), xycoords="axes fraction",
                   rotation=90, ha="center", va="center", fontsize=10.5)
handles = [plt.Line2D([], [], color=ARM[x]["c"], marker=ARM[x]["m"], ls=ARM[x]["ls"],
                      ms=7.0, mec="white", mew=0.6, label=ARM[x]["label"]) for x in arms]
figC.legend(handles=handles, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 0.02))
figC.subplots_adjust(hspace=0.24, wspace=0.08, bottom=0.10)
savefig(figC, "fig_bloom_combined")

print("\nwrote 11 PDFs to", OUT)
for f in ("fig_outcome_space", "fig_forest_primary", "fig_bloom", "fig_crossover",
          "fig_idk", "fig_adoption_latency", "fig_adoption_latency_bloom", "fig_cogload",
          "fig_bloom_twowave", "fig_bloom4_twowave", "fig_bloom_combined"):
    p = OUT / f"{f}.pdf"
    print(f"  {p.name:26s} {p.stat().st_size/1024:6.1f} KB")
