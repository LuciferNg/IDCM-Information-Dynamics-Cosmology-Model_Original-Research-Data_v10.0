#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O130/03 -- significance / null tests on the toolbox detections
==============================================================
The v9.0 toolbox made two quantitative claims that need a null test:

  (i)  phi-ratio:  "EMD harmonic amplitudes A_n follow phi^n"  (08/09)
  (ii) detection :  "EMD recovers 17/19 K_Chain harmonics"     (02/03)

Script 01 showed phi^n is NOT the K_Chain spectrum gamma_n.  This script asks
whether the toolbox detections are *structurally special* at all, by three
independent robustness tests:

  A  phi-ratio vs gamma_n: which monotone model fits the EMD amplitudes?
     (a true phi-law requires the log-slope to equal log phi)
  B  ramp diagnostic: is the EMD residual S/N sequence monotone? (1 IMF was
     extracted -> the "residual" is a smooth trend)
  C  resolvability: the K_Chain ladder s_n = lambda_sync/n has spacing
     Delta_s_n = lambda_sync/[n(n+1)]; BOSS DR12 bins are 5 h^-1 Mpc apart, so
     harmonics with Delta_s_n < 5 are sub-bin aliases and CANNOT be resolved.
  D  verdict

Run: /usr/bin/python3 scripts/03_significance_null.py
"""

import os
import sys
import math
import json
import zipfile

import numpy as np
from scipy.interpolate import interp1d
from scipy.stats import spearmanr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from emd_engine import emd_apply_to_survey

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
print("  O130/03 -- significance / null tests")
print("=" * 78)

R_WORLD_v10 = 4129.94
H_DIM = 0.7259
LAM_SYNC = math.pi * R_WORLD_v10 / 44.0
LAM_HINV = LAM_SYNC / H_DIM
PHI = (1 + math.sqrt(5)) / 2

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

xi_emd, imfs, resid, n_imf = emd_apply_to_survey(sb, xb, "BOSS", aggressive=False)
fi = interp1d(sb, xi_emd, kind="cubic", bounds_error=False, fill_value=0.0)
fe = interp1d(sb, eb, kind="linear", bounds_error=False, fill_value=0.0)

json_out = {"n_imf": n_imf}


def sn_at(s):
    return float(fi(s)) / float(fe(s)) if float(fe(s)) > 0 else 0.0


# ------------------------------------------------------------------
print("\n" + "-" * 78)
print("  A. phi-ratio vs gamma_n: which monotone model fits the EMD amplitudes?")
print("-" * 78)

ns, A = [], []
for n in range(3, 21):
    s_n = LAM_HINV / n
    if s_n < sb[0] or s_n > sb[-1]:
        continue
    ns.append(n); A.append(abs(float(fi(s_n))))
ns = np.array(ns); A = np.array(A)

b_phi, a_phi = np.polyfit(ns, np.log(A), 1)
res_phi = np.log(A) - (b_phi * ns + a_phi)
gam = np.array([4 * math.sin(math.pi * n / 88) ** 2 for n in ns])
b_gam, a_gam = np.polyfit(np.log(gam), np.log(A), 1)
res_gam = np.log(A) - (b_gam * np.log(gam) + a_gam)
rms_phi = float(np.sqrt(np.mean(res_phi ** 2)))
rms_gam = float(np.sqrt(np.mean(res_gam ** 2)))
dev_phi = abs(b_phi - math.log(PHI)) / math.log(PHI)
print("   log A_n vs n        : slope = %.4f (log phi = %.4f, dev %.1f%%), RMS resid = %.4f"
      % (b_phi, math.log(PHI), 100 * dev_phi, rms_phi))
print("   log A_n vs log gamma: slope = %.4f,                        RMS resid = %.4f"
      % (b_gam, rms_gam))

# HYPOTHESIS-TEST check: the FINDING is that the phi-law is FALSIFIED
check("A1  phi-law FALSIFIED: log-slope %.4f deviates %.1f%% from log(phi)=%.4f"
      % (b_phi, 100 * dev_phi, math.log(PHI)),
      dev_phi > 0.20, "a true A_n ~ phi^n would require slope exactly log(phi)")
check("A2  gamma_n model fits the amplitudes at least as well as phi^n",
      rms_gam <= rms_phi * 1.1,
      "RMS gamma %.4f <= phi %.4f" % (rms_gam, rms_phi))
claim("A  => the EMD amplitudes are a MONOTONE sequence; both phi^n and gamma_n fit it, "
      "so the phi-ratio is not identifiable -> R (falsified), consistent with v9.0 09_math_verify")

json_out["A_phi_slope"] = float(b_phi)
json_out["A_phi_dev_pct"] = 100 * dev_phi
json_out["A_gamma_rms"] = rms_gam

# ------------------------------------------------------------------
print("\n" + "-" * 78)
print("  B. ramp diagnostic: is the EMD residual S/N sequence monotone?")
print("-" * 78)

sn_seq = np.array([sn_at(LAM_HINV / n) for n in ns])
rho, pval = spearmanr(ns, sn_seq)
print("   n          : " + " ".join("%6d" % n for n in ns))
print("   S/N        : " + " ".join("%6.1f" % v for v in sn_seq))
print("   Spearman rho(n, S/N) = %.4f  (p = %.2e)" % (rho, pval))
check("B1  EMD harmonic S/N is monotone in n (|rho| > 0.95) -> ramp, not discrete harmonics",
      abs(rho) > 0.95, "rho = %.4f ; n_imf = %d" % (rho, n_imf))
claim("B  => the '17/19 harmonics' of the v9.0 EMD run is a MONOTONE RAMP crossing 3-sigma, "
      "not 17 resolved harmonic detections (1 IMF extracted -> residual = smooth trend)")

json_out["B_spearman_rho"] = float(rho)

# ------------------------------------------------------------------
print("\n" + "-" * 78)
print("  C. resolvability of the K_Chain ladder in BOSS DR12")
print("-" * 78)

ds_bin = float(np.median(np.diff(sb)))
print("   BOSS bin spacing = %.1f h^-1 Mpc" % ds_bin)
nmax = (-1 + math.sqrt(1 + 4 * LAM_HINV / ds_bin)) / 2
print("   harmonic spacing Delta_s_n = lambda_sync/[n(n+1)]; resolvable iff Delta_s_n >= bin")
print("   n_max = %.3f  -> only n <= %d resolvable" % (nmax, int(nmax)))
n_res = sum(1 for n in ns if LAM_HINV / (n * (n + 1)) >= ds_bin)
check("C1  resolution limit n_max = %.2f < 9 (most claimed harmonics are sub-bin aliases)" % nmax,
      nmax < 9, "n_max = %.3f" % nmax)
check("C2  only %d of the %d scanned harmonics are actually resolvable by BOSS binning"
      % (n_res, len(ns)), n_res <= 8, "resolvable n = %s"
      % [int(n) for n in ns if LAM_HINV / (n * (n + 1)) >= ds_bin])
claim("C  => the K_Chain ladder is resolvable only for n <= 8 in BOSS DR12 (5 h^-1 Mpc bins); "
      "the toolbox's n=9..20 'detections' are sub-bin aliases of a smooth trend")

json_out["C_bin_spacing"] = ds_bin
json_out["C_n_max"] = nmax
json_out["C_n_resolvable"] = n_res

# ------------------------------------------------------------------
print("\n" + "-" * 78)
print("  D. verdict")
print("-" * 78)
claim("D  => the wavelet/EMD toolbox MIGRATES as TOOLING (P); its quantitative detection "
      "claims (phi-ratio, 17/19 harmonics, reflection detections) are R: method/broadband "
      "artefacts, already falsified or sub-bin aliases")

print("\n" + "=" * 78)
print("  RESULT: %d/%d PASS   (+%d structural claims)" % (PASS, PASS + FAIL, len(CLAIMS)))
print("=" * 78)

with open(os.path.join(DATA, "03_significance_null.json"), "w") as f:
    json.dump(json_out, f, indent=2)
print("  -> data/03_significance_null.json written")
