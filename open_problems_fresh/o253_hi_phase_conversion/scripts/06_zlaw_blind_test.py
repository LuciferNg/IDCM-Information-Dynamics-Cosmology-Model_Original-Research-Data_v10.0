#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
O253 scripts/06 — R3: can a closed IDCM z-dependence supply the required
                     n_struct evolution 1.822 (raw) / 2.196 (corrected)?

Candidate z-laws are PRE-REGISTERED (docs/02 §七 R3) and enumerated mechanically.
No candidate is added after seeing the residuals; each carries its provenance.
Targets: n_struct(z=0.41)/n_struct(0) = 1.8222 (raw) / 2.1964 (corr).
Cross-check anchor: CSFRD factor 2.46, tolerance +-10% (ASSUMED, not quoted by the paper).
"""
import json
import os

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


# ------------------------------------------------------------ cosmology (own)
H0 = mp.mpf("67.4071")           # km/s/Mpc  (O127/O168 closed value)
Om = mp.mpf(19) / 60
OL = mp.mpf(41) / 60
T_ring = mp.mpf("84.637")        # Gyr (O121)
HUBBLE_GYR = mp.mpf("977.7922214") / H0   # 1/H0 in Gyr
LOOKBACK = mp.mpf("4.5")         # Gyr, paper's z-window

HI_RAW = mp.mpf("1.35")          # Omega_HI drop, paper abstract
HI_CORR = mp.mpf("1.12")         # with the paper's systematics correction
CSFRD = mp.mpf("2.46")
TOL = mp.mpf("0.10")


def lookback_frac(z):
    """t_lookback(z)/t0 for flat LCDM (unitless)."""
    f = lambda zz: 1 / ((1 + zz) * mp.sqrt(Om * (1 + zz) ** 3 + OL))
    return mp.quad(f, [0, z]) / mp.quad(f, [0, mp.inf])


T0_univ = HUBBLE_GYR * mp.quad(lambda zz: 1 / ((1 + zz) * mp.sqrt(Om * (1 + zz) ** 3 + OL)),
                               [0, mp.inf])


def z_of_lookback(dt):
    return mp.findroot(lambda zz: lookback_frac(zz) * T0_univ - dt, 0.4)


z = z_of_lookback(LOOKBACK)
one_plus_z = 1 + z
ell = mp.log(one_plus_z) / mp.log(4)
Ez = mp.sqrt(Om * one_plus_z ** 3 + OL)
t_now_rel = T_ring  # placeholder, replaced below by real age ratio
t_frac_now = T0_univ / T_ring                       # t0/T_ring
t_frac_then = (T0_univ - LOOKBACK) / T_ring

print("=" * 78)
print("O253/06  R3: closed z-laws vs required n_struct evolution")
print("=" * 78)
print("z = %s ; 1+z = %s ; l = log4(1+z) = %s" % (mp.nstr(z, 10), mp.nstr(one_plus_z, 10), mp.nstr(ell, 10)))
print("E(z) = H(z)/H0 = %s ; t0/T_ring = %s ; t(z)/T_ring = %s"
      % (mp.nstr(Ez, 10), mp.nstr(t_frac_now, 10), mp.nstr(t_frac_then, 10)))
ck("H1 z(4.5 Gyr) = 0.4088433 (reproduces scripts/01 C1)",
   abs(z - mp.mpf("0.4088433")) < mp.mpf("1e-6"), "z = %s" % mp.nstr(z, 10))

# --------------------------------------------------- pre-registered candidates
CAND = [
    ("Z1  4^-l = (1+z)^-1", 4 ** (-ell), "O76 / O173-P1 (the only DERIVED z-law)"),
    ("Z2  4^+l = (1+z)^+1", 4 ** ell, "P1 inverted (no provenance, control)"),
    ("Z3  (t/T_ring)^-1", t_frac_now / t_frac_then, "O121 ring phase (no provenance)"),
    ("Z4  (t/T_ring)^+1", t_frac_then / t_frac_now, "O121 ring phase (no provenance)"),
    ("Z5  E(z)", Ez, "O215 background expansion"),
    ("Z6  E(z)^2", Ez ** 2, "O215 background expansion"),
    ("Z7  1+l", 1 + ell, "level-count (no provenance)"),
    ("Z8  1/(1+l)", 1 / (1 + ell), "level-count (no provenance)"),
    ("Z9  4^(l/2) = (1+z)^(1/2)", 4 ** (ell / 2), "half-level (no provenance)"),
    ("Z10 1 (spectral-only)", mp.mpf(1), "constant coefficient (killed in R1 D5)"),
]

REQ_RAW = CSFRD / HI_RAW
REQ_CORR = CSFRD / HI_CORR
band_lo = CSFRD * (1 - TOL)
band_hi = CSFRD * (1 + TOL)
print()
print("required n_struct evolution: raw %s / corr %s" % (mp.nstr(REQ_RAW, 8), mp.nstr(REQ_CORR, 8)))
print("CSFRD anchor %s ; assumed +-%d%% band [%s, %s]"
      % (mp.nstr(CSFRD, 6), int(TOL * 100), mp.nstr(band_lo, 6), mp.nstr(band_hi, 6)))
print()
print(" cand | z-law ratio | SFRD(raw) | dev(raw) | SFRD(corr) | dev(corr) | band? | provenance")
in_band, near = [], []
for name, r, prov in CAND:
    sf_raw = HI_RAW * r
    sf_corr = HI_CORR * r
    dev_raw = 100 * (sf_raw - CSFRD) / CSFRD
    dev_corr = 100 * (sf_corr - CSFRD) / CSFRD
    ok = band_lo <= sf_raw <= band_hi
    if ok:
        in_band.append(name)
    if abs(dev_raw) <= 25:
        near.append(name)
    print(" %-26s | %-10s | %-9s | %+7.1f%% | %-10s | %+7.1f%% | %-5s | %s"
          % (name, mp.nstr(r, 6), mp.nstr(sf_raw, 5), float(dev_raw),
             mp.nstr(sf_corr, 5), float(dev_corr), "YES" if ok else "no", prov))

print()
print("[BAND] strict +-10%%: %d candidate(s) inside -> %s"
      % (len(in_band), ", ".join(in_band) if in_band else "NONE"))
print("[NEAR] +-25%%:      %d candidate(s) -> %s"
      % (len(near), ", ".join(near) if near else "NONE"))

ck("H2 strict band: zero candidates reproduce the CSFRD drop",
   len(in_band) == 0, "%d inside" % len(in_band))
ck("H3 loose band: >=2 candidates survive => non-unique if tolerance relaxed",
   len(near) >= 2, "%d candidates within 25%%" % len(near))
ck("H4 the only DERIVED z-law (Z1, P1) points the WRONG way (SFRD would fall less than HI)",
   HI_RAW * (4 ** (-ell)) < HI_RAW, "Z1 SFRD factor %s < HI factor %s"
   % (mp.nstr(HI_RAW * 4 ** (-ell), 5), mp.nstr(HI_RAW, 5)))

# ------------------------------------------- required exponent & its provenance
k_raw = mp.log(REQ_RAW) / mp.log(one_plus_z)
k_corr = mp.log(REQ_CORR) / mp.log(one_plus_z)
print()
print("[EXP] required power-law exponent k = %s (raw) / %s (corr)" % (mp.nstr(k_raw, 6), mp.nstr(k_corr, 6)))
print("      note: ANY k can be written as a ratio of two counts from a ~40-number pool")
print("      (e.g. L4/B = 7/4 = 1.750 vs k_raw = %s) -> density, not identity" % mp.nstr(k_raw, 5))
half_ints = [mp.mpf(m) / 2 for m in range(-6, 7)]
d_half = min(abs(k_raw - h) for h in half_ints)
print("      nearest half-integer exponent |delta k| = %s -> %s"
      % (mp.nstr(d_half, 5),
         "NOT a closed 4^(m*l) exponent (m integer) nor a sqrt-level (m/2)" if d_half > mp.mpf('0.05')
         else "IS a half-integer exponent"))
ck("H5 required k is not a closed 4^(k*l) exponent (k half-integer)",
   d_half > mp.mpf("0.05"),
   "k_raw = %s ; nearest half-integer delta = %s" % (mp.nstr(k_raw, 6), mp.nstr(d_half, 5)))
ck("H6 count-ratio 'hit' L4/B = 7/4 = %s is a density decoy (0.03%% from k_raw), not an identity"
   % mp.nstr(mp.mpf(7) / 4, 5),
   abs(mp.mpf(7) / 4 - k_raw) < mp.mpf("0.01"),
   "|L4/B - k_raw| = %s ; any k is writable as a ratio of two counts"
   % mp.nstr(abs(mp.mpf(7) / 4 - k_raw), 4))

print()
print("VERDICT: no closed IDCM z-dependence supplies 1.822/2.196.")
print("         strict +-10%% band -> 0/10 candidates; loose +-25%% -> %d (non-unique)." % len(near))

payload = {
    "script": "06_zlaw_blind_test.py",
    "z": float(z), "one_plus_z": float(one_plus_z), "ell": float(ell), "Ez": float(Ez),
    "t_frac_now": float(t_frac_now), "t_frac_then": float(t_frac_then),
    "required_raw": float(REQ_RAW), "required_corr": float(REQ_CORR),
    "candidates": [{"name": n, "ratio": float(r), "sfrd_raw": float(HI_RAW * r),
                    "dev_raw_pct": float(100 * (HI_RAW * r - CSFRD) / CSFRD),
                    "in_band": bool(band_lo <= HI_RAW * r <= band_hi), "provenance": p}
                   for n, r, p in CAND],
    "in_band": in_band, "near_25": near,
    "k_raw": float(k_raw), "k_corr": float(k_corr),
    "assumption": "CSFRD +-10% band is an ASSUMED tolerance (paper quotes the factor without error)",
    "verdict": "no closed z-law matches; strict 0/10, loose %d/10 non-unique" % len(near),
    "pass": "%d/%d" % (PASS, TOTAL),
}
with open(os.path.join(DATA, "06_zlaw_blind_test.json"), "w") as fh:
    json.dump(payload, fh, indent=1, ensure_ascii=False)
print()
print("RESULT: %d/%d PASS" % (PASS, TOTAL))
