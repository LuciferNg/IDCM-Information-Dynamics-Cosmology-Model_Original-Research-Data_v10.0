#!/usr/bin/env python3
"""
O62 十期 59: 真正 25 anomaly — 唔涉 point 36
==============================================
anomaly 54 = 25 (kappa divisors 內) + 29 (涉 point 36)
point 36 = -point 8 (L₇ 反點) — 唔係 kappa divisor

真正 25 anomaly (0-35 內) 嘅結構:
  1. 佢哋全部有共同 edge 但列 SR
  2. edge star 幾多?
  3. 對應 κ 值 (兩同 index)
"""
import sys, os, json
import numpy as np
from itertools import combinations

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")

print("=" * 72)
print("O62 十期 59: 真正 25 anomaly")
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

d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
simplices = d["simplices"]
sr_sage = d["sr_ideal"]
kappa36 = np.array(json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))["kappa"])[:36,:36,:36]

faces_1d = set()
for s in simplices:
    for e in combinations(s, 2):
        faces_1d.add(tuple(sorted(e)))
no_edge = set()
for i in range(36):
    for j in range(i+1, 36):
        if (i, j) not in faces_1d:
            no_edge.add((i, j))
sr_set = set(tuple(sorted(p)) for p in sr_sage)
# anomaly 只睇 kappa divisors (0-35)
anomaly = sorted((sr_set - no_edge) & set(combinations(range(36), 2)))
print(f"[1] 真正 anomaly (0-35): {len(anomaly)}")
print(f"  {anomaly}")

# ============ 1. 每個 anomaly 嘅 edge star + κ ============
print("\n[2] anomaly 結構")
for (i, j) in anomaly:
    n_simp = sum(1 for s in simplices if i in set(s) and j in set(s))
    k_iij = kappa36[i, i, j]
    k_ijj = kappa36[i, j, j]
    print(f"  ({i:2d},{j:2d}): star={n_simp:2d}, κ_iij={k_iij:6.1f}, κ_ijj={k_ijj:6.1f}")

# ============ 2. 特徵分析 ============
print("\n[3] 特徵")
# 邊啲點出現?
from collections import Counter
pt_count = Counter()
for (i, j) in anomaly:
    pt_count[i] += 1
    pt_count[j] += 1
print(f"  點出現次數: {dict(sorted(pt_count.items()))}")

# 高-star 點 (動態 7)?
high7 = {0, 6, 12, 14, 17, 30, 32}
anom_pts = set()
for (i, j) in anomaly:
    anom_pts.add(i); anom_pts.add(j)
print(f"  涉及點: {sorted(anom_pts)}")
print(f"  同 7 動態重疊: {sorted(anom_pts & high7)}")
print(f"  唔係 7 動態: {sorted(anom_pts - high7)}")

# ============ 3. 共同模式 ============
print("\n[4] 共同模式")
# anomaly 全部係「兩同」→ κ_iij 同 κ_ijj
# 檢查: κ_iij + κ_ijj = 0?
tot = 0
for (i, j) in anomaly:
    tot += kappa36[i, i, j] + kappa36[i, j, j]
print(f"  Σ(κ_iij + κ_ijj) = {tot}")

# ============ 4. 總結 ============
print("\n" + "=" * 72)
print("十期 59 總結:")
print("=" * 72)
out = {
    "test": "O62 十期 59: 真正 anomaly",
    "anomaly": anomaly,
    "pt_count": {str(k): v for k, v in sorted(pt_count.items())},
    "high7_overlap": sorted(anom_pts & high7),
    "sum_k": float(tot),
    "passed": passed, "failed": failed
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "59_true_anomaly25.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 十期 59 完成!")
