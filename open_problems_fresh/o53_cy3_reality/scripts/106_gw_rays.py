#!/usr/bin/env python3
"""
O53 方向①: GW/GV invariants (修正版)
========================================
用 mori_cone_cap().extremal_rays() 做 mcap_generators
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 70)
print("O53: GW/GV invariants (extremal rays)")
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

# 1. extremal rays
mcap = cy.mori_cone_cap()
try:
    rays = mcap.extremal_rays()
    rays = np.array(rays)
    print(f"[1] extremal rays: {rays.shape}")
except Exception as e:
    print(f"[1] extremal_rays FAIL: {str(e)[:100]}")
    rays = None

# 2. GW invariants
if rays is not None:
    try:
        print(f"\n[2] compute_gw (extremal rays, max_deg=2):")
        gw = cy.compute_gw(mcap_generators=rays, max_deg=2)
        print(f"  GW: {gw}")
    except Exception as e:
        print(f"[2] compute_gw FAIL: {str(e)[:200]}")

    try:
        print(f"\n[3] compute_gv (extremal rays, max_deg=2):")
        gv = cy.compute_gv(mcap_generators=rays, max_deg=2)
        print(f"  GV: {gv}")
    except Exception as e:
        print(f"[3] compute_gv FAIL: {str(e)[:200]}")

# 3. curve volumes — 用 tip
try:
    tip = cy.toric_kahler_cone().tip_of_stretched_cone(1)
    print(f"\n[4] compute_curve_volumes (tip):")
    cv = cy.compute_curve_volumes(tip)
    print(f"  curve volumes: {cv}")
except Exception as e:
    print(f"[4] compute_curve_volumes FAIL: {str(e)[:150]}")

# 4. divisor volumes
try:
    print(f"\n[5] compute_divisor_volumes (tip):")
    dv = cy.compute_divisor_volumes(tip)
    print(f"  divisor volumes: {dv}")
except Exception as e:
    print(f"[5] compute_divisor_volumes FAIL: {str(e)[:150]}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)