#!/usr/bin/env python3
"""
O53 方向③: curve volumes 深度分析
======================================
curve volumes (tip) 有 φ 近整數信號 (27% vs 7.6%)
深度: 1. 值分佈 2. φ 指數 3. 對應 divisor block
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 70)
print("O53: curve volumes 深度分析")
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

tip = cy.toric_kahler_cone().tip_of_stretched_cone(1)
cv = np.array(cy.compute_curve_volumes(tip))
print(f"curve volumes: {cv.shape}")

# 1. 值分佈
print(f"\n[1] 值分佈:")
print(f"  min={cv.min()}, max={cv.max()}, mean={cv.mean():.1f}, median={np.median(cv):.0f}")
print(f"  <10: {(cv < 10).sum()} ({(cv<10).mean()*100:.0f}%)")
print(f"  <100: {(cv < 100).sum()} ({(cv<100).mean()*100:.0f}%)")
print(f"  >100: {(cv > 100).sum()} ({(cv>100).mean()*100:.0f}%)")

# 2. φ 指數
print(f"\n[2] φ 指數 (ln(v)/lnφ):")
ns = []
for v in cv:
    if v > 0:
        ns.append(math.log(v) / math.log(phi))
ns = np.array(ns)
print(f"  n ∈ [{ns.min():.2f}, {ns.max():.2f}]")
print(f"  mean n = {ns.mean():.2f}")

# 近整數統計 (唔同 threshold)
for th in [0.02, 0.05, 0.1]:
    near = sum(1 for n in ns if abs(n - round(n)) < th)
    print(f"  Δ<{th}: {near}/{len(ns)} = {near/len(ns)*100:.1f}%")

# 3. 分數結構: n = a/b 有理數?
print(f"\n[3] n 值分佈 (unique):")
unique_n = np.unique(np.round(ns, 2))
print(f"  {len(unique_n)} unique values: {unique_n[:20]}...")

# 4. 對應 divisor blocks (用 curve basis)
cb = np.array(cy.curve_basis()) - 1
blocks = {'Block 0 (<12)': [], 'Block 1 (12-23)': [], 'Block 2 (24+)': []}
for i, d in enumerate(cb):
    if d < 12:
        blocks['Block 0 (<12)'].append(cv[i])
    elif d < 24:
        blocks['Block 1 (12-23)'].append(cv[i])
    else:
        blocks['Block 2 (24+)'].append(cv[i])

print(f"\n[4] block 分佈:")
for name, vals in blocks.items():
    vals = np.array(vals)
    ns_b = [math.log(v)/math.log(phi) for v in vals if v > 0]
    near_b = sum(1 for n in ns_b if abs(n - round(n)) < 0.05)
    print(f"  {name}: {len(vals)} 個, mean={vals.mean():.1f}, φ近整數={near_b}/{len(vals)}")

# 5. 特殊: 大值 (>100) 嘅 φ 指數
print(f"\n[5] 大值 (>100) φ 分析:")
big = cv[cv > 100]
for v in big:
    n = math.log(v)/math.log(phi)
    print(f"  v={v:.0f}: n={n:.2f}, Δ={abs(n-round(n)):.3f} {'★' if abs(n-round(n))<0.05 else ''}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)