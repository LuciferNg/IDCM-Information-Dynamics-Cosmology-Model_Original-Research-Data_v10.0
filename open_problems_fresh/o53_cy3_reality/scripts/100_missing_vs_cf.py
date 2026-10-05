#!/usr/bin/env python3
"""
O53 決定性測試: 缺失 5 divisors 同 c_f 矩陣嘅關係
=====================================================
缺失 divisors [0,3,4,7,8]:
  point 0: [0,0,0,0] (origin)
  point 3: [0,0,1,0]
  point 4: [1,2,0,0]
  point 7: [0,0,0,1]
  point 8: [1,1,0,0]

c_f 矩陣 (代×電荷, 3×3):
  gen1 (u,d,e): [0,-2,3]
  gen2 (c,s,μ): [2,-2,-1]
  gen3 (t,b,τ): [1,3,-2]

檢查: 5 個缺失 divisors 有冇 charge 結構對應?
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53: 缺失 divisors vs c_f")
print("=" * 70)

with open(os.path.join(BASE, 'cy36_98_sage_export.json')) as f:
    sage = json.load(f)
pts = np.array(sage['points'])

missing = [0, 3, 4, 7, 8]
print(f"[1] 缺失 divisors 嘅 polytope points:")
for m in missing:
    print(f"  div {m}: {pts[m]}")

# GLSM charges (如果有)
glsm = sage.get('glsm_charge_matrix', None)
if glsm is not None:
    glsm = np.array(glsm)
    print(f"\n[2] GLSM charge matrix: {glsm.shape}")
    # 每個 field (column) 對應 polytope point
    # 檢查缺失 divisors 嘅 charges
    print(f"  缺失 divisors 對應 GLSM columns:")
    for m in missing:
        print(f"    div {m}: charges = {glsm[:, m]}")
else:
    print(f"\n[2] 冇 GLSM charge matrix 喺 export json")

# 3c_f 矩陣
M = np.array([
    [0, -2, 3],
    [2, -2, -1],
    [1, 3, -2]
])
print(f"\n[3] 3c_f 矩陣 (代×電荷):")
print(M)
print(f"  行 = 代 (u,d,e / c,s,μ / t,b,τ)")
print(f"  列 = 電荷 (Q_up, Q_down, Q_lepton)")

# 有趣: 缺失 5 divisors 對應嘅係「非-basis」方向
# 即係: 36 維 divisor 空間入面, 32 個 basis + 5 個 redundant
# 但 32+5 = 37 > 36? 唔對!
# 等等: 36 divisors, 32 basis → 4 redundant? 但缺失 5 個?
print(f"\n[4] 數數:")
print(f"  36 divisors, basis = 32")
print(f"  缺失 = 5 個 (divisor_basis 返回 32 個, 缺 5)")
print(f"  32 + 5 = 37 ≠ 36 — 即係 divisor_basis 係 1-based!")

# 檢查: divisor_basis [1..36] 1-based → 0-based [0..35]
db = [1, 2, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]
db0 = [d - 1 for d in db]
missing0 = sorted(set(range(36)) - set(db0))
print(f"  1-based basis 最後: {db[-3:]}")
print(f"  0-based basis 最後: {db0[-3:]}")
print(f"  0-based 缺失: {missing0}")
print(f"  → 真正缺失 (0-based): {missing0}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)