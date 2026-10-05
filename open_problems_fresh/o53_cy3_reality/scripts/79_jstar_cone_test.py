#!/usr/bin/env python3
"""
O53 決定性測試: J* 係咪喺 Kähler cone?
==========================================
Kähler cone dim=32, J* 36D — 檢查 J* 係咪喺 cone
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53: J* 喺 Kähler cone?")
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

# Kähler cone
kc = cy.toric_kahler_cone()
print(f"Kähler cone: dim={kc.dim()}")
print(f"  generators: {kc.generators() if hasattr(kc, 'generators') else 'N/A'}")

# J*
with open(os.path.join(BASE, 'Jstar_36D.json')) as f:
    jstar = json.load(f)
J0 = np.array(jstar['Jstar_36D'])
print(f"J* (36D): min={J0.min():.5f}, max={J0.max():.5f}")

# 檢查 cone 包含
try:
    contains = kc.contains(J0)
    print(f"J* 喺 Kähler cone: {contains}")
except Exception as e:
    print(f"contains FAIL: {type(e).__name__}: {e}")
    # 可能 dim 唔匹配, 試 32D
    try:
        contains32 = kc.contains(J0[:32])
        print(f"J*[:32] 喺 Kähler cone: {contains32}")
    except Exception as e2:
        print(f"contains32 FAIL: {e2}")

# 檢查 J* 有冇 redundant dims (最後 4 個)
print(f"\nJ* 最後 4 個值: {J0[-4:]}")
print(f"J* 頭 32 個: min={J0[:32].min():.5f}, max={J0[:32].max():.5f}")

# 用 J*[:32] 做 Y
with open(os.path.join(BASE, 'cy36_98_intersection_full.json')) as f:
    ct = json.load(f)
K_ct = np.array(ct['kappa'])
# K 36³, 用頭 32 做
Y32 = np.einsum('ijk,k->ij', K_ct[:32,:32,:32], J0[:32])
Y32 = (Y32 + Y32.T) / 2
ev32 = np.linalg.eigvalsh(Y32)
ev32_sorted = np.sort(ev32)[::-1]
phi = (1 + math.sqrt(5)) / 2
print(f"\nY32 = κ[:32]·J*[:32] 譜:")
print(f"  λ₁ = {ev32_sorted[0]:.4f}")
print(f"  φ^(1/3) = {phi**(1/3):.4f} (誤差 {abs(ev32_sorted[0]-phi**(1/3))/phi**(1/3)*100:.2f}%)")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)