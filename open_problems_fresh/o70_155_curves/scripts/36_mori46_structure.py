#!/usr/bin/env python3
"""
O70 — 36: 46 Mori rays rank 檢查 + 深層結構
============================================
1. 46 條 facet-defining Mori rays 嘅 rank (應該 32?)
2. 如果 rank < 32 → cone 有 redundancy/lineality 結構
3. 有冇 pair 係 scalar multiple? (redundant)
"""
import os, sys, numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

M = np.load(os.path.join(DATA, "22_mori_cone_rays_32d.npy")).astype(float)
idx = np.load(os.path.join(DATA, "32_facet_defining_indices.npy"))
Mf = M[idx].astype(int)

print(f"46 facet-defining Mori rays: {Mf.shape}")
print(f"rank: {np.linalg.matrix_rank(Mf.astype(float))}")

# 檢查 pair-wise collinearity
from itertools import combinations
collinear = []
for i, j in combinations(range(46), 2):
    a, b = Mf[i], Mf[j]
    # cross product magnitude (32D)
    if np.allclose(a, 0) or np.allclose(b, 0):
        continue
    # cos angle
    cosang = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    if abs(abs(cosang) - 1) < 1e-10:
        collinear.append((i, j, cosang))
print(f"collinear pairs: {len(collinear)}")
for c in collinear[:5]:
    print(f"  {c}")

# 每條 ray 嘅 norm & 結構
norms = np.linalg.norm(Mf, axis=1)
print(f"\nnorms: min {norms.min()}, max {norms.max()}")
# L1 norms
l1 = np.abs(Mf).sum(axis=1)
print(f"L1: min {l1.min()}, max {l1.max()}")

# 檢查: 每條 Mori ray 嘅 entries pattern (有冇 zeros)
nz = (Mf != 0).sum(axis=1)
print(f"nonzero entries per ray: min {nz.min()}, max {nz.max()}, median {np.median(nz)}")

# 46 嘅結構: 對應邊啲 curves?
# Mori ray index 對應 curve 邊類 (155 adjacency vs 30 extra)?
print(f"\nfacet-defining 嘅 Mori ray 原始 index: {idx}")
# 155 adjacency curves 同 30 extra 點分? 睇原始 185 嘅結構
# 用 curve volumes at t=1 嘅 sign 或者 volume magnitude 分?
# 由 Q matrix: Q[i] 係 curve i 嘅 volume gradient
Q = np.load(os.path.join(DATA, "22_Q_matrix_185x32.npy"))
print(f"\nQ 矩陣 (185×32) — 46 條 facet Mori rays 對應嘅 Q rows:")
# Mori ray 同 Q row 嘅 alignment?
Qn = Q / np.linalg.norm(Q, axis=1, keepdims=True)
Mfn = Mf / np.linalg.norm(Mf, axis=1, keepdims=True)
C = np.abs(Qn @ Mfn.T)  # 185×46
best = C.argmax(axis=0)  # 每條 Mori ray 最似邊條 Q row
scores = C.max(axis=0)
print(f"46 Mori rays 嘅 Q-row alignment (cos > 0.9): {(scores > 0.9).sum()}/46")
