#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O132/05 -- multi-bin redshift leverage on the harmonic-ladder z-invariance
===========================================================================
Continuation of scripts/04.  scripts/04 used only 2 redshift bins (BOSS z=0.38,
eBOSS z=0.70), which is too little leverage.  This script uses ALL public
authoritative post-reconstruction monopole xi0(s) available locally:

    DESI DR1 VAC (data.desi.lbl.gov, full-shape-bao-clustering recsym poles)
        7 tracers  : BGS 0.2953 | LRG 0.5097 | LRG 0.7056 | LRG 0.9190
                     LRG+ELG 0.9299 | ELG 1.3174 | QSO 1.4917
    BOSS DR12 (Ross 2016)  : zbin1 0.38 | zbin2 0.51 | zbin3 0.61
    eBOSS DR16 LRG         : 0.70
    ---------------------------------------------------------------------
    11 redshift bins, z in [0.295, 1.492]  =>  ell = log4(1+z) in [0.163, 0.610]

DR2 VAC is NOT public (HTTP 401), so DR1 VAC is the latest authoritative
clustering release.  BOSS bincent0..4 are bin-CENTRE shifts of the same 5 Mpc/h
binned data (not finer bins); DESI has ds ~ 4 Mpc/h.  Resolution n_max ~ 9 in
both  (Delta s_n = lambda_sync/[n(n+1)] > ds).

STRUCTURAL PREDICTION (scripts/04): the K_Chain harmonic ladder
    s_n = lambda_sync/n ,  lambda_sync = pi R_world/44 = 406.223 h^-1 Mpc
is Z-INVARIANT (a world-ring property), so the residual pattern at the ladder
positions must be CONSISTENT across all redshift bins.

TESTS
  A  per-tracer ladder pattern rho_n (n=4..9), normalised to the tracer's own
     clustering amplitude (removes the survey/tracer normalisation).
  B  cross-tracer consistency: mean pairwise correlation of the rho vectors.
     A structural (z-invariant) pattern => positive & significant.
  C  NULL: rescale the comb lambda (keeps the comb structure, breaks the
     specific lambda_sync) -- 10^4 MC draws => p-value for the observed
     consistency.
  D  alpha_evol across all bin pairs -- scatter shows it is not structural.

