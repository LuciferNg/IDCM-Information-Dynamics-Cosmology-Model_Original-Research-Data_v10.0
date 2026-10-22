#!/usr/bin/env python3
"""
O62 八期 24: 目標一 — SR 理想消去定理 (第一性原理)
====================================================
定理候選: 904 個 Co-simplex Triples 中, 554 個 κ=0
          ⇔ 命中 Stanley-Reisner 理想 (無公共 3-cone)

推導:
  1. 載入 polytope (48 點, 144 simplices, 484 SR pairs)
  2. 由 simplices 構建全部 3D cones (maximal cones)
  3. 對每對射線 (i,j): 檢查有冇公共 cone
  4. 對每個 triple (i,j,k): 三射線喺唔喺同一 cone?
     → 唔喺 → SR 理想 → κ_ijk = 0 必然
  5. 統計: 幾多 κ=0 係 SR 解釋到? 剩餘?
  6. 驗證 554 數字
"""
import sys, os, math, json
import numpy as np
from itertools import combinations

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")

print("=" * 72)
print("O62 八期 24: SR 理想消去定理")
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
pts = np.array(d["points"])          # 48×4
simplices = d["simplices"]           # 144×5
sr_pairs = d["sr_ideal"]             # 484×2
n_vtx = d["n_vertices"]              # 6
kappa = np.array(json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))["kappa"])

print(f"[1] 數據")
print(f"  點數: {len(pts)} (6 頂點 + 42 內部)")
print(f"  4-simplices: {len(simplices)}")
print(f"  SR pairs: {len(sr_pairs)}")
print(f"  κ shape: {kappa.shape}, 非零: {np.count_nonzero(kappa)}")
print(f"  κ=0: {np.count_nonzero(kappa == 0)}")

# ============ 1. 由 4-simplex 構建 3D cones ============
print("\n[2] 3D cones (triangulation 嘅 facets)")
# 每個 4-simplex (5 點) 有 C(5,4) = 5 個 3-facets
cones = set()
for s in simplices:
    for f in combinations(s, 4):
        cones.add(tuple(sorted(f)))
print(f"  3D cones 數: {len(cones)}")
# 3D cone = 4 個射線 span (喺 4D 係 full-dimensional)

# ============ 2. 每對射線有冇公共 cone ============
print("\n[3] 射線對 → 公共 cone 查詢表")
# 對 (i,j): 有冇 cone 同時含 i, j?
pair_cone = {}
for c in cones:
    for i, j in combinations(c, 2):
        pair_cone.setdefault((i, j), set()).add(c)
print(f"  有公共 cone 嘅對: {len(pair_cone)}")
# 全部對數 C(48,2) = 1128
n_pairs = 48*47//2
print(f"  總對數: {n_pairs}, 冇公共 cone: {n_pairs - len(pair_cone)}")
check("冇公共 cone 對數 = SR pairs 數?", n_pairs - len(pair_cone), 0, 0) if False else None
no_cone_pairs = [(i, j) for i, j in combinations(range(48), 2) if (i, j) not in pair_cone]
print(f"  SR 理想應有 {len(no_cone_pairs)} 對 (冇公共 cone)")
print(f"  sage SR pairs: {len(sr_pairs)}")
# 比較
sr_set = set(tuple(sorted(p)) for p in sr_pairs)
no_cone_set = set(no_cone_pairs)
common = sr_set & no_cone_set
print(f"  SR ∩ 冇cone: {len(common)}")
print(f"  SR − 冇cone: {len(sr_set - no_cone_set)} (SR 有但 cone 有?)")
print(f"  冇cone − SR: {len(no_cone_set - sr_set)} (cone 冇但 SR 冇?)")
check("SR ideal = 冇公共 cone 對", len(sr_set - no_cone_set) == 0, f"(差 {len(sr_set - no_cone_set)})")

# ============ 3. Triple 消去 ============
print("\n[4] Triple (i,j,k) 消去定理")
# 定理: κ_ijk = 0 ⇔ 冇任何 cone 同時含 i,j,k
# (三射線唔喺同一 3D cone)
triple_cone = set()
for c in cones:
    for t in combinations(c, 3):
        triple_cone.add(tuple(sorted(t)))
print(f"  有公共 cone 嘅 triple: {len(triple_cone)}")

# 全部 triple: C(48,3) = 17296
n_triples = 48*47*46//6
print(f"  總 triple: {n_triples}")

# 但 κ 只喺 36 個 Kähler 模 (h11) 上定義 — 邊 36 個點?
# O53: h11 = 36 → Kähler divisors 對應 36 個「相關」點
# 通常: 內部點全部 (42) 但 h11 = 36 → 6 個內部點係冗餘?
# 或者 Kähler cone 由特定 36 個 rays 生成
# 用 κ 嘅非零 index 反推:
nonzero_idx = set()
for i, j, k in zip(*np.nonzero(kappa)):
    nonzero_idx.add(int(i))
    nonzero_idx.add(int(j))
    nonzero_idx.add(int(k))
