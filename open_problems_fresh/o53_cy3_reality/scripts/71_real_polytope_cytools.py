#!/usr/bin/env python3
"""
O53 路徑三: 用 CYTools 對真實 (36,98) polytope 計算 κ
==========================================================
用 Sage export 48 points → Polytope → triangulate → ToricVariety → CalabiYau → κ
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53 路徑三: 真實 polytope CYTools κ")
print("=" * 70)

from cytools import Polytope
from cytools.toricvariety import ToricVariety
from cytools.calabiyau import CalabiYau
from cytools.config import enable_experimental_features
enable_experimental_features()

# 讀取 Sage export 嘅 48 points
with open(os.path.join(BASE, 'cy36_98_sage_export.json')) as f:
    sage = json.load(f)
pts = np.array(sage['points'])
print(f"Sage points: {pts.shape}")

p = Polytope(pts)
print(f"Polytope: reflex={p.is_reflexive()}, h11={p.h11()}, h12={p.h12()}, chi={p.chi('M')}")
print(f"  n_vertices={len(p.vertices())}, n_points={len(p.points())}")

# triangulate
tri = p.triangulate()
print(f"Triangulation: {tri}")

# ToricVariety + CalabiYau
tv = ToricVariety(tri)
print(f"ToricVariety OK")
cy = CalabiYau(tv)
print(f"CY: h11={cy.h11()}, h12={cy.h12()}, chi={cy.chi()}")

# κ matrix
try:
    kappa = cy.compute_kappa_matrix()
    print(f"κ matrix: {kappa.shape}")
    out = os.path.join(BASE, 'cy36_98_cytools_kappa.json')
    with open(out, 'w') as f:
        json.dump({'kappa': kappa.tolist()}, f)
    print(f"✅ κ saved: {out}")
except Exception as e:
    print(f"κ FAIL: {type(e).__name__}: {e}")

# GW invariants
try:
    gws = cy.compute_gws()
    print(f"GW invariants: {gws}")
except Exception as e:
    print(f"GW FAIL: {type(e).__name__}: {str(e)[:150]}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)