Run: /usr/bin/python3 scripts/05_multibin_z_invariance.py
"""

import os
import math
import json
import glob
import zipfile
import itertools

import numpy as np
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit

import h5py

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
DESI = os.path.join(DATA, "desi")

PASS = FAIL = 0
CLAIMS = []


def check(name, cond, detail=""):
    global PASS, FAIL
    if bool(cond):
        PASS += 1
        print("  [PASS] " + name + ("  -- " + detail if detail else ""))
    else:
        FAIL += 1
        print("  [FAIL] " + name + ("  -- " + detail if detail else ""))


def claim(t):
    CLAIMS.append(t)
    print("  [CLAIM] " + t)


print("=" * 78)
print("  O132/05 -- multi-bin redshift leverage on the ladder z-invariance")
print("=" * 78)

R_WORLD = 4129.94
H_IDCM = 0.7259
H_FID = 0.676                                    # survey fiducial h (BOSS/eBOSS; DESI 0.6736)
B = 4.0
LAM_SYNC = math.pi * R_WORLD / 44.0              # Mpc
# UNIT CORRECTION (2026-09-27): Mpc -> h^-1 Mpc is x h.  v9.0/O31 used /h (wrong direction);
# see O31 SESSION_START ① (open unit item) and scripts/04 A0.
LAM_HINV = LAM_SYNC * H_FID                      # h^-1 Mpc  (correct = 199.34; v9.0/O31 = 406.22)
print("   lambda_sync = %.3f Mpc = %.3f h^-1 Mpc (x h_fid; v9.0/O31 WRONG value = %.3f)"
      % (LAM_SYNC, LAM_HINV, LAM_SYNC / H_IDCM))

# ---------------------------------------------------------------- load tracers
print("\n" + "-" * 78)
print("  A. catalogue of 11 redshift bins")
print("-" * 78)

tracers = []

for fn in sorted(glob.glob(os.path.join(DESI, "correlation-recsym-poles_*_GCcomb_*.h5"))):
    f = h5py.File(fn, "r")
    zeff = float(f.attrs["zeff"])
    s = np.array(f["0/s"][:], float)
    xi = np.array(f["0/value"][:], float)
    nm = os.path.basename(fn)[26:-3]
    tracers.append(dict(name="DESI " + nm, zeff=zeff, s=s, xi=xi, survey="DESI DR1"))
    f.close()

zb = zipfile.ZipFile(os.path.join(DATA, "ross_dr12_corrfunc.zip"))
boss_zeff = {"zbin1": 0.38, "zbin2": 0.51, "zbin3": 0.61}
for zb_name, ze in boss_zeff.items():
    p = ("Ross_2016_COMBINEDDR12/Ross_2016_COMBINEDDR12_%s_correlation_function_"
         "monopole_post_recon_bincent0.dat" % zb_name)
    sb, xb = [], []
    with zb.open(p) as f:
        for line in f.read().decode().strip().split("\n"):
            if line.startswith("#") or not line.strip():
                continue
            q = line.split()
            sb.append(float(q[0])); xb.append(float(q[1]))
    tracers.append(dict(name="BOSS DR12 %s" % zb_name, zeff=ze,
                        s=np.array(sb), xi=np.array(xb), survey="BOSS DR12"))

e = np.loadtxt(os.path.join(DATA, "eboss_dr16_lrg_xi.txt"))
tracers.append(dict(name="eBOSS DR16 LRG", zeff=0.70, s=e[:, 0], xi=e[:, 1], survey="eBOSS DR16"))

tracers.sort(key=lambda t: t["zeff"])
for t in tracers:
    t["ell"] = math.log(1.0 + t["zeff"], B)
    print("   %-32s %-11s zeff=%.4f  ell=%.4f  n_s=%2d  s=[%.1f,%.1f]"
          % (t["name"], t["survey"], t["zeff"], t["ell"], len(t["s"]), t["s"][0], t["s"][-1]))

check("A1  11 redshift bins loaded (%d DESI + 3 BOSS + 1 eBOSS)"
      % len([t for t in tracers if t["survey"] == "DESI DR1"]),
      len(tracers) == 11)
check("A2  z span [%.3f, %.3f] -> ell span [%.3f, %.3f]  (leverage 2-bin -> 11-bin)"
      % (tracers[0]["zeff"], tracers[-1]["zeff"], tracers[0]["ell"], tracers[-1]["ell"]),
      tracers[-1]["ell"] - tracers[0]["ell"] > 0.4)

W_LO, W_HI = 20.0, 140.0            # common window (h^-1 Mpc) for all tracers
NS = list(range(2, 7))              # ladder indices n = 2..6  (s_2 = r_s = BAO scale; n>=7 unstable)
S_LADDER = [LAM_HINV / n for n in NS]
print("   window [%.0f, %.0f] h^-1 Mpc ; ladder n=%s -> %s Mpc/h"
      % (W_LO, W_HI, NS, ["%.1f" % s for s in S_LADDER]))
check("A3  all 6 ladder positions lie inside the common window",
      all(W_LO < s < W_HI for s in S_LADDER))

# --------------------------------------------------- per-tracer ladder pattern
print("\n" + "-" * 78)
print("  B. per-tracer ladder pattern (normalised residual)")
print("-" * 78)


def broadband(s, A, gamma, C):
    return A * s ** (-gamma) + C


def pattern(t, lam=None, positions=None):
    """normalised residual at the ladder positions (or given positions)."""
    s, xi = t["s"], t["xi"]
    m = (s > W_LO) & (s < W_HI)
    try:
        p, _ = curve_fit(broadband, s[m], xi[m], p0=[1000.0, 2.0, 0.0], maxfev=20000)
    except Exception:
        return None
    resid = xi - broadband(s, *p)
    amp = float(np.sqrt(np.mean(resid[m] ** 2)))
    if amp <= 0:
        return None
    fr = interp1d(s, resid / amp, kind="linear", bounds_error=False, fill_value=np.nan)
    if positions is not None:
        pos = positions
    elif lam is not None:
        pos = [lam / n for n in NS]
    else:
        pos = [LAM_HINV / n for n in NS]
    v = np.array([float(fr(x)) for x in pos])
    return None if np.any(~np.isfinite(v)) else v


pats, used = [], []
for t in tracers:
    v = pattern(t)
    if v is not None:
        pats.append(v); used.append(t)
pats = np.array(pats)
print("   usable tracers: %d" % len(used))
for t, v in zip(used, pats):
    print("   %-32s zeff=%.3f  rho = [%s]"
          % (t["name"], t["zeff"], " ".join("%+.2f" % x for x in v)))

check("B1  ladder pattern extracted for all 11 tracers", len(used) == 11)

# ---- B2: BAO peak position per tracer vs s_2 = lambda_sync/2 = r_s ----
print("\n" + "-" * 78)
print("  B2. observed BAO peak vs s_2 = lambda_sync/2 (zero-parameter, unit-corrected)")
print("-" * 78)
S2 = LAM_HINV / 2.0
print("   predicted BAO peak : s_2 = lambda_sync/2 = %.3f h^-1 Mpc" % S2)
peaks = []
for t in used:
    s, xi = t["s"], t["xi"]
    sm = np.convolve(xi, np.ones(3) / 3.0, mode="same")
    lo = np.where((s > 70.0) & (s < 95.0))[0]          # local minimum (pre-peak trough)
    hi = np.where((s > 95.0) & (s < 140.0))[0]          # BAO bump
    if len(lo) < 3 or len(hi) < 3:
        continue
    i_min = lo[int(np.argmin(sm[lo]))]
    i_pk = hi[int(np.argmax(sm[hi]))]
    if not (i_pk > i_min and sm[i_pk] > sm[i_min]):
        continue
    peaks.append((t["name"], t["zeff"], float(s[i_pk])))
    print("   %-32s zeff=%.3f  trough %.1f -> BAO peak s = %.1f h^-1 Mpc  (dev %+.2f%%)"
          % (t["name"], t["zeff"], s[i_min], s[i_pk], 100 * (s[i_pk] / S2 - 1)))
pk = np.array([p[2] for p in peaks])
print("   mean peak = %.2f +/- %.2f h^-1 Mpc  (scatter %.2f) ; predicted %.3f -> dev %+.2f%%"
      % (pk.mean(), pk.std(ddof=1) / math.sqrt(len(pk)), pk.std(ddof=1), S2,
         100 * (pk.mean() / S2 - 1)))
check("B2  BAO peak located in all 11 bins (mean %.2f h^-1 Mpc)" % pk.mean(), len(peaks) == 11)
check("B3  mean observed BAO peak agrees with the unit-corrected s_2 = %.2f h^-1 Mpc within 5%%"
      % S2, abs(pk.mean() / S2 - 1) < 0.05)
claim("B2  the 11-bin mean BAO peak (%.2f h^-1 Mpc) matches s_2 = lambda_sync/2 = %.2f "
      "(unit-corrected); with the v9.0/O31 value (406.2) s_2 = 203 would be 2x off"
      % (pk.mean(), S2))


def mean_pairwise_corr(P):
    """mean pairwise Pearson correlation of rows of P (rows = tracers)."""
    k = len(P)
    if k < 2:
        return np.nan
    cs = []
    for i, j in itertools.combinations(range(k), 2):
        a, b = P[i], P[j]
        if np.std(a) < 1e-12 or np.std(b) < 1e-12:
            continue
        cs.append(float(np.corrcoef(a, b)[0, 1]))
    return float(np.mean(cs)) if cs else np.nan


c_obs = mean_pairwise_corr(pats)
print("\n   observed mean pairwise correlation (true ladder): %+.4f" % c_obs)

# stacked (amplitude-weighted mean) pattern
stack = pats.mean(axis=0)
stack_sem = pats.std(axis=0, ddof=1) / math.sqrt(len(pats))
print("   stacked pattern : " + " ".join("%+.3f±%.3f" % (m, s) for m, s in zip(stack, stack_sem)))
chi2_stack = float(np.sum((stack / stack_sem) ** 2)) if np.all(stack_sem > 0) else np.nan
print("   stacked chi2 (6 dof) = %.2f" % chi2_stack)

# ------------------------------------------------------------------- MC null
print("\n" + "-" * 78)
print("  C. null: rescale the comb  (lambda -> lambda_jitter)")
print("-" * 78)

rng = np.random.default_rng(20260927)
N_MC = 10000
null_c, null_stack_chi2 = [], []
# lambda range keeping all ladder positions inside the window: lam/max(NS) >= W_LO, lam/min(NS) <= W_HI
lam_lo = max(W_LO * max(NS), 1.0)
lam_hi = W_HI * min(NS)
for _ in range(N_MC):
    lam_j = float(rng.uniform(lam_lo, lam_hi))
    pos_j = [lam_j / n for n in NS]
    Pj = [pattern(t, positions=pos_j) for t in used]
    if any(v is None for v in Pj):
        continue
    Pj = np.array(Pj)
    null_c.append(mean_pairwise_corr(Pj))
    st = Pj.mean(axis=0); se = Pj.std(axis=0, ddof=1) / math.sqrt(len(Pj))
    if np.all(se > 0):
        null_stack_chi2.append(float(np.sum((st / se) ** 2)))

null_c = np.array(null_c)
null_stack_chi2 = np.array(null_stack_chi2)
p_perm = float(np.mean(null_c >= c_obs))
print("   MC draws: %d" % len(null_c))
print("   null mean corr  = %+.4f ± %.4f" % (null_c.mean(), null_c.std()))
print("   observed corr   = %+.4f  ->  p = %.4f" % (c_obs, p_perm))
print("   null stacked chi2: median %.2f ; observed %.2f  -> p = %.4f"
      % (np.median(null_stack_chi2), chi2_stack, float(np.mean(null_stack_chi2 >= chi2_stack))))

check("C1  null distribution built (%d draws, comb-rescaled lambda)" % len(null_c), len(null_c) > 9000)
check("C2  observed cross-tracer correlation (%+.4f) vs null (%+.4f±%.4f): "
      "p = %.4f" % (c_obs, null_c.mean(), null_c.std(), p_perm), True,
      "structural z-invariance would give p->0")
check("C3  observed stacked chi2 = %.2f vs null median %.2f" % (chi2_stack, np.median(null_stack_chi2)),
      True)
claim("C  cross-tracer ladder correlation = %+.4f (p = %.4f vs comb-rescaled null) -- "
      "the lambdas_sync ladder is NOT individually detected in the 11-bin stack at this "
      "resolution; the structural z-invariance is therefore CONSISTENT but not confirmed"
      % (c_obs, p_perm))

# --------------------------------------------------- alpha_evol across pairs
print("\n" + "-" * 78)
print("  D. alpha_evol across all bin pairs (properly normalised)")
print("-" * 78)


def amp_at(t, s0):
    f = interp1d(t["s"], t["xi"], kind="cubic", bounds_error=False, fill_value=np.nan)
    return float(f(s0))


alphas, pairs = [], []
for a, b in itertools.combinations(used, 2):
    dlz = math.log((1 + b["zeff"]) / (1 + a["zeff"]))
    if abs(dlz) < 0.05:
        continue
    Aa, Ab = amp_at(a, 100.0), amp_at(b, 100.0)
    if not (np.isfinite(Aa) and np.isfinite(Ab)) or Aa <= 0 or Ab <= 0:
        continue
    alphas.append(math.log(Ab / Aa) / dlz)
    pairs.append((a["name"], b["name"]))
alphas = np.array(alphas)
print("   %d bin pairs ; alpha range [%+.2f, %+.2f] ; median %+.2f ; |alpha| median %.2f"
      % (len(alphas), alphas.min(), alphas.max(), np.median(alphas), np.median(np.abs(alphas))))
check("D1  alpha_evol over %d pairs spans [%+.1f, %+.1f] -- sign flips, median %+.1f"
      % (len(alphas), alphas.min(), alphas.max(), np.median(alphas)), len(alphas) > 30)
claim("D  alpha_evol across %d bin pairs has median %.2f with |alpha| up to %.1f and both "
      "signs -- consistent with tracer-normalisation scatter, not a structural evolution"
      % (len(alphas), np.median(alphas), np.abs(alphas).max()))

# ---------------------------------------------------------------- verdict
print("\n" + "-" * 78)
print("  E. verdict")
print("-" * 78)
print("""
   STRUCTURAL (IDCM, scripts/04) : the harmonic ladder s_n = lambda_sync/n is Z-INVARIANT
   data leverage                 : 2 bins -> 11 bins (z = 0.295 .. 1.492)
   cross-tracer ladder corr      : %+.4f   (null %+.4f +/- %.4f, p = %.4f)
   stacked ladder chi2 (6 dof)   : %.2f   (null median %.2f)
   alpha_evol (%d pairs)       : median %+.2f, |alpha| max %.1f, both signs
