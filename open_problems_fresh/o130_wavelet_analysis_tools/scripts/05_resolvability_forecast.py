#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O130/05 -- resolvability law, window leakage, and survey forecast
=================================================================
CONSTRUCTIVE continuation of the O130 migration verdict.  The migrated (P)
structure is the K_Chain ladder

    peaks at  s_n = lambda_sync/n ,  lambda_sync = pi*R_world/44 = 198.63 h^-1 Mpc

⚠️ 2026-09-28 UNITS CORRECTION: lambda_sync = 294.877026 Mpc (PHYSICAL Mpc).
The survey xi(s) axis is in h^-1 Mpc, so lambda_sync[h^-1 Mpc] = 294.877*h_fid
= 198.63.  v9.0 `_core.py` wrote LAMBDA_SYNC/H (divide!), giving 406.22, which
is 1/h^2 = 1.897x too long, and the migration carried it verbatim -- every
number in the earlier revision of this script was therefore computed at the
wrong scale.  See docs/04_unit_correction.md; the empirical proof of the axis
unit is that the BAO bump of the released DESI DR2 best-fit theory curve sits
at s = 102.0 h^-1 Mpc = r_d(147.09 Mpc) * h_fid.

  A  sampling law: harmonic spacing Delta_s_n = lambda/[n(n+1)] vs bin width
  B  window (Rayleigh) resolution + explicit leakage matrix of the ring basis
  C  survey table + structural thresholds (n = N_d/2, N_d)
  D  z = 17 = F_proj boundary: the v10.0-native form of the v9.0 'horizon aliasing'
  E  verdict + forecast

