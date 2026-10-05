#!/usr/bin/env python3
"""
O53: HF (36,98) vs Sage (36,98) — 同一 polytope?
====================================================
HF: 20 vertices → CYTools h11=43, h12=37
Sage: 48 points → CYTools h11=36, h12=98 ✅

檢查: HF 嘅 vertices 係咪 Sage polytope 嘅 dual / 或者等價
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53: HF vs Sage (36,98)")
print("=" * 70)

from cytools import Polytope

# Sage polytope (48 points)
with open(os.path.join(BASE, 'cy36_98_sage_export.json')) as f:
    sage = json.load(f)
pts_sage = np.array(sage['points'])
p_sage = Polytope(pts_sage)
print(f"Sage polytope: h11={p_sage.h11()}, h12={p_sage.h12()}")
print(f"  n_vertices={len(p_sage.vertices())}, n_points={len(p_sage.points())}")

# HF polytope (20 vertices)
verts_hf = []
with open(os.path.join(BASE, 'cy36_98_hf.poly')) as f:
    for line in f:
        line = line.strip()
        if line:
            verts_hf.append([int(x) for x in line.split()])
verts_hf = np.array(verts_hf)
p_hf = Polytope(verts_hf)
print(f"\nHF polytope: h11={p_hf.h11()}, h12={p_hf.h12()}")
print(f"  n_vertices={len(p_hf.vertices())}, n_points={len(p_hf.points())}")

# 比較: 兩個 polytope 係咪 linearly equivalent?
print(f"\n比較: HF vs Sage")
try:
    eq = p_hf.is_linearly_equivalent(p_sage)
    print(f"  linearly equivalent: {eq}")
except Exception as e:
    print(f"  is_linearly_equivalent FAIL: {e}")

try:
    aff = p_hf.is_affinely_equivalent(p_sage)
    print(f"  affinely equivalent: {aff}")
except Exception as e:
    print(f"  is_affinely_equivalent FAIL: {e}")

# HF 嘅 vertices 係咪喺 Sage 嘅 48 points 入面?
hf_set = {tuple(v) for v in verts_hf}
sage_set = {tuple(p) for p in pts_sage}
common = hf_set & sage_set
print(f"\n  HF 20 vertices 同 Sage 48 points 共同: {len(common)}")
print(f"  HF 獨有: {len(hf_set - sage_set)}")
print(f"  Sage 獨有: {len(sage_set - hf_set)}")

# HF 嘅 dual 呢?
p_hf_dual = p_hf.dual()
print(f"\nHF dual: h11={p_hf_dual.h11()}, h12={p_hf_dual.h12()}")
try:
    eq2 = p_hf_dual.is_linearly_equivalent(p_sage)
    print(f"  HF-dual vs Sage linearly equivalent: {eq2}")
except Exception as e:
    print(f"  FAIL: {e}")

# HF vertices 有冇喺 Sage dual points 入面?
try:
    dual_pts = p_hf_dual.points()
    dual_set = {tuple(p) for p in dual_pts}
    common2 = hf_set & dual_set
    print(f"\n  HF vertices 同 HF-dual points 共同: {len(common2)}")
except Exception as e:
    print(f"  FAIL: {e}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)