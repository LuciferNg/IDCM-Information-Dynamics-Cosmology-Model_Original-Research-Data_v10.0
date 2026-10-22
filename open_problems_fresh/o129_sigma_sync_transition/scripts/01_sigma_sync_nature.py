#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O129/01 -- sigma_sync nature verdict + v9.0 operator under the v10.0 geometry
=============================================================================
Context: O126 docs/05 section D RETRACTED the v9.0 sync dip (z_c = F4/F5 = 3/5 = 0.6)
as an inflation-era artefact. O126 handed the item back to O129 with the request:
    decide whether O129's sigma_sync IS the dip POSITION (retracted)
    or a WIDTH / OTHER quantity (may survive).

This script answers that by direct inspection + recomputation:

  A  lambda_sync under v9.0 vs v10.0 -- same geometric object? (real compute)
  B  sigma_sync definition classification (operator vs position) -- structural claim
  C  recompute sigma_sync(R_n) from BOSS DR12 xi(s); reproduce the v9.0 table (real compute)
  D  sigma_8 (8 h^-1 Mpc) vs the sigma_sync ladder lambda_sync/(2n) -- on/off ladder (real compute)
  E  v10.0-native owner of the sigma8/sigma_sync question -- structural cross-reference

Run: /usr/bin/python3 scripts/01_sigma_sync_nature.py
"""

import os
import sys
import math
import json
import zipfile

import numpy as np
import mpmath as mp
from mpmath import mpf, pi, sqrt, log
from scipy.interpolate import interp1d

mp.mp.dps = 40

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")

PASS = FAIL = 0
CLAIMS = []          # structural claims: printed but NOT counted in PASS/FAIL


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


def rel(a, b):
    return abs(a - b) / abs(b)


print("=" * 78)
print("  O129/01 -- sigma_sync nature verdict")
print("=" * 78)

# ------------------------------------------------------------------
# constants (v9.0 _core.py + v10.0 O73 definition)
# ------------------------------------------------------------------
C_LIGHT = 299792.458              # km/s (SI)
H0_IDCM = 72.59                   # km/s/Mpc  (v9.0 H0_IDCM; v10.0 omega_ring)
H_DIM = H0_IDCM / 100.0           # 0.7259 dimensionless

R_H_v9 = C_LIGHT / H0_IDCM        # v9.0 "Hubble radius" = 4129.94 Mpc
LAMBDA_SYNC_v9 = 2 * math.pi * R_H_v9 / 88.0    # v9.0 sigma_sync geometry

R_WORLD_v10 = 4129.94             # Mpc (v10.0 O167/O171 definition)
LAMBDA_SYNC_v10 = math.pi * R_WORLD_v10 / 44.0  # v10.0 O73: lambda_sync = pi*R/44

# ==================================================================
print("\n" + "-" * 78)
print("  A. lambda_sync: v9.0 vs v10.0 -- same geometric object?")
print("-" * 78)

# A1: the two FORMULAS are the same object -- test with a common R (algebraic identity)
chk_a = rel(mpf(2 * pi * mpf(R_WORLD_v10) / 88), mpf(pi * mpf(R_WORLD_v10) / 44))
check("A1 lambda_sync formula: 2*pi*R/88 == pi*R/44 (algebraic identity, dev < 1e-30)",
      chk_a < mpf('1e-30'),
      "dev = %.2e" % float(chk_a))
# A2: v10.0 registered R_world equals c/H0 to the registered precision (6 s.f.)
dev_R = rel(mpf(R_WORLD_v10), mpf(R_H_v9))
check("A2 R_world(v10 registered 4129.94) == c/H0 = %.4f Mpc (dev < 1e-5, 6 s.f. rounding)"
      % R_H_v9, dev_R < mpf('1e-5'),
      "dev = %.2e  (v9 lambda_sync %.6f vs v10 %.6f Mpc)"
      % (float(dev_R), LAMBDA_SYNC_v9, LAMBDA_SYNC_v10))
check("A3 BAO = lambda_sync/2 = %.4f Mpc (= r_d proxy)" % (LAMBDA_SYNC_v10 / 2),
      rel(mpf(LAMBDA_SYNC_v10 / 2), mpf(147.4386)) < mpf('1e-4'),
      "lambda_sync/2 = %.4f" % (LAMBDA_SYNC_v10 / 2))

# ==================================================================
print("\n" + "-" * 78)
print("  B. sigma_sync definition -- operator vs position (structural)")
print("-" * 78)
print("""
  v9.0 sigma_sync/01_derive_sigma_sync.py defines:

      sigma_sync^2(R_n) = INT xi(s) * W(s; R_n) ds ,   R_n = lambda_sync/(2n)

  i.e. a HARMONIC-SCALE VARIANCE OPERATOR (a width / amplitude quantity),
  explicitly introduced to REPLACE sigma_8 (8 h^-1 Mpc scale).

  The v9.0 'sync dip POSITION'  z_c = F4/F5 = 3/5 = 0.6  is a DIFFERENT object,
  living in:
      open_problems_fresh/runtime_isa/15_sync_dip_derivation.md
      sync_bump_analysis/01_sync_bump_observer_relative.md
      sync_bump_analysis/03_sync_dip_to_bump_evolution.md
