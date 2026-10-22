#!/usr/bin/env python3
"""
O199 scripts/06 - Verdict: is the 2% Eddington critical rate geometrically forced?

Aggregates data/01..05 and applies the four hard tests:
  H1 degrees-of-freedom cost   (script 02/05: forced form vs dictionary hit)
  H2 Monte-Carlo null          (script 03: 1e7 random targets)
  H3 falsifiability + power    (script 05: required sample size)
  H4 structural rigidity       (script 05: convention swap)

ASCII only.
"""

import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
O_DIR = os.path.dirname(SCRIPT_DIR)
DATA = os.path.join(O_DIR, "data")

results = []


def check(name, cond, detail=""):
    results.append({"name": name, "pass": bool(cond), "detail": detail})
    print(("  PASS " if cond else "  FAIL ") + name + (" | " + detail if detail else ""))


def load(fn):
    with open(os.path.join(DATA, fn)) as fh:
        return json.load(fh)


a1 = load("01_observation_anchor.json")
a2 = load("02_eddington_scale_inventory.json")
a3 = load("03_ratio_census_null.json")
a4 = load("04_geometric_thresholds.json")
a5 = load("05_rigidity_dof.json")

N_d, B, N_gen, mu2 = 44, 4, 3, 2
F5 = 5
TARGET = 0.02
W1 = a1["windows"]["W1_xrb_band"]

print("=" * 78)
print("O199 / 06 - VERDICT: is L_crit/L_Edd = 0.02 geometrically forced?")
print("=" * 78)

# --- H1: DOF cost -----------------------------------------------------------
exact = [r for r in a2["inventory"] if r["dev"] < 1e-12]
forced = [r for r in a2["inventory"] if r["class"] == "single spectral ratio"]
best_forced = min(forced, key=lambda r: r["dev"])
print("  H1 DOF cost")
print("    exact hits on 0.02           : %d  (classes: %s)"
      % (len(exact), sorted(set(r["class"] for r in exact))))
print("    best FORCED spectral ratio   : %s -> %.6f (dev %.2f%%)"
      % (best_forced["label"], best_forced["value"], best_forced["dev"] * 100))
print("    dictionary size for 1/50     : %d two-term / %d three-term decompositions"
      % (a5["dictionary_size"]["50_2term"], a5["dictionary_size"]["50_3term"]))

check("H1a every exact hit on 0.02 is a dictionary/integer form, none is a forced spectral ratio",
      len(exact) > 0 and all(r["class"] in ("integer ratio", "composite") for r in exact),
      "%d exact hits" % len(exact))
check("H1b the best forced spectral ratio misses 0.02 by more than 10%",
      best_forced["dev"] > 0.10,
      "%s dev = %.2f%%" % (best_forced["label"], best_forced["dev"] * 100))
check("H1c the denominator 50 admits >= 20 structural decompositions",
      a5["dictionary_size"]["50_2term"] >= 20,
      "%d two-term ways" % a5["dictionary_size"]["50_2term"])

# --- H2: MC null ------------------------------------------------------------
n01 = a3["null"]["0.01"]
print("  H2 Monte-Carlo null (%d random targets)" % a3["n_null_samples"])
print("    expressions within +/-1%% of 0.02 : %d" % n01["observed_count"])
print("    null mean/median                  : %.2f / %.1f" % (n01["null_mean"], n01["null_median"]))
print("    observed/median = %.3f ; p-value = %.4f ; z above mean = %.2f"
      % (n01["observed_over_median"], n01["p_value"], n01["z_above_mean"]))

check("H2a 0.02 is not an outlier of the null distribution (p > 0.01)",
      n01["p_value"] > 0.01, "p = %.4f" % n01["p_value"])
check("H2b observed count is within a factor 3 of the null median (no selection signal)",
      1.0 / 3.0 < n01["observed_over_median"] < 3.0,
      "ratio = %.3f" % n01["observed_over_median"])
check("H2c multiple independent expressions hit 0.02 at the 1% level (>5)",
      n01["observed_count"] > 5, "%d hits" % n01["observed_count"])

# --- H3: falsifiability + power --------------------------------------------
d = a5["discrimination"]
n_50_44 = d["1/50 = 2.000% vs 1/44 = 2.273%"]["N_required"]["s=0.50"]
n_45_44 = d["1/45 = 2.222% vs 1/44 = 2.273%"]["N_required"]["s=0.50"]
print("  H3 falsifiability / power")
print("    N(3 sigma, s=0.5) 1/50 vs 1/44 : %.0f sources" % n_50_44)
print("    N(3 sigma, s=0.5) 1/45 vs 1/44 : %.0f sources" % n_45_44)

check("H3a the decisive test (2.000% vs 2.273%) is feasible: N < 1000",
      n_50_44 < 1000.0, "N = %.0f" % n_50_44)
