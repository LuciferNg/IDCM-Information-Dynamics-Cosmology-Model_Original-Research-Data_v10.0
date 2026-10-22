#!/usr/bin/env python3
"""
O70 — 35: active=31 anomaly 檢查
================================
有一條 ray 只 active 31 facets (tol 1e-6)。檢查係咪 numerical artifact:
— 用更緊 tolerance 睇嗰條「第 32 條」不等式嘅值
"""
import os, sys, numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

M = np.load(os.path.join(DATA, "22_mori_cone_rays_32d.npy")).astype(float)
idx = np.load(os.path.join(DATA, "32_facet_defining_indices.npy"))
Mf = M[idx]
R = np.load(os.path.join(DATA, "33_exact_extreme_rays_ppl.npy"))

vals = Mf @ R.T  # 46 × 3732
n_active = (np.abs(vals) < 1e-6).sum(axis=0)
anom = np.where(n_active < 32)[0]
print(f"active < 32 嘅 rays: {len(anom)}")
for j in anom:
    v = vals[:, j]
    print(f"\nray #{j}: active(tol=1e-6) = {n_active[j]}")
    # 睇最接近 0 嘅 5 個值
    order = np.argsort(np.abs(v))
    print(f"  最接近 0 嘅值:")
    for k in order[:8]:
        print(f"    facet {idx[k]}: {v[k]:.3e}")
    # 真正 active 應該 exactly 0 (PPL exact) — 點解有 1e-7 級?
    # 可能: float conversion 誤差
    print(f"  |v| < 1e-9 數目: {(np.abs(v) < 1e-9).sum()}")
    print(f"  |v| < 1e-12 數目: {(np.abs(v) < 1e-12).sum()}")
