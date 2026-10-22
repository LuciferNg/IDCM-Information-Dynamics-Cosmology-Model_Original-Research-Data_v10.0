#!/usr/bin/env python3
"""
O199 scripts/05 - Rigidity, DOF cost, and discrimination power

Three of the four hard tests are applied here:

  (i)  degrees-of-freedom cost:  is the candidate a UNIQUE spectral expression
       of registered invariants (zero dictionary choice), or does it require
       picking a particular integer decomposition out of many?
  (ii) structural rigidity: perturb the primitives, and re-express the candidate
       under the framework's OTHER registered convention (176 half-set).
  (iii) falsifiability with quantified power: how precise must a TDE sample be
       to separate 2.000% (1/50) from 2.222% (1/45) and 2.273% (1/44)?

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
F5, F7 = 5, 13
F_proj, M_tree, L10 = 17, 33, 123
A5_V, A5_E = 60, 120
TARGET = 0.02

# pool = closure of the registered primitives, [1,400]  (same rule as script 03)
PRIMS = [2, 3, 4, 5, 7, 8, 11, 12, 13, 17, 18, 30, 33, 44, 60, 88, 120, 176]
CAP = 400
pool = set(PRIMS)
frontier = set(PRIMS)
while frontier:
    new = set()
    for a in list(frontier):
        for b in PRIMS + list(pool):
            for v in (a + b, a * b, abs(a - b)):
                if 1 <= v <= CAP and v not in pool:
                    new.add(v)
    pool |= new
    frontier = new
P = sorted(pool)

print("=" * 78)
print("O199 / 05 - Rigidity, DOF cost, discrimination power")
print("=" * 78)

# ---------------------------------------------------------------------------
# (i) dictionary size: how many integer decompositions give the value?
# ---------------------------------------------------------------------------
def count_decompositions(n, k):
    """number of unordered k-tuples of DISTINCT pool values summing to n"""
    Pset = set(P)
    cnt = 0
    examples = []
    if k == 2:
        for a in P:
            b = n - a
            if b in Pset and a < b:
                cnt += 1
                if len(examples) < 6:
                    examples.append((a, b))
    elif k == 3:
        for i, a in enumerate(P):
            for b in P[i + 1:]:
                c = n - a - b
                if c in Pset and c > b:
                    cnt += 1
                    if len(examples) < 6:
                        examples.append((a, b, c))
    return cnt, examples


for n, k in ((50, 2), (50, 3), (45, 2), (44, 2), (52, 2), (48, 2)):
    c, ex = count_decompositions(n, k)
    print("  integer %d as sum of %d distinct pool elements : %4d ways   e.g. %s"
          % (n, k, c, ex[:3]))

d50_2, ex50_2 = count_decompositions(50, 2)
d50_3, ex50_3 = count_decompositions(50, 3)
d45_2, ex45_2 = count_decompositions(45, 2)
d44_2, ex44_2 = count_decompositions(44, 2)

check("R1 the denominator 50 has many structural decompositions (dictionary hit)",
      d50_2 >= 5, "%d two-term ways (+ %d three-term ways)" % (d50_2, d50_3))
check("R2 denominators 45 and 44 have their own structural decompositions too",
      d45_2 >= 3 and d44_2 >= 3, "45: %d ways ; 44: %d ways" % (d45_2, d44_2))

# ---------------------------------------------------------------------------
# (ii) convention re-expression (176 half-set convention)
# ---------------------------------------------------------------------------
# Under the 176-Laplacian half-set convention the registered chain length is
# 2*N_d = 88 and the spectral sum is 178, so the same *structural role* gives
# different integers.  A candidate that only works in one convention is
# convention-fragile.
cand_conv = {
    "C_energy (44-chain)": mu2 / (2 * N_d + mu2),
    "C_energy (176 half-set, mu^2/(sum+mu^2))": mu2 / (178.0 + mu2),
    "1/(N_d+B+mu^2) (44-chain)": 1.0 / (N_d + B + mu2),
    "1/(2N_d+B+mu^2) (176 convention)": 1.0 / (2 * N_d + B + mu2),
}
print("-" * 78)
for k, v in cand_conv.items():
    print("  %-42s = %.6f  (dev %.2f%%)" % (k, v, abs(v - TARGET) / TARGET * 100))
conv_dev = {k: abs(v - TARGET) / TARGET for k, v in cand_conv.items()}
swapped = {k: d for k, d in conv_dev.items() if "176" in k}
check("R3 re-expressing the 2%-scale candidates in the 176 half-set convention destroys them",
      all(d > 0.05 for d in swapped.values()),
      "176-convention devs: %s" % ", ".join("%s = %.1f%%" % (k.split("(")[0].strip(), d * 100)
                                            for k, d in swapped.items()))

# ---------------------------------------------------------------------------
# (iii) discrimination power: how many TDEs to separate the candidates?
# ---------------------------------------------------------------------------
cands = {"1/50 = 2.000%": 1.0 / 50.0, "1/45 = 2.222%": 1.0 / 45.0, "1/44 = 2.273%": 1.0 / 44.0}
keys = list(cands)
print("-" * 78)
print("  pairwise separation and required per-source scatter / sample size:")
disc = {}
for i in range(len(keys)):
    for j in range(i + 1, len(keys)):
        a, b = cands[keys[i]], cands[keys[j]]
        rel = abs(a - b) / ((a + b) / 2.0)
        # 3-sigma separation of two means with per-source fractional scatter s:
        #   N = (2 s / (rel/3))^2  ~ (6 s / rel)^2
        rows = {}
        for s in (0.30, 0.50, 0.80):
            N_req = (6.0 * s / rel) ** 2
            rows["s=%.2f" % s] = N_req
        disc["%s vs %s" % (keys[i], keys[j])] = {"rel_sep": rel, "N_required": rows}
        print("    %s vs %s : relative separation %.2f%% -> N(3sigma) = %s"
              % (keys[i], keys[j], rel * 100,
                 ", ".join("%s: %.0f" % (k, v) for k, v in rows.items())))

worst = max(d["N_required"]["s=0.50"] for d in disc.values())
best = min(d["N_required"]["s=0.50"] for d in disc.values())
check("R4 current 10-source sample cannot separate any candidate pair at 3 sigma",
      best > 10.0, "smallest requirement N = %.0f sources for s = 0.50 (have 10)" % best)
check("R5 the 1/50-vs-forced-pair question is decidable with N ~ 600-800 sources, "
      "but the 1/45-vs-1/44 pair is not (N ~ 1.8e4)",
      disc["1/50 = 2.000% vs 1/44 = 2.273%"]["N_required"]["s=0.50"] < 1000.0 and
      disc["1/45 = 2.222% vs 1/44 = 2.273%"]["N_required"]["s=0.50"] > 10000.0,
      "1/50 vs 1/44: N = %.0f ; 1/45 vs 1/44: N = %.0f (s = 0.50)"
      % (disc["1/50 = 2.000% vs 1/44 = 2.273%"]["N_required"]["s=0.50"],
         disc["1/45 = 2.222% vs 1/44 = 2.273%"]["N_required"]["s=0.50"]))

# ---------------------------------------------------------------------------
# (iv) threshold-vs-dictionary classification
# ---------------------------------------------------------------------------
print("-" * 78)
print("  classification of the three 2%-scale candidates:")
cls = [
    ("1/45 = C_energy", "spectral invariant (Z2 sector capacity asymmetry), unique expression",
     "FORCED FORM (no dictionary choice)", 1.0 / 45.0),
    ("1/44 = mu^2/(2N_d)", "spectral invariant (2 phase slips per ring period), unique expression",
     "FORCED FORM (no dictionary choice)", 1.0 / 44.0),
    ("1/50 = 1/(N_d+B+mu^2)", "integer sum with >= %d decompositions in the pool" % d50_2,
     "DICTIONARY HIT (choice of decomposition)", 1.0 / 50.0),
]
for name, why, klass, val in cls:
    print("    %-22s %-10s %s" % (name, "%.4f%%" % (val * 100), klass))
    print("      reason: %s" % why)

check("R6 the two forced forms (1/45, 1/44) both miss the quoted value by > 10%",
      abs(1.0 / 45.0 - TARGET) / TARGET > 0.10 and abs(1.0 / 44.0 - TARGET) / TARGET > 0.10,
      "1/45 dev %.2f%% ; 1/44 dev %.2f%%"
      % (abs(1.0 / 45.0 - TARGET) / TARGET * 100, abs(1.0 / 44.0 - TARGET) / TARGET * 100))
check("R7 the only exact hits are dictionary hits",
      min(abs(v - TARGET) for v in (1.0 / 45.0, 1.0 / 44.0)) > 0.0 and abs(1.0 / 50.0 - TARGET) < 1e-15,
      "1/50 exact but dictionary-classified")

out = {
    "dictionary_size": {"50_2term": d50_2, "50_3term": d50_3, "45_2term": d45_2, "44_2term": d44_2,
                        "examples_50_2term": ex50_2, "examples_50_3term": ex50_3,
                        "examples_45_2term": ex45_2, "examples_44_2term": ex44_2},
    "convention_swap": cand_conv,
    "discrimination": disc,
    "classification": [{"candidate": c[0], "why": c[1], "class": c[2], "value": c[3]} for c in cls],
}
os.makedirs(DATA, exist_ok=True)
with open(os.path.join(DATA, "05_rigidity_dof.json"), "w") as fh:
    json.dump(out, fh, indent=2)

n_pass = sum(1 for r in results if r["pass"])
print("=" * 78)
print("TOTAL: %d/%d PASS" % (n_pass, len(results)))
print("wrote data/05_rigidity_dof.json")
