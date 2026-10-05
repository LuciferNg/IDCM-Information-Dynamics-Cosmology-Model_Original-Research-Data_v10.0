#!/usr/bin/env python3
"""
O53 方向①: GW invariants — basis 修正
==========================================
mcap rays 37D, curve basis 32D
用 basis 參數做轉換
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53: GW invariants (basis 修正)")
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

# 1. curve basis (32D)
cb = np.array(cy.curve_basis())
print(f"[1] curve_basis: {cb.shape}")

# 2. mcap rays (37D)
mcap = cy.mori_cone_cap()
rays = np.array(mcap.extremal_rays())
print(f"[2] extremal rays: {rays.shape}")

# 3. GLSM charge matrix (可能有 37 columns)
glsm = cy.glsm_charge_matrix()
print(f"[3] GLSM charge matrix: {glsm.shape}")

# 4. 試 compute_gw 用 glsm 做 basis
try:
    print(f"\n[4] compute_gw (mcap rays, max_deg=2, format='array'):")
    gw = cy.compute_gw(mcap_generators=rays, max_deg=2, format='array')
    print(f"  GW: {gw}")
except Exception as e:
    print(f"[4] FAIL: {str(e)[:150]}")

# 5. 試 min_points 模式
try:
    print(f"\n[5] compute_gw (min_points=10):")
    gw2 = cy.compute_gw(min_points=10, format='array')
    print(f"  GW: {gw2}")
except Exception as e:
    print(f"[5] FAIL: {str(e)[:150]}")

# 6. 試 grading_vec
try:
    print(f"\n[6] compute_gv (min_points=10):")
    gv = cy.compute_gv(min_points=10, format='array')
    print(f"  GV: {gv}")
except Exception as e:
    print(f"[6] FAIL: {str(e)[:150]}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)