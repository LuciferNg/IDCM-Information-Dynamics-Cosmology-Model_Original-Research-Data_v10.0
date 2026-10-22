#!/usr/bin/env python3
"""
O62 八期 25: SR 消去定理深入 — 搵 554 + 有cone但κ=0 結構
==========================================================
上次發現:
  - SR 消去定理 ✅: 6690 冇cone triple 全部 κ=0
  - 有公共 cone triple: 450 (36模)
  - 但 κ36 非零 1341 > 450! 點解?

關鍵: κ_ijk 唔單指 (i,j,k) 互異 — 可以 i=j, i=k 等!
  κ_ijk 有 36³ = 46656 entries
  非零 1341 (包括對角 i=j=k, i=j≠k 等)

重新計數:
  1. 450 有cone triple (i<j<k) 中, κ≠0 幾多?
  2. 有cone+κ≠0: 即真正嘅三重相交
  3. κ 非零嘅 (i,j,k) 全部分佈 (diag/mixed)
  4. 554 = ? 試: 有cone triple 450 + 104? 
     或 904 co-simplex − 350?
"""
import sys, os, math, json
import numpy as np
from itertools import combinations

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")

print("=" * 72)
print("O62 八期 25: 554 搜索 + 有cone結構")
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
pts = np.array(d["points"])
simplices = d["simplices"]
kappa = np.array(json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))["kappa"])
kappa36 = kappa[:36, :36, :36]

# ============ 1. 重建 cones ============
cones = set()
for s in simplices:
    for f in combinations(s, 4):
        cones.add(tuple(sorted(f)))
print(f"[1] 3D cones: {len(cones)}")

# 有公共 cone 嘅 triple (i<j<k)
triple_cone = set()
for c in cones:
    for t in combinations(c, 3):
        if max(t) < 36:
            triple_cone.add(tuple(sorted(t)))
print(f"  36模有cone triple: {len(triple_cone)}")

# ============ 2. κ 非零分佈 ============
print("\n[2] κ36 非零分佈")
nnz = np.argwhere(kappa36 != 0)
n_nnz = len(nnz)
print(f"  非零 entries: {n_nnz}")

# 分類: 三 index 互異 / 兩同 / 全同
distinct = 0
two_same = 0
all_same = 0
for i, j, k in nnz:
    if i == j == k:
        all_same += 1
    elif i == j or i == k or j == k:
        two_same += 1
    else:
        distinct += 1
print(f"  三互異 (i<j<k): {distinct}")
print(f"  兩同 (i=i≠k): {two_same}")
print(f"  全同 (i=i=i): {all_same}")

# ============ 3. 有cone triple 中 κ≠0 ============
print("\n[3] 有cone triple 中 κ≠0")
nnz_distinct = 0
for t in triple_cone:
    i, j, k = t
    if kappa36[i, j, k] != 0:
        nnz_distinct += 1
print(f"  有cone triple: {len(triple_cone)}")
print(f"  其中有 κ≠0: {nnz_distinct}")
print(f"  有cone但κ=0: {len(triple_cone) - nnz_distinct}")
check("有cone triple 大部分 κ≠0?", nnz_distinct > len(triple_cone)*0.5, f"({nnz_distinct}/{len(triple_cone)})")

# ============ 4. 554 搜索 ============
print("\n[4] 554 搜索")
# 候選計數
cands = {
    "有cone triple 中 κ=0": len(triple_cone) - nnz_distinct,
    "三互異非零": distinct,
    "兩同非零": two_same,
    "全同非零": all_same,
    "有cone triple (全48點)": sum(1 for c in cones for t in combinations(c, 3)),
    "SR pairs 484 − 25": 484 - 25,
    "κ 非零 − 有cone": n_nnz - nnz_distinct,
    "κ 非零 − 有cone triple": n_nnz - len(triple_cone),
}
for name, val in cands.items():
    marker = " ★★★ 554!" if val == 554 else ""
    print(f"  {name:28s} = {val}{marker}")

# 904 co-simplex triples?
print(f"\n  904 係邊個數?")
# 試: 有cone triple (全部48點) − 36模有cone?
all48_cone = set()
for c in cones:
    for t in combinations(c, 3):
        all48_cone.add(tuple(sorted(t)))
print(f"  全部48點有cone triple: {len(all48_cone)}")
print(f"  48−36: {len(all48_cone) - len(triple_cone)}")

# co-simplex = 唔喺同一 simplex 嘅 triple?
# 或者: 36 模全部 triple C(36,3) = 7140
# 冇cone 6690 + 有cone 450 = 7140 ✓
# 904? 唔喺 C(36,3) 範圍

# 試: 用「頂點」做嘅 cone? 6 頂點 → C(6,3) = 20
# 試: 有cone triple 中 κ=0 (554?)
print(f"\n  有cone+κ=0 = {len(triple_cone) - nnz_distinct} ← 可能係 554?")

# ============ 5. 兩同非零嘅結構 ============
print("\n[5] 兩同非零 (i=i≠k) 結構")
# 兩同非零: κ_iik ≠ 0 — 呢啲係「第二 Chern 類」相關
# Σ_k κ_iik = ?
row2 = np.einsum("iik->i", kappa36)  # Σ_k κ_iik
print(f"  Σ_k κ_iik (i=0..35):")
print(f"  {np.round(row2, 1)}")
# 有幾多 i 令 row2 ≠ 0?
print(f"  row2 ≠ 0 嘅 i 數: {np.count_nonzero(row2)}")

# ============ 6. 全同非零 ============
print("\n[6] 全同非零 κ_iii")
diag = np.einsum("iii->i", kappa36)
print(f"  κ_iii (i=0..35):")
print(f"  {diag.tolist()}")
print(f"  κ_iii ≠ 0 嘅 i: {np.count_nonzero(diag)}")

# ============ 7. 總結 ============
print("\n" + "=" * 72)
print("八期 25 總結:")
print("=" * 72)
print(f"""
  κ36 非零 = {n_nnz} (三互異 {distinct} + 兩同 {two_same} + 全同 {all_same})

  有cone triple (i<j<k): {len(triple_cone)}
    其中 κ≠0: {nnz_distinct}
    其中 κ=0: {len(triple_cone) - nnz_distinct} ← 可能 554?

  SR 消去定理: 冇cone → κ=0 (6690 全部零, 0 違反) ✅
""")
out = {
    "test": "O62 八期 25: 554 搜索",
    "n_nnz": int(n_nnz), "distinct": int(distinct), "two_same": int(two_same), "all_same": int(all_same),
    "n_triple_cone": len(triple_cone),
    "nnz_in_cone": int(nnz_distinct),
    "zero_in_cone": int(len(triple_cone) - nnz_distinct),
    "row2": row2.tolist(),
    "diag": diag.tolist(),
    "passed": passed, "failed": failed
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "25_554_search.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 八期 25 完成!")
