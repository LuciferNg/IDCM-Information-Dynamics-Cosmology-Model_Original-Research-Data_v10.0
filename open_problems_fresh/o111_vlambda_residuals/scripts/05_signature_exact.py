#!/usr/bin/env python3
"""
O111 攻堅 5: 精確 signature 分析 + Δ 有理數身份
================================================
修正在 script 04 嘅 signature 數錯問題
"""
import sys, os, math, json
import numpy as np

def factorize(n):
    """Simple prime factorization string"""
    if n < 2:
        return str(n)
    factors = []
    d = 2
    temp = abs(n)
    while d * d <= temp:
        while temp % d == 0:
            factors.append(d)
            temp //= d
        d += 1 if d == 2 else 2  # skip evens after 2
    if temp > 1:
        factors.append(temp)
    return "×".join(str(f) for f in factors)

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")

print("=" * 72)
print("O111 攻堅 5: 精確 signature + Δ 有理數身份")
print("=" * 72)

d = json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))
kappa = np.array(d["kappa"])
gamma36 = 4 * np.sin(np.pi * np.arange(1, 37) / 88) ** 2
gamma44 = 4 * np.sin(np.pi * np.arange(1, 45) / 88) ** 2
phi = (1 + math.sqrt(5)) / 2

Fg = np.einsum("ijk,i,j,k", kappa, gamma36, gamma36, gamma36) / 6.0
delta = Fg - 264
Y = np.einsum("ijk,k", kappa, gamma36)
V = Fg
dV = np.einsum("ijk,j,k", kappa, gamma36, gamma36) / 2.0
G = -Y/V + np.outer(dV, dV)/V**2

evY = np.linalg.eigvalsh(Y)
evG = np.linalg.eigvalsh(G)

# 用不同 threshold 睇 signature
print("\n[1] Y(γ) signature vs threshold")
for eps in [1e-12, 1e-10, 1e-8, 1e-6, 1e-4, 1e-2]:
    n_pos = np.sum(evY > eps)
    n_neg = np.sum(evY < -eps)
    n_zero = 36 - n_pos - n_neg
    print(f"  threshold {eps:.0e}: {n_pos} 正, {n_neg} 負, {n_zero} kernel")

print("\n[2] G(γ) signature vs threshold")
for eps in [1e-12, 1e-10, 1e-8, 1e-6, 1e-4, 1e-2]:
    n_pos = np.sum(evG > eps)
    n_neg = np.sum(evG < -eps)
    n_zero = 36 - n_pos - n_neg
    print(f"  threshold {eps:.0e}: {n_pos} 正, {n_neg} 負, {n_zero} kernel")

# 用 1e-8 做標準
eps = 1e-8
Y_pos = np.sum(evY > eps)
Y_neg = np.sum(evY < -eps)
Y_zero = 36 - Y_pos - Y_neg
G_pos = np.sum(evG > eps)
G_neg = np.sum(evG < -eps)
G_zero = 36 - G_pos - G_neg

print(f"\n  Y(γ) signature (1e-8): {Y_pos}+/{Y_neg}-/{Y_zero} kernel")
print(f"  G(γ) signature (1e-8): {G_pos}+/{G_neg}-/{G_zero} kernel")
print(f"  Y_pos = {Y_pos} = ?")
print(f"  Y_neg = {Y_neg} = ?")
print(f"  G_pos = {G_pos} = ?")
print(f"  G_neg = {G_neg} = ?")

# 睇 Y 嘅零本徵值 (近零)
print(f"\n  Y 近零本徵值 (|λ|<1e-4): {np.round(evY[np.abs(evY) < 1e-4], 8)}")
print(f"  Y 正本徵值 (全部): {np.round(sorted(evY[evY > 1e-8]), 4)}")
print(f"  Y 負本徵值 (全部): {np.round(sorted(evY[evY < -1e-8]), 4)}")

# ═══════════════════════════════════════════
# Δ 有理數分析
# ═══════════════════════════════════════════
print("\n" + "=" * 72)
print("Δ 有理數身份")
print("=" * 72)

# convergent 15: 4235787/51574657
cf = [0, 12, 5, 1, 2, 6, 12, 1, 2, 3, 3, 1, 1, 1, 25, 1195, 4, 1, 5, 1]
p = [0, 1]; q = [1, 0]
for i, a in enumerate(cf):
    p.append(a*p[-1] + p[-2])
    q.append(a*q[-1] + q[-2])
    if i >= 2:  # skip [0, 12, ...]
        pn, qn = p[-1], q[-1]
        val = pn/qn
        err = abs(val - delta)/delta
        if err > 1e-12:
            continue
        print(f"\n  ★ convergent {i+1}: {pn}/{qn} = {val:.15f}")
        print(f"    err = {err:.2e}")
        print(f"    numer = {pn} = {factorize(pn)}")
        print(f"    denom = {qn} = {factorize(qn)}")
        print(f"    Δ × denom = {delta * qn:.10f} (near int? {abs(delta*qn - round(delta*qn)):.2e})")

# 4235787/51574657 嘅分解
numer = 4235787
denom = 51574657
print(f"\n\n  Δ ≈ {numer}/{denom}")
print(f"  {numer} = {factorize(numer)}")
print(f"  {denom} = {factorize(denom)}")

# 睇 IDCM 數
idcm_nums = [2, 3, 4, 5, 7, 8, 11, 13, 17, 18, 19, 21, 25, 29, 33, 36, 44, 61, 66, 73, 88, 90, 98, 134, 178, 264, 283, 946]
for n in idcm_nums:
    r = delta * n
    print(f"  Δ × {n:4d} = {r:.10f} (near int? {abs(r - round(r)):.6f})")