#!/usr/bin/env python3
"""
O70 — 37: 3732 rays 結構分析 — active-facet 數分佈
====================================================
3732 條 extreme rays 嘅 active facet 數 (31-45) 分佈,
有冇對稱群/pattern? 每條 ray 嘅 coordinate 結構?
"""
import os, sys, numpy as np
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

M = np.load(os.path.join(DATA, "22_mori_cone_rays_32d.npy")).astype(float)
idx = np.load(os.path.join(DATA, "32_facet_defining_indices.npy"))
Mf = M[idx]
R = np.load(os.path.join(DATA, "33_exact_extreme_rays_ppl.npy"))

# active facet counts
vals = Mf @ R.T
n_active = (np.abs(vals) < 1e-9).sum(axis=0)
cnt = Counter(n_active)
print("─── active-facet 數分佈 ───")
for k in sorted(cnt):
    print(f"  {k} facets: {cnt[k]} rays")

# 每條 ray 嘅 nonzero coordinate pattern
nz = (np.abs(R) > 1e-9).sum(axis=1)
cnt2 = Counter(nz)
print(f"\n─── nonzero coordinate 數分佈 ───")
for k in sorted(cnt2):
    print(f"  {k} coords: {cnt2[k]} rays")

# 有冇 coordinate 永遠 0? (ray 喺 subspace)
always_zero = np.where((np.abs(R) < 1e-9).all(axis=0))[0]
print(f"\n永遠 0 嘅 coordinates: {always_zero}")

# 每條 Mori facet 有幾多 rays active 喺上面 (facet size)
facet_size = (np.abs(vals) < 1e-9).sum(axis=1)
print(f"\n─── 每條 facet 嘅 ray 數 ───")
for i, s in enumerate(facet_size):
    print(f"  facet {idx[i]} (Mori ray {idx[i]}): {s} rays")
