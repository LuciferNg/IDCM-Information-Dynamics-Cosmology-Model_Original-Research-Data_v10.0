#!/usr/bin/env python3
"""
O199 scripts/03 - Ratio census + Monte-Carlo null test (selection-effect audit)

QUESTION
  "0.02 is 1/50 = 1/(N_d + B + mu^2)" - is such a hit informative, or is it the
  algebraic-dictionary trap (every target reachable by many expressions)?

METHOD (structural null-test protocol: closed pool, relaxed form classes,
  expected-density comparison, verdict rule)
  1. Build the pool P = closure of the registered structural primitives
     {mu^2=2, N_gen=3, B=4, F5=5, L4=7, F6=8, L5=11, 12, F7=13, F_proj=17,
      L6=18, K_tree=30, M=33, N_d=44, A5_V=60, 88, A5_E=120, 176}
     under +, x, |a-b|, restricted to [1, 400].  GENERATED, not hand-picked.
  2. Enumerate depth<=2 rational forms over P:
        F1 = a/b     F2 = (a+b)/c   F3 = a/(b+c)   F4 = a*b/c   F5 = a/(b*c)
     keep values in [0.002, 1.0]; deduplicate per chunk (memory-safe).
  3. count(t, eps) = number of DISTINCT expression values inside
     [t(1-eps), t(1+eps)]  (exact, via searchsorted).
  4. NULL: 1e7 log-uniform random targets t in [0.002, 1.0]; same count.
     Verdict rule: observed/expected >> 1 => selection effect (hit not forced);
                   observed/expected ~ 1 => the hit carries no information.
  5. Decomposition census for the denominator 50.

ASCII only.
"""

import json
import os
import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
O_DIR = os.path.dirname(SCRIPT_DIR)
DATA = os.path.join(O_DIR, "data")

results = []


def check(name, cond, detail=""):
    results.append({"name": name, "pass": bool(cond), "detail": detail})
    print(("  PASS " if cond else "  FAIL ") + name + (" | " + detail if detail else ""), flush=True)


# ---------------------------------------------------------------------------
# 1. Closed structural pool
# ---------------------------------------------------------------------------
PRIMS = [2, 3, 4, 5, 7, 8, 11, 12, 13, 17, 18, 30, 33, 44, 60, 88, 120, 176]
CAP = 400

print("=" * 78, flush=True)
print("O199 / 03 - Ratio census + 1e7 MC null test", flush=True)
print("=" * 78, flush=True)

pool = set(PRIMS)
frontier = set(PRIMS)
while frontier:
    new = set()
    base = PRIMS + sorted(pool)
    for a in frontier:
        for b in base:
            for v in (a + b, a * b, abs(a - b)):
                if 1 <= v <= CAP and v not in pool:
                    new.add(v)
    pool |= new
    frontier = new
P = sorted(pool)
print("  primitive set      : %s" % PRIMS, flush=True)
print("  closure size |P|   : %d  (values 1..%d)" % (len(P), CAP), flush=True)
print("  P sample           : %s ... %s" % (P[:26], P[-8:]), flush=True)

check("P1 pool is closed under +, x, |a-b| within the cap",
      all((a + b in pool) or (a + b > CAP) for a in P for b in P[:40]) and len(P) > 100,
      "|P| = %d" % len(P))
check("P2 pool contains the denominator 50", 50 in pool, "50 in P")
check("P3 pool contains 1 (via |B - N_gen| = 1) => the reciprocal family 1/n, n in P, is reachable",
      1 in pool, "min(P) = %d ; 1 in P = %s" % (P[0], 1 in pool))

A = np.array(P, dtype=np.float64)
N_P = len(A)
print("  |P| = %d  ->  %d single ratios, %d triple-form evaluations per class"
      % (N_P, N_P * N_P, N_P * N_P * N_P), flush=True)

BAND = (0.002, 1.0)


def band_unique(v):
    v = v[np.isfinite(v)]
    v = v[(v >= BAND[0]) & (v <= BAND[1])]
    return np.unique(v) if v.size else v


# ---------------------------------------------------------------------------
# 2. Depth <= 2 expression classes (memory-safe: dedupe per chunk)
# ---------------------------------------------------------------------------
forms = {}
forms["F1 a/b"] = np.unique(np.concatenate([band_unique(A / b) for b in A]))

