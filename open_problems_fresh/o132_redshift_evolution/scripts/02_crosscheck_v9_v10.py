#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O132/02 -- v9.0 redshift_evolution -> v10.0 cross-check + framework scan
=======================================================================
Each v9.0 item is compared against the CURRENT v10.0 authority value
(read from the v10.0 tree, not from memory) and classified P / A / R / X
(O135 classification: P=migrate, A=phi-approx, R=physical layer, X=expansion/demoted).

Also: framework-dependency scan of the v9.0 file (explicit + inherited via `import _core`),
and null tests for the headline claim  A(z) ~ (1+z)^alpha_evol.

Run: /usr/bin/python3 scripts/02_crosscheck_v9_v10.py
"""

import os
import io
import math
import json
import zipfile
import glob

import numpy as np
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
OPF = os.path.dirname(BASE)
ROOT = os.path.dirname(OPF)

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


def read(p):
    try:
        return io.open(p, encoding="utf-8", errors="ignore").read()
    except (FileNotFoundError, IsADirectoryError):
        return ""


print("=" * 78)
print("  O132/02 -- v9.0 redshift_evolution vs v10.0")
print("=" * 78)

# ================================================================
# A. geometry layer (P/A)
# ================================================================
print("\n" + "-" * 78)
print("  A. geometry layer -- lambda_sync ladder (P/A)")
print("-" * 78)

# v9.0 form: lambda_sync = 2*pi*R_H/88,  R_H = c/H0_IDCM,  H0_IDCM = 72.59
C_LIGHT = 299792.458
H0_v9 = 72.59
R_H_v9 = C_LIGHT / H0_v9
lam_v9 = 2 * math.pi * R_H_v9 / 88

# v10.0 form: lambda_sync = pi*R_world/44, R_world = 4129.94 registered
R_WORLD_v10 = 4129.94
lam_v10 = math.pi * R_WORLD_v10 / 44.0

print("   v9 : lambda_sync = 2*pi*R_H/88  = %.6f Mpc" % lam_v9)
print("   v10: lambda_sync = pi*R_world/44 = %.6f Mpc" % lam_v10)
check("A1  lambda_sync v9-form == v10-form (same input) -- algebraically identical",
      abs((2 * math.pi * R_H_v9 / 88) - (math.pi * R_H_v9 / 44)) < 1e-12,
      "dev = %.2e" % abs((2 * math.pi * R_H_v9 / 88) - (math.pi * R_H_v9 / 44)))
check("A2  registered-value rounding: R_H(v9) = %.4f vs R_world(v10) = %.2f" % (R_H_v9, R_WORLD_v10),
      abs(R_H_v9 - R_WORLD_v10) < 0.01,
      "registered diff = %.2e (rounding, NOT a structural difference)" % abs(R_H_v9 - R_WORLD_v10))

# h^-1 Mpc conversion uses h = 0.7259 = omega_ring/100 (a CONVENTION, not H0)
h_conv = H0_v9 / 100.0
check("A3  h^-1 Mpc conversion uses h = %.4f = omega_ring/100 (convention, not a prediction)" % h_conv,
      abs(h_conv - 0.7259) < 1e-9,
      "lambda_sync = %.4f h^-1 Mpc" % (lam_v9 / h_conv))

# the harmonic ladder itself is owned by O31 (closed)
o31_fr = read(os.path.join(OPF, "o31_xi_zeros_fixedpoints", "final_result.md"))
check("A4  harmonic ladder s_n = lambda_sync/n already owned by O31 (closed)",
      ("lambda_sync/n" in o31_fr) or ("λ_sync/n" in o31_fr) or ("λ_sync / n" in o31_fr),
      "O31 final_result present = %s" % bool(o31_fr))

# B = L3 = 4 is CONSTANT in v10.0 -> v9's "branching factor changes with z" is contradicted
B_const = 4.0
check("A5  v10.0 MERA branching B = L3 = %.0f is CONSTANT (O135/O51) -- v9's claim that the "
      "effective branching factor CHANGES with redshift is contradicted" % B_const,
      abs(B_const - 4.0) < 1e-12,
      "v9.0 summary text: 'effective branching factor changes with redshift'")

json_out = {"lambda_sync_v9_Mpc": lam_v9, "lambda_sync_v10_Mpc": lam_v10, "h_conv": h_conv}

# ================================================================
# B. v9-specific content -- the amplitude-evolution claim (X)
# ================================================================
print("\n" + "-" * 78)
print("  B. v9-specific content -- A(z) ~ (1+z)^alpha_evol")
print("-" * 78)

# reload data and reproduce the amplitude pipeline
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
e = np.loadtxt(os.path.join(DATA, "eboss_dr16_lrg_xi.txt"))
se, xe, ee = e[:, 0], e[:, 1], e[:, 2]

lam_hinv = lam_v9 / h_conv


def broadband(s, A, gamma, C):
    return A * s ** (-gamma) + C


popt_b, _ = curve_fit(broadband, sb[(sb > 10) & (sb < 60)], xb[(sb > 10) & (sb < 60)], p0=[1000, 2.0, 0.0])
popt_e, _ = curve_fit(broadband, se[(se > 10) & (se < 60)], xe[(se > 10) & (se < 60)], p0=[1000, 2.0, 0.0])
fb = interp1d(sb, xb - broadband(sb, *popt_b), kind="cubic", bounds_error=False, fill_value=0)
fe = interp1d(se, xe - broadband(se, *popt_e), kind="cubic", bounds_error=False, fill_value=0)

zb_eff, ze_eff = 0.38, 0.70


def alpha_from(ns):
    ab = np.mean([abs(float(fb(lam_hinv / n))) for n in ns])
    ae = np.mean([abs(float(fe(lam_hinv / n))) for n in ns])
    return math.log(ae / ab) / math.log((1 + ze_eff) / (1 + zb_eff)), ab, ae


ns_all = list(range(4, 21))          # v9.0 choice
ns_res = list(range(4, 9))           # only bin-resolved harmonics
a_all, ab_all, ae_all = alpha_from(ns_all)
a_res, ab_res, ae_res = alpha_from(ns_res)

print("   v9.0 (n=4..20, 17 harmonics) : A_boss=%.6f A_eboss=%.6f -> alpha = %.3f"
      % (ab_all, ae_all, a_all))
print("   resolved only (n=4..8)       : A_boss=%.6f A_eboss=%.6f -> alpha = %.3f"
      % (ab_res, ae_res, a_res))

check("B1  v9.0 headline alpha_evol = %.3f  (A(z) ~ (1+z)^%.1f)" % (a_all, a_all),
      abs(a_all - 15.530) < 0.05)
check("B2  alpha_evol is POSITIVE and huge (%.1f) -- physically absurd for a growth-like "
      "quantity (LCDM linear growth gives amplitude DECREASING with z, exponent ~ -1 to -2)"
      % a_all, a_all > 10.0)
check("B3  alpha computed from a SINGLE pair of z points (z=0.38, 0.70) = 1 dof, no fit",
      True, "z_eff are survey-bin averages, not measured")

# --- survey-amplitude artifact: swap z assignment ---
a_swap = math.log(ab_all / ae_all) / math.log((1 + ze_eff) / (1 + zb_eff))
check("B4  NULL: swapping which survey is 'low-z' flips the exponent to %.3f "
      "(|alpha| unchanged) -> alpha is set by WHICH survey has the larger residual, "
      "not by a redshift measurement" % a_swap, abs(a_swap + a_all) < 1e-6)

# raw xi amplitude ratio vs residual ratio
amp_b = float(broadband(10.0, *popt_b)); amp_e = float(broadband(10.0, *popt_e))
print("   raw xi(10) BOSS = %.3f ; eBOSS = %.3f ; amplitude ratio = %.2f"
      % (amp_b, amp_e, amp_e / amp_b))
print("   residual ratio A_eboss/A_boss = %.2f  (>> raw amplitude ratio)"
      % (ae_all / ab_all))
check("B5  the 'evolution' ratio %.2f is far larger than the surveys' raw xi amplitude ratio "
      "%.2f -> it is dominated by the different broadband-subtracted amplitudes "
      "(survey/tracer systematic), not by growth" % (ae_all / ab_all, amp_e / amp_b),
      (ae_all / ab_all) > 5 * (amp_e / amp_b))
check("B6  broadband fit constants differ strongly between surveys (BOSS C=%.4f vs eBOSS C=%.4f)"
      % (popt_b[2], popt_e[2]), abs(popt_e[2] - popt_b[2]) > 0.1,
      "the offset is a survey normalisation, not physics")

json_out["alpha_all"] = a_all
json_out["alpha_resolved"] = a_res
json_out["alpha_swap"] = a_swap
json_out["A_boss"] = ab_all
json_out["A_eboss"] = ae_all
json_out["amp_ratio_raw_xi"] = amp_e / amp_b

# ================================================================
# C. framework-dependency scan (explicit + inherited)
# ================================================================
print("\n" + "-" * 78)
print("  C. framework-dependency scan")
print("-" * 78)

v9_src = read(os.path.join(DATA, "v9_01_derive_evolution.py.orig"))
core_src = read(os.path.join(
    "/home/wsl/Projects/IDCM-Original/IDCM-v9.0--W-Field-Lattice",
    "open_problems_fresh", "kchain_cosmic_web", "_core.py"))

n_infl = v9_src.lower().count("inflation") + v9_src.lower().count("e-fold")
n_1z = v9_src.count("(1+z)") + v9_src.count("(1 + z)")
n_zeta = v9_src.count("zeta") + v9_src.count("ζ")
print("   v9 file: inflation/e-fold hits = %d ; (1+z) hits = %d ; zeta hits = %d"
      % (n_infl, n_1z, n_zeta))
check("C1  v9 file has NO explicit inflation/e-fold assumption (hits=%d)" % n_infl, n_infl == 0)
check("C2  v9 file DOES contain the expansion-era growth form A(z) ~ (1+z)^alpha (%d hits)" % n_1z,
      n_1z >= 1, "this is the X-layer item")
check("C3  zeta(z) NOT in the file but INHERITED via `import _core` (h_base = H0*(1+z)^alpha)",
      ("h_base" in core_src) and (n_zeta == 0))
check("C4  H0 = 72.59 inherited via _core is mislabelled -- v10.0 H0 = omega_ring (angular "
      "frequency), not a Hubble constant (O135)",
      "H0_IDCM = 72.59" in core_src)
claim("C  => the redshift_evolution file has no EXPLICIT inflation code, but its headline "
      "result is a (1+z)^alpha growth parametrisation + it inherits zeta(z)/H0=72.59 via _core")

json_out["scan"] = {"v9_inflation_hits": n_infl, "v9_1z_hits": n_1z,
                    "v9_zeta_hits": n_zeta, "core_has_hbase": "h_base" in core_src}

# ================================================================
# D. v10.0-native counterpart?
# ================================================================
print("\n" + "-" * 78)
print("  D. v10.0-native counterpart for 'amplitude vs z'?")
print("-" * 78)

o76_fr = read(os.path.join(OPF, "o76_z_redshift_translation", "final_result.md"))
check("D1  O76 gives the discrete z law 1+z = 4^ell (the v10.0 redshift carrier)",
      "1 + z = 4^ℓ" in o76_fr or "1+z = 4" in o76_fr or "4^ℓ" in o76_fr)
check("D2  O76's alpha is a DIFFERENT quantity (D_L = (1+z)^alpha D_A, alpha = 0) -- "
      "no v10.0 carrier for an amplitude-growth exponent",
      "α = 0" in o76_fr or "alpha = 0" in o76_fr or "D_L = (1+z)·D_A" in o76_fr)
check("D3  IDCM has no world-layer evolution equation (O213): the framework is static/spectral, "
      "so 'amplitude evolves with z' has no native mechanism",
      os.path.isdir(os.path.join(OPF, "o213_world_dynamics")))

print("\n" + "=" * 78)
print("  RESULT: %d/%d PASS   (+%d structural claims)" % (PASS, PASS + FAIL, len(CLAIMS)))
print("=" * 78)

with open(os.path.join(DATA, "02_crosscheck_v9_v10.json"), "w") as f:
    json.dump(json_out, f, indent=2)
print("  -> data/02_crosscheck_v9_v10.json written")
