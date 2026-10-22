#!/usr/bin/env python3
"""
O62 八期 35: 7+29=36 分割驗證 ★★★
====================================
發現:
  7 個內部點 star ≥ 20: [0, 6, 12, 14, 17, 30, 32] = 動態?
  11 個點 star = 0: [37-47] = 唔喺 triangulation
  48 − 11 = 37 = 有效 field
  42 內部點 − 11 star=0 = 31? 唔係 36...

等等: 37 個有效 field (star>0) 中:
  6 頂點 + 31 內部? 37−6 = 31
  但 h11 = 36!

再諗: 37 fields = 48 − 11 (star=0)
  有效內部點 = 37 − 6 = 31
  h11 = 36 ≠ 31...

問題: 邊 36 個點對應 Kähler divisors?
  = 48 − 11 star=0 − 1 冗餘? = 36?
  或者 = 37 有效 − 1 (div0 特殊)?

驗證: 
  1. 37 個 star>0 點
  2. 36 個 Kähler = 37 − 1?
  3. 7 個高 star (≥20) = 動態?
  4. 29 = 36 − 7 = L_7 ✓?
"""
import sys, os, math, json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")

print("=" * 72)
print("O62 八期 35: 7+29=36 分割驗證")
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
pts = np.array(d["points"], dtype=float)
vertices = np.array(d["vertices"], dtype=float)
simplices = d["simplices"]
Q = np.array(d["glsm_matrix"], dtype=float)

vtx_idx = []
for v in vertices:
    for i, p in enumerate(pts):
        if np.allclose(p, v):
            vtx_idx.append(i)
            break
vtx_set = set(vtx_idx)

star = {}
for s in simplices:
    for v in s:
        star[v] = star.get(v, 0) + 1

print("[1] 有效點 (star > 0)")
active = [i for i in range(48) if star.get(i, 0) > 0]
inactive = [i for i in range(48) if star.get(i, 0) == 0]
print(f"  active: {len(active)} (star>0)")
print(f"  inactive: {len(inactive)} (star=0): {inactive}")
check("active = 37 = 48−11", len(active) == 37, f"({len(active)})")
check("inactive = 11 = N_d/B", len(inactive) == 11, f"({len(inactive)})")

# 高 star 內部點
interior = [i for i in active if i not in vtx_set]
high_star = [i for i in interior if star.get(i, 0) >= 20]
low_star = [i for i in interior if star.get(i, 0) < 20]
print(f"\n[2] 內部點 (active): {len(interior)}")
print(f"  高 star (≥20): {sorted(high_star)} ({len(high_star)})")
print(f"  低 star (<20): {sorted(low_star)} ({len(low_star)})")

# 7+29?
check("高 star = 7", len(high_star) == 7, f"({len(high_star)})")
print(f"  7 + {len(low_star)} = {7 + len(low_star)}")
check("7 + 29 = 36?", 7 + len(low_star) == 36, f"({7 + len(low_star)})")

# 但 interior 有幾多?
print(f"  active 內部: {len(interior)}")
print(f"  6 頂點 + {len(interior)} 內部 = {6 + len(interior)}")

# ============ 關鍵: h11 = 36 對應邊啲點? ============
print("\n[3] h11 = 36 嘅 36 個 divisor")
# active 點 37 個, 但 h11 = 36
# 37 − 36 = 1: 邊個 redundant?
# div0 (point 0) star=144 全連接 — 可能係「整體類」redundant?
# 或者 37 active = 36 Kähler + 1 (scaling)

# 如果 36 = 7 高star + 29 低star: 需要 low_star = 29
print(f"  low_star 數: {len(low_star)}")
check("low_star = 29 = L_7?", len(low_star) == 29, f"({len(low_star)})")

# 但 active interior = 31 = 7 + 24? 唔係 7+29!
print(f"  active interior = {len(interior)} = 7 高 + {len(low_star)} 低")

# 咁 36 喺邊? 37 active − 1 = 36
# 或者: 36 = 6 頂點 + 30 內部? 或者...

# 等等 — 可能 7+29 唔係 star 分割!
# γ_7 = 動態模態 (K_Chain), L_7 = 29
# 可能: 37 active 點 → 36 Kähler (div0 做 global scaling) 
# → 36 = 7 動態 + 29 固定

print("\n[4] 另一分割: div0 (point 0) 做 scaling")
print(f"  36 Kähler = 37 active − 1 (div0 scaling)")
print(f"  或者 36 = 7 動態 + 29 固定 (唔關 star 事)")

# ============ 5. 檢查 GLSM field 對應 ============
print("\n[5] GLSM 37 fields ↔ 37 active points?")
# glsm matrix 37 列 — 對應邊 37 個點?
# 如果 Q 嘅列對應 points 0..36 (頭 37 個) 或特定排序?
print(f"  Q shape: {Q.shape}")
# 檢查 Q 有冇 zero columns (對應 inactive points)
col_sum = Q.sum(axis=0)
print(f"  Q column sums: {[int(v) for v in col_sum]}")
zero_cols = [i for i in range(Q.shape[1]) if np.all(Q[:, i] == 0)]
print(f"  Q zero columns: {zero_cols}")

# ============ 6. 總結 ============
print("\n" + "=" * 72)
print("八期 35 總結:")
print("=" * 72)
print(f"""
  ★ 結構發現:
  48 點 = 37 active (star>0) + 11 inactive (star=0)
  11 = N_d/B = 44/4 ✓
  37 active = 6 頂點 + 31 內部
  31 內部 = 7 高-star (≥20) + 24 低-star

  7 高-star: {sorted(high_star)} ← 7 = γ_7 動態!
  div0 (point 0): star=144 全 polytope

  7+29 = 36: 
  {('✅ 31 內部 = 7 高 + 24 低 (24≠29, 唔係直接分割)' if len(low_star) != 29 else '✅ low_star = 29 = L_7!')}

  🟡 需要: 確認 36 Kähler divisor 嘅精確對應
""")
out = {
    "test": "O62 八期 35: 分割",
    "active": active, "inactive": inactive,
    "high_star": sorted(high_star), "low_star": sorted(low_star),
    "n_active": len(active), "n_inactive": len(inactive),
    "n_high": len(high_star), "n_low": len(low_star),
    "zero_cols": zero_cols,
    "passed": passed, "failed": failed
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "35_partition.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 八期 35 完成!")
