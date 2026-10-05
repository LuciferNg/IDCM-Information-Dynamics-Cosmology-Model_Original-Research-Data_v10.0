#!/usr/bin/env python3
"""
O53 路徑三: CYTools 完整 κ 計算 + GW invariants
====================================================
用 HF polytope → triangulate → CalabiYau → κ_ijk
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

def read_poly_points(path):
    pts = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                continue
            pts.append([int(x) for x in parts])
    return np.array(pts, dtype=int)

print("=" * 70)
print("O53 路徑三: CYTools κ 計算")
print("=" * 70)

from cytools import Polytope
from cytools.calabiyau import CalabiYau

for name in ['cy36_98_hf', 'control_h11_36_h12_94']:
    path = os.path.join(BASE, name + '.poly')
    pts = read_poly_points(path)
    print(f"\n=== {name} ({pts.shape[0]} pts) ===")
    try:
        p = Polytope(pts)
        print(f"  reflex={p.is_reflexive()}, h11={p.h11()}, h12={p.h12()}")
        
        # triangulate
        tri = p.triangulate()
        print(f"  triangulated: {tri}")
        
        # ambient toric variety + CY
        cy = CalabiYau(tri)
        print(f"  CY h11={cy.h11()}, h12={cy.h12()}, chi={cy.chi()}")
        
        # intersection numbers
        try:
            kappa = cy.compute_kappa_matrix()
            print(f"  κ matrix: {kappa.shape}")
            # 存檔
            out = os.path.join(OUT, f"{name}_kappa.json")
            with open(out, 'w') as f:
                json.dump({'kappa': kappa.tolist() if hasattr(kappa, 'tolist') else kappa}, f)
            print(f"  ✅ κ saved: {out}")
        except Exception as e:
            print(f"  κ FAIL: {type(e).__name__}: {e}")
        
        # GW invariants (試)
        try:
            gws = cy.compute_gws()
            print(f"  GW: {len(gws)} invariants")
        except Exception as e:
            print(f"  GW FAIL: {type(e).__name__}: {str(e)[:100]}")
    except Exception as e:
        print(f"  FAIL: {type(e).__name__}: {e}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)