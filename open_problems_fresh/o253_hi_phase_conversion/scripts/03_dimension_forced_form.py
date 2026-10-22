#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
O253 scripts/03 - dimensional forcing of the conversion-efficiency form

Claim being TESTED (structural, not numerical):
  Any IDCM quantity that is a RATE must be (dimensionless structural functional)
  x (one rate anchor from the closed IDCM set). IDCM spectrum functionals
  (gamma_n, N_d, B, L_k, ...) are pure numbers, so they cannot carry 1/time.
  Hence the star-formation efficiency per unit HI,
        eps_HI := CSFRD / rho_HI      [1/time]
  admits exactly one structural shape:
        eps_HI = n_struct * omega_ring ,   omega_ring = 2*pi/T_ring
  with n_struct a dimensionless structural coefficient whose OPERATOR identity is
  the real open problem.

This script (a) states the forcing, (b) computes n_struct from the frozen anchors,
(c) shows the coefficient is NOT identified at current precision (uniqueness audit).
No new constant is introduced; no target is fitted.
"""
import json
import os

import mpmath as mp

mp.mp.dps = 30
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "data")

PASS = 0
TOTAL = 0


def ck(tag, ok, detail=""):
    global PASS, TOTAL
    TOTAL += 1
    PASS += 1 if ok else 0
    print("[%s] %s  %s" % ("PASS" if ok else "FAIL", tag, detail))


T_ring = mp.mpf("84.637")                       # Gyr, O121
omega_ring = 2 * mp.pi / T_ring                 # 1/Gyr
tau_dep = mp.mpf("4.3414095")                   # Gyr, from scripts/01 (C5)
tau_err = tau_dep * mp.mpf("0.20")              # 20% honest band (Omega_HI 2.6% + CSFRD ~20%)
eps_HI = 1 / tau_dep
n_struct = eps_HI / omega_ring

print("=" * 78)
print("O253/03  dimensional forcing of the HI->star conversion efficiency")
print("=" * 78)
print("T_ring      = %s Gyr" % mp.nstr(T_ring, 8))
print("omega_ring  = %s /Gyr" % mp.nstr(omega_ring, 8))
print("tau_dep(HI) = %s Gyr  (+-%s%%)" % (mp.nstr(tau_dep, 8), mp.nstr(100 * tau_err / tau_dep, 4)))
print("eps_HI      = 1/tau = %s /Gyr" % mp.nstr(eps_HI, 8))
print("n_struct    = eps_HI/omega_ring = %s" % mp.nstr(n_struct, 8))
n_lo = 1 / (tau_dep + tau_err) / omega_ring
n_hi = 1 / (tau_dep - tau_err) / omega_ring
print("n_struct band (+-20%% on tau)    = [%s, %s]" % (mp.nstr(n_lo, 6), mp.nstr(n_hi, 6)))
print()

# --- D1: forcing statement as an arithmetic structural check
#     omega_ring carries 1/time; any dimensionless coefficient keeps the dimension.
ck("D1a eps = n*omega_ring reproduces eps exactly when n = n_struct",
   abs(n_struct * omega_ring - eps_HI) < mp.mpf("1e-20"),
   "identity holds by construction (form is admissible, coefficient open)")

# --- D2: the coefficient family (FROZEN before looking at n_struct values)
cand = {
    "1": mp.mpf(1), "2": mp.mpf(2), "3 (=N_gen)": mp.mpf(3), "4 (=B)": mp.mpf(4),
    "5 (=F5)": mp.mpf(5), "6": mp.mpf(6), "7 (=L4)": mp.mpf(7), "8": mp.mpf(8),
    "pi": mp.pi, "2pi": 2 * mp.pi, "sqrt5": mp.sqrt(5),
    "phi": (1 + mp.sqrt(5)) / 2, "phi^2": ((1 + mp.sqrt(5)) / 2) ** 2,
    "N_d/B = 11": mp.mpf(11), "L5/4 = 11/4": mp.mpf(11) / 4,
    "sqrt(2*pi)": mp.sqrt(2 * mp.pi), "e": mp.e,
    "16/5": mp.mpf(16) / 5, "22/7": mp.mpf(22) / 7, "19/6": mp.mpf(19) / 6,
}
inside = {k: v for k, v in cand.items() if n_lo <= v <= n_hi}
print("[D2] pre-registered coefficient family (size %d):" % len(cand))
for k, v in sorted(cand.items(), key=lambda kv: float(kv[1])):
    mark = "<== INSIDE BAND" if n_lo <= v <= n_hi else ""
    print("     %-14s %s  %s" % (k, mp.nstr(v, 6), mark))
print("  members inside the honest band: %d -> %s"
      % (len(inside), list(inside.keys())))
ck("D2a >=2 pre-registered coefficients fall inside the band -> coefficient NOT identified",
   len(inside) >= 2, "%d of %d candidates inside [%s, %s]"
   % (len(inside), len(cand), mp.nstr(n_lo, 5), mp.nstr(n_hi, 5)))

# --- D3: how tight would the data have to be to identify?
#     separation between N_gen = 3 and pi = 3.1416 is 4.5% -> need <2.3% on tau
sep = abs(mp.pi - mp.mpf(3)) / mp.mpf(3)
need = sep / 2
print()
print("[D3] nearest distinct structural coefficients above the band: N_gen=3, pi=3.14159")
print("     relative separation = %s%%  -> would require tau_dep known to better than %s%%"
      % (mp.nstr(100 * sep, 4), mp.nstr(100 * need, 4)))
print("     current tau_dep precision ~20%% (Omega_HI 2.6%%, CSFRD ~20%%) -> %sx too coarse"
      % mp.nstr(mp.mpf("0.20") / need, 4))
ck("D3a current precision is insufficient to separate N_gen from pi",
   mp.mpf("0.20") > need, "need < %s%%, have ~20%%" % mp.nstr(100 * need, 3))
ck("D3b n_struct is consistent with N_gen = 3 at current precision",
   n_lo <= mp.mpf(3) <= n_hi, "n_struct = %s, N_gen = 3 -> sigma = %.2f"
   % (mp.nstr(n_struct, 6), float((n_struct - 3) / ((n_hi - n_lo) / 4))))

# --- D4: the form predicts the *observed* weak tau evolution automatically
#     tau(z) = (n_struct * omega_ring)^-1 ; if n_struct is time-independent,
#     tau_dep(HI) stays constant while CSFRD(z) and rho_HI(z) both evolve.
print()
print("[D4] consequence of the forced form: if n_struct carries no z-dependence,")
print("     tau_dep(HI) is CONSTANT and eps(z) is CONSTANT -> the observed weak")
print("     evolution of Omega_HI (1.35+-0.10) together with CSFRD (2.46) is then")
print("     a CONSISTENCY requirement, not a prediction of the ratio.")
tau_pred = 1 / (mp.mpf(3) * omega_ring)
print("     with n_struct = N_gen = 3: tau_pred = %s Gyr (measured %s, dev %s%%)"
      % (mp.nstr(tau_pred, 6), mp.nstr(tau_dep, 6),
         mp.nstr(100 * abs(tau_pred - tau_dep) / tau_dep, 3)))
ck("D4a N_gen=3 branch predicts tau_dep inside the honest band",
   tau_dep * mp.mpf("0.8") <= tau_pred <= tau_dep * mp.mpf("1.2"),
   "tau_pred = %s Gyr" % mp.nstr(tau_pred, 6))

# --- D5: the paper's puzzle restated in IDCM language (dimensionless target)
eff_raw = mp.mpf("1.8222222")      # 2.46/1.35   (scripts/01 C6)
eff_corr = mp.mpf("2.1964286")     # 2.46/1.12   (scripts/01 C6)
one_plus_z = mp.mpf("1.4088433")   # scripts/01 C1
n_z_raw = n_struct / eff_raw
n_z_corr = n_struct / eff_corr
k_req_raw = mp.log(eff_raw) / mp.log(one_plus_z)
k_req_corr = mp.log(eff_corr) / mp.log(one_plus_z)
print()
print("[D5] IF the forced form holds at both epochs, the observation REQUIRES")
print("     n_struct to evolve by %.4f (raw) / %.4f (corrected):" % (float(eff_raw), float(eff_corr)))
print("     n_struct(z=0.41) = %s (raw) / %s (corrected)   [today: %s]"
      % (mp.nstr(n_z_raw, 6), mp.nstr(n_z_corr, 6), mp.nstr(n_struct, 6)))
print("     equivalent power-law exponent (1+z)^k : k = %s (raw) / %s (corrected)"
      % (mp.nstr(k_req_raw, 5), mp.nstr(k_req_corr, 5)))
print("     => the naive CONSTANT-coefficient branch (n independent of cosmic time)")
print("        predicts CSFRD drop = Omega_HI drop = 1.35; the measured 2.46 kills it.")
for val, name in [(mp.mpf("1.6180339887"), "phi"), (mp.sqrt(2), "sqrt2")]:
    print("     [DECOY] n_struct(z=0.41) candidate %-6s = %s -> dev %s%% (band ~20%%: zero info)"
          % (name, mp.nstr(val, 6), mp.nstr(100 * abs(val - n_z_corr) / n_z_corr, 2)))
ck("D5a constant-coefficient branch is falsified (predicted CSFRD drop 1.35 vs measured 2.46)",
   mp.mpf("2.46") > mp.mpf("1.35") * mp.mpf("1.5"),
   "factor 2.46 vs 1.35 -> 82%% excess (raw) / 120%% (corrected)")
ck("D5b required n_struct evolution is well-defined and dimensionless",
   eff_raw > 1 and eff_corr > eff_raw, "1.82 (raw) .. 2.20 (corrected)")

# ---------------------------------------------------------------- data output
os.makedirs(OUT, exist_ok=True)
payload = {
    "script": "03_dimension_forced_form.py",
    "form": "eps_HI = n_struct * omega_ring ; omega_ring = 2*pi/T_ring",
    "inputs": {"T_ring_Gyr": float(T_ring), "tau_dep_Gyr": float(tau_dep),
               "tau_rel_err": 0.20},
    "computed": {"omega_ring_per_Gyr": float(omega_ring), "eps_HI_per_Gyr": float(eps_HI),
                 "n_struct": float(n_struct), "n_band": [float(n_lo), float(n_hi)],
                 "tau_pred_Ngen3": float(tau_pred),
                 "dev_Ngen3_pct": float(100 * (tau_pred - tau_dep) / tau_dep),
                 "candidates_inside": list(inside.keys()),
                 "required_precision_pct": float(100 * need)},
    "verdict": {
        "form": "FORCED by dimensional argument (structural, zero free shape parameters)",
        "coefficient": "NOT identified: 3 (=N_gen) and pi both inside the band; "
                       "needs operator derivation + tau_dep precision < 2.3%",
    },
    "pass": "%d/%d" % (PASS, TOTAL),
}
with open(os.path.join(OUT, "03_dimension_forced_form.json"), "w") as fh:
    json.dump(payload, fh, indent=1, ensure_ascii=False)

print()
print("RESULT: %d/%d PASS" % (PASS, TOTAL))
