#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O130/08 -- DESI DR2 official BAO multipoles: ladder test + DR1 replication
==========================================================================
Fourth data set, and the first out-of-sample replication test of the DR1
marginal edge (LRG3, delta = 0, p = 0.030 in the wide window).

Data (Zenodo 10.5281/zenodo.16644577, official DESI DR2 BAO supplement;
size + md5 verified, see data/desi/dr2/PROVENANCE.md):
  dr2/figure5/multipoles_<tracer>_data.txt    s  xi_0  xi_0_err  xi_2  xi_2_err
                                              23 pts, s = 62.04..150.02, ds = 4
  dr2/figure5/multipoles_<tracer>_theory.txt  DESI best-fit LCDM+BAO curve
  8 tracers (DR2 adds ELG z0.8-1.1 to the 7 DR1 tracers)

  A  load, grid, in-window structural-node count (power statement)
  B  per-tracer matched filter at the STRUCTURAL lambda_sync (delta = 0), raw
  C  trial-corrected statistic + local MC null + argmax diagnostic
  D  GLOBAL look-elsewhere over 8 tracers (joint null), incl. the decisive delta=0 test
  E  DR1 vs DR2 SAME-WINDOW replication + window-dependence of the DR1 edge
  F  DECISIVE CONTROL: ladder on top of the DESI best-fit LCDM+BAO curve
  G  adequate-broadband statistic (drop the over-stiff knots = 4 option)

DECLARED LIMITATIONS (not hidden):
 * The DR2 figure-5 release carries DIAGONAL errors only (no covariance), so this
   script uses a diagonal chi^2 unlike script 07 (official RascalC covariance).
   Absolute p-values are therefore not directly comparable with 07 -> section E
   compares DR1 and DR2 on the SAME window with the SAME statistic.
 * The null and the observations use the SAME sigma, so any common error-scale
   error cancels in the p-value (section B1 states this explicitly).

METHOD NOTE (why "raw Delta-chi^2 ~ 13" is not a detection, exposed by DR2):
  A cubic-spline broadband with only 4 knots is too stiff to describe xi(s) over
  the BAO range, so the ladder column absorbs part of the *smooth* xi(s) shape.
  Signature: the trial-corrected argmax picks knots = 4 for every single tracer,
  the fitted amplitude comes out uniformly POSITIVE, and Delta-chi^2 reaches
  +13..+15 even though the Monte-Carlo null has a mean of the same order.
  Sections F and G show the effect vanishing once the broadband is physically
  adequate -- the DESI best-fit curve, or knots >= 5.

