"""sap_estimators.py — single source of truth for the SAP estimators.

Extracted VERBATIM (same formulas, same options, same decision logic) from
rct_data_literacy_analysis_3.ipynb (v3), so that the Monte Carlo validation notebook
(rct_data_literacy_sap_validation.ipynb) exercises the exact code that will run on real
data. Both notebooks import this module; neither re-implements an estimator.

Implements the live SAP (sections/SAP_04_07.tex, decisions D1-D9):
  fit_primary_acc   eq:primary-acc  — MixedLM REML, Wave 0/1 dummy (immediate = 0)
  lincom            linear contrast + SE from any statsmodels-like result
  gatekeeper        D3/D6 fixed sequence: H1a superiority -> H2a non-inferiority
                    (90% CI vs -Delta, ITT AND per-protocol) -> supporting contrast
  fit_cox_st        eq:primary-st   — wave-stratified Cox with arm x wave terms,
                    participant-clustered robust SE (lifelines cluster_col)
  cox_lincom        contrast on the fitted Cox
  fit_bloom_gee     eq:bloom confirmatory engine — participant-clustered logistic GEE
  h4a_from_gee      focal one-sided interaction test (H1: beta5 < 0)
  h5a_simple_effect D9-R1 delayed-wave simple effect beta2+beta5 (H1: < 0)
  holm_family       one-sided Holm across {H4a, H5a}
  lee_bounds        two-sided Lee (2009) trimming bounds
  kr20              KR-20 internal consistency of an item block
  fit_aft_fallback  log-normal AFT fallback (fires when the PH test rejects) with
                    participant-level cluster-bootstrap SEs/CIs/p-values (lifelines
                    AFT fitters have no cluster_col; naive SEs are anticonservative)

Behavioural guard added for degenerate inputs (edge-case check 8): fitting functions
raise an informative ValueError when a model covariate has ~zero variance, instead of
letting the underlying optimiser fail cryptically or return a silently unstable fit.
"""
import numpy as np
import pandas as pd
import scipy.stats as st
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests
from lifelines import CoxPHFitter

Z90 = 1.644853627         # one-sided 95% / two-sided 90%
Z95 = 1.959963985         # two-sided 95%


# ---------------------------------------------------------------- helpers
def z_onesided_p(est, se, direction):
    """One-sided p. direction=-1 tests H1: est<0 ; +1 tests H1: est>0."""
    z = est / se
    return float(st.norm.cdf(z)) if direction < 0 else float(st.norm.sf(z))


def ci95(est, se):
    return est - Z95 * se, est + Z95 * se


def ci90(est, se):
    return est - Z90 * se, est + Z90 * se


def _check_covariates(data, cols, context):
    for c in cols:
        v = pd.to_numeric(data[c], errors="coerce")
        if v.notna().sum() == 0 or float(np.nanvar(v)) < 1e-12:
            raise ValueError(
                f"[{context}] model covariate '{c}' has ~zero variance "
                f"(var={float(np.nanvar(v)):.2e}); the design matrix is singular or "
                "near-singular. Check the covariate mapping before fitting."
            )


def lincom(res, Ld):
    """Estimate and SE of a linear combination of coefficients of a fitted
    statsmodels result (works for MixedLMResults, OLSResults, GEEResults)."""
    names = list(res.params.index)
    L = pd.Series(Ld, index=names).fillna(0).values
    est = float(L @ res.params.values)
    V = res.cov_params()
    V = V.values if hasattr(V, "values") else np.asarray(V)
    se = float(np.sqrt(L @ V @ L))
    return est, se


# ---------------------------------------------------------------- primary accuracy
PRIMARY_ACC_FORMULA = "acc ~ (socratic + unrestricted) * wave_d + minivlat_c + aiuse_c"


