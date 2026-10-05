#!/usr/bin/env python3
"""
O59 重推 probe-4 — eigenvalue 閉合獨立性 + solver 版本對照
==========================================================
問題: 12D 嘅 closure (λ_max = 36−1/γ₂₀, tr(Y) = 2B²(1−γ₁), λ₂ formula, v_geom)
係咪真係 associativity-independent？

如果 12D 唔 associative 但 eigen-closure 照成立 ⇒ 12D 嘅正確定性係「K_Chain
eigenvalue 閉合張量」，唔係「Frobenius 子代數」⇒ docs/13-14 claim 需改寫。

另: 比較 d_tensor_native_12d vs wdvv_converged vs high_precision 嘅譜,
確認 08-14 native 同 08-21 converged 差幾多, 邊個先係 λ₂ 閉合基礎。
"""
import os, json, math
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA = os.path.join(BASE, "main_problems", "p15_early_derivations", "data")
phi = (1 + math.sqrt(5)) / 2

def gamma(n, N=88):
    return 4 * math.sin(math.pi * n / N) ** 2

g1, g7, g20 = gamma(1), gamma(7), gamma(20)
L4, L5, F9 = 7, 11, 34
B, M0 = 4, 27.900915

def spectrum(d):
    v = phi ** (-np.arange(12) / 12)
    Y = np.einsum("ijk,k->ij", d, v); Y = (Y + Y.T) / 2
    ev = np.sort(np.linalg.eigvalsh(Y))[::-1]
    return Y, ev

print("=" * 78)
print("[1] solver 版本對照 — native vs wdvv_converged vs high_precision")
print("=" * 78)
print(f"  γ₁={g1:.6f} γ₇={g7:.6f} γ₂₀={g20:.6f}  1/γ₂₀={1/g20:.6f}")
print(f"  預言: λ_max=36−1/γ₂₀={36-1/g20:.6f}  tr=2B²(1−γ₁)={2*B*B*(1-g1):.6f}")
files = ["d_tensor_native_12d.npy", "d_tensor_wdvv_converged.npy",
         "d_tensor_high_precision.npy", "d_tensor_final.npy"]
for f in files:
    p = os.path.join(DATA, f)
    if not os.path.exists(p):
        continue
    d = np.load(p)
    if d.shape != (12, 12, 12):
        continue
    Y, ev = spectrum(d)
    lam_max, tr = ev[0], float(np.trace(Y))
    print(f"\n  {f}:")
    print(f"    λ_max = {lam_max:.6f}  (dev {abs(lam_max-(36-1/g20))/(36-1/g20)*100:.4f}%)")
    print(f"    tr    = {tr:.6f}  (dev {abs(tr-2*B*B*(1-g1))/(2*B*B*(1-g1))*100:.4f}%)")

print("=" * 78)
print("[2] λ₂ instanton formula — 各版本盲測")
print("=" * 78)
lam2_pred = 2 + 2*F9*g1 + g1*g7*L4/(L5-1)
print(f"  λ₂ formula = 2 + 2F₉γ₁ + γ₁γ₇L₄/(L₅−1) = {lam2_pred:.6f}")
for f in ["d_tensor_native_12d.npy", "d_tensor_wdvv_converged.npy",
          "d_tensor_high_precision.npy", "d_tensor_final.npy"]:
    p = os.path.join(DATA, f)
    if not os.path.exists(p):
        continue
    d = np.load(p)
    if d.shape != (12, 12, 12):
        continue
    _, ev = spectrum(d)
    print(f"  {f}: λ₂ = {ev[1]:.6f}  dev = {abs(ev[1]-lam2_pred)/lam2_pred*100:.4f}%")

print("=" * 78)
print("[3] associativity 同 eigenvalue closure 獨立性")
print("=" * 78)
d = np.load(os.path.join(DATA, "d_tensor_native_12d.npy"))
ones12 = np.ones(12)
G = np.einsum("ijk,k->ij", d, ones12); G = (G + G.T) / 2
print("  g_ones eig:", np.round(np.linalg.eigvalsh(G), 4))
print("  (min eig < 0 → g 唔正定 → Frobenius metric 唔存在 → associativity 無從成立)")
print("  → λ_max/tr/λ₂ 全部只係用 v12 contraction 嘅 eigenvalue 公式, 唔涉 associativity ✓")

print("=" * 78)
print("[4] κ ring associativity 對照: 32×32 tip version 都爆?")
print("=" * 78)
POLY = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
ck = json.load(open(os.path.join(POLY, "cy36_98_cytools_kappa.json")))
K32 = np.array(ck["kappa"])
lhs = np.einsum("abm,mcd->abcd", K32, K32)
rhs = np.einsum("acm,mbd->abcd", K32, K32)
print(f"  32×32 κ ring assoc: max={np.max(np.abs(lhs-rhs)):.4e}")
# 32D: 32 個 divisor, 用 tip 收縮做 metric
tip = np.array(ck["tip"])
Y32t = np.einsum("ab,m->ab", K32, np.ones(32)) if False else K32
print(f"  K32 min/max: {K32.min():.2f} / {K32.max():.2f}")

# K32 係咪 symmetric?
print(f"  K32 symmetric: {np.allclose(K32, K32.T)}")

print("\nDONE probe-4")