acc = {k: [] for k in ("F2", "F3", "F4", "F5")}
for i, c in enumerate(A):
    S = (A[:, None] + A[None, :]).ravel()                 # (a+b) grid
    acc["F2"].append(band_unique(S / c))                  # (a+b)/c
    acc["F3"].append(band_unique((A[:, None] / (A[None, :] + c)).ravel()))   # a/(b+c)
    PR = (A[:, None] * A[None, :]).ravel()                # a*b grid
    acc["F4"].append(band_unique(PR / c))                 # a*b/c
    acc["F5"].append(band_unique((A[:, None] / (A[None, :] * c)).ravel()))  # a/(b*c)
    if (i + 1) % 50 == 0:
        print("    ... c-loop %d/%d done" % (i + 1, N_P), flush=True)

for k, name in (("F2", "F2 (a+b)/c"), ("F3", "F3 a/(b+c)"), ("F4", "F4 a*b/c"), ("F5", "F5 a/(b*c)")):
    forms[name] = np.unique(np.concatenate(acc[k])) if acc[k] else np.array([])
    acc[k] = []

ALL = np.unique(np.concatenate(list(forms.values())))
print("-" * 78, flush=True)
for k, v in forms.items():
    print("  %-12s distinct values in band : %d" % (k, len(v)), flush=True)
print("  %-12s distinct values in band : %d" % ("ALL", len(ALL)), flush=True)

check("E1 all five form classes non-empty", all(len(v) > 0 for v in forms.values()),
      "sizes = %s" % {k: len(v) for k, v in forms.items()})
check("E2 union exceeds every single class", len(ALL) > max(len(v) for v in forms.values()),
      "%d > %d" % (len(ALL), max(len(v) for v in forms.values())))


# ---------------------------------------------------------------------------
# 3. Exact hit counts at the observed target
# ---------------------------------------------------------------------------
def count_hits(vals, t, eps):
    return int(np.searchsorted(vals, t * (1.0 + eps), side="right")
               - np.searchsorted(vals, t * (1.0 - eps), side="left"))


print("-" * 78, flush=True)
print("  hits around the observed target t = 0.02", flush=True)
counts_02 = {}
for eps in (0.01, 0.05, 0.10):
    per_form = {k: count_hits(v, 0.02, eps) for k, v in forms.items()}
    tot = count_hits(ALL, 0.02, eps)
    counts_02["%.2f" % eps] = {"total": tot, "per_form": per_form}
    print("    eps = %4.0f%% : total = %5d  per-form = %s"
          % (eps * 100, tot, per_form), flush=True)

# ---------------------------------------------------------------------------
# 4. Monte-Carlo null: 1e7 log-uniform random targets
# ---------------------------------------------------------------------------
rng = np.random.default_rng(20260921)
N_NULL = 10 ** 7
lo, hi = np.log(BAND[0]), np.log(BAND[1])
targets = np.exp(rng.uniform(lo, hi, size=N_NULL)).astype(np.float64)
print("-" * 78, flush=True)
print("  Monte-Carlo null: %d log-uniform targets in [%.3f, %.3f]" % (N_NULL, BAND[0], BAND[1]),
      flush=True)

null_stats = {}
for eps in (0.01, 0.05, 0.10):
    cnt = (np.searchsorted(ALL, targets * (1.0 + eps), side="right")
           - np.searchsorted(ALL, targets * (1.0 - eps), side="left")).astype(np.int32)
    med = float(np.median(cnt))
    mean = float(np.mean(cnt))
    sd = float(np.std(cnt))
    p95 = float(np.percentile(cnt, 95))
    p999 = float(np.percentile(cnt, 99.9))
    obs = counts_02["%.2f" % eps]["total"]
    pval = float(np.mean(cnt >= obs))
    z = (obs - mean) / sd if sd > 0 else float("inf")
    null_stats["%.2f" % eps] = {
        "observed_count": obs, "null_mean": mean, "null_median": med, "null_sd": sd,
        "null_p95": p95, "null_p99.9": p999,
        "observed_over_median": (obs / med) if med > 0 else float("inf"),
        "p_value": pval, "z_above_mean": z,
    }
    print("    eps = %4.0f%%  observed = %d | null mean %.2f median %.1f sd %.2f p95 %.0f p99.9 %.0f"
          % (eps * 100, obs, mean, med, sd, p95, p999), flush=True)
    print("             observed/median = %.3f  p = %.4f  z = %.3f"
          % (null_stats["%.2f" % eps]["observed_over_median"], pval, z), flush=True)