Run: /usr/bin/python3 scripts/08_desi_dr2_test.py
"""

import os
import math
import json

import numpy as np
import h5py
from scipy.interpolate import BSpline

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data", "desi")
DR2 = os.path.join(DATA, "dr2")

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


def claim(text):
    CLAIMS.append(text)
    print("  [CLAIM] " + text)


def note(text):
    print("  [NOTE] " + text)


print("=" * 78)
print("  O130/08 -- DESI DR2 official BAO multipoles: ladder test + DR1 replication")
print("=" * 78)

# --- UNITS: corrected 2026-09-28 (see docs/04_unit_correction.md) -------------
# lambda_sync = 2*pi*R_H/88 = pi*R_world/44 = 294.877026 Mpc  -- PHYSICAL Mpc.
# The survey xi(s) axis is in h^-1 Mpc with that survey's fiducial h, so
#     lambda_sync[h^-1 Mpc] = lambda_sync[Mpc] * h_fid
# v9.0 _core.py wrote  LAMBDA_SYNC / H  (divide!), giving 406.22 -> 1/h^2 = 1.897x
# too long, and the migration carried it verbatim.  Empirical proof of the axis
# unit: the BAO bump in the released DESI DR2 best-fit theory curve sits at
# s = 102.0 h^-1 Mpc = r_d(147.09 Mpc) * h_fid  => the axis really is h^-1 Mpc.
LAM_MPC = 294.877026
H_FID = 0.6736                                   # DESI/BOSS/eBOSS fiducial h
LAM = LAM_MPC * H_FID                            # 198.63 h^-1 Mpc
GAM = lambda n: 4 * math.sin(math.pi * n / 88) ** 2
SIGMA = 10.0
KNOT_SET = (4, 5, 6)
KNOT_ADQ = (5, 6)                                # adequate broadband (see METHOD NOTE)
BAND = list(range(3, 10))
DELTA_GRID = [-0.10, -0.05, -0.02, -0.01, 0.0, 0.01, 0.02, 0.05, 0.10]
NSUR = 300
SEED = 20260929
deg = 3

# DR2 tag -> (data file, DR1 tag or None, DR1 correlation file)
TRACERS = [
    ("BGS", "multipoles_BGS_BRIGHT-21.35_0.1_0.4_data.txt", "BGS",
     "correlation-recsym-poles_BGS_BRIGHT-21.5_GCcomb_z0.1-0.4.h5"),
    ("LRG1", "multipoles_LRG_0.4_0.6_data.txt", "LRG1",
     "correlation-recsym-poles_LRG_GCcomb_z0.4-0.6.h5"),
    ("LRG2", "multipoles_LRG_0.6_0.8_data.txt", "LRG2",
     "correlation-recsym-poles_LRG_GCcomb_z0.6-0.8.h5"),
    ("LRG3", "multipoles_LRG_0.8_1.1_data.txt", "LRG3",
     "correlation-recsym-poles_LRG_GCcomb_z0.8-1.1.h5"),
    ("LRG+ELG", "multipoles_LRG+ELG_LOPnotqso_0.8_1.1_data.txt", "LRG+ELG",
     "correlation-recsym-poles_LRG%2BELG_LOPnotqso_GCcomb_z0.8-1.1.h5"),
    ("ELGlo", "multipoles_ELG_LOPnotqso_0.8_1.1_data.txt", None, None),
    ("ELG", "multipoles_ELG_LOPnotqso_1.1_1.6_data.txt", "ELG",
     "correlation-recsym-poles_ELG_LOPnotqso_GCcomb_z1.1-1.6.h5"),
    ("QSO", "multipoles_QSO_0.8_2.1_data.txt", "QSO",
     "correlation-recsym-poles_QSO_GCcomb_z0.8-2.1.h5"),
]

# ------------------------------------------------------------------
print("\n" + "-" * 78)
print("  A. load DR2 multipoles (official figure-5 release) + power statement")
print("-" * 78)

samples = {}
for tag, fn, d1tag, d1fn in TRACERS:
    fp = os.path.join(DR2, fn)
    assert os.path.exists(fp), fp
    dat = np.loadtxt(fp)
    s, xi0, e0 = dat[:, 0], dat[:, 1], dat[:, 2]
    th = np.loadtxt(os.path.join(DR2, fn.replace("_data.txt", "_theory.txt")))
    samples[tag] = dict(s=s, xi=xi0, sig=e0, Cinv=np.diag(1.0 / e0 ** 2),
                        Cinv_diag=1.0 / e0 ** 2, th=th[:, 1], d1tag=d1tag, d1fn=d1fn)
    print("   %-8s N=%2d  s=%.2f..%.2f  ds=%.3f  med sigma_0=%.2e  med |xi_0|/sigma=%.1f"
          % (tag, len(s), s[0], s[-1], s[2] - s[1], np.median(e0),
             np.median(np.abs(xi0) / e0)))

check("A1  all 8 official DESI DR2 tracers loaded from the figure-5 release",
      len(samples) == 8 and all(len(d["s"]) == 23 for d in samples.values()),
      "8 tracers x 23 s-bins")
ds_bin = float(samples["LRG3"]["s"][2] - samples["LRG3"]["s"][1])
nmax = (-1 + math.sqrt(1 + 4 * LAM / ds_bin)) / 2
check("A2  DESI DR2 binning ds = %.2f h^-1 Mpc -> bin-Nyquist n_max = %.2f (same as DR1)"
      % (ds_bin, nmax), abs(ds_bin - 4.0) < 1e-2)

s_lo, s_hi = float(samples["LRG3"]["s"][0]), float(samples["LRG3"]["s"][-1])
nodes = []
for n in BAND:
    for j in range(1, 4):
        sn = j * LAM / n
        if s_lo <= sn <= s_hi:
            nodes.append((round(sn, 2), n, j))
distinct = sorted(set(v[0] for v in nodes))
print("   fit window [%.2f, %.2f] contains %d distinct structural node positions:"
      % (s_lo, s_hi, len(distinct)))
print("     " + ", ".join("%.1f(n=%d)" % (v[0], v[1]) for v in nodes))
check("A3  the DR2 fit window contains >= 4 distinct structural ladder nodes "
      "(the test has power)", len(distinct) >= 4, "%d distinct positions" % len(distinct))
claim("A  => the DR2 fit window starts at s = %.0f h^-1 Mpc (BAO-fit range): the "
      "bin-Nyquist crowding at small s is NOT the obstruction here, the window start is. "
      "Errors are diagonal only (no covariance in this release)." % s_lo)


def spline_basis(x, knots, d=deg):
    kn = np.concatenate([[knots[0]] * d, knots, [knots[-1]] * d])
    return np.column_stack([BSpline.basis_element(kn[i:i + d + 2], extrapolate=True)(x)
                            for i in range(len(kn) - d - 1)])


def template(s, lam, band=BAND, sigma=SIGMA):
    t = np.zeros_like(s)
    for n in band:
        k = 2 * math.pi * n / lam
        t += GAM(n) * np.cos(k * s) * math.exp(-0.5 * (k * sigma) ** 2)
    return t


def make_fitter(s, Ci):
    """Pre-compute every y-independent matrix; the returned closure re-fits a new y."""
    ctx = {}
    for nk in KNOT_SET:
        B = spline_basis(s, np.linspace(s[0], s[-1], nk))
        BtCiB = B.T @ Ci @ B
        ctx[("B", nk)] = B
        ctx[("BtCiB", nk)] = BtCiB
        for dd in DELTA_GRID:
            T = template(s, LAM * (1 + dd))
            ctx[("T", nk, dd)] = T
            ctx[("BtCiT", nk, dd)] = B.T @ Ci @ T
            ctx[("TtCiT", nk, dd)] = float(T @ Ci @ T)
    nb = {nk: ctx[("B", nk)].shape[1] for nk in KNOT_SET}

    def fit(y):
        Ciy = Ci @ y
        yCiy = float(y @ Ciy)
        out = {}
        for nk in KNOT_SET:
            BtCiB = ctx[("BtCiB", nk)]
            bty = ctx[("B", nk)].T @ Ciy
            cb = np.linalg.solve(BtCiB, bty)
            c0 = yCiy - float(bty @ cb)
            for dd in DELTA_GRID:
                btt = ctx[("BtCiT", nk, dd)]
                ttt = ctx[("TtCiT", nk, dd)]
                tty = float(ctx[("T", nk, dd)] @ Ciy)
                A = np.block([[BtCiB, btt[:, None]],
                              [btt[None, :], np.array([[ttt]])]])
                rhs = np.concatenate([bty, [tty]])
                cc = np.linalg.solve(A, rhs)
                c1 = yCiy - float(rhs @ cc)
                out[(nk, dd)] = (c0 - c1, c0, float(cc[-1]))
        return out, nb

    return fit


def theory_control(d):
    """Ladder on top of the DESI best-fit curve: fixed theory + one free amplitude."""
    resid = d["xi"] - d["th"]
    w = d["Cinv_diag"]
    T = template(d["s"], LAM)
    c_th = float(np.sum(w * resid ** 2))
    amp = float(np.sum(w * T * resid) / np.sum(w * T * T))
    c_add = float(np.sum(w * (resid - amp * T) ** 2))
    return c_th, c_th - c_add, amp


for tag, d in samples.items():
    d["fit"] = make_fitter(d["s"], d["Cinv"])
    d["c_th"], d["dchi2_th"], d["amp_th"] = theory_control(d)

# ------------------------------------------------------------------
print("\n" + "-" * 78)
print("  B. matched-filter test at the STRUCTURAL lambda_sync (delta = 0), raw")
print("-" * 78)

print("   tracer    N   chi2_bb  chi2/dof  dchi2(delta=0)   amplitude   "
      "dchi2 on DESI theory")
for tag, d in samples.items():
    out, nb = d["fit"](d["xi"])
    for nk in KNOT_SET:
        d.setdefault("prof", {})[nk] = out[(nk, 0.0)]
    v, c0, a = d["prof"][5]
    d["dof"] = len(d["s"]) - nb[5]
    d["c05"], d["a5"], d["d5"] = c0, a, v
    print("   %-8s %3d  %7.1f  %8.2f  %+14.2f   %+.3e   %+8.2f"
          % (tag, len(d["s"]), c0, c0 / d["dof"], v, a, d["dchi2_th"]))

maxdof = max(d["c05"] / d["dof"] for d in samples.values())
check("B1  the diagonal DR2 errors are not UNDER-estimated (no tracer with chi2/dof > 1.5) "
      "-- the test is calibrated or conservative, never anti-conservative", maxdof <= 1.5,
      "chi2/dof %.2f - %.2f (conservative values expected: marginal errors on correlated "
      "bins); the null uses the same sigma so the error scale cancels in p"
      % (min(d["c05"] / d["dof"] for d in samples.values()), maxdof))

big = {t: d for t, d in samples.items() if d["d5"] >= 10.0}
print("   tracers with raw dchi2(delta=0) >= 10: %s"
      % (", ".join("%s(%+.2f)" % (t, d["d5"]) for t, d in big.items()) or "none"))
dmin = min(d["d5"] for d in samples.values())
dmax = max(d["d5"] for d in samples.values())
check("B2  NO tracer shows a large raw dchi2(delta=0) at the corrected structural "
      "lambda_sync -- range %+.2f to %+.2f over 8 tracers (1 dof each): there is nothing "
      "for the DESI best-fit curve to absorb" % (dmin, dmax),
      len(big) == 0,
      "raw dchi2(delta=0) range: %+.2f - %+.2f" % (dmin, dmax))
tmax = max(samples, key=lambda t: samples[t]["d5"])
claim("B  => at the corrected scale (lambda_sync = %.1f h^-1 Mpc) the raw Delta-chi^2 at "
      "delta = 0 is at most %+.2f (%s) over all 8 DR2 tracers -- the ladder column finds "
      "nothing.  (The uniform-sign +10..+20 raw excess of the pre-correction revision came "
      "from the pre-correction lambda_sync = 406.22 h^-1 Mpc, which placed the n = 4 node "
      "at 101.6 h^-1 Mpc -- exactly on the BAO bump at 102.0.)"
      % (LAM, samples[tmax]["d5"], tmax))

json_out = dict(LAM=LAM, s_min=s_lo, s_max=s_hi, n_tracers=len(samples), ds_bin=ds_bin,
                n_max=nmax, dchi2_delta0={t: d["d5"] for t, d in samples.items()},
                amplitude_delta0={t: d["a5"] for t, d in samples.items()},
                dchi2_on_theory={t: d["dchi2_th"] for t, d in samples.items()},
                amplitude_on_theory={t: d["amp_th"] for t, d in samples.items()})

# ------------------------------------------------------------------
print("\n" + "-" * 78)
print("  C. trial-corrected statistic, argmax diagnostic, and local MC null")
print("-" * 78)

rng = np.random.default_rng(SEED)
print("   tracer   D_obs   argmax(knots,delta)  p_local   p_delta0  p_delta0(adq)")
for tag, d in samples.items():
    out, _ = d["fit"](d["xi"])
    D_obs = max(v[0] for v in out.values())
    arg = max(out, key=lambda k: out[k][0])
    D0_obs = max(out[(nk, 0.0)][0] for nk in KNOT_SET)
    D0a_obs = max(out[(nk, 0.0)][0] for nk in KNOT_ADQ)
    B = spline_basis(d["s"], np.linspace(d["s"][0], d["s"][-1], 5))
    cb = np.linalg.solve(B.T @ d["Cinv"] @ B, B.T @ (d["Cinv"] @ d["xi"]))
    bb = B @ cb
    Dn = np.empty(NSUR)
    D0n = np.empty(NSUR)
    D0an = np.empty(NSUR)
    draws = []
    for i in range(NSUR):
        yy = bb + d["sig"] * rng.standard_normal(len(d["s"]))
        draws.append(yy)
        o2, _ = d["fit"](yy)
        Dn[i] = max(v[0] for v in o2.values())
        D0n[i] = max(o2[(nk, 0.0)][0] for nk in KNOT_SET)
        D0an[i] = max(o2[(nk, 0.0)][0] for nk in KNOT_ADQ)
    d.update(D_obs=D_obs, arg=arg, D0_obs=D0_obs, D0a_obs=D0a_obs, Dn=Dn, D0n=D0n,
             D0an=D0an, draws=np.array(draws))
    d["p_local"] = float(np.mean(Dn >= D_obs))
    d["p_delta0"] = float(np.mean(D0n >= D0_obs))
    d["p_delta0_adq"] = float(np.mean(D0an >= D0a_obs))
    print("   %-8s %+7.2f   knots=%d delta=%+.2f    %.3f     %.3f     %.3f"
          % (tag, D_obs, arg[0], arg[1], d["p_local"], d["p_delta0"], d["p_delta0_adq"]))

worst = min(d["p_local"] for d in samples.values())
worst_tag = [t for t, d in samples.items() if d["p_local"] == worst][0]
print("   -> smallest local p = %.3f (%s, argmax knots=%d delta=%+.2f)"
      % (worst, worst_tag, samples[worst_tag]["arg"][0], samples[worst_tag]["arg"][1]))
check("C1  the DR2 tracer with the smallest local p peaks at a NON-structural lambda "
      "shift (|delta| > 0)", abs(samples[worst_tag]["arg"][1]) > 0.0,
      "%s: argmax delta = %+.2f (structural = 0)" % (worst_tag, samples[worst_tag]["arg"][1]))

k4 = [t for t, d in samples.items() if d["arg"][0] == 4]
print("   -> tracers whose trial-corrected argmax picks the over-stiff knots = 4: %d/8"
      % len(k4))
check("C2  the trial-corrected argmax picks the over-stiff knots = 4 for (almost) every "
      "tracer -- the systematic signature of broadband under-fitting, not of a ladder",
      len(k4) >= 7, "%d/8 tracers choose knots = 4" % len(k4))

flagged = [t for t, d in samples.items() if d["p_delta0"] <= 0.02 or d["p_delta0_adq"] <= 0.02]
print("   -> tracers with p_delta0 <= 0.02 (either knot set): %s"
      % (", ".join(flagged) or "none"))
check("C3  no DR2 tracer reaches p_delta0 <= 0.02 under either broadband choice",
      len(flagged) == 0, "flagged: %s" % (", ".join(flagged) or "none"))
json_out["p_local"] = {t: d["p_local"] for t, d in samples.items()}
json_out["p_delta0"] = {t: d["p_delta0"] for t, d in samples.items()}
json_out["p_delta0_adequate_knots"] = {t: d["p_delta0_adq"] for t, d in samples.items()}
json_out["argmax"] = {t: [d["arg"][0], d["arg"][1]] for t, d in samples.items()}

# ------------------------------------------------------------------
print("\n" + "-" * 78)
print("  D. GLOBAL look-elsewhere over 8 tracers (joint null)")
print("-" * 78)

D_global = max(d["D_obs"] for d in samples.values())
g_tag = max(samples, key=lambda t: samples[t]["D_obs"])
D0_global = max(d["D0_obs"] for d in samples.values())
g0_tag = max(samples, key=lambda t: samples[t]["D0_obs"])
D0a_global = max(d["D0a_obs"] for d in samples.values())
Dg = np.empty(NSUR)
D0g = np.empty(NSUR)
D0ag = np.empty(NSUR)
for i in range(NSUR):
    outs = {t: d["fit"](d["draws"][i])[0] for t, d in samples.items()}
    Dg[i] = max(max(v[0] for v in o.values()) for o in outs.values())
    D0g[i] = max(max(o[(nk, 0.0)][0] for nk in KNOT_SET) for o in outs.values())
    D0ag[i] = max(max(o[(nk, 0.0)][0] for nk in KNOT_ADQ) for o in outs.values())
p_global = float(np.mean(Dg >= D_global))
p_delta0_global = float(np.mean(D0g >= D0_global))
p_delta0_global_adq = float(np.mean(D0ag >= D0a_global))
print("   D_global(observed) = %+.2f (best tracer %s)  joint null mean %+.2f max %+.2f"
      % (D_global, g_tag, Dg.mean(), Dg.max()))
print("   -> p_global (8 tracers x 3 knots x 9 shifts) = %.3f" % p_global)
print("   D0_global(observed) = %+.2f (best tracer %s)  joint null mean %+.2f max %+.2f"
      % (D0_global, g0_tag, D0g.mean(), D0g.max()))
print("   -> p_delta0_global (8 tracers x 3 knots, delta = 0) = %.3f" % p_delta0_global)
print("   -> p_delta0_global with the adequate knots (5,6) = %.3f" % p_delta0_global_adq)
print("   (null treats tracers as independent; DESI tracers share footprint and the")
print("    z=0.8-1.1 samples share galaxies -> the true null is broader (optimistic test))")
check("D1  GLOBAL p-value (trial-corrected, 8 tracers) > 0.01", p_global > 0.01,
      "p_global = %.3f" % p_global)
check("D2  GLOBAL delta=0 p-value over 8 tracers x 3 knot counts > 0.01",
      p_delta0_global > 0.01, "p = %.3f" % p_delta0_global)
check("D3  GLOBAL delta=0 p-value with the adequate knots (5,6) > 0.01",
      p_delta0_global_adq > 0.01, "p = %.3f" % p_delta0_global_adq)
claim("D  => the whole DR2 ensemble (best tracer, best knot count, best lambda shift) is "
      "consistent with the no-ladder null (p_global = %.3f); the decisive STRUCTURAL test "
      "(delta = 0, corrected over 8 tracers) gives p = %.3f (knots 4-6) and %.3f "
      "(adequate knots 5-6)." % (p_global, p_delta0_global, p_delta0_global_adq))
json_out.update(D_global=float(D_global), p_global=p_global, D0_global=float(D0_global),
                p_delta0_global=p_delta0_global,
                p_delta0_global_adequate_knots=p_delta0_global_adq)

# ------------------------------------------------------------------
print("\n" + "-" * 78)
print("  E. DR1 vs DR2 SAME-WINDOW replication (headline)")
print("-" * 78)

dr1 = {}
for tag, d in samples.items():
    if d["d1tag"] is None:
        continue
    with h5py.File(os.path.join(DATA, d["d1fn"]), "r") as h:
        xi0 = h["0/value"][:]
    with h5py.File(os.path.join(DATA, "covariance_" + d["d1fn"]), "r") as h:
        s_cov, C = h["observable/0/s"][:], h["value"][:]
    xi_cov = xi0[5:5 + len(s_cov)]
    C0 = C[:len(s_cov), :len(s_cov)]
    m = (s_cov >= s_lo - 2.0) & (s_cov <= s_hi + 2.0)
    s1, y1, C1 = s_cov[m], xi_cov[m], C0[np.ix_(m, m)]
    Ci1 = np.linalg.pinv(C1)
    fit1 = make_fitter(s1, Ci1)
    o1, _ = fit1(y1)
    dr1[tag] = dict(N=len(s1), D0=max(o1[(nk, 0.0)][0] for nk in KNOT_SET),
                    amp=o1[(5, 0.0)][2], s1=s1, fit=fit1, y1=y1,
                    sig=np.sqrt(np.diag(C1)), Cinv=Ci1)

check("E1  DR1 same-window reload reproduces the DR2 window size (23 bins)",
      all(v["N"] == 23 for v in dr1.values()),
      "N per tracer: %s" % sorted(set(v["N"] for v in dr1.values())))
print("   tracer     DR1 N   D0(DR1, same window)  amp(DR1)     D0(DR2)   amp(DR2)")
for tag, v in dr1.items():
    d = samples[tag]
    print("   %-9s %3d     %+18.2f   %+.2e   %+8.2f   %+.2e"
          % (tag, v["N"], v["D0"], v["amp"], d["d5"], d["a5"]))

dr2_lrg3, dr1_lrg3 = samples["LRG3"], dr1["LRG3"]
rng2 = np.random.default_rng(SEED + 1)
n1 = len(dr1_lrg3["s1"])
B1 = spline_basis(dr1_lrg3["s1"], np.linspace(dr1_lrg3["s1"][0], dr1_lrg3["s1"][-1], 5))
cb1 = np.linalg.solve(B1.T @ dr1_lrg3["Cinv"] @ B1, B1.T @ (dr1_lrg3["Cinv"] @ dr1_lrg3["y1"]))
bb1 = B1 @ cb1
L1 = np.linalg.cholesky(np.diag(dr1_lrg3["sig"] ** 2) + 1e-12 * np.eye(n1))
D0n1 = np.empty(NSUR)
for i in range(NSUR):
    o, _ = dr1_lrg3["fit"](bb1 + L1 @ rng2.standard_normal(n1))
    D0n1[i] = max(o[(nk, 0.0)][0] for nk in KNOT_SET)
p1 = float(np.mean(D0n1 >= dr1_lrg3["D0"]))
print("   DR1 LRG3 restricted to the DR2 window: D0 = %+.2f -> p_local(delta=0) = %.3f"
      % (dr1_lrg3["D0"], p1))
print("   DR2 LRG_0.8_1.1 (same window, larger data): D0 = %+.2f -> p_delta0 = %.3f"
      % (dr2_lrg3["D0_obs"], dr2_lrg3["p_delta0"]))
check("E2  at the corrected scale there is no DR1 edge to replicate: both the DR1 "
      "same-window test and the DR2 test are null (min p > 0.05)",
      min(p1, dr2_lrg3["p_delta0"]) > 0.05,
      "DR1 same-window p = %.3f vs DR2 p = %.3f" % (p1, dr2_lrg3["p_delta0"]))
check("E3  the larger DR2 sample does not systematically raise the structural D0 "
      "(|D0(DR2) - D0(DR1 same window)| <= 5)",
      abs(dr2_lrg3["D0_obs"] - dr1_lrg3["D0"]) <= 5.0,
      "D0(DR1) = %+.2f (p = %.3f) -> D0(DR2) = %+.2f (p = %.3f)"
      % (dr1_lrg3["D0"], p1, dr2_lrg3["D0_obs"], dr2_lrg3["p_delta0"]))

j7 = os.path.join(DATA, "07_desi_dr1_test.json")
if os.path.exists(j7):
    with open(j7) as f:
        prev = json.load(f)
    p_wide = float(prev["p_delta0"]["LRG3"])
    print("   DR1 LRG3 in the WIDE window (script 07, s >= 40, official RascalC): "
          "p_delta0 = %.3f" % p_wide)
    check("E4  at the corrected scale the DR1 LRG3 verdict is WINDOW-INDEPENDENT: the wide "
          "window (s >= 42, script 07) and the DR2 window give the same null "
          "(|p_wide - p_narrow| < 0.10)", abs(p_wide - p1) < 0.10,
          "wide window p = %.3f -> DR2 window p = %.3f" % (p_wide, p1))
    json_out["replication"] = dict(dr1_wide_window_p=p_wide, dr1_window_p=p1,
                                   dr1_window_D0=float(dr1_lrg3["D0"]),
                                   dr2_lrg3_D0=float(dr2_lrg3["D0_obs"]),
                                   dr2_lrg3_p=dr2_lrg3["p_delta0"],
                                   dr1_D0={t: float(v["D0"]) for t, v in dr1.items()})
    claim("E  => replication verdict at the CORRECTED scale: DR1 LRG3 gives p = %.3f in the "
          "wide window and p = %.3f in the DR2 window; DR2's larger LRG z0.8-1.1 sample "
          "gives p = %.3f (D0 = %+.2f).  All are null.  NOTE: the 'window-dependent LRG3 "
          "edge' of the pre-correction revision (p = 0.013 wide vs 0.92 narrow) does NOT "
          "survive the units fix -- it was produced by lambda_sync = 406.22 h^-1 Mpc, which "
          "put the n = 4 node (101.6) exactly on the BAO bump (102.0)."
          % (p_wide, p1, dr2_lrg3["p_delta0"], dr2_lrg3["D0_obs"]))
else:
    note("07_desi_dr1_test.json missing -> E4 (window dependence) skipped")

# ------------------------------------------------------------------
print("\n" + "-" * 78)
print("  F. DECISIVE CONTROL -- ladder on top of the DESI best-fit theory curve")
print("-" * 78)

for tag, d in samples.items():
    print("   %-8s  chi2(theory)=%8.1f   dchi2(adding ladder)=%+7.2f   amp=%+.2e"
          % (tag, d["c_th"], d["dchi2_th"], d["amp_th"]))
check("F1  DESI best-fit theory curves load on the same s-grid for all 8 tracers",
      all(len(d["th"]) == len(d["s"]) for d in samples.values()), "8/8 theory curves aligned")
fmax = max(d["dchi2_th"] for d in samples.values())
ftag = max(samples, key=lambda t: samples[t]["dchi2_th"])
from scipy.stats import chi2 as _chi2
p_single = float(_chi2.sf(fmax, 1))
p_bonf = min(1.0, p_single * len(samples))
check("F2  the largest single-tracer improvement on the DESI best-fit curve (+%.2f, %s) is "
      "NOT significant after the look-elsewhere correction over 8 tracers "
      "(p_single = %.4f -> Bonferroni p = %.2f > 0.01)" % (fmax, ftag, p_single, p_bonf),
      p_bonf > 0.01, "p_single = %.4f, 8 tracers -> p_corr = %.3f" % (p_single, p_bonf))
th_amps = np.array([d["amp_th"] for d in samples.values()])
sp_amps = np.array([d["a5"] for d in samples.values()])
n_pos_sp = int((sp_amps > 0).sum())
n_pos_th = int((th_amps > 0).sum())
med_sp = float(np.median(np.abs(sp_amps)))
med_th = float(np.median(np.abs(th_amps)))
print("   amplitudes: spline broadband -> %d positive / %d negative, median |a| = %.2e"
      % (n_pos_sp, len(sp_amps) - n_pos_sp, med_sp))
print("              DESI theory curve -> %d positive / %d negative, median |a| = %.2e"
      % (n_pos_th, len(th_amps) - n_pos_th, med_th))
check("F3  against the DESI best-fit curve the fitted amplitudes are smaller than in the "
      "spline-broadband test (median |a| %.2e -> %.2e) and NOT uniformly signed "
      "(%d positive / %d negative)" % (med_sp, med_th, n_pos_th, len(th_amps) - n_pos_th),
      med_th < med_sp and 0 < n_pos_th < len(th_amps),
      "median |a| down by %.1fx ; spline test sign pattern %d+/%d-"
      % (med_sp / max(med_th, 1e-30), n_pos_sp, len(sp_amps) - n_pos_sp))
claim("F  => against the DESI best-fit model itself (which already contains the BAO "
      "wiggle) the structural ladder adds at most dchi2 = %+.2f for any single tracer (not "
      "significant after the 8-tracer correction) and the median fitted amplitude drops "
      "~%.1fx.  There is no residual ladder in the DR2 data at the corrected scale.  "
      "NOTE: this control is CONSERVATIVE for IDCM by construction -- the LCDM+BAO model "
      "already contains a bump at ~102 h^-1 Mpc and IDCM identifies that scale with "
      "lambda_sync/2 (the n = 2 node), so the control removes part of the structure the "
      "ladder predicts; it tests 'ladder beyond LCDM BAO', not the ladder itself."
      % (fmax, med_sp / max(med_th, 1e-30)))

# ------------------------------------------------------------------
print("\n" + "-" * 78)
print("  G. adequate-broadband statistic (knots 5-6 only, no over-stiff option)")
print("-" * 78)

print("   tracer   D0(adq, obs)  p_delta0(adq)   D0(3 knots, obs)  p_delta0(3 knots)")
for tag, d in samples.items():
    print("   %-8s %+12.2f     %10.3f   %+16.2f   %16.3f"
          % (tag, d["D0a_obs"], d["p_delta0_adq"], d["D0_obs"], d["p_delta0"]))
med_adq = float(np.median([d["D0a_obs"] for d in samples.values()]))
med_raw = float(np.median([d["D0_obs"] for d in samples.values()]))
check("G1  removing the over-stiff knots = 4 option shrinks the typical structural "
      "Delta-chi^2 (median) by a factor >= 2", med_adq * 2.0 <= med_raw,
      "median D0: %.2f (knots 4-6) -> %.2f (knots 5-6)" % (med_raw, med_adq))
claim("G  => the trial-corrected statistic is dominated by the over-stiff knots = 4 "
      "broadband; with an adequate broadband the typical structural Delta-chi^2 falls "
      "from %.2f to %.2f.  Both are consistent with the no-ladder null (D3: p = %.3f on "
      "the adequate knots)." % (med_raw, med_adq, p_delta0_global_adq))
json_out["median_D0_3knots"] = med_raw
json_out["median_D0_adequate_knots"] = med_adq

# ------------------------------------------------------------------
print("\n" + "-" * 78)
print("  H. robustness: structural band restricted to RESOLVABLE modes only")
print("-" * 78)
_nmax_bin = (-1 + math.sqrt(1 + 4 * LAM / ds_bin)) / 2
_res_band = [n for n in BAND if n <= int(_nmax_bin)]
_dropped = [n for n in BAND if n > int(_nmax_bin)]
print("   ds = %.3f h^-1 Mpc -> n_max = %.2f -> resolvable band %s (aliased dropped: %s)"
      % (ds_bin, _nmax_bin, _res_band, _dropped))
_D0res, _nullres = {}, {}
_gband = list(BAND)
BAND[:] = _res_band
try:
    for tag, d in samples.items():
        f = make_fitter(d["s"], d["Cinv"])
        o, _ = f(d["xi"])
        o0 = max(o[(nk, 0.0)][0] for nk in KNOT_SET)
        arr = np.empty(NSUR)
        for i in range(NSUR):
            o2, _ = f(d["draws"][i])
            arr[i] = max(o2[(nk, 0.0)][0] for nk in KNOT_SET)
        _D0res[tag] = float(o0)
        _nullres[tag] = arr
finally:
    BAND[:] = _gband
print("   tracer     D0(res band)  p_delta0(res band)")
for tag in samples:
    print("   %-8s %+12.2f  %14.3f"
          % (tag, _D0res[tag], float(np.mean(_nullres[tag] >= _D0res[tag]))))
_D0g_res = max(_D0res.values())
_nullg_res = np.array([max(_nullres[t][i] for t in samples) for i in range(NSUR)])
_p_res = float(np.mean(_nullg_res >= _D0g_res))
check("H1  with the sub-bin aliased modes dropped (resolvable band n = %s) the DR2 structural "
      "test is STILL null (global p = %.3f > 0.01)" % (_res_band, _p_res), _p_res > 0.01,
      "global D0 = %+.2f (resolvable band), p = %.3f" % (_D0g_res, _p_res))
claim("H  => robustness: with the ladder template restricted to the modes the %.0f h^-1 Mpc "
      "binning can resolve (n = %s), the DR2 verdict is UNCHANGED -- global p = %.3f "
      "(median per-tracer p = %.3f), even though the individual dchi2 rise (the low-n modes "
      "carry the spline's residual broadband shape).  The null is not an artefact of sub-bin "
      "aliasing."
      % (ds_bin, _res_band, _p_res,
         float(np.median([np.mean(_nullres[t] >= _D0res[t]) for t in samples]))))
json_out["D0_resolvable_band"] = _D0res
json_out["p_delta0_global_resolvable_band"] = _p_res

print("\n" + "=" * 78)
print("  RESULT: %d/%d PASS   (+%d structural claims)" % (PASS, PASS + FAIL, len(CLAIMS)))
print("=" * 78)

with open(os.path.join(DR2, "08_desi_dr2_test.json"), "w") as f:
    json.dump(json_out, f, indent=2)
print("  -> data/desi/dr2/08_desi_dr2_test.json written")