def fit_primary_acc(data):
    """eq:primary-acc — participant random intercept LMM, REML, Wave 0/1 dummy.

    Optimizer fallback chain (pre-specified): lbfgs -> bfgs -> powell -> cg.
    Monte Carlo validation (Check 1b) showed that a bare lbfgs call raises
    LinAlgError('Singular matrix') on realistic 16-item binomial-proportion outcomes
    whenever the profiled random-intercept variance approaches zero mid-iteration;
    the chain rescues those fits with identical results wherever lbfgs succeeds."""
    _check_covariates(data, ["minivlat_c", "aiuse_c"], "fit_primary_acc")
    m = smf.mixedlm(PRIMARY_ACC_FORMULA, data=data, groups=data["pid"], missing="drop")
    last = None
    for method in ("lbfgs", "bfgs", "powell", "cg"):
        try:
            return m.fit(reml=True, method=method)
        except (np.linalg.LinAlgError, ValueError, OverflowError) as e:
            last = e
    raise RuntimeError(
        f"fit_primary_acc: every optimizer in the pre-specified chain failed "
        f"(last error: {type(last).__name__}: {last})."
    )


def gatekeeper(acc_pw, pp_ids, alpha=0.05, delta=0.085, res=None):
    """D3/D6 fixed-sequence gatekeeper on the primary accuracy model.

    All three contrasts are ALWAYS estimated (SAP: quantities beyond a closed gate are
    still reported as estimates with CIs); the fixed sequence governs only the verdicts.
    Returns a dict with estimates, CIs, p-values, and the sequential verdicts.
    """
    if res is None:
        res = fit_primary_acc(acc_pw)
    b2, se2 = lincom(res, {"unrestricted": 1})                     # H1a  immediate U-G
    b1, se1 = lincom(res, {"socratic": 1})                         # H2a  immediate S-G
    bs, ses = lincom(res, {"socratic": 1, "unrestricted": -1})     # supporting  S-U

    p_h1a = z_onesided_p(b2, se2, -1)
    rej1 = p_h1a < alpha

    lo90_itt = b1 - Z90 * se1
    p_ni_itt = float(st.norm.sf((b1 + delta) / se1))
    ni_itt = lo90_itt > -delta

    lo90_pp, ni_pp, b1_pp, n_pp = np.nan, None, np.nan, len(pp_ids)
    try:
        d_pp = acc_pw[acc_pw.pid.isin(pp_ids)]
        if d_pp["pid"].nunique() >= 6 and d_pp["arm"].nunique() == 3:
            # full compliance => PP sample is the ITT sample; the REML fit is
            # deterministic, so reuse the ITT fit instead of refitting identical data
            res_pp = res if len(d_pp) == len(acc_pw) else fit_primary_acc(d_pp)
            b1_pp, se1_pp = lincom(res_pp, {"socratic": 1})
            lo90_pp = b1_pp - Z90 * se1_pp
            ni_pp = bool(lo90_pp > -delta)
    except Exception:
        pass  # ni_pp stays None -> NI cannot be declared

    p_sup = z_onesided_p(bs, ses, +1)

    ni_declared = bool(rej1 and ni_itt and (ni_pp is True))
    rej3 = bool(ni_declared and p_sup < alpha)

    return dict(
        res=res,
        b2=b2, se2=se2, ci95_b2=ci95(b2, se2), p_h1a=p_h1a, rej_h1a=rej1,
        b1=b1, se1=se1, ci95_b1=ci95(b1, se1),
        lo90_itt=lo90_itt, p_ni_itt=p_ni_itt, ni_itt=ni_itt,
        b1_pp=b1_pp, lo90_pp=lo90_pp, ni_pp=ni_pp, n_pp=n_pp,
        ni_declared=ni_declared,
        bs=bs, ses=ses, ci95_bs=ci95(bs, ses), p_sup=p_sup, rej_sup=rej3,
    )


def h5a_simple_effect(res):
    """D9-R1: persistence = delayed-wave simple effect beta2+beta5 (H1: < 0)."""
    est, se = lincom(res, {"unrestricted": 1, "unrestricted:wave_d": 1})
    return est, se, z_onesided_p(est, se, -1)


