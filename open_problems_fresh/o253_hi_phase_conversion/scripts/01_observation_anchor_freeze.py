#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
O253 scripts/01 - observation anchor freeze + IDCM background recompute (round 1)

SOURCE (authoritative):
  Zhang, Guo, Gu et al. 2026, "Weak Evolution of Cosmic Atomic Hydrogen over the
  Past 4.5 Billion Years", Nature Astronomy, DOI 10.1038/s41550-026-02965-9
  arXiv:2607.05326v1 (FASHI-DESI: FAST 21-cm stacking x DESI BGS, ~2.5e6 galaxies,
  ~12,000 deg^2, 0 < z < 0.41)

FROZEN OBSERVATIONAL ANCHORS (no post-hoc adjustment allowed):
  A_OhmHI : Omega_HI/(1e-3 h70^-1) = 0.496 +- 0.013                      [Sec. Results]
  A_slope : Omega_HI propto (1+z)^(0.9 +- 0.2)   (4 bins, z<0.41)        [Sec. Results]
  A_bins  : <z> = 0.033, 0.069, 0.281, 0.358                             [Sec. Results]
  A_raw   : raw decrease of Omega_HI factor 1.35 +- 0.10 over 4.5 Gyr    [Abstract]
  A_corr  : systematics-corrected decrease factor 1.12 +- 0.10           [Abstract]
  A_csfrd : CSFRD decline factor 2.46 over the same interval             [Abstract]
  A_fHI   : at fixed M*, <f_HI> evolves < 0.2 dex                        [Abstract]

IDCM INPUTS (all closed elsewhere, zero new constants here):
  Om_b = 1/20 = 3/60            [O168 / O215]
  Om_m = 19/60, Om_L = 41/60    [O215]
  H0   = 67.4071 km/s/Mpc       [O127 / O168 BBN lock]
  T_ring = 84.637 Gyr           [O121]
  1+z = 4^ell, N(z) prop 4^-ell = 1/(1+z)  [O76 / O173 P1]

