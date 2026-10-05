#!/usr/bin/env python3
"""
O53 路徑三: 用 CYTools 本地算 κ_ijk
======================================
CYTools 可以本地 triangulate + 算 intersection numbers
用 HF 提取嘅 polytope (normal form)
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

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

# 讀取 control polytope
ctrl = read_poly_points(os.path.join(BASE, 'control_h11_36_h12_94.poly'))
print(f"control polytope: {ctrl.shape}")
print(f"  points: {ctrl[:3]}")

try:
    p = Polytope(ctrl)
    print(f"Polytope OK: reflex={p.is_reflexive()}, n_vertices={len(p.vertices())}, n_points={len(p.points())}")
    # 搵 CY
    cy = p.calabi_yau()
    print(f"CY: h11={cy.h11()}, h12={cy.h12()}")
    # 算 intersection numbers
    try:
        inter = cy.intersection_numbers()
        print(f"intersection numbers: {len(inter)} entries")
    except Exception as e:
        print(f"intersection FAIL: {type(e).__name__}: {e}")
except Exception as e:
    print(f"Polytope FAIL: {type(e).__name__}: {e}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)