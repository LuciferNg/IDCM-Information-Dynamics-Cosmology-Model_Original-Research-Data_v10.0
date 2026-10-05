#!/usr/bin/env python3
"""
O53: Block 0 內部結構 — 12 divisors 嘅 3×4 分解
====================================================
Block 0: 12 divisors, 4 個缺失 (redundant), 8 個 basis
12 = 3×4? 4 = B?

c_f = n/3 → 可能 Block 0 有 3 個子結構?

測試: Block 0 嘅 12×12 κ block 有冇 3×4 子結構?
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53: Block 0 3×4 子結構")
print("=" * 70)

from cytools import Polytope
from cytools.config import enable_experimental_features
enable_experimental_features()

with open(os.path.join(BASE, 'cy36_98_sage_export.json')) as f:
    sage = json.load(f)
pts = np.array(sage['points'])
p = Polytope(pts)
tri = p.triangulate()
cy = tri.get_cy()

with open(os.path.join(BASE, 'cy36_98_intersection_full.json')) as f:
    ct = json.load(f)
K = np.array(ct['kappa'])

with open(os.path.join(BASE, 'Jstar_36D.json')) as f:
    jstar = json.load(f)
J0 = np.array(jstar['Jstar_36D'])

# Y = κ·J*
Y = np.einsum('ijk,k->ij', K, J0)
Y = (Y + Y.T) / 2

# Block 0 (0:12)
B0 = Y[0:12, 0:12]
print(f"[1] Block 0 (12×12):")
print(B0)

# 檢查 3×4 子結構: 試唔同分組 (3 組 × 4)
print(f"\n[2] 3×4 子結構測試:")
# 順序分組: [0-3], [4-7], [8-11]
groups = [(0, 4), (4, 8), (8, 12)]
in_strength = []
cross_strength = []
for gi, (a1, a2) in enumerate(groups):
    for gj, (b1, b2) in enumerate(groups):
        block = np.abs(B0[a1:a2, b1:b2]).sum()
        if gi == gj:
            in_strength.append(block)
        else:
            cross_strength.append(block)
print(f"  同組 (3×4 對角): {in_strength}, Σ = {sum(in_strength)}")
print(f"  跨組 (3×4 非對角): {cross_strength}, Σ = {sum(cross_strength)}")
ratio34 = sum(in_strength) / sum(cross_strength)
print(f"  ratio = {ratio34:.3f}")

# 對照: 隨機分組
rng = np.random.default_rng(15)
ratios = []
for _ in range(500):
    perm = rng.permutation(12)
    g = [perm[:4], perm[4:8], perm[8:]]
    ins, crs = 0, 0
    for gi in range(3):
        for gj in range(3):
            block = np.abs(B0[np.ix_(g[gi], g[gj])]).sum()
            if gi == gj:
                ins += block
            else:
                crs += block
    ratios.append(ins / crs)
ratios = np.array(ratios)
print(f"\n  隨機對照 (500): mean = {ratios.mean():.3f}, std = {ratios.std():.3f}")
z = (ratio34 - ratios.mean()) / ratios.std()
print(f"  z = {z:.2f}")

# 順序分組 vs 隨機 — 順序可能冇意義!
# 試「實際缺失」分組: missing [2,3,6,7]
print(f"\n[3] 缺失 divisor 分組:")
missing = [2, 3, 6, 7]
basis12 = [i for i in range(12) if i not in missing]
print(f"  缺失: {missing} (4 個)")
print(f"  basis: {basis12} (8 個)")
# 12 = 4 missing + 8 basis — 呢個先係「自然」分解!
Y_missing = np.abs(B0[np.ix_(missing, missing)]).sum()
Y_mb = np.abs(B0[np.ix_(missing, basis12)]).sum()
Y_bb = np.abs(B0[np.ix_(basis12, basis12)]).sum()
print(f"  |Y|(missing,missing) = {Y_missing:.3f}")
print(f"  |Y|(missing,basis) = {Y_mb:.3f}")
print(f"  |Y|(basis,basis) = {Y_bb:.3f}")

# c_f 分數結構: 12 = 4+8, 4 = B
print(f"\n[4] 12 = 4+8 = B + 2B:")
print(f"  4 = B (缺失, redundant)")
print(f"  8 = 2B (basis, independent)")
print(f"  3×4 = 12: 3 個 block × 4 = 12")
print(f"  c_f = n/3: n ∈ {-2,-1,0,1,2,3}")
print(f"  → 12 個 divisor = 3 組 × 4 個")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)