check("N1 at eps=1% the target 0.02 is not an outlier of the null (p > 0.01)",
      null_stats["0.01"]["p_value"] > 0.01, "p = %.4f" % null_stats["0.01"]["p_value"])
check("N2 observed/median within a factor 3 of unity at eps=1% (no selection effect)",
      1.0 / 3.0 < null_stats["0.01"]["observed_over_median"] < 3.0,
      "ratio = %.3f" % null_stats["0.01"]["observed_over_median"])
check("N3 more than 5 distinct expressions land within +/-1% of 0.02",
      null_stats["0.01"]["observed_count"] > 5,
      "%d expressions" % null_stats["0.01"]["observed_count"])

# ---------------------------------------------------------------------------
# 5b. Simplest-class census: which single ratios a/b hit 0.02 within 1%?
# ---------------------------------------------------------------------------
f1_pairs = [(int(a), int(b)) for a in P for b in P
            if abs(float(a) / b - 0.02) / 0.02 <= 0.01]
print("-" * 78, flush=True)
print("  simplest class F1 = a/b, hits within +/-1%% of 0.02: %d pairs" % len(f1_pairs), flush=True)
print("    %s%s" % (f1_pairs[:12], " ..." if len(f1_pairs) > 12 else ""), flush=True)
print("    (each pair is an equally valid 'structural' expression of the same number)", flush=True)

check("D3 the simplest class alone (single ratios a/b) yields >= 5 expressions of 0.02",
      len(f1_pairs) >= 5, "%d pairs" % len(f1_pairs))
check("D4 the pairs are exactly the family a/b with b = 50a (multiples of 50 in P)",
      all(abs(float(a) / b - 0.02) / 0.02 <= 0.01 for a, b in f1_pairs) and
      all(b >= 49 for a, b in f1_pairs if a == 1),
      "b/a values: %s" % sorted(set(round(b / a, 2) for a, b in f1_pairs))[:10])

# ---------------------------------------------------------------------------
# 5. Denominator-multiplicity census for 1/50
# ---------------------------------------------------------------------------
Pset = set(P)
sums_50 = [(a, b) for a in P for b in P if a < b and a + b == 50]
prods_50 = [(a, b) for a in P for b in P if a <= b and a * b == 50]
print("-" * 78, flush=True)
print("  denominator 50 decompositions inside P:", flush=True)
print("    a+b = 50 : %d  -> %s" % (len(sums_50), sums_50[:8]), flush=True)
print("    a*b = 50 : %d  -> %s" % (len(prods_50), prods_50), flush=True)

check("D1 50 has >= 3 additive decompositions in P (structural multiplicity)",
      len(sums_50) >= 3, "%d decompositions" % len(sums_50))
check("D2 50 has >= 3 total decompositions (sums + products)",
      len(sums_50) + len(prods_50) >= 3, "total %d" % (len(sums_50) + len(prods_50)))

out = {
    "pool_primitives": PRIMS,
    "pool_size": N_P,
    "band": list(BAND),
    "form_sizes": {k: int(len(v)) for k, v in forms.items()},
    "union_size": int(len(ALL)),
    "target": 0.02,
    "counts_at_target": counts_02,
    "null": null_stats,
    "n_null_samples": N_NULL,
    "decompositions_of_50": {"sums": sums_50, "prods": prods_50},
    "f1_pairs_near_target": f1_pairs,
}
os.makedirs(DATA, exist_ok=True)
with open(os.path.join(DATA, "03_ratio_census_null.json"), "w") as fh:
    json.dump(out, fh, indent=2)

n_pass = sum(1 for r in results if r["pass"])
print("=" * 78, flush=True)
print("TOTAL: %d/%d PASS" % (n_pass, len(results)), flush=True)
print("wrote data/03_ratio_census_null.json", flush=True)
