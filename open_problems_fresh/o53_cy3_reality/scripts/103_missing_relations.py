#!/usr/bin/env python3
"""
O53: 缺失 4 divisors 嘅 redundant 關係
=========================================
divisor_basis 缺 [2,3,6,7] — 呢 4 個可以由其他 32 個線性表示?
如果有 explicit 關係 → 可以理解 block 0 嘅結構
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53: 缺失 divisors 線性關係")
print("=" * 70)

with open(os.path.join(BASE, 'cy36_98_sage_export.json')) as f:
    sage = json.load(f)
pts = np.array(sage['points'])

missing = [2, 3, 6, 7]
basis = [i for i in range(36) if i not in missing]

# polytope points 36×4
# 每個 divisor 對應一個 4D point
# 線性關係: 缺失 point = Σ c_i · basis point?

# 用 points (36×4) 做線性回歸
A = pts[basis]  # 32×4
targets = pts[missing]  # 4×4

print(f"[1] basis points: {A.shape}, missing points: {targets.shape}")
print(f"  呢個係 4D 空間 — 32 個 basis points 肯定 span R⁴")
print(f"  → 線性表示一定存在 (trivial)")
print(f"  → 真正問題係: 缺失 divisors 有冇「特別」嘅線性組合? (例如 ±1 係數)")

# 直接檢查: 缺失 divisor 3 = e3, 7 = e4 係 unit vectors
# div 3: [0,0,1,0], div 7: [0,0,0,1]
print(f"\n[2] 缺失 divisors 幾何:")
print(f"  div 2: {pts[2]} = [-15,-10,-4,0]")
print(f"  div 3: {pts[3]} = [0,0,1,0] = e₃")
print(f"  div 6: {pts[6]} = [-7,-5,-2,0]")
print(f"  div 7: {pts[7]} = [0,0,0,1] = e₄")

# div 2 同 div 6 差 2 倍左右
print(f"\n[3] div2/div6 比例 (首 3 個分量):")
r = pts[2][:3] / pts[6][:3]
print(f"  {r} — 接近 2? {np.allclose(r, 2, atol=0.1)}")

# 搵其他 divisors 有冇同 div2/div6 成比例
print(f"\n[4] 邊啲其他 divisors 同 div 2/6 成比例?")
for i in range(36):
    if i in missing:
        continue
    p = pts[i]
    # 檢查 p 同 pts[2] 成比例
    if np.all(p[:3] != 0) and np.all(pts[2][:3] != 0):
        r2 = p[:3] / pts[2][:3]
        if np.allclose(r2, r2[0], atol=1e-6):
            print(f"  div {i}: {p} ∝ div 2 (ratio {r2[0]:.3f})")
    if np.all(p[:3] != 0) and np.all(pts[6][:3] != 0):
        r6 = p[:3] / pts[6][:3]
        if np.allclose(r6, r6[0], atol=1e-6):
            print(f"  div {i}: {p} ∝ div 6 (ratio {r6[0]:.3f})")

# 檢查: 有冇其他 divisors 係 unit vectors?
print(f"\n[5] 其他 unit vector divisors:")
for i in range(36):
    if i in missing:
        continue
    p = pts[i]
    if np.count_nonzero(p) == 1 and np.sum(np.abs(p)) == 1:
        print(f"  div {i}: {p}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)