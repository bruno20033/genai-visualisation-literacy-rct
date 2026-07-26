"""Monte-Carlo calibration of sap_estimators.fit_aft_fallback (2026-07-16 AFT fix).

Claim under test: on pilot-shaped, participant-clustered log-normal success-time data,
the naive LogNormalAFTFitter CIs/p-values are anticonservative, and the participant-level
cluster-bootstrap (percentile) CIs restore ~nominal 95% coverage. Exercises the EXACT
module code (D10 spirit: validate the code that runs on real data, not a re-implementation).

DGP (mirrors pilot batch 1): 9/10/9 participants (google/socratic/unrestricted), 16 items
each; log T = 3.3 - 0.36*soc + 0.00*unr - 0.10*minivlat_c + 0.10*aiuse_c + b_i + eps,
b_i ~ N(0, 0.6^2) participant effect (log-scale ICC ~ 0.33), eps ~ N(0, 0.85^2);
administrative censoring at 45 s (event rate ~ 0.70, pilot ~ 0.72).

Outputs: per-sim CSV + printed coverage/error-rate summary.
  - coverage of true beta_soc = -0.36: naive 95% CI vs bootstrap percentile 95% CI
  - false-positive rate on beta_unr (true 0): naive p vs bootstrap p at alpha = .05
"""
import os, sys, time

# pin BLAS to one thread per process BEFORE numpy import: with 4 pool workers, default
# multi-threaded BLAS oversubscribes the 4 performance cores catastrophically (observed:
# the first run degraded concurrent lifelines fits >6x)
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_v] = "1"

from multiprocessing import Pool

import numpy as np
import pandas as pd

sys.path.insert(0, "/Users/brunokneffel/Downloads")
from sap_estimators import fit_aft_fallback

N_SIMS = 80
N_BOOT = 199
TRUE = dict(mu0=3.3, b_soc=-0.36, b_unr=0.0, b_mv=-0.10, b_ai=0.10,
            tau=0.60, sigma=0.85, censor_s=45.0)
ARMS = [("google", 9, 0, 0), ("socratic", 10, 1, 0), ("unrestricted", 9, 0, 1)]
K_ITEMS = 16


def simulate(rng):
    rows = []
    pid = 0
    for arm, n, soc, unr in ARMS:
        for _ in range(n):
            pid += 1
            mv = rng.normal(0, 2.0)
            ai = rng.normal(0, 1.5)
            b = rng.normal(0, TRUE["tau"])
            logt = (TRUE["mu0"] + TRUE["b_soc"] * soc + TRUE["b_unr"] * unr
                    + TRUE["b_mv"] * mv + TRUE["b_ai"] * ai + b
                    + rng.normal(0, TRUE["sigma"], K_ITEMS))
            t = np.exp(logt)
            ev = (t < TRUE["censor_s"]).astype(int)
            dur = np.minimum(t, TRUE["censor_s"])
            for j in range(K_ITEMS):
                rows.append((f"p{pid:03d}", arm, soc, unr, mv, ai, dur[j], ev[j]))
    return pd.DataFrame(rows, columns=["pid", "arm", "socratic", "unrestricted",
                                       "minivlat_c", "aiuse_c", "duration_s", "event"])


def run_sim(s):
    rng = np.random.default_rng(777_000 + s)
    df = simulate(rng)
    try:
        res = fit_aft_fallback(df, n_boot=N_BOOT, seed=888_000 + s)
    except Exception as e:
        return dict(sim=s, ok=0, err=type(e).__name__)
    tab = res["table"]
    aft = res["aft"]
    smry = aft.summary.loc["mu_"]
    out = dict(sim=s, ok=1, n_ok=res["n_ok"], n_failed=res["n_failed"],
               ev_rate=float(df["event"].mean()))
    for c, truth in [("socratic", TRUE["b_soc"]), ("unrestricted", TRUE["b_unr"])]:
        n_lo, n_hi = float(smry.loc[c, "coef lower 95%"]), float(smry.loc[c, "coef upper 95%"])
        b_lo, b_hi = float(np.log(tab.loc[c, "TR_ci95_lo"])), float(np.log(tab.loc[c, "TR_ci95_hi"]))
        out[f"{c}_coef"] = float(tab.loc[c, "coef"])
        out[f"{c}_cov_naive"] = int(n_lo <= truth <= n_hi)
        out[f"{c}_cov_boot"] = int(b_lo <= truth <= b_hi)
        out[f"{c}_p_naive"] = float(tab.loc[c, "p_naive"])
        out[f"{c}_p_boot"] = float(tab.loc[c, "p_boot"])
    return out


if __name__ == "__main__":
    t0 = time.time()
    with Pool(4) as pool:
        res = pool.map(run_sim, range(N_SIMS))
    df = pd.DataFrame(res)
    df.to_csv(sys.path[0] and
              "/private/tmp/claude-501/-Users-brunokneffel-Library-Mobile-Documents-com-apple-CloudDocs-gymnasium-steglitz-B-SC-Frankfurt-School-Oxford-Thesis-WIP-thesis-latex/0145de83-90ff-40f7-b571-0303bbdd8d74/scratchpad/mc_aft_calibration_results.csv",
              index=False)
    ok = df[df.ok == 1]
    print(f"\n=== fit_aft_fallback MC calibration: {len(ok)}/{N_SIMS} sims OK, "
          f"{time.time()-t0:.0f}s, B={N_BOOT}/sim ===")
    print(f"mean event rate {ok.ev_rate.mean():.3f} | mean failed refits/sim {ok.n_failed.mean():.2f}")
    se = lambda p, n: (p * (1 - p) / n) ** 0.5
    for c, truth in [("socratic", TRUE["b_soc"]), ("unrestricted", TRUE["b_unr"])]:
        cn, cb = ok[f"{c}_cov_naive"].mean(), ok[f"{c}_cov_boot"].mean()
        print(f"\n{c} (true beta = {truth:+.2f}; mean est {ok[f'{c}_coef'].mean():+.3f}):")
        print(f"  95% CI coverage  naive {cn:.3f} (SE {se(cn, len(ok)):.03f})   "
              f"bootstrap {cb:.3f} (SE {se(cb, len(ok)):.3f})")
        if truth == 0.0:
            fn = (ok[f"{c}_p_naive"] < 0.05).mean()
            fb = (ok[f"{c}_p_boot"] < 0.05).mean()
            print(f"  false-positive rate @ .05  naive {fn:.3f}   bootstrap {fb:.3f}")
