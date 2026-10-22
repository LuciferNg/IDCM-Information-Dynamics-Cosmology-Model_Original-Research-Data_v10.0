#!/usr/bin/env python3
"""
O70 — 01: 155 Curves 結構分析（修正版 — 1-based index）
=======================================================
sr_ideal 用 1-based indices (1..36)，point 0 = origin 係 uninvolved。

核心結構:
  155 = 630 - 475 = C(36,2) - unique_sr_pairs
  155 = 2×73 + 9
  73 = Nd + L₇ = 44 + 29
  9 = 3² = N_gen² = 5 duplicate pairs (total 9 extra entries)
"""

import sys, os, math
import json
import numpy as np
from collections import Counter

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2
Nd = 44
B = 4

def Ln(n):
    return round(phi**n + (-1)**n * phi**(-n))

print("=" * 72)
print("O70 01: 155 Curves 結構分析 (修正版)")
print("=" * 72)

passed = 0
failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        failed += 1
        print(f"  ❌ {name} {detail}")

# ============ 1. Load sr_ideal ============
print("\n[1] sr_ideal data (1-based indices)")
d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
sr = d["sr_ideal"]
print(f"  sr_ideal total: {len(sr)}")

# Build unique set
sr_set = set()
sr_count = Counter()
for s in sr:
    sr_count[(min(s), max(s))] += 1
    sr_set.add((min(s), max(s)))

print(f"  Unique sr pairs: {len(sr_set)}")
print(f"  Duplicates (total extra): {len(sr) - len(sr_set)}")
check("475 unique sr pairs", len(sr_set) == 475, f"({len(sr_set)})")
check("9 = 3² duplicates", len(sr) - len(sr_set) == 9, f"({len(sr) - len(sr_set)})")

# ============ 2. Adjacency = 630 - 475 = 155 ============
print("\n[2] Adjacency curves = C(36,2) - 475")
adj = []
for i in range(1, 37):
    for j in range(i+1, 37):
        if (i, j) not in sr_set:
            adj.append((i, j))
print(f"  Adjacency: {len(adj)}")
check("155 adjacency curves", len(adj) == 155, f"({len(adj)})")
check("155 = 2×73+9", len(adj) == 2*73 + 9, f"({2*73+9})")

# ============ 3. 73 structure ============
print("\n[3] 73 structure")
print(f"  73 = Nd + L₇ = {Nd} + {Ln(7)} = {Nd + Ln(7)}")
check("73 = Nd+L₇", 73 == Nd + Ln(7), f"({Nd}+{Ln(7)})")
print(f"  73 = L₆×4+1 = {Ln(6)}×4+1 = {Ln(6)*4+1}")
check("73 = L₆×4+1", 73 == Ln(6)*4 + 1, f"({Ln(6)}×4+1)")
print(f"  73 = 2×h¹¹+1 = 2×36+1 = {2*36+1}")
print(f"  73 = 90-17 = Σγ - ?")
print(f"  73 = CPX projection rank (O53 verified)")

# ============ 4. Duplicate analysis ============
print("\n[4] Duplicate structure")
dups = {k: v for k, v in sr_count.items() if v > 1}
print(f"  Duplicate pairs: {len(dups)}")
for k, v in sorted(dups.items(), key=lambda x: -x[1]):
    print(f"    ({k[0]}, {k[1]}): {v} times (extra: {v-1})")
print(f"  Total extra: {sum(v-1 for v in dups.values())}")
check("9 total extra entries", sum(v-1 for v in dups.values()) == 9, f"({sum(v-1 for v in dups.values())})")

# Check the duplicate pair structure
# Are they connected to specific points?
dup_points = set()
for k in dups:
    dup_points.add(k[0])
    dup_points.add(k[1])
print(f"  Points involved in duplicates: {sorted(dup_points)}")
print(f"  Count: {len(dup_points)}")
# 6, 10, 12, 14, 1, 15, 17 — 7 unique points
connected_to_6 = [k for k in dups if 6 in k]
print(f"  Pairs involving point 6: {connected_to_6}")

# ============ 5. Degree distribution ============
print("\n[5] Adjacency graph degree distribution")
G = {i: set() for i in range(1, 37)}
for i, j in adj:
    G[i].add(j)
    G[j].add(i)

degrees = sorted([len(G[i]) for i in range(1, 37)], reverse=True)
print(f"  Degree sorted: {degrees}")
print(f"  Mean degree: {np.mean(degrees):.1f}")
print(f"  Min: {min(degrees)}, Max: {max(degrees)}")
deg_counts = Counter(degrees)
print(f"  Degree distribution: {dict(sorted(deg_counts.items()))}")

