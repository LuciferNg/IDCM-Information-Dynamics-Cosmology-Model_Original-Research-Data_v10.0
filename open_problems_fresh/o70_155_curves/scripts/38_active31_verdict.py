#!/usr/bin/env python3
"""
O70 — 38: active=31 "anomaly" 最終判決
=======================================
理論: 32D pointed cone 嘅 extreme ray (1-dim face) 嘅 active facet rows
rank 必須 = 31 (= 32−1), 因為 ray 方向 r 喺 active rows 嘅 null space。
active 數目 ≥ 31, 多過 31 嘅 facets 係 dependent (redundant at that ray)。

Script 34 check "≥32" 係錯 threshold — 正確係 rank ≥ 31。
驗證: 每條 ray 嘅 active rows rank 係咪 = 31。
"""
import os, sys, numpy as np
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

M = np.load(os.path.join(DATA, "22_mori_cone_rays_32d.npy")).astype(float)
idx = np.load(os.path.join(DATA, "32_facet_defining_indices.npy"))
Mf = M[idx]  # 46×32
R = np.load(os.path.join(DATA, "33_exact_extreme_rays_ppl.npy"))  # 3732×32
print(f"46 facets × 3732 rays")

vals = Mf @ R.T  # 46×3732
n_active = (np.abs(vals) < 1e-9).sum(axis=0)
print(f"active-facet 數分佈: {dict(sorted(Counter(n_active).items()))}")

# 每條 ray: active rows 嘅 rank (應該全部 = 31)
ranks = []
bad = []
for j in range(len(R)):
    act = np.where(np.abs(vals[:, j]) < 1e-9)[0]
    if len(act) >= 31:
        rk = np.linalg.matrix_rank(Mf[act])
    else:
        rk = -1
    ranks.append(rk)
    if rk != 31:
        bad.append((j, len(act), rk))

ranks = np.array(ranks)
print(f"\nactive-rows rank 分佈: {dict(sorted(Counter(ranks).items()))}")
print(f"rank=31 (正確 extreme 1-dim face): {(ranks==31).sum()}/{len(R)}")
if bad:
    print(f"\n⚠️ 異常 rays (rank≠31): {len(bad)}")
    for j, na, rk in bad[:5]:
        print(f"  ray {j}: active={na}, rank={rk}")
else:
    print(f"\n✅ 全部 3732 rays 嘅 active facet rows rank = 31")
    print(f"   → 全部係 genuine 1-dim extreme faces")
    print(f"   → 'active=31 anomaly' = 正常 (我 script 34 threshold 錯)")

# 補充: 確認 active rows 嘅 null space 就係 ray 方向 (±)
from scipy.linalg import null_space
ok_null = 0
for j in range(0, len(R), 100):  # 抽樣
    act = np.where(np.abs(vals[:, j]) < 1e-9)[0]
    ns = null_space(Mf[act])
    if ns.shape[1] == 1:
        v = ns[:, 0]
        v = v / np.linalg.norm(v)
        r = R[j]
        if abs(abs(v @ r) - 1) < 1e-6:
            ok_null += 1
print(f"\n抽樣驗證: active rows 嘅 null space = ray 方向: {ok_null}/{len(range(0,len(R),100))}")
