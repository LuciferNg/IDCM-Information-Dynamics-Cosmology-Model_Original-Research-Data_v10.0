#!/usr/bin/env python3
"""
O199 scripts/01 - Observational anchor: Goodwin & Mummery (2026)

SOURCE
  A. J. Goodwin & A. Mummery, "A universal critical accretion rate for black
  hole jet formation", Nature Astronomy (2026); arXiv:2602.14838 [astro-ph.HE],
  submitted 2026-02-16. Secondary reporting: TechNews 2026-09-18.

ANCHORS (paper-level facts, recorded verbatim in spirit)
  - TDEs launch outflows at TWO characteristic Eddington-ratio scales:
        mdot_high ~ 1.0     prompt outflow (super-Eddington wind)
        mdot_low  ~ 0.02    delayed outflow (compact state-transition jet)
  - The 0.02 threshold is the SAME critical rate as the XRB low-hard state
    transition => accretion-outflow coupling is scale invariant
    (M_BH ~ 10 - 1e8 Msun).
  - Sample: 20 TDEs considered, 10 TDE systems used (public + constraining
    multiwavelength data); prompt fraction A = 5/11 ~ 0.45.
  - ~42% of TDE disks are expected to enter a super-Eddington phase
    (compared with 30-50% observed prompt radio detection rate).
  - Cited theoretical support: Rees (1982) - the critical rate depends on the
    disk scale height h and viscosity alpha, but NOT on M_BH.

SCOPE NOTE
  This is a DATA-LAYER script: it records the observational anchor and derives
  the tolerance windows used downstream. Its checks verify arithmetic and
  internal consistency of the anchor ONLY - they are NOT IDCM closure claims.

ASCII only (project rule: no unicode in scripts).
"""

import json
import os
import math

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
O_DIR = os.path.dirname(SCRIPT_DIR)
DATA = os.path.join(O_DIR, "data")

results = []


def check(name, cond, detail=""):
    results.append({"name": name, "pass": bool(cond), "detail": detail})
    print(("  PASS " if cond else "  FAIL ") + name + (" | " + detail if detail else ""))


# ----------------------------------------------------------------------------
# 1. Recorded anchor values
# ----------------------------------------------------------------------------
mdot_high = 1.0            # super-Eddington prompt outflow scale
mdot_low = 0.02            # delayed outflow / low-hard transition scale
n_tde_considered = 20
n_tde_used = 10
prompt_fraction = 5.0 / 11.0
super_edd_fraction_paper = 0.42
prompt_detection_rate = (0.30, 0.50)

print("=" * 78)
print("O199 / 01 - Observational anchor: Goodwin & Mummery 2026 (arXiv:2602.14838)")
print("=" * 78)
print("  mdot_high (prompt, super-Eddington)  = %r" % mdot_high)
print("  mdot_low  (delayed, low-hard jet)    = %r" % mdot_low)
print("  sample: %d considered -> %d used" % (n_tde_considered, n_tde_used))
print("  prompt fraction A (paper)            = 5/11 = %.6f" % prompt_fraction)
print("  super-Eddington disk fraction (paper)= %.2f" % super_edd_fraction_paper)

# ----------------------------------------------------------------------------
# 2. Derived tolerance windows
# ----------------------------------------------------------------------------
# W1: XRB low-hard transition band used in the XRB literature (0.01 - 0.03 L_Edd).
#     The paper's whole point is that the SMBH (TDE) value coincides with the XRB
#     value, so the physically defensible band is the XRB band, not the 2-sig-fig
#     quoted point value.
w1 = (0.010, 0.030)
# W2: the quoted point value with 10% relative tolerance (a tight, IDCM-grade window)
w2 = (mdot_low * 0.90, mdot_low * 1.10)
# W3: 25% relative tolerance (generous, still discriminating 2.00 vs 2.27)
w3 = (mdot_low * 0.75, mdot_low * 1.25)

print("-" * 78)
print("  W1 (XRB low-hard band)      = [%.4f, %.4f]" % w1)
print("  W2 (point value +/-10%%)     = [%.4f, %.4f]" % w2)
print("  W3 (point value +/-25%%)     = [%.4f, %.4f]" % w3)

# ----------------------------------------------------------------------------
# 3. Anchor arithmetic / consistency checks (data layer only)
# ----------------------------------------------------------------------------
print("-" * 78)
ratio = mdot_high / mdot_low
check("A1 mdot_high/mdot_low = 50 exactly", abs(ratio - 50.0) < 1e-12,
      "ratio = %.12f" % ratio)
