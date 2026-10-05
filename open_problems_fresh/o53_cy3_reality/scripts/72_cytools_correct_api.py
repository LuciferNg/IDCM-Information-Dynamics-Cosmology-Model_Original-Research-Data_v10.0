#!/usr/bin/env python3
"""
O53 路徑三: CYTools 完整計算 (正確 API)
==========================================
t.get_cy() → κ matrix + GW invariants
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53 路徑三: CYTools 完整計算")
print("=" * 70)

from cytools import Polytope
from cytools.config import enable_experimental_features
enable_experimental_features()

with open(os.path.join(BASE, 'cy36_98_sage_export.json')) as f:
    sage = json.load(f)
pts = np.array(sage['points'])
p = Polytope(pts)
print(f"Polytope: h11={p.h11()}, h12={p.h12()}")

tri = p.triangulate()
cy = tri.get_cy()
print(f"CY: h11={cy.h11()}, h12={cy.h12()}, chi={cy.chi()}")

# Kähler cone tip
try:
    tip = cy.toric_kahler_cone().tip_of_stretched_cone(1)
    print(f"Kähler cone tip: {tip}")
except Exception as e:
    print(f"cone FAIL: {e}")
    tip = None

# κ matrix at tip
if tip is not None:
    try:
        kappa = cy.compute_kappa_matrix(tip)
        print(f"κ matrix: {kappa.shape}")
        out = os.path.join(BASE, 'cy36_98_cytools_kappa.json')
        with open(out, 'w') as f:
            json.dump({'kappa': kappa.tolist(), 'tip': tip.tolist()}, f)
        print(f"✅ κ saved: {out}")
    except Exception as e:
        print(f"κ FAIL: {type(e).__name__}: {e}")

# GW invariants
try:
    mcap = cy.toric_mori_cone().mcap_generators()
    print(f"mori cone generators: {len(mcap)}")
    gws = cy.compute_gws(mcap_generators=mcap, max_deg=5)
    print(f"GW invariants: {gws}")
except Exception as e:
    print(f"GW FAIL: {type(e).__name__}: {str(e)[:150]}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)