#!/usr/bin/env python3
"""
O70 — 33: Sage PPL on 46 facet-defining inequalities
====================================================
Kähler cone K = {t : M_facet·t ≥ 0}, 46 條 facet-defining。
用 Sage Polyhedron(ieqs) PPL backend — 46 條 vs 185 條, 應該可行。
"""
import os, sys, numpy as np
from sage.all import Polyhedron

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

M = np.load(os.path.join(DATA, "22_mori_cone_rays_32d.npy")).astype(int)
idx = np.load(os.path.join(DATA, "32_facet_defining_indices.npy"))
Mf = M[idx]
print(f"Facet-defining Mori rays: {Mf.shape}")

# Sage Polyhedron from inequalities Mf·t ≥ 0
# ieq = [b, -a] for a·x ≤ b;  Mf·t ≥ 0 → -Mf·t ≤ 0 → a=-Mf, b=0 → ieq = [0, Mf row]
ieqs = [tuple([0] + [int(x) for x in row]) for row in Mf]
print(f"Building Polyhedron with {len(ieqs)} ieqs in 32D (PPL)...")
P = Polyhedron(ieqs=ieqs, backend='ppl')
print(f"Dim: {P.dim()}, compact: {P.is_compact()}")

rays = P.rays()
print(f"\nExtreme rays: {len(rays)}")
rlist = []
for r in rays:
    v = np.array([float(x) for x in r.vector().list()])
    n = np.linalg.norm(v)
    if n > 0:
        rlist.append(v / n)
R = np.array(rlist)
np.save(os.path.join(DATA, "33_exact_extreme_rays_ppl.npy"), R)
print(f"Saved: {R.shape} → data/33_exact_extreme_rays_ppl.npy")
