#!/usr/bin/env python3
"""
O53 路徑一/二匯合: k 值 cluster + 3×12D sector
==================================================
k = -ln(J*)/ln(φ) ∈ [6.77, 13.99]

測試:
  1. k 值 3-cluster? (對應 3×12D sector)
  2. 36 個 k 值嘅原始順序 — 有冇 block 結構?
  3. k 同 Y 嘅 3×12D block 對應?
"""
import os, json, math, sys
import numpy as np
from scipy import stats
from scipy.optimize import minimize

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2
lnphi = math.log(phi)

with open(os.path.join(BASE, "Jstar_36D.json")) as f:
    jstar = json.load(f)
J0 = np.array(jstar['Jstar_36D'])
lnJ = np.log(J0)
k = -lnJ/lnphi

print("=" * 70)
print("O53 匯合: k 值 cluster 分析")
print("=" * 70)

# --- [1] 原始順序 k 值 (36 個, 依 moduli 索引) ---
print("\n[1] k 值原始順序:")
for i in range(0, 36, 6):
    print(f"    {i:2d}-{i+5:2d}: " + " ".join(f"{v:6.2f}" for v in k[i:i+6]))

# --- [2] 3×12 block 嘅 k 統計 ---
print("\n[2] 3×12 block k 統計:")
for g in range(3):
    kb = k[g*12:(g+1)*12]
    print(f"    Block {g}: mean k = {kb.mean():.2f}, std = {kb.std():.2f}, min = {kb.min():.2f}, max = {kb.max():.2f}")
    print(f"      k 值: {np.array2string(np.sort(kb), precision=2)}")

# --- [3] k 同 3×12D 有冇對應? ---
print("\n[3] k 分佈 (3 組):")
k_sorted = np.sort(k)
# 試 3 等分
q1, q2 = np.quantile(k, [1/3, 2/3])
g1 = k[k < q1]
g2 = k[(k >= q1) & (k < q2)]
g3 = k[k >= q2]
print(f"    q33 = {q1:.2f}, q66 = {q2:.2f}")
print(f"    G1: {len(g1)} 個, mean = {g1.mean():.2f}")
print(f"    G2: {len(g2)} 個, mean = {g2.mean():.2f}")
print(f"    G3: {len(g3)} 個, mean = {g3.mean():.2f}")

# --- [4] 原始 block 嘅 k 有冇分離? ---
print("\n[4] 原始 3×12 block k 分離度:")
b_means = [k[g*12:(g+1)*12].mean() for g in range(3)]
b_stds = [k[g*12:(g+1)*12].std() for g in range(3)]
print(f"    Block means: {[f'{m:.2f}' for m in b_means]}")
print(f"    Block stds: {[f'{s:.2f}' for s in b_stds]}")
# ANOVA
b0, b1, b2 = k[0:12], k[12:24], k[24:36]
F, p = stats.f_oneway(b0, b1, b2)
print(f"    ANOVA F = {F:.2f}, p = {p:.4f}")
print(f"    → {'✅ 3 block k 顯著唔同' if p < 0.05 else '❌ 3 block k 冇顯著差異'}")

# --- [5] 全體 k 嘅混合模型 ---
print("\n[5] k 嘅 3-Gaussian 混合:")
from scipy.optimize import minimize
def neg_ll(params):
    mu1, s1, mu2, s2, mu3, s3, w1, w2 = params
    w3 = 1 - w1 - w2
    if s1 < 0.01 or s2 < 0.01 or s3 < 0.01 or w3 < 0:
        return 1e9
    l1 = stats.norm.pdf(k, mu1, s1)
    l2 = stats.norm.pdf(k, mu2, s2)
    l3 = stats.norm.pdf(k, mu3, s3)
    return -np.sum(np.log(w1*l1 + w2*l2 + w3*l3 + 1e-300))

best = None
for seed in range(5):
    rng = np.random.default_rng(seed)
    x0 = [rng.uniform(7, 13), rng.uniform(0.3, 1.5), rng.uniform(7, 13), 
          rng.uniform(0.3, 1.5), rng.uniform(7, 13), rng.uniform(0.3, 1.5),
          rng.uniform(0.2, 0.4), rng.uniform(0.2, 0.4)]
    res = minimize(neg_ll, x0, method='Nelder-Mead', 
                   options={'maxiter': 5000, 'xatol': 1e-6})
    if best is None or res.fun < best.fun:
        best = res
print(f"    3-Gaussian fit:")
mu1, s1, mu2, s2, mu3, s3, w1, w2 = best.x
w3 = 1 - w1 - w2
print(f"    G1: μ={mu1:.2f}, σ={s1:.2f}, w={w1:.2f}")
print(f"    G2: μ={mu2:.2f}, σ={s2:.2f}, w={w2:.2f}")
print(f"    G3: μ={mu3:.2f}, σ={s3:.2f}, w={w3:.2f}")
print(f"    → {'✅ 3 cluster 分離' if min(s1,s2,s3) < 1.0 and min(mu1,mu2,mu3) < max(mu1,mu2,mu3) - 2 else '❌ 無 3 cluster'}")

# --- [6] k 同 Y 本徵值相關? ---
print("\n[6] k 同 Y 3×12D block 相關?")
# 如果 k 值 3 組對應 3 個 block, 咁 k 嘅 3 組同 block 0/1/2 對應?
print(f"    Block mean k: {[f'{m:.2f}' for m in b_means]}")
print(f"    → 如果 block 0 係最大 k (最細 J*), 即最細 moduli?")

print("\n" + "=" * 70)
print("分析完成")
print("=" * 70)
