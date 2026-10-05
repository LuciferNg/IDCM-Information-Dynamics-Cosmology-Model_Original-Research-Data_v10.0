#!/usr/bin/env python3
"""O146 §10 審計: CKM/PMNS beat/beat 公式 — 後驗搜索 vs 結構痕跡
=================================================================
審計 main_problems/p15_early_derivations/docs/ckm_derivation.md + pmns_derivation.md 嘅 beat/beat「閉合」:
1. 係咪後驗搜索產物? (83 萬拍頻比密佈 → 1e-7 匹配必然?)
2. 有冇結構痕跡? (d=1 相鄰對超額, 分子細/分母大傾向, 群速度身份)
"""
import math
import numpy as np
import json

w = lambda n: 2*math.sin(math.pi*n/88)
beat = lambda i,j: abs(w(i)-w(j))

# ============ 1. 拍頻比集合密度 ============
pairs = [(i,j) for i in range(1,45) for j in range(i+1,45)]
B = np.array(sorted(beat(i,j) for i,j in pairs))
R = np.array([b1/b2 for b1 in B for b2 in B if b2 > 1e-6])
R = R[R < 10]
R.sort()
print(f"拍頻比集合: {len(R)} 個, 範圍 [{R.min():.4f}, {R.max():.4f}]")
print(f"平均間距中位數: {np.median(np.diff(R)):.2e}")

# 隨機目標 δ_min
rng = np.random.default_rng(42)
targets = rng.uniform(0.01, 2.0, 2000)
idx = np.searchsorted(R, targets)
idx = np.clip(idx, 1, len(R)-1)
d_rand = np.minimum(np.abs(R[idx]-targets), np.abs(R[idx-1]-targets))

# 真實目標
real = [0.231604, 0.041563, 0.003508, 0.225, 0.04182, 0.00369, 0.83,
        0.659629, 0.906745, 1.150368, 0.1485]
idx = np.searchsorted(R, np.array(real))
idx = np.clip(idx, 1, len(R)-1)
d_real = np.minimum(np.abs(R[idx]-np.array(real)), np.abs(R[idx-1]-np.array(real)))

print(f"\n隨機目標 δ_min: 中位數 {np.median(d_rand):.2e}")
print(f"真實目標 δ_min: 中位數 {np.median(d_real):.2e}")
print(f"比例: {np.median(d_rand)/np.median(d_real):.1f}x")

# ============ 2. 模式對結構 ============
formulas = [
    ('CKM tanθ₁₂', 0.231604, (5,6), (19,25)),
    ('CKM tanθ₂₃', 0.041563, (33,35), (3,22)),
    ('CKM sinθ₁₃', 0.003508, (42,43), (10,31)),
    ('CKM λ', 0.22500, (25,35), (6,37)),
    ('CKM V_cb', 0.04182, (13,14), (6,37)),
    ('CKM V_ub', 0.00369, (41,42), (3,37)),
    ('CKM A', 0.830, (16,35), (10,28)),
    ('PMNS tanθ₁₂', 0.659629, (4,13), (9,25)),
    ('PMNS tanθ₂₃', 0.906745, (11,23), (12,26)),
    ('PMNS tanθ₂₃b', 1.150368, (4,14), (22,44)),
    ('PMNS sinθ₁₃', 0.1485, (25,29), (3,20)),
]
print(f"\n{'公式':>14} {'值':>9} {'分子d':>5} {'分母d':>5} {'分子rank%':>9} {'分母rank%':>9}")
num_ranks, den_ranks, num_d, den_d = [], [], [], []
for name, obs, p1, p2 in formulas:
    r1 = np.searchsorted(B, beat(*p1))/946*100
    r2 = np.searchsorted(B, beat(*p2))/946*100
    d1 = abs(p1[0]-p1[1]); d2 = abs(p2[0]-p2[1])
    num_ranks.append(r1); den_ranks.append(r2); num_d.append(d1); den_d.append(d2)
    print(f"{name:>14} {obs:>9.5f} {d1:>5d} {d2:>5d} {r1:>8.0f}% {r2:>8.0f}%")

print(f"\n分子 rank 中位數: {np.median(num_ranks):.0f}% (期望 50%)")
print(f"分母 rank 中位數: {np.median(den_ranks):.0f}% (期望 50%)")
n_lt = sum(1 for a,b in zip(num_ranks,den_ranks) if a<b)
print(f"分子<分母: {n_lt}/{len(formulas)}")

# ============ 3. d=1 超額統計 (超幾何) ============
used_pairs = [p for _,_,p1,p2 in formulas for p in (p1,p2)]
n_d1 = sum(1 for i,j in used_pairs if abs(i-j)==1)
print(f"\nd=1 (相鄰) 對: {n_d1}/{len(used_pairs)} (隨機期望 {43/946*len(used_pairs):.1f})")
from math import comb
k_obs = n_d1; n_tot = len(used_pairs)
p_hyper = sum(comb(43,k)*comb(903,n_tot-k)/comb(946,n_tot) for k in range(k_obs, n_tot+1))
print(f"超幾何 p(≥{k_obs} d=1): {p_hyper:.4f}")

# ============ 4. 群速度身份 ============
ok_vg = all(abs(beat(n,n+1) - 4*math.sin(math.pi/176)*math.cos((2*n+1)*math.pi/176)) < 1e-12
            for n in range(1,44))
print(f"\nbeat(n,n+1) = 4sin(π/176)·v_g(n+1/2) 恆等式 (43/43): {ok_vg}")

res = {
    "ratio_density": {"n": len(R), "median_spacing": float(np.median(np.diff(R)))},
    "random_vs_real_dmin": {"random_median": float(np.median(d_rand)),
                            "real_median": float(np.median(d_real))},
    "mode_pair_stats": {"num_rank_median_pct": float(np.median(num_ranks)),
                        "den_rank_median_pct": float(np.median(den_ranks)),
                        "num_lt_den": n_lt, "n_formulas": len(formulas),
                        "d1_count": n_d1, "d1_expected": 43/946*len(used_pairs),
                        "hypergeometric_p": float(p_hyper)},
    "vg_identity": ok_vg,
}
import os
out = os.path.join(os.path.dirname(__file__), "..", "data", "10_ckm_pmns_beat_audit.json")
with open(out, "w") as f:
    json.dump(res, f, indent=2, default=lambda o: float(o) if hasattr(o,'item') else o)
print(f"\n結果: {out}")
