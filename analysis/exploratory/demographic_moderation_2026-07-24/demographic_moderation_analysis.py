#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
EXPLORATORY demographic moderation analysis - immediate wave only.  2026-07-24.

*** EVERYTHING IN THIS SCRIPT IS EXPLORATORY / HYPOTHESIS-GENERATING. ***
*** NOTHING HERE IS PRE-REGISTERED, CONFIRMATORY, OR BEARS ON THE     ***
*** TRIAL'S PRIMARY (SAP) CONCLUSIONS.                                ***

Question: do Prolific demographic characteristics moderate the arm effect
(google / socratic / unrestricted) on immediate unaided post-test accuracy
(and, secondarily, on "I don't know" abstention)?

Data provenance (deliberate design decision):
  - Outcomes + covariates come from the SAP pipeline's own pickled frames
    (~/Downloads/analysis_frames_2026-07-21/, written by
    rct_data_literacy_analysis_4_FINAL_2026-07-21.ipynb). This reuses the
    trial's exact analysable-set filter (Finished & consent & dedup &
    researcher-PID removal & >=1 immediate item), its exact answer-key
    scoring (16 immediate 'sa' items), the key-scored Mini-VLAT covariate
    (the survey's own minivlat_score column is an attempts count - known
    bug), and the AIUse (Q71) covariate. Re-deriving any of that from the
    merged CSV would risk silent divergence from the trial's numbers.
  - Demographics come from the demo__* columns of
    ~/Downloads/merged_immediate_demographics_2026-07-20.csv (Prolific
    export merged onto the Qualtrics export by PROLIFIC_PID; 3 Qualtrics
    header rows, first row = names).

Missing-demographics handling: complete-case per moderator. The gap is
export-coverage / consent-revocation driven (administrative, not outcome
driven); match rates are arm-balanced; and imputing the *moderator* in a
moderation-discovery analysis would manufacture the very quantity under
study. Representativeness of the matched subset is checked empirically.

Models: OLS on participant-level accuracy (proportion of 16 items) with
HC3 robust SEs - the same outcome scale as the SAP's ANCOVA/LMM.
  acc ~ socratic + unrestricted + M + socratic:M + unrestricted:M
        + minivlat_c + aiuse_c
Moderation test = robust Wald F on the two interaction terms (omnibus).
Freedman-Lane residual-permutation p (B=2000) as a small-sample check for
any moderator with omnibus p < .10. Multiplicity: Benjamini-Hochberg FDR
across the family of omnibus tests (one family per outcome).

