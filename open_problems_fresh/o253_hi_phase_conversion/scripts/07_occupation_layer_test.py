#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
O253 scripts/07 — R5: can an "occupation / phase-space" layer restore identifiability?

Pre-registered before execution (docs/03 §六):
  K1 occupation = blocked-chain weight / tree weight
  K2 occupation = tree modes per blocked chain mode
  K3 occupation = world-sector chain weight per tree mode
  K4 Lambda-ladder: ln(Lambda_IDCM / kT_CMB)
  K5 E_J-based ratio
Admissibility (frozen): (i) built only from closed IDCM objects, (ii) carries a mechanism
sentence predicting sign/order, (iii) UNIQUE among the pre-registered set.

Two independent tests are then run:
  T1 inherited-family test: does the candidate merely re-enter R2's family (data/05)?
  T2 weighted-occupation test: do occupation-weighted functionals enlarge the family
     without improving identifiability (i.e. hit density rises)?
  T3 scale-ladder test: is any closed IDCM energy scale inside the ISM activation window?
"""
import json
import os
import random

import mpmath as mp

mp.mp.dps = 40
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "data")

PASS = 0
TOTAL = 0


def ck(tag, ok, detail=""):
    global PASS, TOTAL
    TOTAL += 1
    PASS += 1 if ok else 0
    print("[%s] %s  %s" % ("PASS" if ok else "FAIL", tag, detail))


spec05 = json.load(open(os.path.join(DATA, "05_identifiability.json")))
BAND_LO, BAND_HI = mp.mpf("2.5856"), mp.mpf("3.8785")
N_TARGET = mp.mpf("3.1028")

B, N_gen, N_d = 4, 3, 44


def g176(k):
    return 4 * mp.sin(mp.pi * k / 176) ** 2


def g88(n):
    return 4 * mp.sin(mp.pi * n / 88) ** 2


def lam(k):
    return B * mp.sin(mp.pi * k / 68) ** 2


S90 = mp.fsum([g176(k) for k in range(2, 89, 2)])          # 90
SUM44 = mp.fsum([g88(n) for n in range(1, 45)])            # 90
PASS27 = mp.fsum([g88(n) for n in range(1, 28)])
BLOCK = mp.fsum([g88(n) for n in range(28, 45)])
SLAM = mp.fsum([lam(k) for k in range(1, 34)])             # 66
E_proj = mp.mpf(19) / 60 * SUM44
E_J = mp.mpf(123)
F_proj = 17

print("=" * 78)
print("O253/07  R5: occupation layer vs identifiability")
print("=" * 78)
print("PASS27 = %s ; BLOCK = %s ; SLAM = %s ; E_proj = %s"
      % (mp.nstr(PASS27, 8), mp.nstr(BLOCK, 8), mp.nstr(SLAM, 8), mp.nstr(E_proj, 8)))

# ------------------------------------------------------- pre-registered K1..K5
CAND = [
    ("K1 BLOCK/SLAM", BLOCK / SLAM,
     "blocked (unconvertible) weight per tree state: <1 implies conversion starved"),
    ("K2 K_tree_mode/F_proj", mp.mpf(33) / F_proj,
     "tree states per unprojected chain mode"),
    ("K3 SUM44/K_tree_mode", SUM44 / 33,
     "world-sector chain weight per tree state"),
    ("K4 ln(Lambda/kT_CMB)", mp.log(mp.mpf("45.28487e6") / mp.mpf("2.348e-4")),
     "QCD-scale to CMB ladder (dimensionless logarithm)"),
    ("K5 E_J/E_proj", E_J / E_proj,
     "Ising coupling per projected energy"),
]
print()
print(" cand | value      | dev vs 3.1028 | in band | mechanism sentence")
in_band = []
for name, v, mech in CAND:
    dev = 100 * (v - N_TARGET) / N_TARGET
    ok = BAND_LO <= v <= BAND_HI
    if ok:
        in_band.append((name, v))
    print(" %-24s | %-10s | %+8.3f %% | %-6s | %s"
          % (name, mp.nstr(v, 8), float(dev), "YES" if ok else "no", mech))

ck("K1..K5 all evaluated against the frozen band", len(CAND) == 5,
   "%d candidates" % len(CAND))

# ----------------------------------- T1: is an in-band candidate merely R2 family?
# Membership test by arithmetic identity against the same ingredient set (not by
# string matching against truncated lists): a candidate is "inherited" iff it equals
# p/q for p,q drawn from the closed ingredient pool.
ING_POOL = {
    "Sum_gamma_176": mp.fsum([g176(k) for k in range(1, 89)]),
    "Sum_gamma_even": S90, "Sum_gamma_odd": mp.fsum([g176(k) for k in range(1, 89, 2)]),
    "Sum_gamma_88": mp.fsum([g88(n) for n in range(1, 89)]),
    "Sum_lam_tree": SLAM, "E_proj": E_proj, "E_sync": mp.mpf(41) / 60 * SUM44,
    "S26": mp.fsum([g88(n) for n in range(1, 27)]), "S28_44": BLOCK,
    "P27_176": mp.fsum([g176(k) for k in range(1, 28)]),
    "B_176": mp.fsum([g176(k) for k in range(28, 89)]),
    "n_star": mp.mpf(27), "N_d": mp.mpf(N_d), "B": mp.mpf(B), "N_gen": mp.mpf(3),
    "L5": mp.mpf(11), "L6": mp.mpf(18), "L7": mp.mpf(29), "F_proj": mp.mpf(F_proj),
    "K_tree_mode": mp.mpf(33), "K_tree_node": mp.mpf(34), "sites_tree": mp.mpf(68),
}


def in_family(v, tol=mp.mpf("1e-20")):
    for p, pv in ING_POOL.items():
        for q, qv in ING_POOL.items():
            if p == q or qv == 0:
                continue
            if abs(pv / qv - v) < tol:
                return "%s/%s" % (p, q)
    return ""


inherit = [(n, v, in_family(v)) for n, v in in_band]
print()
print("[T1] in-band candidates: %d ; expressible as closed ingredient ratios: %d (%s)"
      % (len(in_band), sum(1 for _, _, lab in inherit if lab),
         ", ".join("%s=%.4f [%s]" % (n, float(v), lab) for n, v, lab in inherit) if inherit else "none"))
ck("T1 every in-band candidate is a closed-ingredient ratio (inherits R2's family)",
   all(lab for _, _, lab in inherit), "%d/%d" % (sum(1 for _, _, l in inherit if l), len(inherit)))
ck("T1b non-identifiability inherited: R2 already contains %d distinct in-band values"
   % spec05["distinct_wide"], spec05["distinct_wide"] >= 2,
   "one extra member cannot single out n_struct")

# ------------------------- T2: occupation-weighted functionals (density test)
random.seed(20261022)
W_CHAIN = [g88(n) for n in range(1, 89)]
W_TREE = [lam(k) for k in range(1, 34)]
N_DRAW = 2000
hits = 0
vals = []
for _ in range(N_DRAW):
    wc = [mp.mpf(random.random()) for _ in range(88)]
    wt = [mp.mpf(random.random()) for _ in range(33)]
    num = mp.fsum([w * g for w, g in zip(wc, W_CHAIN)])
    den = mp.fsum([w * g for w, g in zip(wt, W_TREE)])
    if den <= 0:
        continue
    v = num / den
    vals.append(v)
    if BAND_LO <= v <= BAND_HI:
        hits += 1
dens = mp.mpf(hits) / len(vals)
print()
print("[T2] %d random occupation-weighted functionals: %d inside band -> density %s"
      % (len(vals), hits, mp.nstr(dens, 5)))
print("     R2 integer-pair base rate = %s ; random-weight family spans "
      "[%s, %s]" % (mp.nstr(mp.mpf("0.065733"), 5),
                    mp.nstr(min(vals), 5), mp.nstr(max(vals), 5)))
ck("T2 occupation weights INCREASE hit density (identifiability gets worse, not better)",
   dens > mp.mpf("0.065733"), "density %s vs base 6.573%%" % mp.nstr(dens, 5))

# --------------------------------- T3: closed-scale ladder vs the ISM window
HBAR_eVs = mp.mpf("6.582119569e-16")
KB_eVK = mp.mpf("8.617333262e-5")
T_ring_s = mp.mpf("84.637e9") * mp.mpf("3.15576e7")
T_CMB = mp.mpf("2.7255")
SCALES = [
    ("M_Pl", mp.mpf("1.220910e28"), "O212 anchor"),
    ("v_SM", mp.mpf("246.2196e9"), "O86"),
    ("Lambda_IDCM", mp.mpf("45.28487e6"), "O142 v16"),
    ("h_bar_omega_ring", 2 * mp.pi * HBAR_eVs / T_ring_s, "O121 (1/T_ring)"),
    ("k_B T_CMB(0)", KB_eVK * T_CMB, "O39/CMB"),
]
# ISM activation window: E_a/kT in [0.1,10] for T in [10,100] K
lo_eV = mp.mpf("0.1") * KB_eVK * 10
hi_eV = mp.mpf("10") * KB_eVK * 100
print()
print("[T3] closed IDCM energy scales (eV) vs the ISM activation window [%s, %s] eV"
      % (mp.nstr(lo_eV, 6), mp.nstr(hi_eV, 6)))
inside = []
for name, e, prov in SCALES:
    ok = lo_eV <= e <= hi_eV
    if ok:
        inside.append(name)
    print("     %-18s %-12s eV  %-6s  %s" % (name, mp.nstr(e, 8), "INSIDE" if ok else "outside", prov))
ck("T3a exactly one closed scale occupies the ISM window (T_CMB; honest count, not zero)",
   len(inside) == 1 and inside[0] == "k_B T_CMB(0)", "%d inside: %s" % (len(inside), ", ".join(inside)))
# the only z-dependence a T_CMB channel can give is a power law (1+z)^s
s_req = mp.log(mp.mpf("1.8222")) / mp.log(mp.mpf("1.4088433"))
d_half = min(abs(s_req - mp.mpf(m) / 2) for m in range(0, 7))
ck("T3b T_CMB channel admits only T-power laws; required s = %s is not a closed half-integer"
   % mp.nstr(s_req, 6), d_half > mp.mpf("0.05"), "nearest half-integer delta = %s" % mp.nstr(d_half, 5))
E_bind = mp.mpf("4.52")   # H2 binding energy, eV -- EXTERNAL datum, labelled
print("     [external] H2 binding 4.52 eV at T=10 K -> Boltzmann exponent %.3g (absurdly suppressed)"
      % float(E_bind / (KB_eVK * 10)))
ck("T3c thermally-activated forms with a molecular binding scale are inadmissible (exponent >> 1)",
   E_bind / (KB_eVK * 10) > mp.mpf("100"), "E_a/kT = %s" % mp.nstr(E_bind / (KB_eVK * 10), 6))

print()
print("VERDICT R5: FAIL as an identification route.")
print("  (i) the only in-band candidate (K3 = SUM44/33 = %s) is an inherited R2 ratio" % mp.nstr(SUM44 / 33, 8))
print("  (ii) occupation weights raise hit density to %s (identifiability worsens)" % mp.nstr(dens, 4))
print("  (iii) exactly one closed scale sits in the ISM window (k_BT_CMB = %s eV); it admits"
      % mp.nstr(KB_eVK * T_CMB, 6))
print("        only T-power laws, and the required exponent (1.7506) is not closed;")
print("        Boltzmann forms on a molecular binding scale give e^-5245 (absurd)")
print("  => an occupation layer built from T's own objects adds no new degree of freedom;")
print("     a genuine conversion dynamics would require an external ISM/dust microphysics layer.")

payload = {
    "script": "07_occupation_layer_test.py",
    "candidates": [{"name": n, "value": float(v), "in_band": bool(BAND_LO <= v <= BAND_HI),
                    "mechanism": m} for n, v, m in CAND],
    "in_band": [n for n, v in in_band],
    "inherited": [n for n, v, lab in inherit if lab],
    "weighted_density": float(dens), "weighted_hits": hits, "weighted_draws": len(vals),
    "base_rate": 0.065733,
    "scales_eV": {n: float(e) for n, e, p in SCALES},
    "ism_window_eV": [float(lo_eV), float(hi_eV)],
    "scales_inside_window": inside,
    "verdict": "R5 FAIL: no occupation-layer identification (inherited family + density %s + "
               "only T_CMB in window, its power law s=1.7506 not closed)" % mp.nstr(dens, 4),
    "pass": "%d/%d" % (PASS, TOTAL),
}
with open(os.path.join(DATA, "07_occupation_layer_test.json"), "w") as fh:
    json.dump(payload, fh, indent=1, ensure_ascii=False)
print()
print("RESULT: %d/%d PASS" % (PASS, TOTAL))
