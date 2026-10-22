#!/usr/bin/env python3
"""
O70 — 12: Kähler Cone Extreme Rays — 直接反演法
=================================================
使用 155 條 adjacency curves 嘅 32 個獨立 rows 來計算 cone extreme rays。
"""

import sys, os, math, json, numpy as np
import scipy.linalg
import cytools
from cytools import Polytope
from cytools.config import enable_experimental_features
enable_experimental_features()

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O70 12: Extreme Rays via 155 Adjacency Curves")
print("=" * 72)

# Load data
d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
pts = np.array(d["points"])
p = Polytope(pts)
tri = p.triangulate()
cy = tri.get_cy()
basis = cy.divisor_basis()
basis_0 = np.array([b-1 for b in basis])
print(f"Divisor basis: {len(basis)}")

# 155 adjacency curves in 32D (rank 29 — not enough!)
sr_set = set()
for s in d["sr_ideal"]:
    sr_set.add((min(s), max(s)))
adj = [(i, j) for i in range(1, 37) for j in range(i+1, 37) if (i, j) not in sr_set]
kappa = np.array(json.load(open(os.path.join(O53, "cy36_98_intersection_full.json"))).get("kappa"))
V_adj = np.array([kappa[:, i-1, j-1] for i, j in adj])  # 155×36
V_32 = V_adj[:, basis_0]  # 155×32
r_155 = np.linalg.matrix_rank(V_32)
print(f"155 adjacency curves rank in 32D: {r_155} (need 32)")

# Use FULL 185 curves (Q_ij) which has rank 32
print("Computing Q_ij (185×32)...")
t_test = phi ** (-np.arange(36))
t32 = np.array([t_test[b-1] for b in basis])
eps = 1e-5
Q = np.zeros((185, 32))
for j in range(32):
    tp = t32.copy(); tm = t32.copy()
    tp[j] += eps; tm[j] -= eps
    cvp = np.array(cy.compute_curve_volumes(tp))
    cvm = np.array(cy.compute_curve_volumes(tm))
    Q[:, j] = (cvp - cvm) / (2*eps)

rank_Q = np.linalg.matrix_rank(Q)
print(f"Q_ij rank: {rank_Q}/32")

# Find 32 independent rows from Q via QR
Qn = Q / (np.linalg.norm(Q, axis=1, keepdims=True) + 1e-15)
_, _, piv = scipy.linalg.qr(Qn.T, pivoting=True)
rows = piv[:32]
print(f"Selected rows from Q: {sorted(rows)}")

# Build 32×32 basis matrix
Vb = Q[rows]  # 32×32
cond_Vb = np.linalg.cond(Vb)
print(f"Vb cond: {cond_Vb:.2f}")

# Inverse
Vb_inv = np.linalg.inv(Vb)

# Compute extreme rays and check both signs
rays = []
for k in range(32):
    ek = np.zeros(32); ek[k] = 1.0
    for sign in [1, -1]:
        t = sign * Vb_inv @ ek
        t = t / np.linalg.norm(t)
        if np.all(V_32 @ t > -1e-6):
            rays.append((k, sign, t))
            break

print(f"Valid extreme rays: {len(rays)}/32")

# Analyze the rays
if len(rays) > 0:
    R = np.array([r[2] for r in rays])
    rank_R = np.linalg.matrix_rank(R)
    print(f"Rank of rays: {rank_R}/{len(rays)}")
    
    # Already computed Q earlier
    # Check each ray against ALL 185 constraints
    in_cone = []
    for k, (idx, sgn, t) in enumerate(rays):
        vols = Q @ t
        if np.all(vols > -1e-6):
            in_cone.append(k)
    print(f"Rays in full cone: {len(in_cone)}/32")
    
    # Save
    np.save(os.path.join(os.path.dirname(__file__), "..", "data", "12_extreme_rays.npy"), R)
    if len(rays) == 32 and rank_R == 32:
        print("✅ Full 32D cone spanned by 32 extreme rays!")
    else:
        print(f"⚠️ Only {len(rays)} rays, rank {rank_R}")

print("Done.")