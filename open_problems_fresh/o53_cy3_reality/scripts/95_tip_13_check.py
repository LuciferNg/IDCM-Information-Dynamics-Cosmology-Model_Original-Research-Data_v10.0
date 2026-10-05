#!/usr/bin/env python3
"""
O53 A1: block 譜 1/3 結構 — tip J 對照
==========================================
J* 下 Block 0 有 λ=0.3330 ≈ 1/3 (Δ=0.0003 幾乎精確!)
檢查: 用合法 Kähler tip J 係咪都有 1/3 結構?
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53: block 1/3 結構 — tip 對照")
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

# tip (32D) — 需要 36D 版本?
tip32 = cy.toric_kahler_cone().tip_of_stretched_cone(1)
print(f"tip 32D: {tip32[:5]}...")

# divisor basis — CYTools 用 36 個 divisors
# tip 32D 對應 32 個 basis divisors
# 需要: κ_ijk 用 divisor basis → tip 係 32D
# 直接方法: 用 CYTools compute_kappa_matrix(tip) 得 32×32
with open(os.path.join(BASE, 'cy36_98_cytools_kappa.json')) as f:
    ck = json.load(f)
K_tip = np.array(ck['kappa'])  # 32×32 = κ(tip)

# 32×32 嘅 block 結構 (32 = 12+12+8 唔係 3×12)
# 試唔同分組
print(f"\n[1] K(tip) 32×32 譜:")
ev_tip = np.linalg.eigvalsh(K_tip)
ev_sorted = np.sort(ev_tip)[::-1]
for e in ev_sorted[:10]:
    n = round(e * 3)
    dist = abs(e - n/3)
    marker = "★" if dist < 0.05 else ""
    print(f"  λ = {e:10.4f} → n/3 = {n}/3 ({n/3:.4f}), Δ = {dist:.4f} {marker}")

# 近 n/3 統計
near = sum(1 for e in ev_sorted if abs(e - round(e*3)/3) < 0.05)
print(f"\n  近 n/3: {near}/32 = {near/32*100:.1f}%")

# J* 36D 版 block 1/3 結構 — 對比
with open(os.path.join(BASE, 'Jstar_36D.json')) as f:
    jstar = json.load(f)
J0 = np.array(jstar['Jstar_36D'])
Y = np.einsum('ijk,k->ij', K, J0)
Y = (Y + Y.T) / 2
blocks = [(0,12), (12,24), (24,36)]

print(f"\n[2] J* 36D block 1/3 本徵值 (Δ<0.01):")
for bi, (a, b) in enumerate(blocks):
    B = Y[a:b, a:b]
    ev = np.linalg.eigvalsh(B)
    ev_sorted = np.sort(ev)[::-1]
    for e in ev_sorted:
        n = round(e * 3)
        if abs(e - n/3) < 0.01:
            print(f"  Block {bi}: λ = {e:8.4f} = {n}/3 精確!")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)