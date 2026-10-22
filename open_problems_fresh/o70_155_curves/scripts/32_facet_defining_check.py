#!/usr/bin/env python3
"""
O70 — 32: Facet-defining 檢查 + 決定性 extreme ray 數
=====================================================
1. 185 Mori rays 有幾多條真係 facet-defining (Kähler cone 嘅 facet normal)?
   一條 Mori ray m_i 係 facet-defining iff 存在 t: m_i·t=0, m_j·t>0 ∀j≠i
   → LP: max s s.t. M_{-i}·t ≥ s, m_i·t = 0, ||t||≤1; s>0?
2. 用 facet-defining subset 重新諗 extreme rays 數目
"""
import os, sys, numpy as np
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

M = np.load(os.path.join(DATA, "22_mori_cone_rays_32d.npy")).astype(float)
n_rays, dim = M.shape
print(f"Mori rays: {n_rays}×{dim}")

# 每條 Mori ray 係咪 facet-defining?
# m_i facet-defining ⇔ 存在 t 令 m_i·t = 0 且 m_j·t > 0 ∀ j≠i
# 即 cone {t: M t ≥ 0} 嘅 facet i 非空 (relative interior)
# 等價: 存在 t ∈ K 令 m_i·t = 0 但 m_j·t > 0 (j≠i)
# LP: max s  s.t. M_{-i}·t ≥ s·1, m_i·t = 0, -1 ≤ t ≤ 1
# s > 0 表示 facet i 存在

facet_defining = []
redundant = []
for i in range(n_rays):
    mask = np.ones(n_rays, dtype=bool)
    mask[i] = False
    M_others = M[mask]  # (n-1)×32
    # variables: [s, t(32)]
    # max s: minimize -s
    c = np.zeros(1 + dim)
    c[0] = -1
    # constraints: M_others @ t - s >= 0  =>  -M_others@t + s <= 0
    A_ub = np.hstack([np.ones((n_rays - 1, 1)), -M_others])
    b_ub = np.zeros(n_rays - 1)
    # equality: m_i @ t = 0
    A_eq = np.array([[0.0] + list(M[i])])
    b_eq = [0.0]
    bounds = [(None, None)] + [(-1, 1)] * dim
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                  bounds=bounds, method='highs')
    if res.success and -res.fun > 1e-7:
        facet_defining.append(i)
    else:
        redundant.append(i)

print(f"\nfacet-defining Mori rays: {len(facet_defining)}")
print(f"redundant: {len(redundant)}")
print(f"\nfacet-defining indices: {facet_defining}")
np.save(os.path.join(DATA, "32_facet_defining_indices.npy"), np.array(facet_defining))
np.save(os.path.join(DATA, "32_redundant_indices.npy"), np.array(redundant))
print("Saved.")
