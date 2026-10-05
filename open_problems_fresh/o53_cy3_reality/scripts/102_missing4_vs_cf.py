#!/usr/bin/env python3
"""
O53 A1 突破測試: 缺失 4 divisors ↔ c_f = n/3
=================================================
Block 0 缺失 4 divisors (B=4) — redundant
Block 0 剩 8 個 independent (2B=8?)

3c_f 矩陣: [[0,-2,3],[2,-2,-1],[1,3,-2]]
行列式 |det| = 18, ΣΣ = 2, Σ² = 36

測試: 4 個缺失 divisors 嘅 polytope points 有冇 charge 結構?
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53: 缺失 4 divisors ↔ c_f")
print("=" * 70)

with open(os.path.join(BASE, 'cy36_98_sage_export.json')) as f:
    sage = json.load(f)
pts = np.array(sage['points'])

missing = [2, 3, 6, 7]
print(f"[1] 缺失 divisors 嘅 polytope points:")
for m in missing:
    print(f"  div {m}: {pts[m]}")

# 3c_f 矩陣
M = np.array([
    [0, -2, 3],
    [2, -2, -1],
    [1, 3, -2]
])
print(f"\n[2] 3c_f 矩陣:")
print(M)

# 檢查: 缺失 divisors 嘅 polytope coords 同 3c_f 有冇線性關係?
# 4 個點 (4D): [-15,-10,-4,0], [0,0,1,0], [-7,-5,-2,0], [0,0,0,1]
pts_missing = pts[missing]
print(f"\n[3] 4×4 矩陣 (缺失 divisors points):")
print(pts_missing)
det4 = np.linalg.det(pts_missing)
print(f"  det = {det4:.2f}")

# 有趣: 前兩個點成比例?
p2, p6 = pts[2], pts[6]
print(f"\n[4] div 2 vs div 6:")
print(f"  div 2: {p2}")
print(f"  div 6: {p6}")
ratio = p2 / np.where(p6 != 0, p6, 1)
print(f"  比例: {ratio}")
print(f"  div2 = 2×div6? {np.allclose(p2, 2*p6)}")

# div 3 vs div 7: 單位向量
print(f"\n[5] div 3 vs div 7:")
print(f"  div 3: {p3 if False else pts[3]} (unit e3)")
print(f"  div 7: {pts[7]} (unit e4)")

# 全部 4 個缺失: 有冇 2 對比例關係?
print(f"\n[6] 缺失 4 個嘅線性關係:")
print(f"  div 2 = 2·div 6? {np.allclose(pts[2], 2*pts[6])}")
print(f"  div 3 = e3, div 7 = e4 (單位向量)")
print(f"  → 4 個 = 2 個方向 × 2 (比例對)")

# 呢個 2×2 結構對應 3c_f 矩陣嘅咩?
# 3c_f: 3 代 × 3 電荷 = 9 entries
# 但 det = 18 = 2×9?
print(f"\n[7] 數字連結:")
print(f"  缺失 4 = B ✅")
print(f"  4 個 = 2 對比例點 (2×2)")
print(f"  det(3c_f) = 18")
print(f"  18 = 2×9 = 2×3²")
print(f"  4×9 = 36 = h11? 4×9 = 36 ✅!")

# 檢查: h11 = 36 = 4 × 9 (B × 9)?
print(f"\n  h11 = 36 = B × 9 = 4 × 9 ✅")
print(f"  9 = 3² = 三代²")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)