""")
claim("B1 sigma_sync = harmonic-scale VARIANCE OPERATOR at R_n = lambda_sync/(2n), NOT a position")
claim("B2 the dip POSITION z_c = 0.6 lives in a different v9.0 object (runtime_isa/15 + sync_bump_analysis/)")
claim("=> O126 section D (retraction of z_c = 0.6) does NOT, by itself, kill the sigma_sync operator")

# ==================================================================
print("\n" + "-" * 78)
print("  C. recompute sigma_sync(R_n) from BOSS DR12 xi(s)  (v9.0 reproduction)")
print("-" * 78)

zip_path = os.path.join(DATA, "ross_dr12_corrfunc.zip")
dat_in_zip = ("Ross_2016_COMBINEDDR12/"
              "Ross_2016_COMBINEDDR12_zbin1_correlation_function_monopole_post_recon_bincent0.dat")

s_b, xi_b, err_b = [], [], []
with zipfile.ZipFile(zip_path) as z:
    with z.open(dat_in_zip) as f:
        for line in f.read().decode().strip().split("\n"):
            if line.startswith("#") or not line.strip():
                continue
            p = line.split()
            s_b.append(float(p[0])); xi_b.append(float(p[1])); err_b.append(float(p[2]))
s_b = np.array(s_b); xi_b = np.array(xi_b); err_b = np.array(err_b)
print("  BOSS DR12 xi(s): %d points, s in [%.1f, %.1f] h^-1 Mpc"
      % (len(s_b), s_b[0], s_b[-1]))

lam_sync_hinv = LAMBDA_SYNC_v9 / H_DIM          # 406.2 h^-1 Mpc
xi_interp = interp1d(s_b, xi_b, kind="cubic", bounds_error=False, fill_value=0)

# v9.0 recorded table (problem_record section 4.6): n -> (R_n[h^-1], sigma_sync)
V9_TABLE = {2: (101.6, 0.0662), 3: (67.7, 0.1157), 4: (50.8, 0.1732),
            5: (40.6, 0.2339), 8: (25.4, 0.4164), 10: (20.3, 0.5280)}

print("  %-4s %-14s %-12s %-12s %-10s" % ("n", "R_n(h^-1Mpc)", "sigma_sync", "v9.0 value", "dev"))
print("  " + "-" * 58)
recomputed = {}
for n in range(2, 21):
    R_n = lam_sync_hinv / (2 * n)
    if R_n < s_b[0] or R_n > s_b[-1]:
        continue
    s_grid = np.linspace(max(s_b[0], R_n * 0.5), min(s_b[-1], R_n * 1.5), 200)
    xi_grid = np.array([float(xi_interp(s)) for s in s_grid])
    weights = np.exp(-(s_grid - R_n) ** 2 / (2 * (R_n / 2) ** 2))
    ss = math.sqrt(abs(np.trapezoid(xi_grid * weights, s_grid) / np.trapezoid(weights, s_grid)))
    recomputed[n] = (R_n, ss)
    if n in V9_TABLE:
        R_v9, ss_v9 = V9_TABLE[n]
        print("  %-4d %-14.1f %-12.4f %-12.4f %+.2f%%"
              % (n, R_n, ss, ss_v9, 100 * (ss - ss_v9) / ss_v9))

# the table's R_n column must match lambda_sync/(2n)
ok_R = all(abs(recomputed[n][0] - V9_TABLE[n][0]) < 0.6 for n in V9_TABLE if n in recomputed)
check("C1 R_n = lambda_sync/(2n) reproduces v9.0 table R column", ok_R,
      "e.g. n=2 -> %.1f h^-1 Mpc (v9.0 101.6)" % recomputed[2][0])

# sigma_sync values: recompute vs v9.0 record (the v9.0 script used the same formula)
devs = [abs(recomputed[n][1] - V9_TABLE[n][1]) / V9_TABLE[n][1]
        for n in V9_TABLE if n in recomputed]
maxdev = max(devs)
check("C2 sigma_sync(R_n) recomputation reproduces v9.0 table (max dev < 2%)",
      maxdev < 0.02, "max dev = %.3f%%" % (100 * maxdev))

# monotonic: sigma_sync increases as R_n decreases (smaller scales = larger variance)
ns_sorted = sorted(recomputed)
mono = all(recomputed[ns_sorted[i]][1] < recomputed[ns_sorted[i + 1]][1]
           for i in range(len(ns_sorted) - 1))
check("C3 sigma_sync monotonic increasing as R_n shrinks (n up)", mono,
      "n=%d..%d: %.4f -> %.4f" % (ns_sorted[0], ns_sorted[-1],
                                  recomputed[ns_sorted[0]][1], recomputed[ns_sorted[-1]][1]))

claim("C4 sigma_sync values are MEASURED from BOSS DR12 xi(s) -- v9.0 gave ZERO first-principles content")

# ==================================================================
print("\n" + "-" * 78)
print("  D. sigma_8 (8 h^-1 Mpc) vs the sigma_sync ladder  lambda_sync/(2n)")
print("-" * 78)

R8_Mpc = 8.0 / H_DIM                     # 11.021 Mpc
n_equiv = LAMBDA_SYNC_v9 / (2 * R8_Mpc)  # which ladder rung would 8 h^-1 Mpc sit on?
print("  8 h^-1 Mpc = %.3f Mpc" % R8_Mpc)
print("  nearest sigma_sync rung: n = lambda_sync/(2*R8) = %.4f" % n_equiv)
off = abs(n_equiv - round(n_equiv))
check("D1 8 h^-1 Mpc is OFF the sigma_sync ladder (n = %.3f, non-integer)" % n_equiv,
      off > 0.1, "distance to nearest rung = %.4f" % off)
# k-scale
k8 = 2 * math.pi / R8_Mpc
dk = 2 * math.pi / LAMBDA_SYNC_v9
print("  k(8 h^-1 Mpc) = 2*pi/R8 = %.4f Mpc^-1" % k8)
print("  harmonic spacing dk = 2*pi/lambda_sync = %.5f Mpc^-1" % dk)
print("  ratio k8/dk = %.1f harmonic spacings" % (k8 / dk))
check("D2 sigma_8 scale sits many harmonic spacings above the ladder fundamental",
      k8 / dk > 5, "k8/dk = %.1f" % (k8 / dk))
claim("D3 sigma_sync is the ON-LADDER replacement for sigma_8 (which is off-ladder, sub-grid)")

# ==================================================================
print("\n" + "-" * 78)
print("  E. v10.0-native owner of the sigma8 / amplitude question (cross-reference)")
print("-" * 78)
print("""
  In v10.0 the sigma8 / spectral-amplitude question is already owned by:

    O100  (C_l -> P(k), inverse projection operator M)   -- docs/03 sigma8_verdict
    O133  (P(k) chain spectrum, migrated from v9.0 pk_chain_spectrum/)
          -> sigma8 = 0.7482 vs BOSS 0.783 (dev -4.4%)
    O128  (sigma8 normalization, migrated from v9.0 sigma8_norm/)  -- UNSTARTED
    O99   docs/11: sigma_8 pure first-principles = NOT possible
          (genuine sub-grid gap; only calibration via BOSS xi(s) works)
