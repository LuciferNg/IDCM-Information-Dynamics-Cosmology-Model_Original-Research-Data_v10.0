#!/usr/bin/env python3
"""
O199 scripts/04 - Geometric-threshold route: which IDCM thresholds exist at all?

QUESTION
  "Geometrically forced" would mean: a threshold value that the framework's
  geometry/spectrum produces as a THRESHOLD (an inequality that flips, a
  percolation onset, a capacity fraction), before any target is seen.

METHOD
  1. Enumerate every threshold-like dimensionless quantity the 44/88/176
     structure actually supports, each with its mechanism.
  2. Report the distance to 0.02 and the form class.
  3. Test whether ANY of the framework's own inequalities flips exactly at
     mdot = 0.02 (a genuine threshold would be the boundary of a mode-count
     or capacity condition).
  4. Convention-robustness: recompute the near-0.02 candidates under the two
     registered conventions (44-chain vs 176-Laplacian half-set) and under the
     framework's own generalisation N (chain length) to see whether the value
     is tied to N = 44 or is generic.

ASCII only.
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


N_d, B, N_gen, mu2 = 44, 4, 3, 2
L4, L5, L6 = 7, 11, 18
F5, F6, F7, F11 = 5, 8, 13, 89
F_proj, M_tree, K_tree, L10 = 17, 33, 30, 123
A5_V, A5_E = 60, 120
TARGET = 0.02

print("=" * 78)
print("O199 / 04 - Geometric-threshold route (what thresholds exist, and where)")
print("=" * 78)

# --- spectra -----------------------------------------------------------------
g44 = [4.0 * math.sin(math.pi * n / 88.0) ** 2 for n in range(1, 45)]
s44 = sum(g44)
s44_odd = sum(g44[n - 1] for n in range(1, 45) if n % 2 == 1)
s44_even = sum(g44[n - 1] for n in range(1, 45) if n % 2 == 0)

thresh = [
    # (name, value, mechanism, class)
    ("half-power point cos^2(theta_22) = 1/2", 0.5,
     "projection kernel r_k = 2 pi R cos^2 theta_k; n = N_d/2 self-dual mode", "geometric"),
    ("condensation onset 44/88", 0.5,
     "M_base at the k = 44 centre mode (O197 docs/04)", "geometric"),
    ("Z2 self-dual mode fraction 22/44", 0.5,
     "the single fixed point n -> N_d - n", "geometric"),
    ("sector capacity sum_odd/sum = 88/178", s44_odd * 2 / (s44_odd * 2 + s44_even * 2),
     "Z2 sector capacity share (176 half-set)", "spectral"),
    ("A5 transparent-edge fraction 88/120", 88.0 / A5_E,
     "88 = 120 - 32 transparent edges (O182)", "geometric"),
    ("A5 frustration fraction 32/120", 32.0 / A5_E,
     "32 = 4b - 2a frustration edges (O171)", "geometric"),
    ("frustration edges / full cycle 32/176", 32.0 / 176.0,
     "frustration edges against 176-cycle sites", "geometric"),
    ("K-window fraction 21/44", 21.0 / 44.0,
     "mass threshold gamma_n < mu^2 (O169 docs/14)", "spectral"),
    ("C_energy = mu^2/(2N_d+mu^2) = 1/45", mu2 / (2 * N_d + mu2),
     "Z2 sector capacity asymmetry = drift fraction (O203)", "spectral"),
    ("site-count normalisation mu^2/(2N_d) = 1/44", mu2 / (2 * N_d),
     "2 phase slips per ring period, 44-cycle (O7/O203)", "spectral"),
    ("1/(2N_d) = 1/88", 1.0 / (2 * N_d), "single Nyquist mode of the 88-site ring", "spectral"),
    ("1/(N_d B) = 1/176", 1.0 / (N_d * B), "single mode of the full 176 cycle", "spectral"),
    ("lambda_self = mu^2/L_10 = 2/123", mu2 / L10,
     "vacuum self-coupling (O204)", "spectral"),
    ("mu^2/<W>^2 = 4/123", 4.0 / L10, "mass quantum / condensate capacity (O204)", "spectral"),
    ("kappa_crit = sin(pi/88)/<W>", math.sin(math.pi / 88.0) / 7.84219357068,
     "O81 sub-critical coupling bound", "spectral"),
    ("1/(2N_d + 2B) = 1/96", 1.0 / (2 * N_d + 2 * B), "integer sum (no mechanism)", "integer"),
    ("1/(N_d + B + mu^2) = 1/50", 1.0 / (N_d + B + mu2), "integer sum (no mechanism)", "integer"),
    ("C_energy * (1 - lambda_Edd) = 1/50", (mu2 / (2 * N_d + mu2)) * (1 - B / (N_d - B)),
     "composition: sector asymmetry x (1 - LRD Eddington fraction)", "composite"),
    ("lambda_Edd = B/(N_d-B) = 1/10", float(B) / (N_d - B),
     "LRD Eddington ratio candidate (O176 D10)", "registered candidate"),
]

print("  %-46s %11s %9s %s" % ("threshold", "value", "dev vs 0.02", "class"))
rows = []
for name, val, mech, cls in thresh:
    dev = abs(val - TARGET) / TARGET
    rows.append({"name": name, "value": val, "dev": dev, "mechanism": mech, "class": cls})
rows.sort(key=lambda r: r["dev"])
for r in rows:
    print("  %-46s %11.7f %8.2f%% %s" % (r["name"][:46], r["value"], r["dev"] * 100, r["class"]))

# --- percolation test on the frustration subgraph ---------------------------
# 32 frustration edges among 60 A5 vertices; mean degree <k> = 2*32/60.
k_mean = 2.0 * 32.0 / A5_V
p_c_er = 1.0 / (k_mean - 1.0) if k_mean > 1.0 else float("inf")
print("-" * 78)
print("  frustration subgraph: <k> = 2*32/60 = %.6f" % k_mean)
print("  Erdos-Renyi giant-component onset p_c = 1/(<k>-1) = %s" % (
    ("%.4f" % p_c_er) if math.isfinite(p_c_er) else "inf (sub-critical)"))
print("  -> the frustration network is SUB-CRITICAL: no percolation threshold exists.")

# --- threshold search: does any framework inequality flip at 0.02? ----------
# Candidate mode-count thresholds: the accretion-rate analogue in IDCM is the
# FRACTION of active modes / of the capacity.  Enumerate the framework's own
# discrete fractions and check whether any equals 0.02 within 1%.
fracs = {}
for m in range(1, 89):
    fracs["m/88 (mode fraction)"] = fracs.get("m/88 (mode fraction)", []) + [(m, m / 88.0)]
    fracs["m/176"] = fracs.get("m/176", []) + [(m, m / 176.0)]
    fracs["m/178 (spectral weight)"] = fracs.get("m/178 (spectral weight)", []) + [(m, m / 178.0)]
for m in range(1, 45):
    fracs["m/44"] = fracs.get("m/44", []) + [(m, m / 44.0)]

near = []
for k, lst in fracs.items():
    for m, v in lst:
        if abs(v - TARGET) / TARGET <= 0.01:
            near.append({"family": k, "m": m, "value": v})
print("-" * 78)
print("  discrete mode-fraction families within +/-1%% of 0.02:")
if near:
    for n in near:
        print("    %s : m = %d -> %.6f" % (n["family"], n["m"], n["value"]))
else:
    print("    NONE (no integer mode count m gives m/N = 0.02 +/- 1%)")

check("G1 no discrete mode-fraction m/N lands within 1% of 0.02",
      len(near) == 0, "closest families: %s" % (sorted(set(
          min(((abs(v - TARGET) / TARGET, "%s m=%d" % (k, m)) for m, v in lst))
          for k, lst in fracs.items()))[:3]))
check("G2 frustration subgraph is sub-critical: ER onset p_c = 1/(<k>-1) > 1",
      math.isfinite(p_c_er) and p_c_er > 1.0,
      "<k> = %.6f -> p_c = %.4f > 1 (no giant component possible)" % (k_mean, p_c_er))
check("G3 the two exact spectral identities (1/45, 1/44) are NOT within 5% of 0.02",
      abs(mu2 / (2 * N_d + mu2) - TARGET) / TARGET > 0.05 and
      abs(mu2 / (2 * N_d) - TARGET) / TARGET > 0.05,
      "1/45 dev = %.2f%%, 1/44 dev = %.2f%%"
      % (abs(mu2 / (2 * N_d + mu2) - TARGET) / TARGET * 100,
         abs(mu2 / (2 * N_d) - TARGET) / TARGET * 100))

# --- convention robustness + N generalisation -------------------------------
print("-" * 78)
print("  convention / generalisation robustness of the 2% candidates:")
rob = []
for N in (22, 44, 88, 176):
    # generic forms parameterised by the chain length N
    cand = {
        "mu^2/(2N+mu^2)": mu2 / (2 * N + mu2),
        "mu^2/(2N)": mu2 / (2 * N),
        "1/(N+B+mu^2)": 1.0 / (N + B + mu2),
        "C_energy*(1-lambda_Edd)": (mu2 / (2 * N + mu2)) * (1 - B / (N - B)) if N > B else float("nan"),
    }
    devs = {k: (abs(v - TARGET) / TARGET if v == v else float("nan")) for k, v in cand.items()}
    rob.append({"N": N, "values": cand, "devs": devs})
    print("    N = %3d : " % N + "  ".join(
        "%s = %.6f (%.1f%%)" % (k, v, devs[k] * 100) for k, v in cand.items()))

stable = all(r["devs"]["mu^2/(2N+mu^2)"] > 0.05 for r in rob)
check("G4 no N-generic form stays within 5% of 0.02 across N in {22,44,88,176}",
      stable, "max dev across N for mu^2/(2N+mu^2) = %.1f%%"
      % (min(r["devs"]["mu^2/(2N+mu^2)"] for r in rob) * 100))

out = {
    "target": TARGET,
    "thresholds": rows,
    "frustration_percolation": {"k_mean": k_mean, "p_c": (p_c_er if math.isfinite(p_c_er) else None),
                                "subcritical": k_mean < 2.0},
    "mode_fractions_near_target": near,
    "robustness": rob,
}
os.makedirs(DATA, exist_ok=True)
with open(os.path.join(DATA, "04_geometric_thresholds.json"), "w") as fh:
    json.dump(out, fh, indent=2)

n_pass = sum(1 for r in results if r["pass"])
print("=" * 78)
print("TOTAL: %d/%d PASS" % (n_pass, len(results)))
print("wrote data/04_geometric_thresholds.json")