def holm_family(p_dict, alpha=0.05):
    """One-sided Holm across a named family; returns DataFrame with p_holm/reject."""
    fam = pd.DataFrame({"one_sided_p": pd.Series(p_dict)})
    fam["p_holm"] = multipletests(fam["one_sided_p"], alpha=alpha, method="holm")[1]
    fam["reject"] = fam["p_holm"] < alpha
    return fam


# ---------------------------------------------------------------- success time
COX_ST_FORMULA = "socratic + unrestricted + soc_wave + unr_wave + minivlat_c + aiuse_c"
COX_ST_COLS = ["duration_s", "event", "socratic", "unrestricted",
               "soc_wave", "unr_wave", "minivlat_c", "aiuse_c", "wave", "pid"]


def fit_cox_st(surv, formula=COX_ST_FORMULA, strata=("wave",), cluster="pid"):
    """eq:primary-st — wave-stratified Cox with arm x wave interaction columns and
    participant-clustered robust SE. Raises informatively on zero-event strata/arms."""
    need = [c for c in COX_ST_COLS if c in surv.columns]
    d = surv.dropna(subset=[c for c in ["duration_s", "event", "socratic", "unrestricted",
                                        "minivlat_c", "aiuse_c"] if c in surv.columns])[need].copy()
    _check_covariates(d, [c for c in ["minivlat_c", "aiuse_c"] if c in d.columns], "fit_cox_st")
    ev = d.groupby(d["socratic"].astype(str) + d["unrestricted"].astype(str))["event"].sum()
    if (ev == 0).any():
        raise ValueError(
            f"[fit_cox_st] at least one arm has ZERO events (correct answers): "
            f"{ev.to_dict()}. The partial likelihood is monotone in that arm's "
            "coefficient; the model cannot be fit. Check the answer key / scoring."
        )
    cph = CoxPHFitter()
    cph.fit(d, duration_col="duration_s", event_col="event",
            strata=list(strata) if strata else None,
            cluster_col=cluster, formula=formula)
    if cluster is not None:
        cph._sap_robust_V = _cluster_robust_V(cph, d, cluster)
    return cph


def _cluster_robust_V(cph, d, cluster):
    """Full cluster-robust (Lin-Wei 1989) covariance MATRIX for a fitted CoxPHFitter.

    FOUND BY MONTE CARLO VALIDATION (Check 5b): with cluster_col, lifelines stores the
    cluster-robust variances only per-coefficient (standard_errors_); variance_matrix_
    silently keeps the NAIVE covariance. Contrasts built from variance_matrix_ therefore
    had SEs ~40-60% too small under realistic within-participant clustering (empirical
    95% CI coverage ~0.70). This rebuilds the full sandwich V = B (sum_g U_g U_g') B from
    cluster-summed score residuals (finite-G corrected), then rescales its diagonal to
    match lifelines' own published robust SEs exactly, so single-coefficient contrasts
    equal cph.summary and multi-coefficient contrasts carry the sandwich correlations.
    """
    names = list(cph.params_.index)
    sc = cph.compute_residuals(d, kind="score")
    U = sc.assign(_g=d.loc[sc.index, cluster].values).groupby("_g")[names].sum()
    B = cph.variance_matrix_.loc[names, names].values
    G = U.shape[0]
    V = B @ (U.values.T @ U.values) @ B * (G / max(G - 1, 1))
    se_manual = np.sqrt(np.diag(V))
    se_ll = cph.standard_errors_.loc[names].values
    scale = np.where(se_manual > 0, se_ll / se_manual, 1.0)
    V = V * np.outer(scale, scale)
    return pd.DataFrame(V, index=names, columns=names)


def cox_lincom(cph, Ld):
    names = list(cph.params_.index)
    L = pd.Series(Ld, index=names).fillna(0.0).values
    est = float(L @ cph.params_.values)
    V = getattr(cph, "_sap_robust_V", None)
    if V is None:                       # unclustered fit: model-based covariance
        V = cph.variance_matrix_
    se = float(np.sqrt(L @ V.loc[names, names].values @ L))
    return est, se


