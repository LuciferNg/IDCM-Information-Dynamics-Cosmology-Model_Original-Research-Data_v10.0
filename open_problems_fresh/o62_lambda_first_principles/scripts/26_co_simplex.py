#!/usr/bin/env python3
"""
O62 八期 26: Co-simplex 消去定理 (正確定義!)
=============================================
O58 定義: co-simplex triple = 三點喺同一 4-simplex (5 點) 內
  904 個 co-simplex triples = 554 K=0 + 350 K≠0

我上次錯用「共 3D cone」(4 點) — 正確應該係「共 4-simplex」(5 點)!

推導:
  1. 由 144 simplices 構建 co-simplex triples (i,j,k 喺同一 simplex)
  2. 計總數 → 係咪 904?
  3. 其中 κ=0 vs κ≠0 → 554/350?
  4. SR 消去定理: 唔 co-simplex → κ=0 (必要條件)
  5. 但 co-simplex 唔保證 κ≠0 (554 個例外 = 數值消去)
     → 需要更強條件: div0 出現? star-product?
"""
import sys, os, math, json
import numpy as np
from itertools import combinations

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")

print("=" * 72)
print("O62 八期 26: Co-simplex 消去定理 (正確)")
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
simplices = d["simplices"]  # 144 個 5-點 4-simplex
kappa36 = np.array(json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))["kappa"])[:36,:36,:36]

# ============ 1. Co-simplex triples ============
print("\n[1] Co-simplex triples (共 4-simplex)")
co_simplex = set()
for s in simplices:
    for t in combinations(s, 3):
        co_simplex.add(tuple(sorted(t)))
print(f"  全部 co-simplex triples (48點): {len(co_simplex)}")

# 限 36 模
co36 = set(t for t in co_simplex if max(t) < 36)
print(f"  36 模 co-simplex: {len(co36)}")

# 唔 co-simplex 嘅 36 模 triple: C(36,3) − len(co36)
n_total36 = 36*35*34//6
non_co = n_total36 - len(co36)
print(f"  36 模總 triple: {n_total36}")
print(f"  非 co-simplex: {non_co}")

# ============ 2. 必要條件驗證 ============
print("\n[2] 必要條件: 非 co-simplex → κ=0")
violations = 0
for t in combinations(range(36), 3):
    if t not in co36 and kappa36[t] != 0:
        violations += 1
print(f"  非 co-simplex 但 κ≠0: {violations}")
check("非 co-simplex → κ=0 (0 違反)", violations == 0, f"(違反 {violations})")

# ============ 3. Co-simplex 中 κ 分佈 ============
print("\n[3] Co-simplex 中 κ 分佈")
co_nnz = 0
co_zero = 0
for t in co36:
    if kappa36[t] != 0:
        co_nnz += 1
    else:
        co_zero += 1
print(f"  co-simplex 總數: {len(co36)}")
print(f"  co-simplex κ≠0: {co_nnz}")
print(f"  co-simplex κ=0: {co_zero}")
print(f"  → 554/350? {co_zero}/{co_nnz}")
check("co-simplex κ=0 = 554?", co_zero == 554, f"({co_zero})")
check("co-simplex κ≠0 = 350?", co_nnz == 350, f"({co_nnz})")
check("總數 = 904?", len(co36) == 904, f"({len(co36)})")

# ============ 4. 三互異限制 ============
print("\n[4] 三互異 (i<j<k) co-simplex")
# κ 三互異非零 = 714 (上次) — 但 co-simplex 只有 350 非零?
# 即 κ 三互異非零 714 中, 只有 350 係 co-simplex?
# 其餘 364 個三互異非零係咪 co-simplex?
nnz_distinct_total = 0
nnz_not_co = 0
for i in range(36):
    for j in range(i+1, 36):
        for k in range(j+1, 36):
            if kappa36[i,j,k] != 0:
                nnz_distinct_total += 1
                if (i,j,k) not in co36:
                    nnz_not_co += 1
print(f"  三互異 κ≠0 總數: {nnz_distinct_total}")
print(f"  其中非 co-simplex: {nnz_not_co}")
check("三互異非零全部 co-simplex?", nnz_not_co == 0, f"(非 co {nnz_not_co})")

# ============ 5. 兩同非零 (i=i≠k) ============
print("\n[5] 兩同非零 κ_iik")
two_same_nnz = 0
for i in range(36):
    for k in range(36):
        if i != k and kappa36[i,i,k] != 0:
            two_same_nnz += 1
print(f"  兩同非零總數: {two_same_nnz}")
# κ_iik 對應嘅係「二次相交」— 唔係 co-simplex triple 嘅嘢
# 呢啲唔關 554/350 事 (只計三互異 co-simplex)

# ============ 6. 554 消去嘅額外條件 ============
print("\n[6] 554 消去條件分析")
# co-simplex 中 κ=0 嘅 554 個 — 點解?
# O58: div0 出現率 33.8% vs 16.6% (2x)
# star-product mean 36977 vs 26720
# → 需要再查: 邊啲 co-simplex κ=0?

# div0 = index 0 (K=-360 個 divisor)?
div0_presence_zero = 0
div0_presence_nnz = 0
for t in co36:
    has0 = (0 in t)
    if has0:
        if kappa36[t] == 0:
            div0_presence_zero += 1
        else:
            div0_presence_nnz += 1
print(f"  co-simplex 含 div0 (i=0): {div0_presence_zero + div0_presence_nnz}")
print(f"    其中 κ=0: {div0_presence_zero}")
print(f"    其中 κ≠0: {div0_presence_nnz}")
if div0_presence_zero + div0_presence_nnz > 0:
    print(f"    div0 傾向: {div0_presence_zero/(div0_presence_zero+div0_presence_nnz)*100:.1f}% 零")

# ============ 7. 總結 ============
print("\n" + "=" * 72)
print("八期 26 總結:")
print("=" * 72)
print(f"""
  Co-simplex 消去定理 (第一性原理):
  κ_ijk ≠ 0 → (i,j,k) 必須共 simplex (必要條件)
  ✅ 非 co-simplex → κ=0: {violations} 違反

  Co-simplex triples (36模): {len(co36)}
    κ=0: {co_zero} (目標 554)
    κ≠0: {co_nnz} (目標 350)

  {'🎉 904 = 554 + 350 完全重現!' if len(co36) == 904 and co_zero == 554 and co_nnz == 350 else '⚠️ 數字未完全對上 — 需要調整改進'}
""")
out = {
    "test": "O62 八期 26: Co-simplex 正確",
    "n_co36": len(co36),
    "co_zero": co_zero, "co_nnz": co_nnz,
    "violations": violations,
    "nnz_distinct_total": nnz_distinct_total,
    "nnz_not_co": nnz_not_co,
    "two_same_nnz": two_same_nnz,
    "div0_zero": div0_presence_zero, "div0_nnz": div0_presence_nnz,
    "passed": passed, "failed": failed
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "26_co_simplex.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 八期 26 完成!")
