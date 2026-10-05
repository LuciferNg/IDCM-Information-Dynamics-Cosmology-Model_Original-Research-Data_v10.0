#!/usr/bin/env python3
"""
O53 方向①: curve volumes block 分析
======================================
curve volumes 185 個 (tip) — 有冇 3×12 block 結構?
如果 curve volumes 有 block 結構 → 反映 κ 嘅 block 結構
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53: curve volumes block 分析")
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

# curve volumes
tip = cy.toric_kahler_cone().tip_of_stretched_cone(1)
cv = np.array(cy.compute_curve_volumes(tip))
print(f"curve volumes: {cv.shape}")

# 用 curve basis (32D)
cb = np.array(cy.curve_basis())
print(f"curve basis: {cb.shape}")

# curve volumes 對應 curve basis 嘅 divisors
# 檢查 3×12 block 結構: curve volumes 大細有冇 block 分佈?
# curve basis 1-based: [1,2,5,6,9,10,...,36]
# 0-based: [0,1,4,5,8,9,...,35]
cb0 = cb - 1
print(f"curve basis 0-based: {cb0}")

# 將 curve volumes 分組到 3 個 block (用原始 divisor indices)
blocks_cv = [[], [], []]
for i, d in enumerate(cb0):
    if d < 12:
        blocks_cv[0].append(cv[i])
    elif d < 24:
        blocks_cv[1].append(cv[i])
    else:
        blocks_cv[2].append(cv[i])

print(f"\n[1] curve volumes 按 block 分佈:")
for bi, vals in enumerate(blocks_cv):
    vals = np.array(vals)
    print(f"  Block {bi}: {len(vals)} 個, mean = {vals.mean():.1f}, median = {np.median(vals):.0f}, max = {vals.max()}")

# 對比: 隨機分組
rng = np.random.default_rng(9)
n_perm = 1000
ratios = []
for _ in range(n_perm):
    perm = rng.permutation(32)
    # 分 3 組 (12, 12, 8) — 但 32 唔係 3 等分
    # 用相同分組方式 (按原始 divisor index 分)
    # 隨機 shuffle 後按位置分
    groups = [perm[0:10], perm[10:20], perm[20:32]]
    means = [cv[g].mean() for g in groups]
    ratios.append(max(means) / min(means))
ratios = np.array(ratios)
obs_ratio = max([np.array(v).mean() for v in blocks_cv]) / min([np.array(v).mean() for v in blocks_cv])
print(f"\n[2] 對照:")
print(f"  觀測 max/min ratio = {obs_ratio:.3f}")
print(f"  隨機 mean = {ratios.mean():.3f}, 99% = {np.percentile(ratios, 99):.3f}")
z = (obs_ratio - ratios.mean()) / ratios.std()
print(f"  z = {z:.2f}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)