# ---------------------------------------------------------------- Bloom (eq:bloom)
BLOOM_GEE_FORMULA = "correct ~ (socratic + unrestricted) * order_hi + minivlat_c + aiuse_c"


def fit_bloom_gee(ub, formula=BLOOM_GEE_FORMULA):
    """Confirmatory engine for H4a — participant-clustered logistic GEE (exchangeable)."""
    _check_covariates(ub, ["minivlat_c", "aiuse_c"], "fit_bloom_gee")
    return smf.gee(formula, groups="pid", data=ub, family=sm.families.Binomial(),
                   cov_struct=sm.cov_struct.Exchangeable()).fit()


def h4a_from_gee(gee):
    """Focal one-sided test: Unrestricted x higher-order interaction < 0."""
    b5 = float(gee.params["unrestricted:order_hi"])
    se5 = float(gee.bse["unrestricted:order_hi"])
    return b5, se5, z_onesided_p(b5, se5, -1)


# ---------------------------------------------------------------- Lee bounds, KR-20
def lee_bounds(y_treat, n_treat, y_ctrl, n_ctrl):
    """Two-sided Lee (2009) bounds: trim whichever arm responded MORE."""
    yt, yc = np.sort(np.asarray(y_treat, float)), np.sort(np.asarray(y_ctrl, float))
    if len(yt) == 0 or len(yc) == 0:
        return np.nan, np.nan
    rt, rc = len(yt) / n_treat, len(yc) / n_ctrl
    if abs(rt - rc) < 1e-9:
        return (yt.mean() - yc.mean(),) * 2
    if rt > rc:                                   # trim treated
        k = max(1, int(round((rc / rt) * len(yt))))
        return yt[:k].mean() - yc.mean(), yt[-k:].mean() - yc.mean()
    k = max(1, int(round((rt / rc) * len(yc))))   # trim control
    return yt.mean() - yc[-k:].mean(), yt.mean() - yc[:k].mean()


def kr20(block):
    piv = block.pivot_table(index="pid", columns="item_id", values="correct").dropna(axis=1, how="all")
    k = piv.shape[1]
    if k < 2:
        return np.nan
    p = piv.mean()
    tot = piv.sum(axis=1).var(ddof=1)
    return (k / (k - 1)) * (1 - (p * (1 - p)).sum() / tot) if tot > 0 else np.nan


# ---------------------------------------------------------------- adoption latency (Delta)
# ADDITIVE (2026-07-12): answer-adoption-latency manipulation check. Depends only on the new
# response_ts / answer_ts / query_ts fields carried by pcp_consolidate.js; existing estimators
# are unchanged, so importing this leaves the v3 and validation notebooks' behaviour identical.
ADOPTION_THRESHOLD_S = 5.0   # direct-adoption cutoff; LOCKED FROM PILOT Delta distribution (measure-first)


def _fit_mixedlm(formula, data, groups):
    """MixedLM with the pre-specified optimizer fallback chain (as in fit_primary_acc)."""
    m = smf.mixedlm(formula, data=data, groups=groups, missing="drop")
    last = None
    for method in ("lbfgs", "bfgs", "powell", "cg"):
        try:
            return m.fit(reml=True, method=method)
        except (np.linalg.LinAlgError, ValueError, OverflowError) as e:
            last = e
    raise RuntimeError(f"_fit_mixedlm: optimizer chain failed ({type(last).__name__}: {last})")


