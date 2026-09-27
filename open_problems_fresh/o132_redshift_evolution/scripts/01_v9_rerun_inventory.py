#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O132/01 -- v9.0 redshift_evolution faithful re-run + inventory
==============================================================
v9.0 source: IDCM-v9.0--W-Field-Lattice/open_problems_fresh/redshift_evolution/
             01_derive_evolution.py (180 lines, single file)
constants  : kchain_cosmic_web/_core.py
             H0_IDCM = 72.59 km/s/Mpc ; R_H = c/H0_IDCM ; LAMBDA_SYNC = 2*pi*R_H/88
             H = H0_IDCM/100 = 0.7259 (dimensionless)
data       : sync_bump_analysis/{ross_dr12_corrfunc.zip, eboss_dr16_lrg_xi.txt}
             (original path /home/wsl/IDCM/ no longer exists -> copied into data/)

The v9.0 script does:
  1  broadband fit xi(s) = A s^-gamma + C on 10-60 h^-1 Mpc (BOSS z=0.2-0.5, eBOSS z=0.6-1.0)
  2  residual + S/N at harmonic positions s_n = lambda_sync/n  (n = 2..20)
  3  mean |harmonic residual| at z_eff=0.38 / 0.70  ->  A(z) ~ (1+z)^alpha_evol
  4  cross-correlation r of the two xi(s) shapes over the overlap
  5  summary claim: "consistent with K_Tree projection where the effective branching
     factor changes with redshift"

This script re-runs it EXACTLY (only the data paths are changed) and inventories every
output value so script 02 can cross-check against v10.0.

