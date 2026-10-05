#!/usr/bin/env python3
"""
O53 方向①: A2 J* 來源 — GW/GV invariants 測試
=================================================
J* ≈ φ^(-n) 嘅來源可能係 instanton 修正 (GW invariants)
用 CYTools compute_gw + compute_gv 計算 (36,98) 嘅 invariants
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 70)
print("O53: GW/GV invariants")
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

print(f"CY: h11={cy.h11()}, h12={cy.h12()}")

# 1. Mori cone cap generators
try:
    mcap = cy.mori_cone_cap()
    print(f"\n[1] mori_cone_cap: {mcap}")
    mcap = np.array(mcap)
    print(f"  shape: {mcap.shape}")
except Exception as e:
    print(f"[1] mori_cone_cap FAIL: {str(e)[:100]}")

# 2. compute_curve_volumes (curve basis)
try:
    cb = cy.curve_basis()
    print(f"\n[2] curve_basis: {cb}")
except Exception as e:
    print(f"[2] curve_basis FAIL: {str(e)[:100]}")

# 3. GW invariants (mcap generators)
try:
    print(f"\n[3] compute_gw (mcap):")
    gw = cy.compute_gw(mcap_generators=mcap, max_deg=3)
    print(f"  GW: {gw}")
except Exception as e:
    print(f"[3] compute_gw FAIL: {str(e)[:150]}")

# 4. GV invariants
try:
    print(f"\n[4] compute_gv (mcap):")
    gv = cy.compute_gv(mcap_generators=mcap, max_deg=3)
    print(f"  GV: {gv}")
except Exception as e:
    print(f"[4] compute_gv FAIL: {str(e)[:150]}")

# 5. 分析 GW/GV 同 φ 有冇關係
print(f"\n[5] φ 對照:")
print(f"  φ = {phi:.6f}")
print(f"  φ^(-1) = {1/phi:.6f}")
print(f"  φ^(-2) = {1/phi**2:.6f}")
print(f"  φ^(-3) = {1/phi**3:.6f}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)