def adoption_latency(items_aided, threshold_s=ADOPTION_THRESHOLD_S):
    """Answer-adoption latency Delta (SAP manipulation check).

    items_aided: item-level aided-block frame with columns pid, arm, adopt_delta_s (seconds
    from the last tool interaction -- final assistant message for the LLM arms, last query/click
    for the search arm -- to answer submission; NaN where no tool interaction, excluded here).

    Returns dict:
      dist          per-arm Delta distribution (n, median, IQR), all three arms -- the
                    measure-first, threshold-free deliverable.
      contrast      log-Delta participant-random-intercept mixed model, Unrestricted vs Socratic
                    (LLM arms only), one-sided (Unrestricted predicted SHORTER => est<0); or None.
      adoption_rate per-arm direct-adoption rate = mean over participants of the share of aided
                    items with Delta < threshold_s (descriptive; cutoff set from pilot).
      threshold_s, n_excluded
    """
    d = items_aided.copy()
    n_excluded = int(d["adopt_delta_s"].isna().sum())
    d = d.dropna(subset=["adopt_delta_s"])
    d = d[d["adopt_delta_s"] >= 0]

    dist = (d.groupby("arm", observed=True)["adopt_delta_s"]
            .agg(n="size", median="median",
                 q25=lambda x: x.quantile(0.25), q75=lambda x: x.quantile(0.75))
            .reset_index())

    contrast = None
    llm = d[d["arm"].isin(["socratic", "unrestricted"])].copy()
    if llm["arm"].nunique() == 2 and llm["pid"].nunique() >= 6 and len(llm) >= 8:
        llm["unrestricted"] = (llm["arm"] == "unrestricted").astype(int)
        llm["log_delta"] = np.log(llm["adopt_delta_s"].clip(lower=1e-3))
        est = se = None
        try:
            m = _fit_mixedlm("log_delta ~ unrestricted", llm, llm["pid"])
            est, se = float(m.params["unrestricted"]), float(m.bse["unrestricted"])
        except Exception:
            est = se = None
        # Guard: a near-zero participant random-effect variance makes MixedLM's covariance
        # singular and its SE explode / go non-finite. Fall back to OLS with participant-
        # cluster-robust SE, which recovers the same point estimate with valid inference.
        if (se is None) or (not np.isfinite(se)) or (se > 10):
            o = smf.ols("log_delta ~ unrestricted", data=llm).fit(
                cov_type="cluster", cov_kwds={"groups": llm["pid"]})
            est, se = float(o.params["unrestricted"]), float(o.bse["unrestricted"])
        contrast = dict(est=est, se=se, ci95=ci95(est, se),
                        p_onesided=z_onesided_p(est, se, -1))   # H1: Unrestricted shorter

    d = d.assign(adopted=(d["adopt_delta_s"] < threshold_s).astype(int))
    part = d.groupby(["pid", "arm"], observed=True)["adopted"].mean().reset_index()
    adoption_rate = part.groupby("arm", observed=True)["adopted"].mean().to_dict()

    return dict(dist=dist, contrast=contrast, adoption_rate=adoption_rate,
                threshold_s=threshold_s, n_excluded=n_excluded)


# ---------------------------------------------------------------- log-normal AFT fallback
# ADDITIVE (2026-07-16): cluster-bootstrap inference for the pre-specified log-normal AFT
# fallback (fires when the Grambsch-Therneau PH test rejects; it did on pilot batch 1).
# lifelines AFT fitters have no cluster_col, so the fallback's model-based SEs treated the
# ~16 items a participant contributes as independent -- anticonservative, the same failure
# mode the Monte Carlo validation caught on the Cox side (Check 5b, _cluster_robust_V).
# Point estimates are UNCHANGED: the returned fitter is the single fit on the observed
# data; only SEs / CIs / p-values come from the bootstrap. Estimators above are untouched.
AFT_FALLBACK_COLS = ["duration_s", "event", "socratic", "unrestricted", "minivlat_c", "aiuse_c"]


