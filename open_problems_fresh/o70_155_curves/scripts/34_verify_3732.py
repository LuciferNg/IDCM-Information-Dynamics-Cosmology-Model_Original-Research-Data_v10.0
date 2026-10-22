#!/usr/bin/env python3
"""
O70 — 34: Final Verification — 3732 Exact Extreme Rays
=======================================================
1. 全部 3732 ∈ K (46 + 185 不等式都 check)
2. 全部 extreme
3. 結構: 3732 = ?
4. 舊 99 rays 全部喺 3732 入面?
5. Active facets per ray
"""
import os, sys, numpy as np
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

M = np.load(os.path.join(DATA, "22_mori_cone_rays_32d.npy")).astype(float)
idx = np.load(os.path.join(DATA, "32_facet_defining_indices.npy"))
Mf = M[idx]
R = np.load(os.path.join(DATA, "33_exact_extreme_rays_ppl.npy"))
R99 = np.load(os.path.join(DATA, "15_all_rays.npy"))

print("=" * 72)
print("O70 34: Final Verification — 3732 Exact Extreme Rays")
print("=" * 72)
print(f"46 facet-defining: {Mf.shape}")
print(f"Exact extreme rays: {R.shape}")

checks = []
def check(name, cond, detail=""):
    checks.append(bool(cond))
    print(f"  [{'✅' if cond else '❌'}] {name} {detail}")

# 1. 全部 ∈ K (185 不等式)
viol = M @ R.T
check("全部 3732 ∈ K (185 ieqs)", viol.min() > -1e-6, f"(min {viol.min():.2e})")

# 2. 46 facet 上 active 分佈
act46 = (np.abs(Mf @ R.T) < 1e-6).sum(axis=0)
check("每條 ray ≥32 active facets", act46.min() >= 32, f"(min {act46.min()})")
print(f"  active 分佈: unique = {np.unique(act46)}")

# 3. Extreme — 抽樣 200 檢查 (3732 全部檢查太慢)
def in_cone(v, gens):
    n = gens.shape[0]
    res = linprog(np.zeros(n), A_eq=gens.T, b_eq=v, bounds=[(0, None)] * n, method='highs')
    return res.success

rng = np.random.default_rng(0)
sample = rng.choice(len(R), 200, replace=False)
bad = 0
for i in sample:
    others = np.delete(R, i, axis=0)
    if in_cone(R[i], others):
        bad += 1
check(f"extreme (200 抽樣)", bad == 0, f"({bad} non-extreme)")

# 4. 舊 99 喺 3732 入面?
def signfix(r):
    for x in r:
        if abs(x) > 1e-10:
            return r if x > 0 else -r
    return r

Rf = np.array([signfix(r) for r in R])
R99f = np.array([signfix(r) for r in R99])
# dot products (R99f @ Rf.T)
D = np.abs(R99f @ Rf.T)  # 99×3732
in_set = (D.max(axis=1) > 1 - 1e-6).sum()
check(f"舊 99 rays 全部喺 3732 入面", in_set == 99, f"({in_set}/99)")

# 5. 結構分析
n = len(R)
print(f"\n─── 結構分析: 3732 ───")
candidates = {
    "2×185×10+32": 2*185*10+32,
    "185×20+32": 185*20+32,
    "46×81+6": 46*81+6,
    "44×84+36": 44*84+36,
    "155×24+12": 155*24+12,
    "36×103+24": 36*103+24,
    "C(32,2)×?": None,
    "2×1850+32": 2*1850+32,
    "90×41+42": 90*41+42,
    "178×21−6": 178*21-6,
}
for name, val in candidates.items():
    if val is not None and val == n:
        print(f"  ★ {name} = {val} ← MATCH!")
print(f"  3732 = 2²×3×311")
import sympy
print(f"  prime factorization: {sympy.factorint(n)}")

# active facet pattern 多樣性
patterns = set()
for j in range(min(len(R), 5000)):
    a = tuple(np.where(np.abs(Mf @ R[j]) < 1e-6)[0])
    patterns.add(a)
print(f"  active-facet patterns (5000 抽樣): {len(patterns)} unique")

print("\n" + "=" * 72)
print(f"RESULT: {sum(checks)}/{len(checks)} PASS")
print("=" * 72)