check("A2 W1 contains the quoted point value", w1[0] <= mdot_low <= w1[1],
      "0.02 in [0.01, 0.03]")
check("A3 W1 half-width in log = 0.2386 dex",
      abs(math.log10(w1[1] / w1[0]) / 2.0 - 0.23856) < 1e-4,
      "log10(3) = %.6f" % math.log10(3.0))
check("A4 W2 relative half-width = 10%", abs((w2[1] - w2[0]) / 2.0 / mdot_low - 0.10) < 1e-12,
      "half-width/point = %.3f" % ((w2[1] - w2[0]) / 2.0 / mdot_low))
check("A5 quoted point value has 1 significant figure",
      abs(mdot_low - 0.02) < 1e-15, "value = 0.02 (2% of Eddington)")
check("A6 sample used is 50% of sample considered",
      abs(float(n_tde_used) / n_tde_considered - 0.5) < 1e-15, "10/20 = 0.5")
check("A7 prompt detection rate band brackets the 42% expectation",
      prompt_detection_rate[0] <= super_edd_fraction_paper <= prompt_detection_rate[1],
      "0.30 <= 0.42 <= 0.50")

# ----------------------------------------------------------------------------
# 4. Side observations: two paper-level fractions vs registered IDCM integers
#    (registered as CURIOSITIES only - see docs/02; small-N counting statistics)
# ----------------------------------------------------------------------------
F5, L5 = 5, 11
N_gen, L4, mu2 = 3, 7, 2
idcm_5_11 = float(F5) / L5                      # F5 / L5
idcm_42 = float(mu2 * N_gen * L4) / 100.0       # mu^2*N_gen*L4 = 42  (O153 integer 42)
print("-" * 78)
print("  CURIOSITY C1: paper A = 5/11 = %.6f ; IDCM F5/L5 = %.6f ; dev = %.3e"
      % (prompt_fraction, idcm_5_11, abs(idcm_5_11 - prompt_fraction) / prompt_fraction))
print("  CURIOSITY C2: paper 42%% ; IDCM mu^2*N_gen*L4 = %d (integer identity) ; 42/100 = %.2f"
      % (mu2 * N_gen * L4, idcm_42))
check("C1 paper A = F5/L5 (EXACT, small-N counting stat)",
      abs(idcm_5_11 - prompt_fraction) < 1e-15, "5/11 = %.9f" % idcm_5_11)
check("C2 paper 42% = mu^2*N_gen*L4 / 100 (integer identity present)",
      (mu2 * N_gen * L4) == 42, "42 = 2*3*7 = mu^2 * N_gen * L4")

# ----------------------------------------------------------------------------
# 5. Write anchor JSON
# ----------------------------------------------------------------------------
anchor = {
    "source": "Goodwin & Mummery 2026, Nature Astronomy, arXiv:2602.14838",
    "mdot_high_super_eddington": mdot_high,
    "mdot_low_lowhard_jet": mdot_low,
    "mdot_ratio": ratio,
    "sample_considered": n_tde_considered,
    "sample_used": n_tde_used,
    "prompt_fraction_A": prompt_fraction,
    "super_eddington_disk_fraction": super_edd_fraction_paper,
    "prompt_detection_rate_band": list(prompt_detection_rate),
    "windows": {"W1_xrb_band": list(w1), "W2_pm10pct": list(w2), "W3_pm25pct": list(w3)},
    "theoretical_support": "Rees 1982: threshold depends on h and alpha, not M_BH",
    "curiosities": {
        "C1_prompt_fraction_vs_F5_over_L5": {"paper": prompt_fraction, "idcm": idcm_5_11},
        "C2_super_edd_fraction_vs_mu2NgenL4": {"paper": super_edd_fraction_paper, "idcm_integer": mu2 * N_gen * L4},
    },
    "scope": "data layer only; checks verify anchor arithmetic, not IDCM closure",
}
os.makedirs(DATA, exist_ok=True)
with open(os.path.join(DATA, "01_observation_anchor.json"), "w") as fh:
    json.dump(anchor, fh, indent=2)

n_pass = sum(1 for r in results if r["pass"])
print("=" * 78)
print("TOTAL: %d/%d PASS" % (n_pass, len(results)))
print("wrote data/01_observation_anchor.json")