def fit_aft_fallback(d, cols=None, cluster="pid", n_boot=1000, seed=2026, alpha=0.05,
                     duration_col="duration_s", event_col="event"):
    """Log-normal AFT (time ratios) with participant-level cluster-bootstrap inference.

    d: item-level survival frame carrying `cols` plus the `cluster` id column. The point
    fit is identical to the previous naive call LogNormalAFTFitter().fit(d[cols], ...) --
    same rows (dropna on `cols`), same design (mu_ ~ regressors, sigma_ ~ 1).

    Inference: participants are resampled with replacement WITHIN ARM (allocation is fixed
    by design; stratifying also keeps every arm represented in each replicate -- strata are
    derived from whichever of the socratic/unrestricted dummies are in `cols`), the AFT is
    refit on each replicate, and every mu_ coefficient gets a bootstrap SE, a percentile
    (1-alpha) CI, and a two-sided bootstrap p -- the sign-flip proportion with the
    (r+1)/(B+1) finite-sample correction (Davison & Hinkley 1997, ch. 4). Replicates whose
    refit fails to converge are dropped and counted (n_failed). The model-based p is kept
    in the table as `p_naive` ONLY to document the correction -- never for inference.

    Returns dict(aft, table, draws, n_boot, n_ok, n_failed, seed).
    """
    import warnings as _warnings
    from lifelines import LogNormalAFTFitter

    if cols is None:
        cols = AFT_FALLBACK_COLS
    cols = list(cols)
    keep = list(dict.fromkeys(cols + [cluster]))
    dd = d.dropna(subset=cols)[keep].reset_index(drop=True)
    _check_covariates(dd, [c for c in cols if c not in (duration_col, event_col)],
                      "fit_aft_fallback")

    aft = LogNormalAFTFitter().fit(dd[cols], duration_col=duration_col, event_col=event_col)
    point = aft.params_.loc["mu_"]
    names = list(point.index)

    # participant row-blocks and design-fixed arm strata (google=0, socratic=1, unrestricted=2)
    blocks = {p: g.values for p, g in dd.groupby(cluster).groups.items()}
    sc = [c for c in ("socratic", "unrestricted") if c in dd.columns]
    if sc:
        first = dd.groupby(cluster)[sc].first()
        stratum = sum((i + 1) * first[c].round().astype(int) for i, c in enumerate(sc))
    else:
        stratum = pd.Series(0, index=pd.Index(blocks.keys(), name=cluster))
    strata_pids = {s: g.index.values for s, g in stratum.groupby(stratum)}

    rng = np.random.default_rng(seed)
    draws, n_failed = [], 0
    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")
        for _ in range(n_boot):
            take = np.concatenate([
                np.concatenate([blocks[p] for p in rng.choice(pids, size=len(pids), replace=True)])
                for pids in strata_pids.values()])
            try:
                # reset_index: resampled rows carry duplicate labels, which lifelines'
                # internal predict_median call cannot reindex on
                bf = LogNormalAFTFitter().fit(dd.loc[take, cols].reset_index(drop=True),
                                              duration_col=duration_col, event_col=event_col)
                draws.append(bf.params_.loc["mu_"].reindex(names).values)
            except Exception:
                n_failed += 1
    if not draws:
        raise RuntimeError(
            "fit_aft_fallback: every bootstrap refit failed to converge; inspect the "
            "survival frame before reporting the AFT fallback."
        )
    draws = pd.DataFrame(np.vstack(draws), columns=names)
    n_ok = len(draws)

    lvl = int(round((1 - alpha) * 100))
    qlo, qhi = np.percentile(draws.values, [100 * alpha / 2, 100 * (1 - alpha / 2)], axis=0)
    r_le = (draws.values <= 0).sum(axis=0)
    r_ge = (draws.values >= 0).sum(axis=0)
    p_boot = np.minimum(1.0, 2.0 * (np.minimum(r_le, r_ge) + 1) / (n_ok + 1))

    table = pd.DataFrame({
        "coef": point.values,
        "se_boot": draws.std(ddof=1).values,
        "exp(coef)": np.exp(point.values),
        f"TR_ci{lvl}_lo": np.exp(qlo),
        f"TR_ci{lvl}_hi": np.exp(qhi),
        "p_boot": p_boot,
        "p_naive": aft.summary.loc["mu_", "p"].reindex(names).values,
    }, index=pd.Index(names, name="covariate"))
    return dict(aft=aft, table=table, draws=draws, n_boot=n_boot, n_ok=n_ok,
                n_failed=n_failed, seed=seed)