Run:  ~/opt/anaconda3/envs/course/bin/python demographic_moderation_analysis.py
"""

import sys
import numpy as np
import pandas as pd
import scipy.stats as st
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

pd.set_option("display.width", 160)
np.set_printoptions(suppress=True)

SEED = 2026
B_PERM = 2000
HOME = "/Users/brunokneffel"
FRAMES = f"{HOME}/Downloads/analysis_frames_2026-07-21"
CSV = f"{HOME}/Downloads/merged_immediate_demographics_2026-07-20.csv"
OUT = f"{HOME}/Downloads/demographic_moderation_2026-07-24"

SENTINELS = {"CONSENT_REVOKED", "DATA_EXPIRED", "Prefer not to say"}

# Explicit occupational collapse: IT / software / data roles (Prolific's own
# role taxonomy strings, matched exactly). Deliberately excluded as ambiguous
# (not clearly IT/data): Quality Assurance Specialist, UX/UI Designer,
# Product Designer, Graphic Designer, Business Analyst, Research Scientist
# (STEM), Market Research Analyst.
TECH_ROLES = {
    "Software Engineer / Developer", "Data Analyst", "IT Project Manager",
    "Web Developer", "Data Engineer", "IT Quality / Testing Specialist",
    "DevOps Engineer", "Systems Administrator",
    "IT Architect / Systems Designer", "Database Administrator (DBA)",
    "Chief Technology Officer (CTO)", "AI / Machine Learning Engineer",
    "AI Research Scientist",
}

BANNER = (
    "=" * 78 + "\nEXPLORATORY, NON-PRE-REGISTERED, HYPOTHESIS-GENERATING ANALYSIS ONLY\n"
    "Not confirmatory; does not bear on the trial's pre-registered conclusions.\n" + "=" * 78
)


def sci(p):
    return "<.0001" if p < 1e-4 else f"{p:.4f}"


# ---------------------------------------------------------------------------
# 1. Build the analysis dataset
# ---------------------------------------------------------------------------

def build_dataset():
    people = pd.read_pickle(f"{FRAMES}/people.pkl")
    acc_pw = pd.read_pickle(f"{FRAMES}/acc_pw.pkl")
    items = pd.read_pickle(f"{FRAMES}/items_unassisted.pkl")

    imm = acc_pw[acc_pw.wave == "immediate"][["pid", "acc", "n_items", "n_correct"]]
    idk = (items[items.wave == "immediate"].groupby("pid")["idk"].mean()
           .rename("idk_rate").reset_index())

    d = people.merge(imm, on="pid", validate="1:1").merge(idk, on="pid", how="left")

    raw = pd.read_csv(CSV, skiprows=[1, 2], dtype=str, low_memory=False)
    n_raw = len(raw)
    demo_cols = [c for c in raw.columns if c.startswith("demo__")] + ["StartDate"]
    dm = (raw[raw["demo__Participant id"].notna()]
          .drop_duplicates("PROLIFIC_PID")
          .rename(columns={"PROLIFIC_PID": "pid"})[["pid"] + demo_cols])
    # also carry StartDate for ALL pids (matched or not) for the coverage story
    sd = (raw.drop_duplicates("PROLIFIC_PID")
          .rename(columns={"PROLIFIC_PID": "pid"})[["pid", "StartDate"]]
          .rename(columns={"StartDate": "start_all"}))

    d = d.merge(dm, on="pid", how="left").merge(sd, on="pid", how="left")

    def clean(s):
        return s.where(~s.isin(SENTINELS))

    d["has_demo_row"] = d["demo__Participant id"].notna()
    d["revoked"] = d["demo__Age"].eq("CONSENT_REVOKED").fillna(False)
    d["matched"] = (d.has_demo_row & ~d.revoked).astype(int)

    # --- derived moderators ------------------------------------------------
    d["age"] = pd.to_numeric(clean(d["demo__Age"]), errors="coerce")
    d["age_c10"] = (d["age"] - d["age"].mean()) / 10.0        # per decade

    sex = clean(d["demo__Sex"])
    d["female"] = sex.map({"Female": 1.0, "Male": 0.0})

    lang = clean(d["demo__Language"])
    d["english_l1"] = (lang == "English").astype(float).where(lang.notna())

    d["uk_res"] = (clean(d["demo__Country of residence"]) == "United Kingdom") \
        .astype(float).where(clean(d["demo__Country of residence"]).notna())

    eth = clean(d["demo__Ethnicity simplified"])
    d["nonwhite"] = eth.map(lambda x: np.nan if pd.isna(x) else (0.0 if x == "White" else 1.0))
    d["black"] = eth.map(lambda x: np.nan if pd.isna(x) else (1.0 if x == "Black" else 0.0))

    emp = clean(d["demo__Employment status"])
    d["parttime"] = emp.map({"Part-Time": 1.0, "Full-Time": 0.0})

    role = clean(d["demo__Current job role"])
    d["tech_job"] = role.map(lambda x: np.nan if pd.isna(x) else float(x in TECH_ROLES))

    d["student"] = clean(d["demo__Student status"]).map({"Yes": 1.0, "No": 0.0})

    appr = pd.to_numeric(clean(d["demo__Total approvals"]), errors="coerce")
    d["log10_appr"] = np.log10(appr.clip(lower=1))
    d["appr_c"] = d["log10_appr"] - d["log10_appr"].mean()

    d["soc"] = d["socratic"].astype(float)
    d["unr"] = d["unrestricted"].astype(float)

    return d, n_raw


# ---------------------------------------------------------------------------
# 2. Model machinery
# ---------------------------------------------------------------------------

def design(sub, mcol, adjusted=True):
    X = pd.DataFrame({
        "const": 1.0,
        "soc": sub["soc"], "unr": sub["unr"], "m": sub[mcol],
        "soc_m": sub["soc"] * sub[mcol], "unr_m": sub["unr"] * sub[mcol],
    })
    if adjusted:
        X["mv"] = sub["minivlat_c"]
        X["ai"] = sub["aiuse_c"]
    return X


def fit_moderation(d, mcol, outcome="acc", adjusted=True):
    need = ["soc", "unr", mcol, outcome] + (["minivlat_c", "aiuse_c"] if adjusted else [])
    sub = d.dropna(subset=need).copy()
    y = sub[outcome].to_numpy(float)
    X = design(sub, mcol, adjusted)
    res = sm.OLS(y, X).fit(cov_type="HC3")
    R = np.zeros((2, X.shape[1]))
    R[0, list(X.columns).index("soc_m")] = 1
    R[1, list(X.columns).index("unr_m")] = 1
    w = res.wald_test(R, use_f=True, scalar=True)
    return sub, X, res, float(w.statistic), float(w.pvalue)


def lincom(res, X, combo):
    """Estimate + robust-t 95% CI + 1df p for a linear combination.
    combo: dict column -> weight."""
    L = np.zeros(X.shape[1])
    for k, v in combo.items():
        L[list(X.columns).index(k)] = v
    t = res.t_test(L)
    lo, hi = t.conf_int()[0]
    return float(t.effect), float(lo), float(hi), float(t.pvalue), float(t.sd)


def fl_perm_p(y, X_full, X_red, int_cols, B=B_PERM, seed=SEED):
    """Freedman-Lane permutation p for the joint interaction Wald F (HC3)."""
    idx = [list(X_full.columns).index(c) for c in int_cols]
    R = np.zeros((len(idx), X_full.shape[1]))
    for k, j in enumerate(idx):
        R[k, j] = 1

    def wf(yv):
        r = sm.OLS(yv, X_full).fit(cov_type="HC3")
        return float(r.wald_test(R, use_f=True, scalar=True).statistic)

    red = sm.OLS(y, X_red).fit()
    fitted, resid = red.fittedvalues, red.resid
    obs = wf(y)
    rng = np.random.default_rng(seed)
    hits = 0
    for _ in range(B):
        ystar = fitted + rng.permutation(resid)
        if wf(ystar) >= obs:
            hits += 1
    return (hits + 1) / (B + 1)


# ---------------------------------------------------------------------------
# 3. Run
# ---------------------------------------------------------------------------

def main():
    print(BANNER)
    d, n_raw = build_dataset()

    # ---- validation anchors ----------------------------------------------
    print("\n### 0. Validation against the SAP pipeline (must match known anchors)")
    print(f"raw merged CSV rows: {n_raw}  (user brief said ~247; 245 data rows after "
          f"the two Qualtrics metadata rows)")
    print(f"analysable immediate participants (from pipeline frames): {len(d)}")
    print("arm counts:", d.arm.value_counts().to_dict(), " [anchor: 69/72/77]")
    sub_all = d.dropna(subset=["acc", "minivlat_c", "aiuse_c"])
    Xv = pd.DataFrame({"const": 1.0, "soc": sub_all.soc, "unr": sub_all.unr,
                       "mv": sub_all.minivlat_c, "ai": sub_all.aiuse_c})
    rv = sm.OLS(sub_all.acc.to_numpy(float), Xv).fit(cov_type="HC3")
    b = rv.params["unr"] * 100
    se = rv.bse["unr"] * 100
    p1 = st.t.cdf(rv.tvalues["unr"], rv.df_resid)  # one-sided (harm) as in SAP
    print(f"immediate ANCOVA U-G: {b:+.2f} pp (SE {se:.2f}), one-sided p={p1:.4f}"
          f"   [anchor: about -5.0 pp, p~.034]")
    gidk = d.groupby("arm").idk_rate.mean() * 100
    print("IDK rate by arm (%):", gidk.round(1).to_dict(), " [anchor: G~4.3, U~8.7]")

    # ---- merge coverage & representativeness -----------------------------
    print("\n### 1. Demographic-merge coverage and representativeness")
    print(f"matched (usable demographics): {int(d.matched.sum())}/218 "
          f"(demo row present: {int(d.has_demo_row.sum())}; consent-revoked: {int(d.revoked.sum())})")
    print("match rate by arm:")
    print((d.groupby("arm").matched.agg(["sum", "count", "mean"]).round(3)).to_string())
    ct = pd.crosstab(d.arm, d.matched)
    chi2, pchi, *_ = st.chi2_contingency(ct)
    print(f"arm x matched chi2 p = {pchi:.3f}")

    sd_all = pd.to_datetime(d["start_all"], errors="coerce")
    for lab, mask in [("matched", d.matched == 1), ("unmatched", d.matched == 0)]:
        print(f"  StartDate range {lab}: {sd_all[mask].min()} .. {sd_all[mask].max()}")

    for var in ["acc", "minivlat_recomputed", "aiuse"]:
        a = d.loc[d.matched == 1, var].dropna()
        bq = d.loc[d.matched == 0, var].dropna()
        sp = np.sqrt((a.var() + bq.var()) / 2)
        smd = (a.mean() - bq.mean()) / sp if sp > 0 else np.nan
        t, pt = st.ttest_ind(a, bq, equal_var=False)
        print(f"  {var}: matched {a.mean():.3f} vs unmatched {bq.mean():.3f} "
              f"(SMD {smd:+.2f}, Welch p={pt:.3f})")

    # does the ARM EFFECT differ between matched and unmatched? (key check)
    dm = d.dropna(subset=["acc", "minivlat_c", "aiuse_c"]).copy()
    Xr = pd.DataFrame({"const": 1.0, "soc": dm.soc, "unr": dm.unr, "m": dm.matched,
                       "soc_m": dm.soc * dm.matched, "unr_m": dm.unr * dm.matched,
                       "mv": dm.minivlat_c, "ai": dm.aiuse_c})
    rr = sm.OLS(dm.acc.to_numpy(float), Xr).fit(cov_type="HC3")
    Rm = np.zeros((2, Xr.shape[1])); Rm[0, 4] = 1; Rm[1, 5] = 1
    wm = rr.wald_test(Rm, use_f=True, scalar=True)
    print(f"  arm-effect x matched interaction (joint Wald): F={float(wm.statistic):.2f}, "
          f"p={float(wm.pvalue):.3f}  -> matched-subset arm effects "
          f"{'do NOT differ detectably from' if wm.pvalue > .05 else 'DIFFER from'} the unmatched remainder")

    mm = d[d.matched == 1]
    print(f"\nProlific status in analysis set: {mm['demo__Status'].value_counts().to_dict()}")
    print(f"Authenticity check 'Bots': {mm['demo__Authenticity check: Bots'].value_counts(dropna=False).to_dict()}"
          "  -> nobody flagged low; flag has no variance (cannot moderate, no exclusion needed)")

    # matched-subset baseline arm effect (context for all moderator models)
    sub_m = mm.dropna(subset=["acc", "minivlat_c", "aiuse_c"])
    Xb = pd.DataFrame({"const": 1.0, "soc": sub_m.soc, "unr": sub_m.unr,
                       "mv": sub_m.minivlat_c, "ai": sub_m.aiuse_c})
    rb = sm.OLS(sub_m.acc.to_numpy(float), Xb).fit(cov_type="HC3")
    ci = rb.conf_int()
    print(f"baseline arm effects in matched subset (n={len(sub_m)}): "
          f"U-G {rb.params['unr']*100:+.2f} pp [{ci.loc['unr',0]*100:+.2f}, {ci.loc['unr',1]*100:+.2f}], "
          f"S-G {rb.params['soc']*100:+.2f} pp [{ci.loc['soc',0]*100:+.2f}, {ci.loc['soc',1]*100:+.2f}]")

    # ---- triage -----------------------------------------------------------
    print("\n### 2. Moderator triage (tested vs not tested, and why)")
    triage = []

    def T(name, decision, reason, detail=""):
        triage.append(dict(variable=name, decision=decision, reason=reason, detail=detail))

    T("Age", "TEST (continuous, per 10 y)",
      f"n={int(mm.age.notna().sum())}, range {mm.age.min():.0f}-{mm.age.max():.0f}, "
      f"mean {mm.age.mean():.1f}, SD {mm.age.std():.1f}; good spread")
    T("Sex", "TEST (female vs male)",
      f"F {int((mm.female==1).sum())} / M {int((mm.female==0).sum())}; 1 'prefer not to say' -> missing",
      "note: arm x sex composition uneven by chance (socratic 69% male vs google ~49%)")
    T("First language English", "TEST (binary)",
      f"English {int((mm.english_l1==1).sum())} vs other {int((mm.english_l1==0).sum())}; near 50/50, "
      "survey+LLM dialogue were English for everyone (UserLanguage=EN)")
    T("Country of residence", "NOT TESTED separately",
      "phi=0.86 with first-language English; near-duplicate construct - testing both double-counts "
      "one construct and inflates the family; UK-vs-not reported descriptively only")
    T("Employment status", "TEST (part-time vs full-time)",
      f"FT {int((mm.parttime==0).sum())} / PT {int((mm.parttime==1).sum())}; everyone employed (screener)",
      "note: PT share uneven across arms by chance (google 22% vs unrestricted 42%)")
    T("Ethnicity", "TEST (White vs non-White, crude)",
      f"White {int((mm.nonwhite==0).sum())} vs non-White {int((mm.nonwhite==1).sum())} "
      f"(Black {int((mm.black==1).sum())}, Asian 8, Mixed 6, Other 2; 3 'prefer not to say' -> missing); "
      "single minority groups too sparse to test alone (Black 15/10/9 per arm), so a crude binary; "
      "flagged as heterogeneous-composition collapse")
    T("Current job role", "TEST only as IT/software/data collapse",
      f"88 distinct roles; explicit list of {len(TECH_ROLES)} tech/data roles -> "
      f"tech {int((mm.tech_job==1).sum())} vs other {int((mm.tech_job==0).sum())}; "
      "full taxonomy far too high-cardinality at this n")
    T("Prolific total approvals", "TEST (log10; auxiliary, not strictly demographic)",
      f"median {pd.to_numeric(mm['demo__Total approvals'], errors='coerce').median():.0f}, "
      f"IQR {pd.to_numeric(mm['demo__Total approvals'], errors='coerce').quantile(.25):.0f}-"
      f"{pd.to_numeric(mm['demo__Total approvals'], errors='coerce').quantile(.75):.0f}; "
      "platform-experience proxy; heavily right-skewed -> log10")
    T("Student status", "NOT TESTED",
      f"only {int((mm.student==1).sum())} students (~6-9 per arm); interaction MDES would be "
      "enormous; descriptive means only")
    T("Country of birth / Nationality", "NOT TESTED",
      "high-cardinality (33 countries) and redundant with residence/first-language")
    T("Fluent languages", "NOT TESTED",
      "multilingualism collinear with first-language English; heterogeneous combinations")
    T("Authenticity check: Bots", "NOT TESTABLE / NO EXCLUSIONS",
      "all non-missing values are 'high' (no variance); nobody to exclude")
    T("Submission ids / timestamps / time-taken / completion code / status",
      "NOT MODERATORS", "tracking metadata, not demographics (status used as sensitivity filter)")

    tri = pd.DataFrame(triage)
    for _, r in tri.iterrows():
        print(f"- {r.variable}: {r.decision}\n    {r.reason}")
        if r.detail:
            print(f"    {r.detail}")
    tri.to_csv(f"{OUT}/triage_decisions.csv", index=False)

    # descriptive: students, UK residence, White-vs-Black means (not tested)
    print("\nDescriptive-only subgroup means (unadjusted immediate accuracy %, no tests):")
    for lab, col in [("student", "student"), ("UK resident", "uk_res"), ("Black (vs White)", "black")]:
        piv = mm.dropna(subset=[col]).groupby(["arm", col]).acc.agg(["mean", "count"])
        piv["mean"] = (piv["mean"] * 100).round(1)
        print(f"  {lab}:")
        print(piv.rename(columns={"mean": "acc%", "count": "n"}).to_string())

    # ---- moderation models ------------------------------------------------
    MODS = [
        ("age", "age_c10", "continuous", "Age (per +10 years)"),
        ("sex", "female", "binary", "Sex (female vs male)"),
        ("english_l1", "english_l1", "binary", "First language English (vs other)"),
        ("employment", "parttime", "binary", "Employment (part-time vs full-time)"),
        ("ethnicity", "nonwhite", "binary", "Ethnicity (non-White vs White, crude)"),
        ("tech_job", "tech_job", "binary", "IT/software/data occupation (vs other)"),
        ("approvals", "appr_c", "continuous", "Prolific approvals (per log10 unit, aux.)"),
    ]

    def run_family(outcome, label):
        print(f"\n### 3{'a' if outcome=='acc' else 'b'}. Arm x moderator interactions on "
              f"{label}  ({'PRIMARY' if outcome=='acc' else 'SECONDARY'} exploratory family)")
        rows, sub_rows = [], []
        for key, mcol, kind, nice in MODS:
            dd = mm if outcome == "acc" else mm.dropna(subset=["idk_rate"])
            sub, X, res, F, p = fit_moderation(dd, mcol, outcome=outcome, adjusted=True)
            n = len(sub)
            bu, lu, hu, pu, su = lincom(res, X, {"unr_m": 1})
            bs, ls, hs, ps, ss = lincom(res, X, {"soc_m": 1})
            _, _, _, _, pUv = fit_moderation(dd, mcol, outcome=outcome, adjusted=False)
            mdes = 2.8016 * su * 100
            # cells
            if kind == "binary":
                cells = sub.groupby(["arm", mcol]).size().to_dict()
                cellmin = min(cells.values())
                celltxt = "; ".join(f"{a}/{'yes' if v==1 else 'no'}:{c}" for (a, v), c in sorted(cells.items()))
            else:
                cells = sub.groupby("arm").size().to_dict()
                cellmin = min(cells.values())
                celltxt = "; ".join(f"{a}:{c}" for a, c in sorted(cells.items()))
            rows.append(dict(
                outcome=outcome, moderator=nice, key=key, kind=kind, n=n, min_cell=cellmin,
                int_UxM_pp=bu * 100, ci_lo=lu * 100, ci_hi=hu * 100,
                int_SxM_pp=bs * 100, s_ci_lo=ls * 100, s_ci_hi=hs * 100,
                omnibus_F=F, omnibus_p=p, omnibus_p_unadj_spec=pUv,
                mdes80_UxM_pp=mdes, cells=celltxt))
            # simple effects of U-G and S-G at moderator levels/quartiles
            if kind == "binary":
                levels = [(0.0, "no"), (1.0, "yes")]
            else:
                q1, q3 = sub[mcol].quantile(.25), sub[mcol].quantile(.75)
                if key == "age":
                    lvln = lambda v: f"age~{d['age'].mean() + 10*v:.0f}"
                else:
                    lvln = lambda v: f"log10appr~{d['log10_appr'].mean() + v:.2f}"
                levels = [(q1, lvln(q1)), (q3, lvln(q3))]
            for v, vl in levels:
                for con, cx in [("U-G", "unr"), ("S-G", "soc")]:
                    e, lo, hi, pp_, _ = lincom(res, X, {cx: 1, f"{cx}_m": v})
                    sub_rows.append(dict(outcome=outcome, moderator=nice, level=vl, contrast=con,
                                         est_pp=e * 100, ci_lo=lo * 100, ci_hi=hi * 100, p=pp_))
        R = pd.DataFrame(rows)
        R["bh_q"] = multipletests(R.omnibus_p, method="fdr_bh")[1]
        # Freedman-Lane permutation for suggestive omnibus results
        R["fl_perm_p"] = np.nan
        for i, r in R.iterrows():
            if r.omnibus_p < 0.10:
                dd = mm if outcome == "acc" else mm.dropna(subset=["idk_rate"])
                sub, X, res, _, _ = fit_moderation(dd, MODS_MAP[r.key],
                                                   outcome=outcome, adjusted=True)
                Xr_ = X.drop(columns=["soc_m", "unr_m"])
                R.loc[i, "fl_perm_p"] = fl_perm_p(sub[outcome].to_numpy(float), X, Xr_,
                                                  ["soc_m", "unr_m"])
        S = pd.DataFrame(sub_rows)
        return R, S

    global MODS_MAP
    MODS_MAP = {k: m for k, m, _, _ in MODS}

    Racc, Sacc = run_family("acc", "immediate unaided accuracy")
    disp = Racc[["moderator", "n", "min_cell", "int_UxM_pp", "ci_lo", "ci_hi",
                 "int_SxM_pp", "omnibus_p", "bh_q", "fl_perm_p", "mdes80_UxM_pp"]].copy()
    for c in ["int_UxM_pp", "ci_lo", "ci_hi", "int_SxM_pp", "mdes80_UxM_pp"]:
        disp[c] = disp[c].round(1)
    for c in ["omnibus_p", "bh_q", "fl_perm_p"]:
        disp[c] = disp[c].round(4)
    print("\nInteraction summary (accuracy, covariate-adjusted, HC3; int = difference in arm "
          "effect, pp):")
    print(disp.to_string(index=False))
    print("\nExpected false positives at raw p<.05 across 7 tests under the global null: ~0.35")

    print("\nSimple effects (arm contrast within moderator level; pp, 95% CI):")
    for mod in Sacc.moderator.unique():
        s = Sacc[Sacc.moderator == mod]
        print(f"  {mod}:")
        for _, r in s.iterrows():
            print(f"    {r.contrast} @ {r.level:<12} {r.est_pp:+6.1f} pp "
                  f"[{r.ci_lo:+6.1f}, {r.ci_hi:+6.1f}]  p={sci(r.p)}")

    print("\nDescriptive arm x level unadjusted accuracy means (%, n) for tested binaries:")
    for key, mcol, kind, nice in MODS:
        if kind != "binary":
            continue
        piv = (mm.dropna(subset=[mcol]).groupby(["arm", mcol]).acc
               .agg(["mean", "count"]))
        piv["mean"] = (piv["mean"] * 100).round(1)
        print(f"  {nice}:")
        print("    " + piv.rename(columns={"mean": "acc%", "count": "n"})
              .to_string().replace("\n", "\n    "))

    Ridk, Sidk = run_family("idk_rate", '"I don\'t know" abstention rate')
    dispi = Ridk[["moderator", "n", "int_UxM_pp", "ci_lo", "ci_hi", "int_SxM_pp",
                  "omnibus_p", "bh_q", "fl_perm_p"]].copy()
    for c in ["int_UxM_pp", "ci_lo", "ci_hi", "int_SxM_pp"]:
        dispi[c] = dispi[c].round(1)
    for c in ["omnibus_p", "bh_q", "fl_perm_p"]:
        dispi[c] = dispi[c].round(4)
    print("\nInteraction summary (IDK abstention, covariate-adjusted, HC3):")
    print(dispi.to_string(index=False))

    # ---- sensitivity: APPROVED-only + unadjusted spec ----------------------
    print("\n### 4. Sensitivities")
    print("(a) unadjusted-spec omnibus p is reported alongside the adjusted one in the "
          "results CSV (column omnibus_p_unadj_spec); differences were "
          f"{'small' if np.allclose(Racc.omnibus_p, Racc.omnibus_p_unadj_spec, atol=.15) else 'notable - see CSV'}.")
    napp = int((mm['demo__Status'] != 'APPROVED').sum())
    print(f"(b) Prolific status: {napp} non-APPROVED (AWAITING REVIEW) in the matched set; "
          "re-running the suggestive moderators without them:")
    appr_only = mm[mm["demo__Status"] == "APPROVED"]
    for _, r in Racc[Racc.omnibus_p < 0.10].iterrows():
        mcol = MODS_MAP[r.key]
        sub, X, res, F, p = fit_moderation(appr_only, mcol, outcome="acc", adjusted=True)
        bu, lu, hu, _, _ = lincom(res, X, {"unr_m": 1})
        print(f"    {r.moderator}: UxM {bu*100:+.1f} pp [{lu*100:+.1f}, {hu*100:+.1f}], "
              f"omnibus p={p:.4f} (n={len(sub)})")
    if not len(Racc[Racc.omnibus_p < 0.10]):
        print("    (no moderator reached omnibus p<.10 - nothing to re-run)")

    # cross-adjustment of correlated moderators (english_l1 vs nonwhite vs age)
    print("(c) cross-adjusted check for any suggestive moderator (adding the other tested "
          "moderators' main effects + their arm interactions is over-parameterised at this n; "
          "instead each suggestive moderator is re-fit adding the MAIN effects of the other six):")
    for _, r in Racc[Racc.omnibus_p < 0.10].iterrows():
        mcol = MODS_MAP[r.key]
        others = [m for k, m, _, _ in MODS if m != mcol]
        need = ["soc", "unr", mcol, "acc", "minivlat_c", "aiuse_c"] + others
        sub = mm.dropna(subset=need).copy()
        X = design(sub, mcol, adjusted=True)
        for o in others:
            X[f"cov_{o}"] = sub[o]
        res = sm.OLS(sub.acc.to_numpy(float), X).fit(cov_type="HC3")
        R2 = np.zeros((2, X.shape[1]))
        R2[0, list(X.columns).index("soc_m")] = 1
        R2[1, list(X.columns).index("unr_m")] = 1
        w = res.wald_test(R2, use_f=True, scalar=True)
        bu, lu, hu, _, _ = lincom(res, X, {"unr_m": 1})
        print(f"    {r.moderator}: UxM {bu*100:+.1f} pp [{lu*100:+.1f}, {hu*100:+.1f}], "
              f"omnibus p={float(w.pvalue):.4f} (n={len(sub)})")

    # ---- save --------------------------------------------------------------
    d.drop(columns=["start_all"]).to_csv(f"{OUT}/analysis_dataset.csv", index=False)
    Racc.to_csv(f"{OUT}/moderation_results_accuracy.csv", index=False)
    Sacc.to_csv(f"{OUT}/subgroup_effects_accuracy.csv", index=False)
    Ridk.to_csv(f"{OUT}/moderation_results_idk.csv", index=False)
    Sidk.to_csv(f"{OUT}/subgroup_effects_idk.csv", index=False)
    print(f"\nSaved: analysis_dataset.csv, triage_decisions.csv, moderation_results_*.csv, "
          f"subgroup_effects_*.csv under {OUT}")
    print(BANNER)


if __name__ == "__main__":
    np.random.seed(SEED)
    main()