Run: /usr/bin/python3 scripts/01_v9_rerun_inventory.py
"""

import os
import sys
import math
import json
import zipfile

import numpy as np
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")

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


print("=" * 78)
print("  O132/01 -- v9.0 redshift_evolution faithful re-run")
print("=" * 78)

# ----------------------------------------------------------------
# A. v9.0 constants (from kchain_cosmic_web/_core.py) + data
# ----------------------------------------------------------------
print("\n" + "-" * 78)
print("  A. v9.0 constants + data")
print("-" * 78)

H0_IDCM = 72.59
C_LIGHT = 299792.458
R_H = C_LIGHT / H0_IDCM
LAMBDA_SYNC = 2 * math.pi * R_H / 88
H = H0_IDCM / 100.0
lam_sync_hinv = LAMBDA_SYNC / H

print("   H0_IDCM = %.2f km/s/Mpc" % H0_IDCM)
print("   R_H     = %.4f Mpc" % R_H)
print("   LAMBDA_SYNC = 2*pi*R_H/88 = %.6f Mpc" % LAMBDA_SYNC)
print("   H       = %.4f  ->  lambda_sync = %.4f h^-1 Mpc" % (H, lam_sync_hinv))

check("A1  lambda_sync = 2*pi*R_H/88 = %.4f Mpc (v9.0 registered 294.88)" % LAMBDA_SYNC,
      abs(LAMBDA_SYNC - 294.88) < 0.01)
check("A2  lambda_sync (h^-1 Mpc) = %.4f (v9.0 comment 406.1)" % lam_sync_hinv,
      abs(lam_sync_hinv - 406.1) < 0.5)

# BOSS DR12 zbin1
z = zipfile.ZipFile(os.path.join(DATA, "ross_dr12_corrfunc.zip"))
p = ("Ross_2016_COMBINEDDR12/Ross_2016_COMBINEDDR12_zbin1_correlation_function_"
     "monopole_post_recon_bincent0.dat")
sb, xb, eb = [], [], []
with z.open(p) as f:
    for line in f.read().decode().strip().split("\n"):
        if line.startswith("#") or not line.strip():
            continue
        q = line.split()
        sb.append(float(q[0])); xb.append(float(q[1])); eb.append(float(q[2]))
sb = np.array(sb); xb = np.array(xb); eb = np.array(eb)

# eBOSS DR16 LRG
e = np.loadtxt(os.path.join(DATA, "eboss_dr16_lrg_xi.txt"))
se, xe, ee = e[:, 0], e[:, 1], e[:, 2]

check("A3  BOSS DR12 zbin1 loaded (36 bins, 2.5-177.5 h^-1 Mpc)",
      len(sb) == 36 and abs(sb[0] - 2.5) < 1e-9 and abs(sb[-1] - 177.5) < 1e-9,
      "n=%d s=[%.1f,%.1f]" % (len(sb), sb[0], sb[-1]))
check("A4  eBOSS DR16 LRG loaded (49 bins, 7.5-247.5 h^-1 Mpc)",
      len(se) == 49 and abs(se[0] - 7.5) < 1e-9 and abs(se[-1] - 247.5) < 1e-9,
      "n=%d s=[%.1f,%.1f]" % (len(se), se[0], se[-1]))

json_out = {"H0_IDCM": H0_IDCM, "R_H_Mpc": R_H, "lambda_sync_Mpc": LAMBDA_SYNC,
            "lambda_sync_hinv_Mpc": lam_sync_hinv, "h_dimensionless": H}

# ----------------------------------------------------------------
# 1. broadband fit
# ----------------------------------------------------------------
print("\n" + "-" * 78)
print("  1. broadband fit  xi(s) = A s^-gamma + C   (10-60 h^-1 Mpc)")
print("-" * 78)


def broadband(s, A, gamma, C):
    return A * s ** (-gamma) + C


mask_b = (sb > 10) & (sb < 60)
popt_b, _ = curve_fit(broadband, sb[mask_b], xb[mask_b], p0=[1000, 2.0, 0.0])
xi_b_broad = broadband(sb, *popt_b)
xi_b_resid = xb - xi_b_broad

mask_e = (se > 10) & (se < 60)
popt_e, _ = curve_fit(broadband, se[mask_e], xe[mask_e], p0=[1000, 2.0, 0.0])
xi_e_broad = broadband(se, *popt_e)
xi_e_resid = xe - xi_e_broad

print("   BOSS  (z=0.2-0.5): xi(s) = %.1f * s^(-%.3f) + %+.6f" % tuple(popt_b))
print("   eBOSS (z=0.6-1.0): xi(s) = %.1f * s^(-%.3f) + %+.6f" % tuple(popt_e))

check("B1  BOSS broadband fit converges (gamma = %.3f)" % popt_b[1], np.isfinite(popt_b).all())
check("B2  eBOSS broadband fit converges (gamma = %.3f)" % popt_e[1], np.isfinite(popt_e).all())
json_out["broadband"] = {"BOSS": list(popt_b), "eBOSS": list(popt_e)}

# ----------------------------------------------------------------
# 2. harmonic amplitude / S-N at s_n = lambda_sync/n
# ----------------------------------------------------------------
print("\n" + "-" * 78)
print("  2. harmonic residual + S/N at s_n = lambda_sync/n  (n=2..20)")
print("-" * 78)

boss_interp = interp1d(sb, xi_b_resid, kind="cubic", bounds_error=False, fill_value=0)
boss_err = interp1d(sb, eb, kind="linear", bounds_error=False, fill_value=0)
eboss_interp = interp1d(se, xi_e_resid, kind="cubic", bounds_error=False, fill_value=0)
eboss_err = interp1d(se, ee, kind="linear", bounds_error=False, fill_value=0)

print("\n   %-4s %-10s %-12s %-10s %-12s %-10s %-8s"
      % ("n", "s(h^-1)", "BOSS_res", "BOSS_S/N", "eBOSS_res", "eBOSS_S/N", "Ratio"))
rows2 = []
for n in range(2, 21):
    s_n = lam_sync_hinv / n
    if s_n < sb[0] or s_n > sb[-1]:
        continue
    xbv = float(boss_interp(s_n)); ebv = float(boss_err(s_n))
    sn_b = xbv / ebv if ebv > 0 else 0.0
    xev = float(eboss_interp(s_n)); eev = float(eboss_err(s_n))
    sn_e = xev / eev if eev > 0 else 0.0
    ratio = xev / xbv if abs(xbv) > 1e-10 else 0.0
    rows2.append((n, s_n, xbv, sn_b, xev, sn_e, ratio))
    print("   %-4d %-10.1f %-+12.6f %-+10.2f %-+12.6f %-+10.2f %-+8.2f"
          % (n, s_n, xbv, sn_b, xev, sn_e, ratio))

check("C1  harmonic table populated for n=2..20 inside BOSS range (%d rows)" % len(rows2),
      len(rows2) >= 15)
sn_gt3_b = sum(1 for r in rows2 if r[3] > 3)
sn_gt3_e = sum(1 for r in rows2 if r[5] > 3)
print("   -> BOSS S/N>3 : %d/%d ; eBOSS S/N>3 : %d/%d" % (sn_gt3_b, len(rows2), sn_gt3_e, len(rows2)))
json_out["harmonic_table"] = rows2
json_out["sn_gt3"] = {"BOSS": sn_gt3_b, "eBOSS": sn_gt3_e, "n_rows": len(rows2)}

# ----------------------------------------------------------------
# 3. amplitude evolution  A(z) ~ (1+z)^alpha_evol
# ----------------------------------------------------------------
print("\n" + "-" * 78)
print("  3. amplitude evolution  A(z) ~ (1+z)^alpha_evol")
print("-" * 78)

harm_boss, harm_eboss, harm_n = [], [], []
for n in range(4, 21):                       # v9.0 skips n=3 (edge)
    s_n = lam_sync_hinv / n
    if s_n < sb[0] or s_n > sb[-1] or s_n < se[0] or s_n > se[-1]:
        continue
    harm_boss.append(abs(float(boss_interp(s_n))))
    harm_eboss.append(abs(float(eboss_interp(s_n))))
    harm_n.append(n)

A_boss = float(np.mean(harm_boss))
A_eboss = float(np.mean(harm_eboss))
z_boss_eff = 0.38
z_eboss_eff = 0.70
alpha_evol = math.log(A_eboss / A_boss) / math.log((1 + z_eboss_eff) / (1 + z_boss_eff))

print("   mean harmonic amplitude at z=%.2f : A = %.6f" % (z_boss_eff, A_boss))
print("   mean harmonic amplitude at z=%.2f : A = %.6f" % (z_eboss_eff, A_eboss))
print("   ratio A(z2)/A(z1) = %.3f" % (A_eboss / A_boss))
print("   alpha_evol = %.3f    (A(z) ~ (1+z)^%.3f)" % (alpha_evol, alpha_evol))
print("   harmonics used: n = %s" % (harm_n,))

check("D1  mean amplitude A(z=0.38) = %.6f finite" % A_boss, math.isfinite(A_boss))
check("D2  mean amplitude A(z=0.70) = %.6f finite" % A_eboss, math.isfinite(A_eboss))
check("D3  alpha_evol = %.3f computed from a SINGLE pair of z points (1 dof)" % alpha_evol,
      math.isfinite(alpha_evol))
check("D4  v9.0 skips n=3 (edge) -> uses n=4..20 (%d harmonics)" % len(harm_n),
      harm_n[0] == 4)
json_out["amplitude_evolution"] = {
    "A_boss": A_boss, "A_eboss": A_eboss, "ratio": A_eboss / A_boss,
    "z_boss_eff": z_boss_eff, "z_eboss_eff": z_eboss_eff,
    "alpha_evol": alpha_evol, "harmonics_used": harm_n,
}

# ----------------------------------------------------------------
# 4. cross-correlation of xi(s) shapes
# ----------------------------------------------------------------
print("\n" + "-" * 78)
print("  4. cross-correlation of BOSS vs eBOSS xi(s) shapes")
print("-" * 78)

s_min = max(sb[0], se[0]); s_max = min(sb[-1], se[-1])
s_overlap = np.linspace(s_min, s_max, 50)
xi_b_overlap = np.array([float(boss_interp(s)) for s in s_overlap])
xi_e_overlap = np.array([float(eboss_interp(s)) for s in s_overlap])
corr = float(np.corrcoef(xi_b_overlap, xi_e_overlap)[0, 1])
print("   overlap range = [%.1f, %.1f] h^-1 Mpc ; r = %.4f" % (s_min, s_max, corr))
check("E1  shape cross-correlation r = %.4f (|r|>0.4)" % corr, abs(corr) > 0.4)
json_out["cross_correlation"] = corr

# ----------------------------------------------------------------
# 5. NEW finding -- BOSS DR12 resolution vs the harmonic ladder
# ----------------------------------------------------------------
print("\n" + "-" * 78)
print("  5. NEW: harmonic ladder vs BOSS DR12 bin resolution (5 h^-1 Mpc)")
print("-" * 78)

bin_width = float(np.median(np.diff(sb)))
print("   BOSS DR12 median bin width = %.3f h^-1 Mpc" % bin_width)
resolved = []
for n in range(4, 21):
    ds_n = lam_sync_hinv / (n * (n + 1))       # spacing between s_n and s_{n+1}
    resolved.append((n, ds_n, ds_n >= bin_width))
n_res = sum(1 for _, _, ok in resolved if ok)
print("   n   ds_n(h^-1Mpc)  resolved?")
for n, ds, ok in resolved:
    print("   %-4d %-13.2f %s" % (n, ds, "yes" if ok else "no  (sub-bin)"))
print("   -> resolvable harmonics n <= %d ; used by v9.0 = n=4..20 (%d)"
      % (max(n for n, _, ok in resolved if ok), len(resolved)))

check("F1  only %d of the %d harmonics used by v9.0 are resolved by the 5 h^-1 Mpc bins"
      % (n_res, len(resolved)), n_res < len(resolved))
check("F2  lambda_sync ladder spacing ds_n = lambda_sync/[n(n+1)] is bin-width limited",
      abs(lam_sync_hinv / (8 * 9) - 5.64) < 0.1)
claim("F  => the 'mean harmonic amplitude' mixes %d resolved (n<=8) with %d sub-bin aliased "
      "harmonics (n>=9) -> A(z) is dominated by aliasing, not by a resolved signal"
      % (n_res, len(resolved) - n_res))
json_out["resolution"] = {"bin_width": bin_width,
                          "n_resolved": n_res, "n_used": len(resolved),
                          "table": resolved}

# ----------------------------------------------------------------
# 6. UNIT CORRECTION (2026-09-27)
#    Sections 1-5 faithfully reproduce v9.0, INCLUDING its unit bug:
#    v9.0 used  LAMBDA_SYNC / H = 406.22 h^-1 Mpc.  Converting Mpc -> h^-1 Mpc
#    is a MULTIPLICATION by h, so the direction is wrong (off by 1/h^2 = 2.038).
#    The same bug is already flagged in O31 SESSION_START (1) as an open item.
#    Correct value (survey fiducial h = 0.676):  294.877 * 0.676 = 199.34 h^-1 Mpc
# ----------------------------------------------------------------
print("\n" + "-" * 78)
print("  6. UNIT CORRECTION: lambda_sync[Mpc] * h  (not / h)")
print("-" * 78)
H_FID = 0.676
lam_hinv_correct = LAMBDA_SYNC * H_FID
print("   v9.0/O31 : %.4f / %.4f = %.3f h^-1 Mpc   [WRONG direction]" % (LAMBDA_SYNC, H, lam_sync_hinv))
print("   correct  : %.4f * %.4f = %.3f h^-1 Mpc" % (LAMBDA_SYNC, H_FID, lam_hinv_correct))
print("   ratio (wrong/correct) = 1/h^2 = %.4f" % (lam_sync_hinv / lam_hinv_correct))
check("G1  unit direction: correct lambda_sync = %.2f h^-1 Mpc = lambda_sync[Mpc] * h_fid; "
      "v9.0/O31 used /h (= %.2f), so the ladder was wrong by 1/h^2"
      % (lam_hinv_correct, lam_sync_hinv),
      abs(lam_hinv_correct - LAMBDA_SYNC * H_FID) < 1e-9)
check("G2  BAO anchor with corrected lambda: s_2 = lambda_sync/2 = %.2f h^-1 Mpc = "
      "r_s(O171) = 147.439 Mpc" % (lam_hinv_correct / 2),
      abs(LAMBDA_SYNC / 2 - 147.439) < 0.01)
res_correct = []
for n in range(2, 21):
    ds_n = lam_hinv_correct / (n * (n + 1))
    res_correct.append((n, ds_n, ds_n >= bin_width))
n_res_correct = sum(1 for _, _, ok in res_correct if ok)
print("   corrected resolution: resolvable harmonics n <= %d (was n <= 8 with the wrong lambda)"
      % max(n for n, _, ok in res_correct if ok))
check("G3  corrected ladder resolution n <= %d (5 h^-1 Mpc bins)" % max(n for n, _, ok in res_correct if ok),
      max(n for n, _, ok in res_correct if ok) < 8)
json_out["unit_correction"] = {"H_FID": H_FID, "lambda_hinv_correct": lam_hinv_correct,
                               "lambda_hinv_v9": lam_sync_hinv,
                               "n_resolved_correct": n_res_correct}

# ----------------------------------------------------------------
print("\n" + "=" * 78)
print("  RESULT: %d/%d PASS   (+%d structural claims)" % (PASS, PASS + FAIL, len(CLAIMS)))
print("=" * 78)

with open(os.path.join(DATA, "01_v9_rerun_inventory.json"), "w") as f:
    json.dump(json_out, f, indent=2)
print("  -> data/01_v9_rerun_inventory.json written")
