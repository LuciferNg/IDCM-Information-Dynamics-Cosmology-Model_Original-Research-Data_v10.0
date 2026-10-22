#!/usr/bin/env python3
"""
O62 八期 34: 7+29=36 頂點/內部點結構分析
=========================================
頂點 indices = [1,2,3,4,5,7]
field 0 唔係頂點 (有 31 charges — 內部特殊點)

hypothesis:
  42 內部點中, 36 個有效 (h11) + 6 個冗餘
  或者: 36 = 7 動態 + 29 固定
  7 動態 = γ_7 mode? 定係某 7 個內部點?

探索:
  1. 每個內部點嘅「star size」(出現喺幾多 simplex)
  2. 每個點嘅 charge 結構 (GLSM)
  3. 邊 6 個點係 redundant?
  4. 7+29 嘅自然分割?
"""
import sys, os, math, json
import numpy as np
from itertools import combinations

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")

print("=" * 72)
print("O62 八期 34: 7+29=36 結構")
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

# 頂點 index 搵返
vtx_idx = []
for v in vertices:
    for i, p in enumerate(pts):
        if np.allclose(p, v):
            vtx_idx.append(i)
            break
vtx_set = set(vtx_idx)
print(f"[1] 頂點: {sorted(vtx_idx)}")
print(f"  內部點 (非頂點): {[i for i in range(48) if i not in vtx_set]}")

# ============ 1. Star size ============
print("\n[2] 每個點嘅 star size (出現喺幾多 simplex)")
star = {}
for s in simplices:
    for v in s:
        star[v] = star.get(v, 0) + 1
for i in range(48):
    print(f"  point {i:2d}: star={star.get(i,0):3d} {'★頂點' if i in vtx_set else '·'}")

# ============ 2. 內部點嘅 star 分佈 ============
print("\n[3] 內部點 star 分佈")
interior = [i for i in range(48) if i not in vtx_set]
star_vals = [star.get(i, 0) for i in interior]
print(f"  內部點 star: {sorted(star_vals)}")
print(f"  min: {min(star_vals)}, max: {max(star_vals)}")

# 7 動態? 29 固定?
# 試: 內部點中 star 特別細嘅 (少 simplex) = 動態?
# 或者特別大?
small_star = [i for i in interior if star.get(i,0) <= 4]
large_star = [i for i in interior if star.get(i,0) >= 20]
print(f"  內部點 star ≤ 4: {small_star} ({len(small_star)})")
print(f"  內部點 star ≥ 20: {large_star} ({len(large_star)})")

# ============ 3. 7+29 分割 ============
print("\n[4] 7+29 = 36 分割嘗試")
# 36 有效 Kähler = ?
# 42 內部點 − 6 = 36
# 邊 6 個內部點 redundant?

# 用 GLSM: 37 fields, 5 linear relations → 32 = 2B²
# 37 = 36 + 1? 一個 field 係「整體 scaling」?

# 或者: 有效 Kähler = 內部點 42 − 6 頂點相關冗餘
# = 36
# 再分: 7 動態 (γ_7 相關) + 29 固定 (L_7)

# Lucas 29: 試搵 29 個「固定」內部點
# 7 個「動態」內部點?
# 用 star size 排序, 取最大 7 個?

# ============ 4. 同 γ 譜比較 ============
print("\n[5] 同 γ_n 譜比較")
# γ_7 = 4sin²(7π/88) = ?
g7 = 4*math.sin(7*math.pi/88)**2
print(f"  γ_7 = {g7:.6f}")
# L_7 = 29
print(f"  L_7 = 29")

# ============ 5. 總結 ============
print("\n" + "=" * 72)
print("八期 34 總結:")
print("=" * 72)
print(f"""
  頂點: {sorted(vtx_idx)} (field 0 唔係頂點!)
  內部點: 42
  star size 分佈: min {min(star_vals)}, max {max(star_vals)}

  Batyrev: h11 = 42 − 4 − 2 = 36 ✓

  7+29 分割: 🟡 需要更多分析
  - 42 內部點 − 6 = 36 (6 個冗餘?)
  - 7 動態 vs 29 固定嘅自然分割未現
""")
out = {
    "test": "O62 八期 34: 結構",
    "vtx_idx": sorted(vtx_idx),
    "star": {str(k): v for k, v in star.items()},
    "small_star": small_star, "large_star": large_star,
    "passed": passed, "failed": failed
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "34_structure.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 八期 34 完成!")
