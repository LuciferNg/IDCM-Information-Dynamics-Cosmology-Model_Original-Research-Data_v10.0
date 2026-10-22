#!/usr/bin/env python3
"""
O62 十期 60: anomaly = 兩同相交零? 驗證
=========================================
hypothesis: 25 anomaly pairs 全部 κ_iij = κ_ijj = 0
  (有共同 edge 但兩同相交零 → sage 列 SR)

驗證 + 對照: 全部 450 no-edge pairs 都係 κ_iij/κ_ijj = 0?
"""
import sys, os, json
import numpy as np
from itertools import combinations

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")

print("=" * 72)
print("O62 十期 60: anomaly = 兩同零")
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
anomaly = sorted((sr_set - no_edge) & set(combinations(range(36), 2)))

print(f"[1] 25 anomaly 兩同相交")
all_zero = True
for (i, j) in anomaly:
    k1 = kappa36[i, i, j]
    k2 = kappa36[i, j, j]
    if k1 != 0 or k2 != 0:
        all_zero = False
        print(f"  ❌ ({i},{j}): κ_iij={k1}, κ_ijj={k2}")
check("全部 anomaly κ_iij=κ_ijj=0", all_zero, "")

# 但 (1,3): 8/6, (1,6): 1/-3, (10,12): -10/0... 唔係全零!
print(f"\n[2] 非零 anomaly")
for (i, j) in anomaly:
    k1 = kappa36[i, i, j]
    k2 = kappa36[i, j, j]
    if k1 != 0 or k2 != 0:
        print(f"  ({i},{j}): κ_iij={k1}, κ_ijj={k2}")

# ============ 1. 對照: no-edge pairs 嘅兩同 ============
print("\n[3] 對照: 450 no-edge pairs")
noedge_nonzero = 0
noedge_zero = 0
for (i, j) in no_edge:
    k1 = kappa36[i, i, j]
    k2 = kappa36[i, j, j]
    if k1 != 0 or k2 != 0:
        noedge_nonzero += 1
    else:
        noedge_zero += 1
print(f"  no-edge pairs 中, 兩同相交非零: {noedge_nonzero}")
print(f"  no-edge pairs 中, 兩同相交零: {noedge_zero}")

# ============ 2. 另一對照: 有 edge 且非 SR (正常) 嘅 pairs ============
print("\n[4] 對照: 有 edge 正常 pairs")
normal = []
for i in range(36):
    for j in range(i+1, 36):
        if (i, j) in faces_1d and (i, j) not in sr_set:
            normal.append((i, j))
print(f"  有 edge 且非 SR: {len(normal)}")
norm_nz = sum(1 for (i,j) in normal if kappa36[i,i,j] != 0 or kappa36[i,j,j] != 0)
print(f"  其中兩同相交非零: {norm_nz}")

# ============ 3. 總結 ============
print("\n" + "=" * 72)
print("十期 60 總結:")
print("=" * 72)
print(f"""
  anomaly 25: 唔係全部兩同零 (有 (1,3): 8/6 等)
  no-edge 450: 有 {noedge_nonzero} 個兩同非零
  normal (edge, 非SR): {len(normal)}, 兩同非零 {norm_nz}

  → anomaly 唔係「兩同相交零」定義!
  → 需要另一解釋: edge 存在但...?
""")
out = {
    "test": "O62 十期 60: 兩同零驗證",
    "anomaly_all_zero": all_zero,
    "noedge_nonzero": noedge_nonzero, "noedge_zero": noedge_zero,
    "normal": len(normal), "normal_nz": norm_nz,
    "passed": passed, "failed": failed
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "60_two_same.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 十期 60 完成!")