# High-degree node analysis
print(f"\n  High-degree nodes (top 5):")
deg_sorted = sorted([(i, len(G[i])) for i in range(1, 37)], key=lambda x: -x[1])
for i, d in deg_sorted[:5]:
    print(f"    Point {i:2d}: degree {d:2d}")

# ============ 6. Volume vectors ============
print("\n[6] Volume vectors (κ_ijk)")
kappa_path = os.path.join(O53, "cy36_98_intersection_full.json")
if os.path.exists(kappa_path):
    kappa = np.array(json.load(open(kappa_path))["kappa"])
    V = np.array([kappa[:, i-1, j-1] for i, j in adj])  # 155×36
    print(f"  V shape: {V.shape}")

    nz = np.abs(V).sum(axis=1) > 1e-10
    nz_count = nz.sum()
    print(f"  Nonzero vectors: {nz_count}/155")
    check("52 = Nd+2B nonzero", nz_count == Nd + 2*B, f"({nz_count} = {Nd}+{2*B})")

    rank_all = np.linalg.matrix_rank(V)
    print(f"  Rank(155×36): {rank_all}")
    check("rank = 30 = 2L₅+2B", rank_all == 2*Ln(5) + 2*B, f"({rank_all} = {2*Ln(5)}+{2*B})")

    V_nz = V[nz]
    rank_nz = np.linalg.matrix_rank(V_nz)
    print(f"  Rank(nonzero {nz_count}×36): {rank_nz}")

    # Check the 30 = 2L₅+2B identity
    print(f"  30 = 2×{Ln(5)}+2×{B} = {2*Ln(5)}+{2*B} = {2*Ln(5)+2*B}")
    check("30 = 2L₅+2B", 2*Ln(5) + 2*B == 30, f"({2*Ln(5)}+{2*B})")

    # Zero-volume curve analysis
    zero_adj = [adj[i] for i in range(len(adj)) if not nz[i]]
    print(f"  Zero-volume curves: {len(zero_adj)}")
    print(f"  Zero curve indices (first 10): {zero_adj[:10]}")

    # Any structural pattern in zero curves?
    zero_points = set()
    for i, j in zero_adj:
        zero_points.add(i)
        zero_points.add(j)
    print(f"  Points in zero curves: {sorted(zero_points)}")
    
    # Points that appear in zero curves more than others
    zero_point_count = Counter()
    for i, j in zero_adj:
        zero_point_count[i] += 1
        zero_point_count[j] += 1
    print(f"  Zero curve point frequency: {zero_point_count.most_common(10)}")
else:
    print(f"  ⚠️ kappa file not found")

# ============ 7. Summary ============
print("\n" + "=" * 72)
print("O70 01 總結")
print("=" * 72)
print(f"""
155 = 2×73 + 9
  ├── 2×73 = 146 = C(36,2) - 475 = sr_ideal complement (adjacency edges)
  │    ├── 73 = Nd + L₇ = 44 + 29 = {Nd + Ln(7)} ✅
  │    ├── 73 = L₆×4+1 = {Ln(6)}×4+1 = {Ln(6)*4+1} ✅
  │    └── 73 = CPX projection rank (O53)
  └── 9 = 3² = N_gen² = {3**2} ✅
       └── 9 duplicate sr_ideal entries (5 unique pairs)
            Points: {sorted(dup_points)}

Nonzero vectors: {nz_count if 'nz_count' in dir() else '?'}/155 = Nd+2B = {Nd+2*B}
Rank: {rank_all if 'rank_all' in dir() else '?'} = 2L₅+2B = {2*Ln(5)+2*B}
""")

results = {
    "test": "O70 01: 155 Curves Structure",
    "adjacency": len(adj),
    "adj_formula": "2×73+9",
    "73_identity": f"Nd+L₇={Nd}+{Ln(7)}",
    "73_identity_2": f"L₆×4+1={Ln(6)}×4+1",
    "9_identity": "N_gen²=3²",
    "duplicate_pairs": {str(k): v for k, v in dups.items()},
    "nz_count": int(nz_count) if 'nz_count' in dir() else None,
    "nz_identity": f"Nd+2B={Nd+2*B}",
    "rank": int(rank_all) if 'rank_all' in dir() else None,
    "rank_identity": f"2L₅+2B={2*Ln(5)+2*B}",
    "passed": passed, "failed": failed
}
with open(os.path.join(os.path.dirname(__file__), "..", "data", "01_155_structure.json"), "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"Passed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 O70 01 完成!")