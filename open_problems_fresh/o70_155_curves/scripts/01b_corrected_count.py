#!/usr/bin/env python3
"""
O70 — 01b: 校正 155 Curves 計數（0-based vs 1-based bug 修正）
==============================================================
問題: 原始 O57 scripts/29 用 range(1,37) 但 sr_ideal 用 0-based index
      → 實際 adjacency = 184 唔係 155

需要釐清:
  1. 真正嘅 155 係咩? (問題記錄話 155 = 2×73+9)
  2. 184 有咩結構意義? (184 = ?)
  3. 155 同 184 嘅關係
  4. 155 條 curve 嘅定義: 係咪 subset of 184?
"""

import sys, os, math
import json
import numpy as np
from collections import Counter

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O70 01b: 校正 155 Curves 計數")
print("=" * 72)

d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
sr = d["sr_ideal"]
points = d["points"]
n_points = len(points)
print(f"Points: {n_points}")
print(f"sr_ideal total: {len(sr)}")

# 1. Check the actual involved point indices
all_idx = set()
for s in sr:
    all_idx.update(s)
involved = sorted(all_idx)
uninvolved = sorted(set(range(n_points)) - all_idx)
print(f"\n[1] Involved points: {involved}")
print(f"    Count: {len(involved)}")
print(f"    Uninvolved: {uninvolved}")
print(f"    Count: {len(uninvolved)}")

# 2. Check what the sr_ideal pairs actually look like
print(f"\n[2] Sample sr_ideal pairs (first 20):")
for s in sr[:20]:
    print(f"    ({s[0]}, {s[1]})")

# 3. Count sr_ideal pairs that are within the 36 involved points
print(f"\n[3] sr_ideal within 36 points vs involving uninvolved")
sr_within = set()
sr_cross = []
for s in sr:
    i, j = min(s), max(s)
    if i in involved and j in involved:
        sr_within.add((i, j))
    else:
        sr_cross.append((i, j))

print(f"  sr_ideal within 36 points: {len(sr_within)}")
print(f"  sr_ideal involving uninvolved: {len(sr_cross)}")
print(f"  Total unique within: {len(sr_within)}")
print(f"  Duplicates within: {len(sr) - len(sr_within) - len(sr_cross)}")

# 4. Count adjacency among the 36 involved points
print(f"\n[4] Adjacency among 36 involved points")
C36_2 = len(involved) * (len(involved) - 1) // 2
print(f"  C(36,2) = {C36_2}")
adj = C36_2 - len(sr_within)
print(f"  Adjacency = {C36_2} - {len(sr_within)} = {adj}")
print(f"  155 = 2×73+9")

# 5. Check duplicate sr_ideal pairs
print(f"\n[5] Duplicate analysis")
sr_count = Counter()
for s in sr:
    sr_count[(min(s), max(s))] += 1
dups = {k: v for k, v in sr_count.items() if v > 1}
print(f"  Duplicate pairs: {len(dups)}")
for k, v in sorted(dups.items()):
    print(f"    ({k[0]}, {k[1]}): {v} times")

# 6. The 155 from the problem record — what is it?
print(f"\n[6] What is the '155' in the problem record?")
print(f"  Option A: 155 = 2×73+9, where 73 = ?")
print(f"  Option B: 155 = total unique curves in the toric variety")
print(f"  Option C: 155 = something else")

# Check the CYTools curve_basis
print(f"\n  Checking CYTools curve_basis count...")
try:
    import cytools
    from cytools import Polytope
    from cytools.config import enable_experimental_features
    enable_experimental_features()
    pts = np.array(d["points"])
    p = Polytope(pts)
    tri = p.triangulate()
    cy = tri.get_cy()
    n_curves = len(cy.curve_basis())
    print(f"  CYTools curve_basis: {n_curves}")
    check_155 = (n_curves == 155)
    print(f"  {'✅' if check_155 else '❌'} curve_basis = 155")
except Exception as e:
    print(f"  ⚠️ CYTools error: {e}")

# 7. Check the 184 adjacency structure
print(f"\n[7] 184 adjacency structure")
print(f"  184 = 630 - 446 (sr_within)")
print(f"  184 = C(36,2) - (484 - 38) = 630 - 446")
print(f"  184 = ?")
print(f"  184 = 2×92 = 2×(?)")
print(f"  184 = 44 + 140? 140 = 2×70?")
print(f"  184 = 90 + 94?")
print(f"  184 = 4×46 = B×46?")
print(f"  184 = 2×73 + 38 = 146 + 38")
print(f"  38 = 2×19 = 2×L₅?")
print(f"  38 = 44 - 6 = Nd - 6?")
print(f"  38 = 36 + 2 = h11 + 2?")
print(f"  38 = ?")

# The 38 pairs that involve uninvolved points
print(f"\n  Cross pairs structure:")
cross_set = set()
for i, j in sr_cross:
    cross_set.add((min(i,j), max(i,j)))
print(f"  Unique cross pairs: {len(cross_set)}")
for i, j in sorted(cross_set):
    in_a = i in involved
    in_b = j in involved
    print(f"    ({i}, {j}): {'involved' if in_a else 'uninvolved'} × {'involved' if in_b else 'uninvolved'}")

# 8. The real 155 from the problem record
print(f"\n[8] The real '155' in the problem")
print(f"  The problem says '155 curves' and '155 = 2×73+9'")
print(f"  But the actual adjacency is 184")
print(f"  Possible interpretations:")
print(f"  1. 155 = subset of 184 that are 'special' (nonzero volume?)")
print(f"  2. 155 = something from toric geometry (CYTools curve_basis?)")
print(f"  3. 155 = 185 - 30 (total curves minus C sector?)")
print(f"  4. The 1-based bug in script 29 accidentally selected 155 specific pairs")
print(f"     that coincidentally have structural meaning")

results = {
    "test": "O70 01b: Corrected 155 Counting",
    "sr_total": len(sr),
    "sr_within_36": len(sr_within),
    "sr_cross_uninvolved": len(sr_cross),
    "adjacency_36": adj,
    "adjacency_1based_bug": 155,  # from O57 script 29 bug
    "involved_count": len(involved),
    "uninvolved_count": len(uninvolved),
    "cross_set_unique": len(cross_set),
}
with open(os.path.join(os.path.dirname(__file__), "..", "data", "01b_corrected_count.json"), "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nResults saved to data/01b_corrected_count.json")