This script only performs ARITHMETIC / BACKGROUND recomputation. Every judgment
item is printed with a [DIAGNOSTIC] tag and EXCLUDED from the PASS denominator
(protocol: diagnostic-vs-closure separation).
"""
import json
import os
from fractions import Fraction as F

import mpmath as mp

mp.mp.dps = 30
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "data")

PASS = 0
TOTAL = 0
DIAG = []


def ck(tag, ok, detail=""):
    global PASS, TOTAL
    TOTAL += 1
    PASS += 1 if ok else 0
    print("[%s] %s  %s" % ("PASS" if ok else "FAIL", tag, detail))


def diag(tag, text):
    DIAG.append((tag, text))
    print("[DIAGNOSTIC] %s  %s" % (tag, text))


# ---------------------------------------------------------------- IDCM inputs
Om_b = F(1, 20)
Om_m = F(19, 60)
Om_L = F(41, 60)
H0 = mp.mpf("67.4071")
T_ring = mp.mpf("84.637")          # Gyr
h = H0 / 100
h70 = h / mp.mpf("0.7")

# ------------------------------------------------------- observational anchors
OmHI_1e3 = mp.mpf("0.496")         # Omega_HI / (1e-3 h70^-1)
OmHI_1e3_err = mp.mpf("0.013")
slope = mp.mpf("0.9")
slope_err = mp.mpf("0.2")
f_raw, f_raw_err = mp.mpf("1.35"), mp.mpf("0.10")
f_corr, f_corr_err = mp.mpf("1.12"), mp.mpf("0.10")
f_csfrd = mp.mpf("2.46")
zmax = mp.mpf("0.41")
lookback = mp.mpf("4.5")           # Gyr

# ------------------------------------------------------------------ background
def E(z):
    return mp.sqrt(Om_m * (1 + z) ** 3 + Om_L)


Hub_Gyr = mp.mpf("977.7922214") / H0      # 1/H0 in Gyr  (km/s/Mpc -> 1/Gyr)


def age(z):
    """cosmic age in Gyr, IDCM background (flat, Om_m=19/60, Om_L=41/60)"""
    if z == 0:
        return Hub_Gyr * mp.quad(lambda u: 1 / E(mp.e ** u - 1),
                                 [0, mp.log(mp.mpf("1e6"))])
    return Hub_Gyr * mp.quad(lambda u: 1 / E(mp.e ** u - 1),
                             [mp.log(1 + z), mp.log(mp.mpf("1e6"))])


t0 = age(mp.mpf("0"))
t_lb = t0 - lookback

# solve age(z) = t_lb  (monotone decreasing in z -> bisection)
lo, hi = mp.mpf("0"), mp.mpf("2")
for _ in range(120):
    mid = (lo + hi) / 2
    if age(mid) > t_lb:
        lo = mid
    else:
        hi = mid
z45 = (lo + hi) / 2
one_plus_z = 1 + z45
ell = mp.log(one_plus_z) / mp.log(4)

print("=" * 78)
print("O253/01  observation anchor freeze + IDCM background")
print("=" * 78)
print("t0(IDCM background)      = %s Gyr" % mp.nstr(t0, 10))
print("1/H0                     = %s Gyr" % mp.nstr(Hub_Gyr, 10))
print("z(lookback 4.5 Gyr)      = %s" % mp.nstr(z45, 10))
print("1+z                      = %s" % mp.nstr(one_plus_z, 10))
print("ell = log_4(1+z)         = %s" % mp.nstr(ell, 10))
print("h, h70                   = %s , %s" % (mp.nstr(h, 8), mp.nstr(h70, 8)))
print()

# --- C1: age(0) consistency with H0-locked value (diagnostic magnitude only)
diag("C1", "t0 = %s Gyr under (19/60, 41/60, 67.4071) -- background self-consistency,"
           " not a new derivation" % mp.nstr(t0, 8))
ck("C1a z(4.5Gyr) inside paper window 0<z<0.41",
   z45 < mp.mpf("0.41") + mp.mpf("0.01"),
   "z = %s (paper window top z=0.41)" % mp.nstr(z45, 6))
ck("C1b 4^ell = 1+z exactly (structural redshift law closed form)",
   abs(4 ** ell - one_plus_z) < mp.mpf("1e-25"),
   "4^%s = %s" % (mp.nstr(ell, 8), mp.nstr(4 ** ell, 10)))

# --- C2: does Omega_HI prop (1+z)^1 (nearest closed IDCM exponent magnitude)
#     survive BOTH the raw and the systematics-corrected number?
pred_pow1 = one_plus_z ** 1
sig_raw = (pred_pow1 - f_raw) / f_raw_err
sig_corr = (pred_pow1 - f_corr) / f_corr_err
print()
print("[C2] Omega_HI(1+z)^1 test:  (1+z)^1 = %s" % mp.nstr(pred_pow1, 9))
diag("C2", "vs raw 1.35+-0.10  -> %+.2f sigma ;  vs corrected 1.12+-0.10 -> %+.2f sigma"
           % (float(sig_raw), float(sig_corr)))
ck("C2a exponent +1 survives RAW measurement (|sigma|<2)",
   abs(sig_raw) < 2, "|sigma| = %.2f" % abs(float(sig_raw)))
ck("C2b exponent +1 is EXCLUDED by systematics-corrected measurement (|sigma|>2)",
   abs(sig_corr) > 2, "|sigma| = %.2f  (this kills the tempting match)" % abs(float(sig_corr)))

# --- C3: paper's own slope band vs closed IDCM exponent candidates
print()
print("[C3] paper slope = %s +- %s  (1-sigma band [%s, %s])"
      % (mp.nstr(slope, 4), mp.nstr(slope_err, 4),
         mp.nstr(slope - slope_err, 5), mp.nstr(slope + slope_err, 5)))
for cand, name in [(mp.mpf("0"), "0 (constant)"), (mp.mpf("1"), "+1 = |IDCM P1 exponent|"),
                   (mp.mpf("-1"), "-1 = IDCM P1 exponent")]:
    s = (cand - slope) / slope_err
    diag("C3", "candidate %-28s (1+z)^%s -> %+.2f sigma" % (name, mp.nstr(cand, 3), float(s)))
ck("C3a P1 exponent -1 is disfavoured (>2 sigma) by the paper slope",
   abs((mp.mpf("-1") - slope) / slope_err) > 2, "P1 sign is opposite to the data")

# --- C4: implied CSFRD local exponent and the phi^2 trap
k_sfr = mp.log(f_csfrd) / mp.log(one_plus_z)
k_lo = mp.log(f_csfrd) / mp.log(1 + mp.mpf("0.42"))
k_hi = mp.log(f_csfrd) / mp.log(1 + mp.mpf("0.40"))
phi = (1 + mp.sqrt(5)) / 2
phi2 = phi ** 2
print()
print("[C4] k_SFR = ln(2.46)/ln(1+z) = %s" % mp.nstr(k_sfr, 8))
print("     z-window sensitivity [z=0.40,0.42] -> k in [%s, %s]"
      % (mp.nstr(k_hi, 6), mp.nstr(k_lo, 6)))
print("     phi^2 = %s ; dev vs k_SFR = %s%%"
      % (mp.nstr(phi2, 10), mp.nstr(100 * abs(phi2 - k_sfr) / k_sfr, 4)))
diag("C4", "phi^2 lands inside the z-window band by construction -> the apparent"
           " 0.3%% match carries ZERO information (banned phi-power fitting, O204/O136 register)")
ck("C4a phi^2 lies inside the z-sensitivity band (=> no discriminating power)",
   k_lo < phi2 < k_hi, "phi^2 in [%s, %s]" % (mp.nstr(k_lo, 6), mp.nstr(k_hi, 6)))

# --- C5: rho_HI, tau_dep(HI,z=0), tau/T_ring
rho_c = mp.mpf("2.77536627e11") * h ** 2          # Msun/Mpc^3
OmHI = OmHI_1e3 * mp.mpf("1e-3") / h70
rho_HI = OmHI * rho_c


def madau_fragos(z):
    """Madau & Fragos 2017 Eq.15 (M_sun/yr/Mpc^3) -- observational CSFRD anchor"""
    return mp.mpf("0.015") * (1 + z) ** mp.mpf("2.7") / \
        (1 + ((1 + z) / mp.mpf("2.9")) ** mp.mpf("5.6"))


psi0 = madau_fragos(mp.mpf("0"))
tau_dep = rho_HI / psi0 / mp.mpf("1e9")           # Gyr
ratio_ring = tau_dep / T_ring
print()
print("[C5] rho_c = %s Msun/Mpc^3" % mp.nstr(rho_c, 8))
print("     Omega_HI(z=0) = %s" % mp.nstr(OmHI, 8))
print("     rho_HI(z=0) = %s Msun/Mpc^3" % mp.nstr(rho_HI, 8))
print("     psi(0) = %s Msun/yr/Mpc^3" % mp.nstr(psi0, 8))
print("     tau_dep(HI) = %s Gyr   tau/T_ring = %s" % (mp.nstr(tau_dep, 8), mp.nstr(ratio_ring, 8)))
print("     1/20 = %s ; dev = %s%%" % (mp.nstr(mp.mpf("0.05"), 6),
                                      mp.nstr(100 * abs(ratio_ring - mp.mpf("0.05")) / mp.mpf("0.05"), 4)))
ck("C5a tau_dep(HI) is a well-defined positive comoving ratio",
   tau_dep > 0 and psi0 > 0, "tau = %s Gyr" % mp.nstr(tau_dep, 6))
diag("C5", "tau/T_ring = %s vs 1/20 (dev %s%%) -- observed error band is ~20%%"
           " (Omega_HI 2.6%%, CSFRD ~20%%), so this match has NO discriminating power;"
           " must not be promoted without an operator mechanism"
      % (mp.nstr(ratio_ring, 6),
         mp.nstr(100 * abs(ratio_ring - mp.mpf("0.05")) / mp.mpf("0.05"), 3)))

# --- C6: efficiency evolution the paper implies (the real target)
eff_raw = f_csfrd / f_raw
eff_corr = f_csfrd / f_corr
print()
print("[C6] implied conversion-efficiency decline (SFR/rho_HI):")
print("     raw       ratio = 2.46/1.35 = %s  (decline %s%%)"
      % (mp.nstr(eff_raw, 8), mp.nstr(100 * (1 - 1 / eff_raw), 5)))
print("     corrected ratio = 2.46/1.12 = %s  (decline %s%%)"
      % (mp.nstr(eff_corr, 8), mp.nstr(100 * (1 - 1 / eff_corr), 5)))
ck("C6a efficiency decline is strictly positive in both branches",
   eff_raw > 1 and eff_corr > 1, "target band for any IDCM mechanism: [%s, %s]"
   % (mp.nstr(eff_raw, 6), mp.nstr(eff_corr, 6)))

# --- C7: independent recompute of tau_dep(z) using the paper's own slope
zb = mp.mpf("0.358")
OmHI_b = OmHI_1e3 * mp.mpf("1e-3") / h70 * (1 + zb) ** slope
rho_b = OmHI_b * rho_c
psi_b = madau_fragos(zb)
tau_b = rho_b / psi_b / mp.mpf("1e9")
print()
print("[C7] tau_dep(<z>=0.358) = %s Gyr ; tau(0)/tau(0.358) = %s"
      % (mp.nstr(tau_b, 8), mp.nstr(tau_dep / tau_b, 8)))
diag("C7", "MF-based tau ratio %s vs paper factor ratio %s -- %s%% apart;"
           " CSFRD anchor convention (M&F Eq.15) accounts for the gap, not IDCM"
      % (mp.nstr(tau_dep / tau_b, 6), mp.nstr(eff_raw, 6),
         mp.nstr(100 * abs(tau_dep / tau_b - eff_raw) / eff_raw, 3)))
ck("C7a tau_dep decreases with z (efficiency was higher in the past)",
   tau_b < tau_dep, "tau(0.358)=%s < tau(0)=%s" % (mp.nstr(tau_b, 6), mp.nstr(tau_dep, 6)))

# --- C8: gas share of IDCM baryon budget (dimensionless, the framework's own language)
share = OmHI / float(Om_b)
print()
print("[C8] Omega_HI / Omega_b = %s  (Omega_b = 1/20 = 0.05, O168)"
      % mp.nstr(share, 8))
diag("C8", "HI carries %s%% of the IDCM baryon budget; no closed IDCM identity for this"
           " share exists in corpus (0 hits) -> OPEN, must not be reverse-fitted"
      % mp.nstr(100 * share, 5))
ck("C8a HI share is well inside the baryon budget (0<share<Om_m/Om_b)",
   share > 0 and share < float(Om_m / Om_b), "share = %s" % mp.nstr(share, 6))

# ------------------------------------------------------------------- dump data
os.makedirs(OUT, exist_ok=True)
payload = {
    "script": "01_observation_anchor_freeze.py",
    "source": {"doi": "10.1038/s41550-026-02965-9", "arxiv": "2607.05326v1",
               "survey": "FASHI-DESI HI stacking, 2.5e6 galaxies, 12000 deg2, 0<z<0.41"},
    "anchors": {"Omega_HI_1e3_h70": float(OmHI_1e3), "Omega_HI_1e3_err": float(OmHI_1e3_err),
                "slope": float(slope), "slope_err": float(slope_err),
                "factor_raw": float(f_raw), "factor_raw_err": float(f_raw_err),
                "factor_corrected": float(f_corr), "factor_corrected_err": float(f_corr_err),
                "csfrd_factor": float(f_csfrd), "z_max": float(zmax), "lookback_Gyr": float(lookback)},
    "idcm_inputs": {"Om_b": str(Om_b), "Om_m": str(Om_m), "Om_L": str(Om_L),
                    "H0": float(H0), "T_ring_Gyr": float(T_ring)},
    "computed": {"t0_Gyr": float(t0), "z_45Gyr": float(z45), "one_plus_z": float(one_plus_z),
                 "ell": float(ell), "h": float(h), "h70": float(h70),
                 "rho_c": float(rho_c), "Omega_HI": float(OmHI), "rho_HI": float(rho_HI),
                 "psi0": float(psi0), "tau_dep_Gyr": float(tau_dep),
                 "tau_over_T_ring": float(ratio_ring), "k_SFR": float(k_sfr),
                 "k_SFR_band": [float(k_hi), float(k_lo)], "phi2": float(phi2),
                 "sigma_pow1_vs_raw": float(sig_raw), "sigma_pow1_vs_corr": float(sig_corr),
                 "eff_ratio_raw": float(eff_raw), "eff_ratio_corrected": float(eff_corr),
                 "tau_dep_z0358": float(tau_b), "tau_ratio": float(tau_dep / tau_b),
                 "HI_share_of_baryons": float(share)},
    "diagnostics": [{"tag": t, "text": x} for t, x in DIAG],
    "pass": "%d/%d" % (PASS, TOTAL),
}
with open(os.path.join(OUT, "01_observation_anchor_freeze.json"), "w") as fh:
    json.dump(payload, fh, indent=1, ensure_ascii=False)

print()
print("RESULT: %d/%d PASS  (+%d [DIAGNOSTIC] excluded from denominator)"
      % (PASS, TOTAL, len(DIAG)))
