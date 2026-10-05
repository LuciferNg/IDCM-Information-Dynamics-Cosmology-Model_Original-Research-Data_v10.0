#!/usr/bin/env python3
"""
O53 方向①: GW invariants — 輕量模式
========================================
compute_gw 全計算太慢 (>5min)
試 min_points 模式 (只計幾個點)
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53: GW 輕量模式")
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

# 輕量: min_points=3
try:
    print("[1] compute_gw(min_points=3):")
    gw = cy.compute_gw(min_points=3, format='array')
    print(f"  GW: {gw}")
except Exception as e:
    print(f"[1] FAIL: {str(e)[:150]}")

# 試 mcap 用少啲 rays (前幾個)
try:
    mcap = cy.mori_cone_cap()
    rays = np.array(mcap.extremal_rays())
    print(f"\n[2] extremal rays: {rays.shape}")
    # 試用前 5 個 rays
    print(f"  試 compute_gw 用前 5 rays...")
    gw2 = cy.compute_gw(mcap_generators=rays[:5], format='array')
    print(f"  GW(5 rays): {gw2}")
except Exception as e:
    print(f"[2] FAIL: {str(e)[:150]}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)