#!/usr/bin/env python3
"""
O70 — 27: FAIL point 詳細檢查 — 係咪 numerical artifact?
========================================================
懷疑: LP min d·t s.t. Mt≥0, -1≤t≤1 嘅 optimum 喺 box vertex (t_j=±1),
norm 好大, in_cone 嘅 LP 因為 tolerance 話 FAIL 但其實係數值問題。
"""
import os, sys, numpy as np
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

M = np.load(os.path.join(DATA, "22_mori_cone_rays_32d.npy")).astype(float)
R = np.load(os.path.join(DATA, "15_all_rays.npy"))

def boundary_point(d):
    res = linprog(d, A_ub=-M, b_ub=np.zeros(len(M)), bounds=[(-1, 1)] * 32, method='highs')
    return res.x if res.success else None

def decompose(v, gens):
    """v = Σ a_i g_i, a≥0 — 回傳 coefficients + 誤差"""
    n = gens.shape[0]
    res = linprog(np.zeros(n), A_eq=gens.T, b_eq=v, bounds=[(0, None)] * n, method='highs')
    if res.success:
        err = np.max(np.abs(gens.T @ res.x - v))
        return res.x, err, True
    return None, np.inf, False

rng = np.random.default_rng(42)
fails_detail = []
for i in range(300):
    d = rng.standard_normal(32)
    t = boundary_point(d)
    if t is None:
        continue
    a, err, ok = decompose(t, R)
    if not ok:
        # 檢查: t 嘅 norm? entries 有冇 ±1?
        fails_detail.append((i, np.linalg.norm(t), np.abs(t).max(), t))
        if len(fails_detail) <= 4:
            print(f"\nFAIL #{i}: |t|={np.linalg.norm(t):.3f}, max|t_j|={np.abs(t).max():.3f}")
            print(f"  entries 喺 ±1: {np.sum(np.abs(np.abs(t)-1) < 1e-8)}/32")

print(f"\nTotal fails: {len(fails_detail)}")
if fails_detail:
    norms = [f[1] for f in fails_detail]
    print(f"fail points norm: min {min(norms):.2f}, max {max(norms):.2f}")

# 對 fail point: 試 normalize 後再 decompose (ray 係方向, scale 唔重要)
print(f"\n─── 試 normalize 後 decompose ───")
fixed = 0
for i, nrm, mx, t in fails_detail[:10]:
    tn = t / nrm  # 單位向量
    a, err, ok = decompose(tn, R)
    if ok:
        fixed += 1
        print(f"  #{i}: normalize 後 OK! err={err:.2e}")
    else:
        print(f"  #{i}: normalize 後仍然 FAIL err={err:.2e}")

print(f"\nfixed by normalization: {fixed}/{min(len(fails_detail), 10)}")
