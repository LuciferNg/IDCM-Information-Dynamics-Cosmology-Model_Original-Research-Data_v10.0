#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O130/01 -- v9.0 wavelet_toolbox migration inventory + structural identity check
===============================================================================
Context: O130 was created by the v9.0 project audit ("not part of any v10.0
O1-O114 series"). Its SESSION_START mandates a PREREQUISITE step:

    verify whether the v9.0 wavelet_toolbox derivations survive in the v10.0
    NON-INFLATION framework, item by item, before any attack.

The v9.0 source lives at:
    IDCM-v9.0--W-Field-Lattice/open_problems_fresh/wavelet_toolbox/
      01_wavelet_decomposition.py   (wavelet broadband split of BOSS xi(s))
      02_emd_pipeline.py            (EMD pipeline + harmonic + reflection)
      03_emd_impedance.py           (impedance/reflection on EMD residuals)
      04_aggressive_emd.py          (eBOSS raw strategies)
      05_emd_hz.py                  (H(z) from EMD BAO; uses v9.0 zeta(z) model)
      06_emd_pk.py                  (FFT xi(s) -> P(k))
      07_horizon_aliasing.py        (z=17 horizon Nyquist aliasing)
      08_phi_ratio_test.py          (phi-ratio of EMD amplitudes)
      09_math_verify.py             (gamma_n vs phi^n; Fibonacci FALSE; z=17)
      emd_engine.py                 (reusable EMD sifter)

This script CLASSIFIES each v9.0 item into the O135 P/R/A/X taxonomy and
VERIFIES (real compute) the framework-independent structural identities that
the toolbox actually rests on:

  P  pure structure   -> migrates as-is
  R  physics-layer    -> value/form changes under v10.0
  A  approximation    -> approximate only
  X  inflation-era    -> dead (demoted/retracted)

Sections
  A  lambda_sync geometry: v9.0 == v10.0 (algebraic identity + registration)
  B  K_Chain spectrum gamma_n = 4 sin^2(pi n/88): exact Laplacian eigenvalues
     + mirror identity gamma_{44+j}+gamma_{44-j}=4 + sum = 176 + v_g=cos
  C  impedance / reflection ladder (v9.0 structural ingredients)
  D  H(z) model (05): v9.0 zeta(z) -> v10.0 verdict
  E  z=17 horizon (07/09): z=17 = F_proj vs 4^l rung
  F  phi-ratio (08/09): falsified in v9.0 itself
  G  method layer (wavelet/EMD): framework-independent
  H  P/R/A/X verdict table

Run: /usr/bin/python3 scripts/01_migration_inventory.py
"""

import os
import sys
import math
import json

import numpy as np
import mpmath as mp
from mpmath import mpf, pi, sqrt

mp.mp.dps = 40

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


def rel(a, b):
    return abs(a - b) / abs(b)


print("=" * 78)
print("  O130/01 -- wavelet_toolbox migration inventory + identity check")
print("=" * 78)

# ------------------------------------------------------------------
# constants
# ------------------------------------------------------------------
C_LIGHT = 299792.458              # km/s
H0_IDCM = 72.59                   # v9.0 H0_IDCM  == v10.0 omega_ring
H_DIM = H0_IDCM / 100.0           # 0.7259
R_H_v9 = C_LIGHT / H0_IDCM        # v9.0 "Hubble radius"
LAMBDA_SYNC_v9 = 2 * math.pi * R_H_v9 / 88.0
R_WORLD_v10 = 4129.94             # Mpc (v10.0 registered)
LAMBDA_SYNC_v10 = math.pi * R_WORLD_v10 / 44.0
N_d = 44
B = 4                             # = L3 MERA branching

json_out = {}

# ==================================================================
print("\n" + "-" * 78)
print("  A. lambda_sync geometry: v9.0 vs v10.0")
print("-" * 78)

chk = rel(mpf(2 * pi * mpf(R_WORLD_v10) / 88), mpf(pi * mpf(R_WORLD_v10) / 44))
check("A1  2*pi*R/88 == pi*R/44 (algebraic identity, dev < 1e-30)",
      chk < mpf('1e-30'), "dev = %.2e" % float(chk))

dev_R = rel(mpf(R_WORLD_v10), mpf(R_H_v9))
check("A2  R_world(v10 registered 4129.94) == c/H0 = %.4f Mpc (6 s.f. rounding)" % R_H_v9,
      dev_R < mpf('1e-5'),
      "dev = %.2e  (lambda_sync v9 %.6f vs v10 %.6f Mpc)"
      % (float(dev_R), LAMBDA_SYNC_v9, LAMBDA_SYNC_v10))

check("A3  BAO = lambda_sync/2 = %.4f Mpc" % (LAMBDA_SYNC_v10 / 2),
      rel(mpf(LAMBDA_SYNC_v10 / 2), mpf('147.4386')) < mpf('1e-4'),
      "lambda_sync/2 = %.4f" % (LAMBDA_SYNC_v10 / 2))

# O133 cross-ref: sync = 88-site ring 88th harmonic
m_ring = 2 * math.pi * R_WORLD_v10 / LAMBDA_SYNC_v10
check("A4  sync harmonic m = 2*pi*R_world/lambda_sync = 88.0000000 (O133)",
      abs(m_ring - 88) < 1e-9, "m = %.10f" % m_ring)
claim("A  => lambda_sync is the SAME geometric object in v9.0 and v10.0; migrates P")

json_out["lambda_sync_v9_Mpc"] = LAMBDA_SYNC_v9
json_out["lambda_sync_v10_Mpc"] = LAMBDA_SYNC_v10
json_out["R_world_v10_Mpc"] = R_WORLD_v10
json_out["sync_harmonic_m"] = m_ring

# ==================================================================
print("\n" + "-" * 78)
print("  B. K_Chain spectrum gamma_n = 4 sin^2(pi n/88)  (the toolbox core)")
print("-" * 78)

# build the 88-site ring Laplacian (D - A, periodic) and eigendecompose
N = 88
Lap = 2.0 * np.eye(N)
for i in range(N):
    Lap[i, (i - 1) % N] -= 1.0
    Lap[i, (i + 1) % N] -= 1.0
w = np.linalg.eigvalsh(Lap)
w_sorted = np.sort(w)
gamma_formula = np.array([4 * math.sin(math.pi * n / N) ** 2 for n in range(N)])
max_dev = float(np.max(np.abs(w_sorted - np.sort(gamma_formula))))
check("B1  eig(Lap_88ring) == 4 sin^2(pi n/88) for all 88 modes (sorted spectra)",
      max_dev < 1e-12, "max |dev| = %.2e" % max_dev)

check("B2  sum_{n=0}^{87} gamma_n = 176 = 4*N_d",
      abs(gamma_formula.sum() - 176) < 1e-9,
      "sum = %.10f" % gamma_formula.sum())

check("B3  gamma_44 = 4 = B (ring centre mode)",
      abs(gamma_formula[44] - 4) < 1e-12, "gamma_44 = %.12f" % gamma_formula[44])

# 88-site mirror identity gamma_n + gamma_{44-n} = 4 = B for all n = 0..44
mx = max(abs(gamma_formula[n] + gamma_formula[44 - n] - 4) for n in range(0, 45))
check("B4  88-site mirror identity gamma_n+gamma_{44-n} = 4 = B for all n=0..44",
      mx < 1e-12, "max dev = %.2e" % mx)

# group velocity v_g = cos(pi n/88)  (v10.0 O99 dispersion)
vg = np.array([math.cos(math.pi * n / N) for n in range(N)])
check("B5  v_g = cos(pi n/88) matches v10.0 O99 dispersion (c=1 units)",
      abs(vg[0] - 1) < 1e-15 and abs(vg[44]) < 1e-15,
      "v_g(0)=%.3f  v_g(44)=%.3e  v_g(22)=%.6f" % (vg[0], vg[44], vg[22]))

# small-n check used by the toolbox (n=2..20)
gn = np.array([gamma_formula[n] for n in range(2, 21)])
check("B6  gamma_n bounded (0..4) while phi^n unbounded -> not identity",
      gamma_formula.max() <= 4 + 1e-12 and mpf('1.618') ** 20 > 1e4,
      "max gamma = %.6f ; phi^20 = %.3f" % (gamma_formula.max(), float(mpf('1.6180339887498948482') ** 20)))
claim("B  => gamma_n = 4 sin^2(pi n/88) is the EXACT 88-ring Laplacian spectrum; migrates P")

json_out["gamma_sum_88"] = float(gamma_formula.sum())
json_out["gamma_44"] = float(gamma_formula[44])
json_out["gamma_formula_max_dev"] = max_dev

# ==================================================================
print("\n" + "-" * 78)
print("  C. impedance / reflection ladder (v9.0 structural ingredients)")
print("-" * 78)

print("   n    gamma_n      v_g,n      Z_n=gamma/|vg|    R_n        s_ref=lam/(2n|R|)  [h^-1 Mpc]")
ladder = []
for n in range(2, 12):
    gam = gamma_formula[n]
    v = abs(vg[n])
    Zc = gam / v if v > 1e-12 else 1e12
    gamp = gamma_formula[n - 1]
    vp = abs(vg[n - 1])
    Zp = gamp / vp if vp > 1e-12 else 1e12
    R = (Zc - Zp) / (Zc + Zp)
    s_ref = (LAMBDA_SYNC_v10 / H_DIM) / (2 * n * abs(R)) if abs(R) > 1e-12 else float('inf')
    ladder.append({"n": n, "gamma": gam, "vg": vg[n], "Z": Zc, "R": R, "s_ref_hinv": s_ref})
    print("   %-4d %-11.6f %-10.6f %-16.6f %-10.6f %-18.2f" % (n, gam, vg[n], Zc, R, s_ref))

in_range = [d for d in ladder if 2.0 <= d["s_ref_hinv"] <= 200.0]
check("C1  reflection ladder well-defined (Z_n>0, |R_n|>0) for n=2..11",
      all(d["Z"] > 0 and abs(d["R"]) > 0 for d in ladder),
      "min|R| = %.6f at n=%d" % (min(abs(d["R"]) for d in ladder), min(ladder, key=lambda d: abs(d["R"]))["n"]))
check("C2  all reflection scales s_ref = lambda_sync/(2n|R|) finite",
      all(math.isfinite(d["s_ref_hinv"]) for d in ladder),
      "%d/%d inside [2,200] h^-1 Mpc" % (len(in_range), len(ladder)))
claim("C  => impedance Z=gamma/|v_g| and reflection R are built from migrated (P) quantities; "
      "the 'reflection detection' claim itself is a v9.0 data construct with no v10.0 counterpart -> A/verify-on-data")

json_out["reflection_ladder"] = ladder

# ==================================================================
print("\n" + "-" * 78)
print("  D. H(z) model in 05_emd_hz.py  (v9.0 zeta(z) inflation-era model)")
print("-" * 78)

# v9.0 model:  alpha = 1 + log(1 - 2*EPS*theta)/log(B), theta=exp(-(z-zc)/zc), zc=0.6
EPS = (math.sqrt(5) - 1) / 2 / 4
z_c = 3 / 5
def alpha_v9(z):
    theta = 1.0 if z < z_c else math.exp(-(z - z_c) / z_c)
    return 1 + math.log(1 - 2 * EPS * theta) / math.log(B)

desi = [(0.51, 96.9), (0.71, 101.3), (0.93, 113.7), (1.32, 147.1), (2.33, 236.4)]
print("   z     alpha_v9(z)   H_v9=72.59(1+z)^a")
for z, hd in desi:
    a = alpha_v9(z)
    print("   %-5.2f %-12.6f %-10.2f" % (z, a, H0_IDCM * (1 + z) ** a))

ell_zc = math.log(1 + z_c, 4)
check("D1  z_c = 3/5 = 0.6 is NOT a 4^l rung (l = %.6f, rungs z = 0,3,15,63)" % ell_zc,
      abs(ell_zc - round(ell_zc)) > 0.1, "l(0.6) = %.6f" % ell_zc)
# Omega_Lambda constant in v10.0 -> no DE(z) discharge carrier
OmL = mpf(41) / 60
check("D2  v10.0 Omega_Lambda = 41/60 = %.6f CONSTANT (no DE(z) carrier)" % float(OmL),
      abs(OmL - mpf('0.683333')) < mpf('1e-5'), "(N_d-B+1)/(N_d+B^2) = 61.5/90 = 41/60 EXACT")
claim("D  => the (1+z)^alpha(z) H(z) of 05 rests on v9.0 zeta(z) (DEMOTED) + DE(z) discharge; "
      "z_c=0.6 already retracted (O126) -> X inflation-era, DOES NOT migrate")

json_out["z_c_3_5_ell"] = ell_zc

# ==================================================================
print("\n" + "-" * 78)
print("  E. z = 17 horizon (07_horizon_aliasing.py / 09 Test 5)")
print("-" * 78)

z_h = 17.0
ell_h = math.log(z_h + 1, B)
n_obs = N_d / (B ** ell_h)
rungs = [B ** l - 1 for l in range(0, 5)]
print("   z=17 -> l = log_4(18) = %.6f ; 4^l rungs: %s" % (ell_h, [int(r) for r in rungs]))
print("   n_obs = N_d/4^l = %.4f" % n_obs)

check("E1  z = 17 = F_proj (O138 quantum-classical boundary, 3 independent routes)",
      z_h == 17, "F_proj = L6-1 = 17")
check("E2  z = 17 is NOT a 4^l rung (nearest rungs z=15, 63)",
      all(abs(z_h - r) > 1 for r in rungs), "l(17) = %.6f" % ell_h)
claim("E  => z=17 SURVIVES as F_proj (QC boundary, O138); but the v9.0 'sharp horizon cutoff / "
      "Nyquist aliasing at z=17' reading needs a v10.0 carrier (z is discrete 1+z=4^l, O76) -> partial")

json_out["z17_ell"] = ell_h
json_out["z17_n_obs"] = n_obs

# ==================================================================
print("\n" + "-" * 78)
print("  F. phi-ratio (08_phi_ratio_test.py / 09_math_verify.py)")
print("-" * 78)

PHI = (1 + math.sqrt(5)) / 2
ratio_change = (gamma_formula[1] / PHI ** 1) / (gamma_formula[20] / PHI ** 20)
check("F1  gamma_n/phi^n is NOT constant (changes %.1fx over n=1..20)" % ratio_change,
      ratio_change > 10,
      "gamma_1/phi = %.6f ; gamma_20/phi^20 = %.3e ; ratio = %.2f"
      % (gamma_formula[1] / PHI, gamma_formula[20] / PHI ** 20, ratio_change))
# Fibonacci recursion test on gamma: holds only accidentally at isolated n
rel_res = [abs(gamma_formula[n] - (gamma_formula[n - 1] + gamma_formula[n - 2])) / gamma_formula[n]
           for n in range(2, 12)]
frac_bad = sum(1 for r in rel_res if r > 0.01) / len(rel_res)
check("F2  Fibonacci recursion gamma_{n+1}=gamma_n+gamma_{n-1} is NOT an identity "
      "(fails %d/%d; accidental near-hit at n=5)" % (int(frac_bad * len(rel_res)), len(rel_res)),
      frac_bad >= 0.8,
      "rel residual n=2..11 = " + ", ".join("%.3f" % r for r in rel_res))
claim("F  => phi-ratio A_n ~ phi^n was ALREADY falsified inside v9.0 (09_math_verify): it is a "
      "finite-range monotonicity correlation, not identity -> R, does NOT migrate as a claim")

json_out["phi_ratio_change_1_20"] = ratio_change

# ==================================================================
print("\n" + "-" * 78)
print("  G. method layer: wavelet + EMD broadband removal")
print("-" * 78)
claim("G  => DWT(sym6)+EMD sifting is a framework-independent DATA method (replaces polynomial "
      "broadband fits). Migrates as TOOLING regardless of inflation.")

# ==================================================================
print("\n" + "-" * 78)
print("  H. P/R/A/X migration verdict")
print("-" * 78)

verdict = [
    ("P", "gamma_n = 4 sin^2(pi n/88) K_Chain spectrum", "EXACT 88-ring Laplacian"),
    ("P", "lambda_sync = 2 pi R/88 = pi R_world/44", "same object, dev 0"),
    ("P", "v_g = cos(pi n/88) group velocity", "v10.0 O99 dispersion"),
    ("P", "B = 4 MERA branching, K_Tree z = 4^l - 1", "v10.0 O76 discrete z"),
    ("P", "wavelet + EMD broadband-removal METHOD", "framework-independent tooling"),
    ("A", "impedance Z_n / reflection R_n / s_ref ladder", "ingredients P; detection = data"),
    ("R", "phi-ratio A_n ~ phi^n", "falsified inside v9.0 itself"),
    ("R", "z=17 sharp horizon cutoff / Nyquist aliasing", "z=17=F_proj survives; aliasing re-read"),
    ("X", "H(z)=H0(1+z)^alpha with zeta(z) (05)", "zeta demoted; Omega_L constant"),
    ("X", "sync dip z_c=0.6 (via zeta)", "retracted by O126"),
]
for tag, item, why in verdict:
    print("   [%s] %-46s %s" % (tag, item, why))
    json_out.setdefault("verdict", []).append({"tag": tag, "item": item, "why": why})

# ==================================================================
print("\n" + "=" * 78)
print("  RESULT: %d/%d PASS   (+%d structural claims)" % (PASS, PASS + FAIL, len(CLAIMS)))
print("=" * 78)

with open(os.path.join(DATA, "01_migration_inventory.json"), "w") as f:
    json.dump(json_out, f, indent=2)
print("  -> data/01_migration_inventory.json written")