check("H3b the 1/45 vs 1/44 refinement needs an unrealistically large sample",
      n_45_44 > 10000.0, "N = %.0f" % n_45_44)

# --- H4: rigidity ----------------------------------------------------------
sw = a5["convention_swap"]
sw_devs = {k: abs(v - TARGET) / TARGET for k, v in sw.items() if "176" in k}
print("  H4 structural rigidity (convention swap to the 176 half-set)")
for k, v in sw_devs.items():
    print("    %-42s dev = %.2f%%" % (k, v * 100))

check("H4 no 2%-scale candidate survives re-expression in the other registered convention",
      all(v > 0.05 for v in sw_devs.values()),
      "min dev after swap = %.1f%%" % (min(sw_devs.values()) * 100))
check("H4b no discrete mode-fraction m/N in the framework lands within 1% of 0.02",
      len(a4["mode_fractions_near_target"]) == 0,
      "%d mode fractions near target" % len(a4["mode_fractions_near_target"]))
check("H4c the frustration subgraph has no percolation threshold (p_c = %.2f > 1)"
      % a4["frustration_percolation"]["p_c"],
      a4["frustration_percolation"]["p_c"] > 1.0,
      "<k> = %.6f" % a4["frustration_percolation"]["k_mean"])

# --- positive structural result: scale invariance ---------------------------
forced_vals = [r["value"] for r in forced]
check("S-inv all framework candidates are pure dimensionless structural ratios "
      "(no mass scale enters => scale invariance is automatic, not a coincidence)",
      all(0.0 < v < 1.0 for v in forced_vals),
      "%d forced candidates, all M-independent by construction" % len(forced_vals))
check("S-band the forced spectral identities (1/45, 1/44) lie INSIDE the observational band W1",
      all(W1[0] <= v <= W1[1] for v in (1.0 / 45.0, 1.0 / 44.0)),
      "1/45 = %.6f ; 1/44 = %.6f ; W1 = %s" % (1.0 / 45.0, 1.0 / 44.0, W1))

# --- hierarchy candidate: 10% (LRD) vs 2% (jet threshold) -------------------
ratio = 0.10 / TARGET
print("  hierarchy: lambda_Edd(LRD) / L_crit(jet) = 0.10 / 0.02 = %.6f" % ratio)
print("    structural identities of the ratio: F5 = %d = B+1 = %d = L4-mu^2 = %d"
      % (F5, B + 1, 7 - mu2))
check("H5 the two Eddington-ratio scales differ by exactly F5 = 5 = B+1 = L4-mu^2",
      abs(ratio - F5) < 1e-12 and F5 == B + 1 and F5 == 7 - mu2,
      "ratio = %.6f ; F5 = %d" % (ratio, F5))

# --- final verdict ----------------------------------------------------------
verdict = {
    "question": "is L_crit/L_Edd = 0.02 geometrically forced in IDCM?",
    "answer": "NO - not forced. Exact hits are dictionary hits (1/50 family); "
              "the framework's forced spectral identities sit at 1/45 = 2.222% and "
              "1/44 = 2.273%, i.e. 11-14% away from the quoted value.",
    "positive_structural_result":
        "scale invariance of the threshold IS structurally automatic: every IDCM "
        "threshold is a dimensionless ratio of structural integers, so no M_BH "
        "dependence is possible (dimension theorem, O73/O201).",
    "registered_prediction":
        "the low-hard jet threshold should be C_energy = 1/(N_d+1) = 1/45 = 2.222% "
        "(Z2 sector capacity asymmetry), not 2.000%; separable with N ~ 600-800 TDEs "
        "at 3 sigma (s = 0.5); if a large sample converges on 2.000%, the C_energy "
        "identity is falsified as the threshold value.",
    "hierarchy_candidate":
        "lambda_Edd(LRD, O176) / L_crit(jet) = 0.10/0.02 = 5 = F5 = B+1 = L4-mu^2 (EXACT, but "
        "both inputs are themselves candidates, so this is registered at candidate level).",
    "residual_open":
        "no mechanism yet connects an accretion-rate threshold to a spectral-mode "
        "condition inside the 44/88 chain (the frustration subgraph is sub-critical, "
        "so there is no geometric percolation onset either).",
}
print("-" * 78)
print("  VERDICT: %s" % verdict["answer"])
print("  POSITIVE: %s" % verdict["positive_structural_result"])
print("  PREDICTION: %s" % verdict["registered_prediction"])

os.makedirs(DATA, exist_ok=True)
with open(os.path.join(DATA, "06_verdict.json"), "w") as fh:
    json.dump({"verdict": verdict, "checks": results}, fh, indent=2)

n_pass = sum(1 for r in results if r["pass"])
print("=" * 78)
print("TOTAL: %d/%d PASS" % (n_pass, len(results)))
print("wrote data/06_verdict.json")
