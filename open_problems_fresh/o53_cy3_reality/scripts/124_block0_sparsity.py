#!/usr/bin/env python3
"""
O53 最終測試: Block 0 稀疏結構 — 0 entries 模式
==================================================
Block 0 (12×12) 好多 0 — 檢查稀疏模式有冇結構
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53: Block 0 稀疏結構")
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

Y = np.einsum('ijk,k->ij', K, J0)
Y = (Y + Y.T) / 2

# Block 0
B0 = Y[0:12, 0:12]
print(f"[1] Block 0 稀疏度:")
nz = np.abs(B0) > 1e-10
print(f"  non-zero: {nz.sum()}/144 = {nz.sum()/144*100:.1f}%")
print(f"  zero: {144 - nz.sum()}/144")

# 稀疏模式
print(f"\n[2] 稀疏模式 (X = non-zero):")
for i in range(12):
    row = ''.join('X' if nz[i, j] else '.' for j in range(12))
    print(f"  {row}")

# 對稱性: 係咪 block diagonal?
print(f"\n[3] 對稱檢查:")
print(f"  係咪對稱? {np.allclose(B0, B0.T)}")

# 0 模式有冇結構?
print(f"\n[4] 每行 non-zero 數:")
for i in range(12):
    print(f"  row {i}: {nz[i].sum()} non-zero")

# 特別: 有冇 rows 係全 zero?
print(f"\n[5] 全零 rows: {[i for i in range(12) if not nz[i].any()]}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)