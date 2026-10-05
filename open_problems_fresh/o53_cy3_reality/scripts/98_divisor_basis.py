#!/usr/bin/env python3
"""
O53 A1: divisor basis 轉換 — 32D↔36D 關係
=============================================
1. divisor_basis() 缺邊 5 個 indices? 係咪全部喺 Block 0?
2. 建立 32D → 36D embedding
3. tip (32D) → 36D J
4. Y = κ·J_36 檢查 Block 0 有冇 1/3
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53: divisor basis 轉換")
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

# divisor basis
db = cy.divisor_basis()
print(f"divisor_basis: {db}")
print(f"  count = {len(db)}")

# 缺嘅 indices
all_divs = set(range(36))
missing = sorted(all_divs - set(db))
print(f"缺失 indices: {missing}")

# 缺嘅係咪全部喺 block 0 (0-11)?
in_block0 = [m for m in missing if m < 12]
in_block1 = [m for m in missing if 12 <= m < 24]
in_block2 = [m for m in missing if m >= 24]
print(f"  Block 0 (0-11): {in_block0}")
print(f"  Block 1 (12-23): {in_block1}")
print(f"  Block 2 (24-35): {in_block2}")

# 讀 κ 36³
with open(os.path.join(BASE, 'cy36_98_intersection_full.json')) as f:
    ct = json.load(f)
K = np.array(ct['kappa'])

# 方法: 用 tip (32D) → 建立 36D J
# tip 32D 對應 db 嘅 32 個 indices
tip32 = cy.toric_kahler_cone().tip_of_stretched_cone(1)
print(f"\ntip32: {tip32.shape}")

# Embedding: J_36[db[i]-1] = tip32[i], 缺嘅 set 0 (或 interpolate)
J_36 = np.zeros(36)
for i, idx in enumerate(db):
    J_36[idx - 1] = tip32[i]
print(f"\nJ_36 (tip embedded): min={J_36.min():.2f}, max={J_36.max():.2f}")
print(f"  block 0: {J_36[:12]}")
print(f"  block 1: {J_36[12:24][:5]}...")
print(f"  block 2: {J_36[24:36][:5]}...")

# Y = κ·J_36
Y = np.einsum('ijk,k->ij', K, J_36)
Y = (Y + Y.T) / 2

# Block 0 譜
B0 = Y[0:12, 0:12]
ev0 = np.linalg.eigvalsh(B0)
ev0_sorted = np.sort(ev0)[::-1]
print(f"\n[Y(tip_36)] Block 0 譜:")
for e in ev0_sorted:
    n = round(e * 3)
    dist = abs(e - n/3)
    marker = "★" if dist < 0.05 else ""
    print(f"  λ = {e:10.4f} → n/3 = {n}/3, Δ = {dist:.4f} {marker}")

# 對比: J* 下 Block 0
with open(os.path.join(BASE, 'Jstar_36D.json')) as f:
    jstar = json.load(f)
J0 = np.array(jstar['Jstar_36D'])
YJ = np.einsum('ijk,k->ij', K, J0)
YJ = (YJ + YJ.T) / 2
B0J = YJ[0:12, 0:12]
ev0J = np.linalg.eigvalsh(B0J)
ev0J_sorted = np.sort(ev0J)[::-1]
print(f"\n[J*] Block 0 譜 (對比):")
print(f"  λ = {ev0J_sorted[:5]}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)