print(f"  κ 非零涉及嘅 index: {len(nonzero_idx)} (max {max(nonzero_idx)+1})")
print(f"  κ 用到嘅 index 範圍: 0..{max(nonzero_idx)}")
# κ 係 36×36×36 → 36 個 divisors 對應 index 0..35
n_36 = 36
triples_36 = list(combinations(range(n_36), 3))
print(f"  36 模嘅 triple: {len(triples_36)} = C(36,3)")

# 邊啲 triple 有公共 cone?
triple_cone_36 = set(t for t in triple_cone if max(t) < 36)
n_with_cone = len(triple_cone_36)
n_without_cone = len(triples_36) - n_with_cone
print(f"  36 模 triple 有 cone: {n_with_cone}")
print(f"  36 模 triple 冇 cone (SR): {n_without_cone}")

# κ 非零數 (只計 36×36×36 區域)
kappa36 = kappa[:36, :36, :36]
nnz36 = np.count_nonzero(kappa36)
print(f"  κ36 非零: {nnz36}")
print(f"  咁 κ36 = 0 數: {36**3 - nnz36}")

# 對比: 冇 cone 嘅 triple 數 vs κ=0?
# κ_ijk = 0 應該 ⊇ 冇 cone triple
# 驗證: 冇 cone triple 全部 κ=0?
violations = 0
sr_zero = 0
for t in triples_36:
    if t not in triple_cone_36:  # 冇公共 cone → SR
        if kappa36[t] != 0:
            violations += 1
        else:
            sr_zero += 1
print(f"  SR triple (冇cone): {sr_zero + violations}")
print(f"  其中 κ=0: {sr_zero}")
print(f"  其中 κ≠0 (違反!): {violations}")
check("SR triple 全部 κ=0", violations == 0, f"(違反 {violations})")

# 反向: κ=0 有幾多係 SR 解釋?
total_zero = np.count_nonzero(kappa36 == 0)
print(f"\n  κ36 = 0 總數: {total_zero}")
print(f"  SR 解釋到: {sr_zero}")
print(f"  SR 解釋率: {sr_zero/total_zero*100:.2f}%")
print(f"  非 SR 零: {total_zero - sr_zero}")

# ============ 4. 554 數字? ============
print("\n[5] 554 係邊個數?")
# 904 co-simplex triples — 可能係「有 cone 但 κ=0」?
# C(36,3) = 7140 triples
print(f"  C(36,3) = {len(triples_36)}")
# 或者 48 點全部: C(48,3) = 17296
# 或者 co-simplex 定義唔同
print(f"  有 cone 但 κ=0: {n_with_cone - nnz36}?")
# nnz36 只數三 index 都 <36 嘅
# 真 κ 非零 1341 (36³ 全域) — 但 1341 包括 i,j,k ∈ 0..35
print(f"  κ36 非零 (全 36³): {np.count_nonzero(kappa36)}")
# 有 cone 嘅 triples 中 κ=0:
with_cone_zero = n_with_cone - np.count_nonzero(kappa36)
print(f"  有cone+κ=0: {with_cone_zero}")
print(f"  冇cone+κ=0: {sr_zero}")
print(f"  total κ36=0: {total_zero}")

# 試 554: 冇cone triple?
print(f"\n  冇cone triple (36模) = {n_without_cone}")
# 554?
print(f"  554? {n_without_cone == 554}")

# ============ 5. 總結 ============
print("\n" + "=" * 72)
print("八期 24 總結:")
print("=" * 72)
print(f"""
  SR 理想消去定理 (第一性原理):
  κ_ijk = 0 若 (i,j,k) 唔喺任何 3D cone 內
  (三射線無公共交點 → 無三重相交)

  驗證結果:
  36 模 triple 有公共 cone: {n_with_cone}
  冇公共 cone (SR): {n_without_cone}
  SR triple 全部 κ=0: {'✅' if violations == 0 else '❌ ' + str(violations)}
  SR 解釋 κ=0 率: {sr_zero/total_zero*100:.2f}%
""")
out = {
    "test": "O62 八期 24: SR 消去定理",
    "n_cones": len(cones),
    "sr_pairs": len(sr_pairs),
    "no_cone_pairs": len(no_cone_pairs),
    "sr_eq_no_cone": len(sr_set - no_cone_set) == 0,
    "n_triples_36": len(triples_36),
    "n_with_cone": n_with_cone,
    "n_without_cone": n_without_cone,
    "sr_zero": sr_zero,
    "violations": violations,
    "total_zero": int(total_zero),
    "sr_coverage_pct": float(sr_zero/total_zero*100),
    "nnz36": int(np.count_nonzero(kappa36)),
    "passed": passed, "failed": failed
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "24_sr_ideal.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 八期 24 完成!")
