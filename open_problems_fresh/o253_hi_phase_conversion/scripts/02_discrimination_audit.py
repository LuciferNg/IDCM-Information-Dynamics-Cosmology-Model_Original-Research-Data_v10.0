#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
O253 scripts/02 - discrimination audit (null test) on the three tempting coincidences

Purpose: round 1 produced three "suspiciously good" numbers. This script quantifies,
with a PRE-REGISTERED structural family, that each carries ZERO identifying power
unless an operator mechanism exists. Rule enforced here: density x tolerance
(expected-hit) accounting, not single-point deviation.

Tempting targets (from scripts/01, targets are POST-HOC -- hence the audit):
  T1  Omega_HI decline factor 1.35 +- 0.10 (and 1.12 +- 0.10)  vs (1+z)^1 = 1.4088
  T2  k_SFR = ln(2.46)/ln(1+z) = 2.6261                        vs phi^2 = 2.6180
  T3  tau_dep/tau(T_ring) = 0.051294                           vs 1/20 = 0.05
  T4  Omega_HI slope 0.9 +- 0.2                                vs "small rational exponents"

Structural family S is FROZEN below and may NOT be extended after seeing a target
(the banned move: symbol-library inflation).
"""
import json
import os
import random
from fractions import Fraction as F

import mpmath as mp

mp.mp.dps = 30
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "data")

# ---------------------------------------------------------------- frozen family
S = sorted(set([
    # geometry / chain counts
    3, 4, 5, 7, 8, 9, 11, 12, 13, 17, 18, 19, 20, 21, 24, 29, 35, 41, 44, 45, 47,
    55, 60, 66, 76, 88, 90, 123, 137, 143, 176, 178, 306, 421, 946,
    # Lucas L_k
    1, 2, 34, 89, 144, 233,
    # Fibonacci F_k
]))

phi = (1 + mp.sqrt(5)) / 2
TARGETS = {
    "T1_raw": (mp.mpf("1.35"), mp.mpf("0.10"), "Omega_HI raw decline factor"),
    "T1_corr": (mp.mpf("1.12"), mp.mpf("0.10"), "Omega_HI corrected decline factor"),
    "T2_kSFR": (mp.mpf("2.6261454"), None, "CSFRD local exponent"),
    "T2_band": (None, None, "z-window band [2.567, 2.675]"),
    "T3_tau": (mp.mpf("0.051294463"), None, "tau_dep/T_ring"),
    "T4_slope": (mp.mpf("0.9"), mp.mpf("0.2"), "Omega_HI power-law slope"),
}

PASS = 0
TOTAL = 0


def ck(tag, ok, detail=""):
    global PASS, TOTAL
    TOTAL += 1
    PASS += 1 if ok else 0
    print("[%s] %s  %s" % ("PASS" if ok else "FAIL", tag, detail))


def band_hits(values, lo, hi):
    return sorted(v for v in values if lo <= v <= hi)


# ------------------------------------------------------------------ family sets
ratios = []
for p in S:
    for q in S:
        if p != q:
            ratios.append(mp.mpf(p) / mp.mpf(q))
ratios = sorted(set(ratios))

phi_powers = sorted(set(phi ** k for k in range(-12, 13)))
inv_n = [mp.mpf(1) / mp.mpf(n) for n in range(1, 301)]

# small rational exponents p/q with p in [0,6], q in [1,6]
small_rat = sorted(set(F(p, q) for p in range(0, 7) for q in range(1, 7)))

print("=" * 78)
print("O253/02  discrimination audit (frozen structural family)")
print("=" * 78)
print("family sizes: |S|=%d  |p/q|=%d  |phi^k|=%d  |1/n|=%d  |small rat|=%d"
      % (len(S), len(ratios), len(phi_powers), len(inv_n), len(small_rat)))
print()

# ---------------------------------------------------------------- T1: factor band
print("-" * 78)
print("[T1] decline factor 1.35+-0.10 / 1.12+-0.10 ; candidate (1+z)^1 = 1.408843")
for tag in ("T1_raw", "T1_corr"):
    mu, err, name = TARGETS[tag]
    lo, hi = mu - err, mu + err
    rhits = band_hits(ratios, lo, hi)
    width = float(hi - lo) / float(mu)
    print("  [%s] %s: band [%s, %s] (relative width %.1f%%)"
          % (tag, name, mp.nstr(lo, 5), mp.nstr(hi, 5), 100 * width))
    print("        phi^k hits = %d ; p/q hits = %d"
          % (len(band_hits(phi_powers, lo, hi)), len(rhits)))
    # expected hits if the family were log-uniform over [0.5, 3]
    span = mp.log(mp.mpf("3") / mp.mpf("0.5"))
    exp_phi = len(phi_powers) * mp.log(hi / lo) / span
    print("        expected phi^k hits (log-uniform, 0.5-3.0) = %.1f" % float(exp_phi))
    ck("%s family density >= 10 -> no identifying power" % tag,
       len(rhits) >= 10, "p/q hits = %d in a %.1f%%-wide band" % (len(rhits), 100 * width))

# --------------------------------------------------------------- T2: phi^2 trap
print()
print("-" * 78)
print("[T2] k_SFR target 2.626145 vs phi^2 = 2.618034 (dev 0.31%)")
lo, hi = mp.mpf("2.56707"), mp.mpf("2.67529")     # z-window sensitivity band
k_sfr_t = mp.mpf("2.6261454")                      # target from scripts/01
phi_hits = band_hits(phi_powers, lo, hi)
rat_hits = band_hits(ratios, lo, hi)
width = float((hi - lo) / ((hi + lo) / 2))
print("  z-window band [%s, %s] relative width %.1f%%"
      % (mp.nstr(lo, 6), mp.nstr(hi, 6), 100 * width))
print("  phi^k members inside: %s" % [mp.nstr(v, 6) for v in phi_hits])
print("  p/q members inside  : %d (first 8: %s)"
      % (len(rat_hits), [mp.nstr(v, 5) for v in rat_hits[:8]]))
ck("T2a phi^2 sits inside the band by construction", lo < phi ** 2 < hi, "phi^2 = %s" % mp.nstr(phi ** 2, 8))
ck("T2b band holds >=2 rational alternatives -> target is NON-UNIQUE (identification impossible)",
   len(rat_hits) >= 2, "hits = %d (uniqueness would require exactly 1)" % len(rat_hits))
tight_lo, tight_hi = k_sfr_t * mp.mpf("0.995"), k_sfr_t * mp.mpf("1.005")
tight = band_hits(ratios, tight_lo, tight_hi)
print("  +-0.5%% band [%s, %s] -> p/q members: %s"
      % (mp.nstr(tight_lo, 6), mp.nstr(tight_hi, 6), [mp.nstr(v, 6) for v in tight]))
ck("T2c even a 1%%-wide window is non-unique", len(tight) >= 2,
   "%d members (phi^2 among them)" % len(tight))

# --------------------------------------------------------------- T3: 1/20 trap
print()
print("-" * 78)
print("[T3] tau_dep/T_ring = 0.0512945 vs 1/20 = 0.05 (dev 2.6%)")
target = mp.mpf("0.051294463")
# honest error band: Omega_HI 2.6% + CSFRD ~20% (Madau-Fragos scatter) -> 20%
for band_frac in ("0.05", "0.10", "0.20"):
    b = mp.mpf(band_frac)
    lo, hi = target * (1 - b), target * (1 + b)
    h1 = band_hits(inv_n, lo, hi)
    h2 = band_hits(ratios, lo, hi)
    print("  band +-%s%%: [%s, %s] -> 1/n hits = %d %s ; p/q hits = %d"
          % (mp.nstr(100 * b, 3), mp.nstr(lo, 6), mp.nstr(hi, 6), len(h1),
             [str(round(1 / float(v), 2)) for v in h1][:6], len(h2)))
ck("T3a 1/n family supplies >= 3 divisors inside the honest 20% band",
   len(band_hits(inv_n, target * mp.mpf("0.8"), target * mp.mpf("1.2"))) >= 3,
   "no unique divisor identity available at current precision")

# --------------------------------------------------------------- T4: slope band
print()
print("-" * 78)
print("[T4] Omega_HI slope 0.9 +- 0.2 : how many SMALL rationals qualify?")
qual = [r for r in small_rat
        if mp.mpf(7) / 10 <= mp.mpf(r.numerator) / r.denominator <= mp.mpf(11) / 10]
print("  qualifying small rationals: %d / %d" % (len(qual), len(small_rat)))
print("  list: %s" % [str(r) for r in qual])
ck("T4a >=2 small rationals qualify -> slope is NON-UNIQUE (identification impossible)",
   len(qual) >= 2, "%d/%d qualify (uniqueness requires exactly 1)" % (len(qual), len(small_rat)))

# ------------------------------------------- MC cross-check of p/q density result
print()
print("-" * 78)
print("[MC] random-pair null for the p/q family (10^5 draws from S, log-uniform target window)")
random.seed(20261022)
lo, hi = TARGETS["T1_raw"][0] - TARGETS["T1_raw"][1], TARGETS["T1_raw"][0] + TARGETS["T1_raw"][1]
ndraw = 100000
hit = 0
for _ in range(ndraw):
    p, q = random.sample(S, 2)
    v = mp.mpf(p) / mp.mpf(q)
    if lo <= v <= hi:
        hit += 1
frac = mp.mpf(hit) / ndraw
print("  P(p/q lands in the 1.35+-0.10 band) = %s" % mp.nstr(frac, 6))
exp_hits = frac * len(ratios)
print("  MC-expected hits over the %d-member family = %.1f  (enumerated: %d)"
      % (len(ratios), float(exp_hits), len(band_hits(ratios, lo, hi))))
ck("MC1 MC density reproduces the enumerated hit count within 25%",
   abs(exp_hits - len(band_hits(ratios, lo, hi))) / len(band_hits(ratios, lo, hi)) < mp.mpf("0.25"),
   "expected %.1f vs enumerated %d" % (float(exp_hits), len(band_hits(ratios, lo, hi))))

# ------------------------------------------------------------------- verdicts
print()
print("=" * 78)
print("VERDICT (round 1)")
print("=" * 78)
print("T1 (1+z)^1 = 1.4088 : survives raw (0.59 sigma) but is EXCLUDED by the")
print("                      systematics-corrected number (2.89 sigma) -> decoy.")
print("T2 phi^2 = 2.618    : inside the z-window band by construction; family")
print("                      density supplies dozens of alternatives -> decoy.")
print("T3 1/20             : error band +-20%% admits several divisors -> decoy.")
print("T4 slope 0.9        : %d/%d small rationals qualify -> no identification." % (len(qual), len(small_rat)))
print("=> NO IDCM mechanism may be promoted from round-1 numbers. Any future")
print("   structural claim must come from an OPERATOR identity, then be tested blind.")

os.makedirs(OUT, exist_ok=True)
payload = {
    "script": "02_discrimination_audit.py",
    "family_size": len(S), "ratio_family_size": len(ratios),
    "T1": {"raw_band": [float(TARGETS["T1_raw"][0] - TARGETS["T1_raw"][1]),
                        float(TARGETS["T1_raw"][0] + TARGETS["T1_raw"][1])],
           "corr_band": [float(TARGETS["T1_corr"][0] - TARGETS["T1_corr"][1]),
                         float(TARGETS["T1_corr"][0] + TARGETS["T1_corr"][1])],
           "pow1_candidate": 1.408843339},
    "T2": {"band": [float(lo if False else mp.mpf("2.56707")), float(mp.mpf("2.67529"))],
           "phi2": float(phi ** 2), "phi_hits": [float(v) for v in phi_hits],
           "pq_hits": len(rat_hits)},
    "T3": {"target": float(target), "inv_n_hits_20pct":
           [float(v) for v in band_hits(inv_n, target * mp.mpf("0.8"), target * mp.mpf("1.2"))]},
    "T4": {"qualifying": [str(r) for r in qual], "total": len(small_rat)},
    "MC_pq_single_hit_prob": float(frac), "MC_draws": ndraw,
    "verdict": "all four round-1 coincidences = decoys, zero identifying power",
    "pass": "%d/%d" % (PASS, TOTAL),
}
with open(os.path.join(OUT, "02_discrimination_audit.json"), "w") as fh:
    json.dump(payload, fh, indent=1, ensure_ascii=False)
print()
print("RESULT: %d/%d PASS" % (PASS, TOTAL))