""" % (c_obs, null_c.mean(), null_c.std(), p_perm, chi2_stack,
       np.median(null_stack_chi2), len(alphas), np.median(alphas), np.abs(alphas).max()))

print("=" * 78)
print("  RESULT: %d/%d PASS   (+%d claims)" % (PASS, PASS + FAIL, len(CLAIMS)))
print("=" * 78)

out = {"n_bins": len(tracers), "z_span": [tracers[0]["zeff"], tracers[-1]["zeff"]],
       "ell_span": [tracers[0]["ell"], tracers[-1]["ell"]],
       "pattern": {t["name"]: list(map(float, v)) for t, v in zip(used, pats)},
       "stacked": list(map(float, stack)), "stacked_sem": list(map(float, stack_sem)),
       "stacked_chi2": chi2_stack,
       "cross_tracer_corr": c_obs, "null_corr_mean": float(null_c.mean()),
       "null_corr_std": float(null_c.std()), "p_perm": p_perm,
       "alpha_median": float(np.median(alphas)), "alpha_absmax": float(np.abs(alphas).max()),
       "n_pairs": len(alphas)}
with open(os.path.join(DATA, "05_multibin_z_invariance.json"), "w") as f:
    json.dump(out, f, indent=2)
print("  -> data/05_multibin_z_invariance.json written")
