#!/usr/bin/env python3
"""
O53 方向③: curve volumes φ 最嚴格測試
=========================================
排除小整數偽影 (v<=10), 只測 v>10
如果 v>10 都高命中 → 真結構
如果跌返隨機 → 小整數偽影
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 70)
print("O53: curve volumes φ 嚴格測試 (v>10)")
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

# 分組
small = cv[cv <= 10]
large = cv[cv > 10]
print(f"[1] 分組: small (≤10) = {len(small)}, large (>10) = {len(large)}")

def phi_near(vals, th=0.05):
    n = 0
    for v in vals:
        if abs(math.log(v)/math.log(phi) - round(math.log(v)/math.log(phi))) < th:
            n += 1
    return n

n_small = phi_near(small)
n_large = phi_near(large)
print(f"[2] φ 近整數 (Δ<0.05):")
print(f"  small: {n_small}/{len(small)} = {n_small/len(small)*100:.1f}%")
print(f"  large: {n_large}/{len(large)} = {n_large/len(large)*100:.1f}%")

# 隨機對照 (同 range)
rng = np.random.default_rng(21)
trials = 1000
rand_counts = []
for _ in range(trials):
    vals = rng.integers(11, 913, len(large))
    c = 0
    for v in vals:
        if abs(math.log(v)/math.log(phi) - round(math.log(v)/math.log(phi))) < 0.05:
            c += 1
    rand_counts.append(c)
rand_counts = np.array(rand_counts)
print(f"[3] 隨機對照 (11-912, 1000 次):")
print(f"  mean = {rand_counts.mean():.1f}/{len(large)} = {rand_counts.mean()/len(large)*100:.1f}%")
print(f"  99% = {np.percentile(rand_counts, 99):.1f}")
z = (n_large - rand_counts.mean()) / rand_counts.std()
print(f"  z = {z:.2f}")

# 大值 (v>100) 單獨
big = cv[cv > 100]
n_big = phi_near(big)
print(f"\n[4] 大值 (>100): {n_big}/{len(big)} = {n_big/len(big)*100:.1f}%")

# 結論
print(f"\n[5] 結論:")
if z > 3:
    print(f"  ✅ v>10 嘅 φ 近整數 z={z:.1f}σ — 真結構!")
else:
    print(f"  ❌ v>10 嘅 φ 近整數 z={z:.1f}σ — 小整數偽影 (冇結構)")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)