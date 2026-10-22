#!/usr/bin/env python3
"""
O62 十期 62: anomaly 共同 simplex 含 div0? 驗證
=================================================
hypothesis: anomaly pairs 嘅共同 simplex 全部含 point 0 (div0)
  → 相交只經 div0 → 唔係「本質」相交 → SR

驗證 + 對照 (正常 pairs)
"""
import sys, os, json
import numpy as np
from itertools import combinations

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")

print("=" * 72)
print("O62 十期 62: anomaly div0 假設")
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
sr_set = set(tuple(sorted(p)) for p in sr_sage)

faces_1d = set()
for s in simplices:
    for e in combinations(s, 2):
        faces_1d.add(tuple(sorted(e)))
no_edge = set()
for i in range(36):
    for j in range(i+1, 36):
        if (i, j) not in faces_1d:
            no_edge.add((i, j))
anomaly = sorted((sr_set - no_edge) & set(combinations(range(36), 2)))

print(f"[1] anomaly 共同 simplex 含 div0?")
anom_has_div0 = []
anom_no_div0 = []
for (i, j) in anomaly:
    common = [s for s in simplices if i in set(s) and j in set(s)]
    all_has_0 = all(0 in set(s) for s in common)
    if all_has_0:
        anom_has_div0.append((i, j))
    else:
        anom_no_div0.append((i, j))
print(f"  全部共同 simplex 含 div0: {len(anom_has_div0)}")
print(f"  有唔含 div0: {len(anom_no_div0)}")
if anom_no_div0:
    print(f"    {anom_no_div0}")

# ============ 1. 對照: 正常 pairs (edge, 非SR) ============
print("\n[2] 對照: 正常 pairs")
normal = []
for i in range(36):
    for j in range(i+1, 36):
        if (i, j) in faces_1d and (i, j) not in sr_set:
            normal.append((i, j))
norm_div0 = []
norm_no_div0 = []
for (i, j) in normal:
    common = [s for s in simplices if i in set(s) and j in set(s)]
    all_has_0 = all(0 in set(s) for s in common)
    if all_has_0:
        norm_div0.append((i, j))
    else:
        norm_no_div0.append((i, j))
print(f"  正常 pairs: {len(normal)}")
print(f"  全部含 div0: {len(norm_div0)}")
print(f"  有唔含 div0: {len(norm_no_div0)}")

# ============ 2. 統計 ============
print("\n[3] 統計")
print(f"  anomaly: 全部含 div0 {len(anom_has_div0)}/{len(anomaly)}")
print(f"  正常: 全部含 div0 {len(norm_div0)}/{len(normal)}")

# ============ 3. 總結 ============
print("\n" + "=" * 72)
print("十期 62 總結:")
print("=" * 72)
out = {
    "test": "O62 十期 62: div0 假設",
    "anom_has_div0": len(anom_has_div0), "anom_no_div0": anom_no_div0,
    "norm_has_div0": len(norm_div0), "norm_no_div0": len(norm_no_div0),
    "passed": passed, "failed": failed
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "62_div0.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 十期 62 完成!")