""")
claim("E1 sigma_sync's role (IDCM-native variance normalization) is ALREADY owned by O100/O133/O128")
claim("E2 v9.0 sigma_sync = the 'route E' (empirical calibration) later formalised as O100/O133")

# ==================================================================
print("\n" + "=" * 78)
print("  VERDICT (section D of O126 vs O129's sigma_sync)")
print("=" * 78)
print("""
  (1) O129's sigma_sync is the v9.0 HARMONIC-SCALE VARIANCE OPERATOR
      sigma_sync^2(R_n) = INT xi(s) W(s;R_n) ds at R_n = lambda_sync/(2n).
      It is a WIDTH / AMPLITUDE quantity -- NOT a dip position.

  (2) The dip POSITION z_c = F4/F5 = 0.6 is a SEPARATE v9.0 object
      (runtime_isa/15 + sync_bump_analysis/), retracted by O126 section D.

  (3) => O126's retraction of z_c = 0.6 does NOT kill the sigma_sync operator.
      But v9.0's sigma_sync is a DATA MEASUREMENT (BOSS xi(s)), with no
      first-principles derivation -- so O129's original proposition
      ("derive sigma_sync from first principles") was NEVER fulfilled.

  (4) The operator's geometry (lambda_sync) is IDENTICAL in v9.0 and v10.0 (A1),
      so the operator migrates cleanly; its v10.0-native home is O100/O133/O128.
""")

print("  PASS: %d/%d   (+ %d structural claims, not counted)"
      % (PASS, PASS + FAIL, len(CLAIMS)))

out = {
    "script": "O129/01_sigma_sync_nature.py",
    "date": "2026-09-27",
    "lambda_sync_v9_Mpc": round(LAMBDA_SYNC_v9, 6),
    "lambda_sync_v10_Mpc": round(LAMBDA_SYNC_v10, 6),
    "lambda_sync_identity_dev": float(chk_a),
    "R_world_vs_c_over_H0_dev": float(dev_R),
    "sigma_sync_recomputed": {str(n): round(v[1], 6) for n, v in recomputed.items()},
    "sigma_sync_v9_table": {str(n): V9_TABLE[n][1] for n in V9_TABLE},
    "sigma_sync_max_dev_vs_v9": round(maxdev, 6),
    "sigma8_off_ladder_n": round(n_equiv, 4),
    "verdict": "sigma_sync = variance operator (width), NOT the dip position; geometry identical v9/v10",
    "pass": PASS, "fail": FAIL, "claims": len(CLAIMS),
}
with open(os.path.join(DATA, "01_sigma_sync_nature.json"), "w") as f:
    json.dump(out, f, indent=2)
print("  Saved -> data/01_sigma_sync_nature.json")

if FAIL:
    raise SystemExit(1)
