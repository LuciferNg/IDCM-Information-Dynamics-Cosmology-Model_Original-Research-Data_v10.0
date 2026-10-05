#!/usr/bin/env python3
"""
O53: J* 喺 Kähler cone? + tip 分析
=====================================
1. J* (36D) 係咪喺 CYTools κ 嘅 Kähler cone 入面
2. 用 tip 做 Y = κ·tip 分析
3. 用「合理」J (positive) 做分析
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 70)
print("O53: J* 合法性 + tip 分析")
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
try:
    kc = cy.toric_kahler_cone()
    print(f"Kähler cone: dim={kc.dim()}")
    # 檢查 J* 係咪喺 cone
    with open(os.path.join(BASE, 'Jstar_36D.json')) as f:
        jstar = json.load(f)
    J0 = np.array(jstar['Jstar_36D'])
    print(f"J* (36D): {J0.shape}, min={J0.min():.4f}, max={J0.max():.4f}")
    if np.all(J0 > 0):
        print(f"  ✅ J* 全部正數 — 可能喺 cone")
    else:
        print(f"  ❌ J* 有負數 — 唔可能喺 Kähler cone")
except Exception as e:
    print(f"Kähler cone FAIL: {e}")

# 用 J* 直接做 Y (唔需要 cone 檢查都做)
with open(os.path.join(BASE, 'cy36_98_intersection_full.json')) as f:
    ct = json.load(f)
K_ct = np.array(ct['kappa'])

# tip (32D) — 需要 36D 版本
# 試用 divisor basis: cy 嘅 prime toric divisors
try:
    divs = cy.prime_toric_divisors()
    print(f"\nprime toric divisors: {len(divs)}")
    print(f"  first: {divs[:3]}")
except Exception as e:
    print(f"divisors FAIL: {e}")

# tip 分析 (用 32×32 κ matrix)
with open(os.path.join(BASE, 'cy36_98_cytools_kappa.json')) as f:
    ck = json.load(f)
tip = np.array(ck['tip'])
K_tip = np.array(ck['kappa'])  # 32×32
print(f"\n[tip 分析] κ(tip) 32×32:")
ev_tip = np.linalg.eigvalsh(K_tip)
ev_tip_sorted = np.sort(ev_tip)[::-1]
print(f"  λ₁ = {ev_tip_sorted[0]:.4f}")
print(f"  λ₂ = {ev_tip_sorted[1]:.4f}")
print(f"  φ^(1/3) = {phi**(1/3):.4f}")
print(f"  誤差 = {abs(ev_tip_sorted[0]-phi**(1/3))/phi**(1/3)*100:.2f}%")
print(f"  tr(κ(tip)²) = {np.trace(K_tip @ K_tip):.2f}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)