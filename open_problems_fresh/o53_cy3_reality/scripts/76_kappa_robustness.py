#!/usr/bin/env python3
"""
O53: CYTools κ 穩健性 — 多個 triangulation 對比
====================================================
確認 CYTools intersection numbers 係咪 triangulation 獨立
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53: κ triangulation 穩健性")
print("=" * 70)

from cytools import Polytope
from cytools.config import enable_experimental_features
enable_experimental_features()

with open(os.path.join(BASE, 'cy36_98_sage_export.json')) as f:
    sage = json.load(f)
pts = np.array(sage['points'])
p = Polytope(pts)

# 多個 triangulation
n_trials = 3
kappas = []
for i in range(n_trials):
    tri = p.triangulate()
    cy = tri.get_cy()
    inter = cy.intersection_numbers()
    K = np.zeros((36, 36, 36))
    for key, val in inter.items():
        if isinstance(key, tuple) and len(key) == 3:
            i0, j, k = key
            if i0 < 36 and j < 36 and k < 36:
                K[i0, j, k] = val
                K[i0, k, j] = val
                K[j, i0, k] = val
                K[j, k, i0] = val
                K[k, i0, j] = val
                K[k, j, i0] = val
    kappas.append(K)
    print(f"  trial {i}: nnz={np.count_nonzero(K)}, chi={cy.chi()}")

# 對比
if len(kappas) >= 2:
    d01 = np.abs(kappas[0] - kappas[1]).max()
    d02 = np.abs(kappas[0] - kappas[2]).max() if len(kappas) > 2 else 0
    print(f"\n  max diff (t0 vs t1): {d01:.6f}")
    print(f"  max diff (t0 vs t2): {d02:.6f}")
    if d01 < 1e-6 and d02 < 1e-6:
        print(f"  ✅ κ 係 triangulation 獨立 (真 intersection numbers)")
    else:
        print(f"  ⚠️ κ 唔係 triangulation 獨立 — 有問題")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)