Run: /usr/bin/python3 scripts/05_resolvability_forecast.py
"""

import os
import sys
import math
import json

import numpy as np

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
print("  O130/05 -- resolvability law, leakage, survey forecast")
print("=" * 78)

# --- UNITS: corrected 2026-09-28 (see docs/04_unit_correction.md) -------------
# lambda_sync = 2*pi*R_H/88 = 294.877026 Mpc (PHYSICAL Mpc); the survey s-axis is
# in h^-1 Mpc => lambda_sync[h^-1 Mpc] = lambda_sync[Mpc] * h_fid.
# v9.0 _core.py wrote LAMBDA_SYNC / H (divide!) = 406.22 -> 1.897x too long.
LAM_MPC = 294.877026
H_FID = 0.6736
LAM = LAM_MPC * H_FID                            # 198.63 h^-1 Mpc
N_d = 44
F_proj = 17
json_out = {"lam_hinv_Mpc": LAM, "lam_Mpc": LAM_MPC, "h_fid": H_FID}

# ------------------------------------------------------------------
print("\n" + "-" * 78)
print("  A. sampling law: Delta_s_n = lambda/[n(n+1)] vs bin width")
print("-" * 78)

print("   harmonic spacing   Delta_s_n = s_n - s_{n+1} = lambda/[n(n+1)]")
print("   resolvable iff     Delta_s_n >= Delta_s_bin")
print("   =>  n_max(Delta_s_bin) = (-1 + sqrt(1 + 4*lambda/Delta_s_bin)) / 2")


def n_max(ds_bin):
    return (-1 + math.sqrt(1 + 4 * LAM / ds_bin)) / 2


for ds in (5, 4, 3, 2, 1, 0.5):
    print("     Delta_s_bin = %-6.3f  ->  n_max = %6.3f" % (ds, n_max(ds)))

check("A1  n_max(5 h^-1 Mpc) = 5.823 (BOSS DR12 / eBOSS DR16 binning)",
      abs(n_max(5.0) - 5.823) < 0.01, "%.3f" % n_max(5.0))
check("A2  n_max(4 h^-1 Mpc) = 6.565 (DESI DR1/DR2 galaxy+QSO)",
      abs(n_max(4.0) - 6.565) < 0.01, "%.3f" % n_max(4.0))
check("A3  law is monotone: finer bins -> more resolvable modes",
      n_max(0.5) > n_max(1.0) > n_max(2.0) > n_max(4.0) > n_max(5.0),
      "%.2f > %.2f > %.2f > %.2f > %.2f"
      % (n_max(0.5), n_max(1.0), n_max(2.0), n_max(4.0), n_max(5.0)))

print("\n   where the ladder actually lives (j = 1 peaks, n = 3..9):")
nodes = [(n, LAM / n) for n in range(3, 10)]
print("     " + ", ".join("n=%d: %.1f" % (n, s) for n, s in nodes))
in_dr2 = [n for n, s in nodes if 62.04 <= s <= 150.02]
print("     DESI DR2 BAO-fit window [62.0, 150.0] contains only n = %s of the j=1 nodes"
      % (in_dr2 or "none"))
check("A4  the DESI DR2 BAO-fit window [62,150] contains only ONE of the seven j=1 "
      "nodes (n = 3 at 66.2 h^-1 Mpc) -- the ladder's j=1 structure lives at "
      "22-66 h^-1 Mpc, i.e. mostly BELOW that window", len(in_dr2) == 1,
      "in-window j=1 nodes: %s" % (in_dr2 or "none"))

json_out["n_max_by_bin"] = {str(d): n_max(d) for d in (5, 4, 3, 2, 1, 0.5, 0.205)}
json_out["ladder_nodes_j1"] = {str(n): LAM / n for n in range(3, 10)}

# ------------------------------------------------------------------
print("\n" + "-" * 78)
print("  B. window (Rayleigh) resolution + leakage matrix of the ring basis")
print("-" * 78)

print("   The ring basis is cos(2*pi*n*s/lambda).  Two modes separated by Delta_n have")
print("   frequency separation Delta_k = 2*pi*Delta_n/lambda; resolving them over a window")
print("   of length T requires T >= 2*pi/Delta_k = lambda/Delta_n.")
print("   =>  mode resolution  Delta_n_res = lambda / T   (Rayleigh)")

for T, name in ((175.0, "BOSS DR12 range"), (240.0, "eBOSS DR16 range"),
                (200.0, "DESI Ly-alpha range"), (LAM, "T = lambda_sync")):
    print("     T = %-6.1f h^-1 Mpc (%-18s) ->  Delta_n_res = %.3f" % (T, name, LAM / T))

dres_boss = LAM / 175.0
check("B1  BOSS DR12 mode resolution Delta_n_res = %.3f is MARGINAL (1.0 < dres < 1.5): "
      "adjacent modes are only just separable over the BOSS window" % dres_boss,
      1.0 < dres_boss < 1.5, "needs T >= lambda_sync = %.1f h^-1 Mpc for dres < 1" % LAM)

# explicit leakage (normalised Gram) over the BOSS window
s0, s1 = 2.5, 177.5
T = s1 - s0


def gram(m, n):
    a = 2 * math.pi * m / LAM
    b = 2 * math.pi * n / LAM
    def F(x):
        t1 = 0.0 if abs(a - b) < 1e-14 else math.sin((a - b) * x) / (2 * (a - b))
        t2 = 0.0 if abs(a + b) < 1e-14 else math.sin((a + b) * x) / (2 * (a + b))
        return t1 + t2
    return abs(F(s1) - F(s0)) / (T / 2)


BAND = list(range(2, 21))
print("\n   normalised leakage matrix |<m|n>| (rows m, cols n = 2..20), BOSS window [2.5,177.5]:")
print("        " + " ".join("%5d" % n for n in BAND))
L = np.zeros((len(BAND), len(BAND)))
for i, m in enumerate(BAND):
    row = []
    for j, n in enumerate(BAND):
        L[i, j] = 1.0 if m == n else gram(m, n)
        row.append("%5.2f" % L[i, j])
    print("     %-3d " % m + " ".join(row))

offdiag = np.array([L[i, j] for i in range(len(BAND)) for j in range(len(BAND)) if i != j])
adj = np.array([L[i, j] for i in range(len(BAND)) for j in range(len(BAND))
                if abs(BAND[i] - BAND[j]) == 1])
check("B2  adjacent-mode leakage is MODEST at the corrected scale (max %.3f for Delta_n = 1, "
      "power %.1f%%) -- lambda_sync = 198.63 h^-1 Mpc makes the BOSS window marginal for "
      "adjacent modes, so mode positions are broadened but not scrambled"
      % (float(adj.max()), 100 * float(adj.max()) ** 2),
      float(adj.max()) < 0.2,
      "adjacent |<m|n>| max = %.3f, median = %.3f ; global max = %.3f"
      % (float(adj.max()), float(np.median(adj)), float(offdiag.max())))
claim("B  => with the corrected scale the '19 harmonics' are NOT independent measurements "
      "(bin Nyquist in A), but the window is NOT the main obstruction any more: the Rayleigh "
      "resolution over the BOSS window is only Delta_n_res = %.2f (marginal) and adjacent-mode "
      "leakage is ~%.2f.  Ranked obstructions: (1) bin Nyquist n_max = %.2f; "
      "(2) broadband degeneracy (script 04); (3) window Rayleigh %.2f."
      % (dres_boss, float(adj.max()), n_max(5.0), dres_boss))

json_out["delta_n_res_BOSS"] = dres_boss
json_out["leakage_median_offdiag"] = float(np.median(offdiag))
json_out["leakage_adjacent_max"] = float(adj.max())

# ------------------------------------------------------------------
print("\n" + "-" * 78)
print("  C. survey table + structural thresholds")
print("-" * 78)

surveys = [
    ("BOSS DR12 post-recon monopole", 5.0, 175.0, "this work / O133"),
    ("eBOSS DR16 LRG", 5.0, 240.0, "data/eboss_dr16_lrg_xi.txt"),
    ("DESI DR1 galaxies+QSO", 4.0, 200.0, "DESI 2024 IV (4 h^-1 Mpc bins)"),
    ("DESI DR2 galaxies+QSO", 4.0, 200.0, "DESI 2025 II (4 h^-1 Mpc bins)"),
    ("DESI Ly-alpha (model grid)", 2.0, 300.0, "DESI 2025 I (2 h^-1 Mpc model)"),
]
print("   survey                          Ds_bin   range    n_max   Dn_res")
for name, ds, T_, src in surveys:
    print("   %-30s %6.1f %8.1f %8.2f %8.2f" % (name, ds, T_, n_max(ds), LAM / T_))

print("\n   structural thresholds (zero-parameter):")
th = [("n = F_proj/2 = 8.5", F_proj / 2), ("n = L5 = 11", 11), ("n = F6 = 8", 8),
      ("n = N_d/2 = 22", N_d / 2), ("n = N_d = 44", N_d)]
print("   target                        n      required Ds_bin (h^-1 Mpc)")
for lab, n in th:
    print("   %-28s %5.1f   %.4f" % (lab, n, LAM / (n * (n + 1))))

req_85 = LAM / (8.5 * 9.5)
dev85 = 100 * abs(req_85 - 5.0) / 5.0
print("\n   NOTE: BOSS DR12 uses 5.0 h^-1 Mpc and lambda/(8.5*9.5) = %.4f (dev %.2f%%)."
      % (req_85, dev85))
print("   The earlier revision of this script reported dev 0.61%% here and recorded it as a")
print("   'coincidence' + possible prediction -- that was an ARTEFACT of the units error")
print("   (lambda_used = 406.22 instead of 198.63).  At the corrected scale the BOSS bin")
print("   width is ~2x COARSER than the n = F_proj/2 threshold, so the coincidence is DEAD.")
check("C0  the BOSS 5 h^-1 Mpc bin is NOT at the n = F_proj/2 threshold "
      "(dev %.1f%% > 10%%) -- the previously reported 0.61%% 'coincidence' was a units "
      "artefact and is retracted" % dev85, dev85 > 10.0, "req_85 = %.4f vs bin 5.0" % req_85)

check("C1  required bin for n = N_d/2 = 22 is %.4f h^-1 Mpc (finer than any current survey)"
      % (LAM / (22 * 23)), LAM / (22 * 23) < 1.0, "%.4f" % (LAM / (22 * 23)))
check("C2  required bin for n = N_d = 44 (ring Nyquist) is %.4f h^-1 Mpc"
      % (LAM / (44 * 45)), LAM / (44 * 45) < 0.3, "%.4f" % (LAM / (44 * 45)))
claim("C  => zero-parameter forecast: no existing or planned galaxy survey binning can resolve "
      "the ladder beyond n = %.2f (BOSS/eBOSS 5 h^-1 Mpc -> %.2f; DESI 4 h^-1 Mpc -> %.2f).  "
      "Resolving n = N_d/2 = 22 needs Delta_s <= %.4f h^-1 Mpc; n = N_d = 44 needs <= %.4f."
      % (n_max(4.0), n_max(5.0), n_max(4.0), LAM / (22 * 23), LAM / (44 * 45)))

json_out["thresholds"] = {lab: LAM / (n * (n + 1)) for lab, n in th}
json_out["boss_bin_vs_Fproj_half_dev_pct"] = dev85

# ------------------------------------------------------------------
print("\n" + "-" * 78)
print("  D. z = 17 = F_proj: v10.0-native form of the v9.0 'horizon aliasing'")
print("-" * 78)

B = 4
rungs = [B ** l - 1 for l in range(0, 6)]
ell_17 = math.log(1 + F_proj, B)
n_obs = N_d / (B ** ell_17)
print("   v10.0 discrete z: 1+z = 4^l  ->  rungs z = %s" % [int(r) for r in rungs])
print("   F_proj = 17 = L6 - 1 (O138 QC boundary) -> l = log_4(18) = %.5f  (NON-INTEGER)" % ell_17)
print("   observable mode count n_obs = N_d/4^l = %.4f  (NON-INTEGER)" % n_obs)

check("D1  F_proj = 17 cuts the K_Tree MID-rung (l = %.5f, not an integer)" % ell_17,
      abs(ell_17 - round(ell_17)) > 0.05, "l = %.5f ; nearest rungs l = 2 (z=15), 3 (z=63)" % ell_17)
check("D2  observable mode count is non-integer (%.4f) -> no sharp mode cutoff" % n_obs,
      abs(n_obs - round(n_obs)) > 0.05, "n_obs = %.4f" % n_obs)
claim("D  => the v9.0 'sharp horizon cutoff / Nyquist aliasing at z = 17' has NO exact v10.0 "
      "carrier: F_proj = 17 cuts the K_Tree mid-rung (l = 2.085), so there is no integer mode "
      "cutoff to fold at.  The correct v10.0-native description of the same physics is the "
      "finite-window spectral leakage of section B.")

json_out["ell_Fproj"] = ell_17
json_out["n_obs_Fproj"] = n_obs

# ------------------------------------------------------------------
print("\n" + "-" * 78)
print("  E. verdict + forecast")
print("-" * 78)
claim("E  => the migrated K_Chain ladder is a well-defined, zero-parameter prediction whose "
      "detectability is fully determined by (bin width, window length).  At the corrected "
      "scale lambda_sync = %.1f h^-1 Mpc (= %.1f Mpc physical), its j=1 nodes sit at "
      "22-66 h^-1 Mpc: BOSS/eBOSS/DESI DR1 can reach n <= %.2f / %.2f and the DESI DR2 "
      "BAO-fit window [62,150] covers only the n = 3 node.  Sub-h^-1 Mpc binning plus a "
      "window of order lambda_sync is required to test the high-n ladder at all."
      % (LAM, LAM_MPC, n_max(5.0), n_max(4.0)))

print("\n" + "=" * 78)
print("  RESULT: %d/%d PASS   (+%d structural claims)" % (PASS, PASS + FAIL, len(CLAIMS)))
print("=" * 78)

with open(os.path.join(DATA, "05_resolvability_forecast.json"), "w") as f:
    json.dump(json_out, f, indent=2)
print("  -> data/05_resolvability_forecast.json written")
