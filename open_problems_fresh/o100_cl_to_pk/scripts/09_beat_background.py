#!/usr/bin/env python3
"""
O100-P1: Beat 背景 σ8 — 全 44-mode 投影權重推導
================================================
已知 9 峰 w_n² = A_m/G_n(0) ≈ 0.64 ± 0.20 (常數, 冇指數衰減!)
非選中 mode 假設: w_n² = 0.64 × f, f ∈ [0.05, 0.3] (K_Tree 側分支抑壓)
Planck C_ℓ 峰間/包絡比 ≈ 0.6 → 提示 f ≈ 0.2-0.3
"""
import numpy as np
R_world = 4129.64; h = 0.6727; D1 = 5750.0; Tcmb = 2.72548e6; R8 = 8.0

def top_hat(x): return 3*(np.sin(x)-x*np.cos(x))/x**3

# 9 峰已知值
n_sel = [5, 12, 18, 23, 25, 30, 32, 33]
A_m = [1.0, 4/9, 4/9, 9/49, 3/14, 16/121, 1/7, 1/9]
G_n = [1/(4*np.sin(n*np.pi/88)) for n in n_sel]
wn2_sel = np.array([A_m[i] / G_n[i] for i in range(len(n_sel))])
w2_avg = np.mean(wn2_sel)
print(f"w_n² (9 峰) = {np.round(wn2_sel, 3)}")
print(f"平均 w² = {w2_avg:.3f}")

# 全 44 mode 計算
ns = np.arange(1, 45)
Gs = np.array([1/(4*np.sin(n*np.pi/88)) for n in ns])
ells = 44 * ns
ks = ells / R_world / h
Ws = np.array([top_hat(k*R8) for k in ks])

def compute_sigma8(f):
    """f = 非選中 mode 嘅 w_n² / w²_avg 比"""
    s8sq = 0.0
    for i, n in enumerate(ns):
        if n in n_sel:
            wn = wn2_sel[n_sel.index(n)]
        else:
            wn = w2_avg * f
        A = wn * Gs[i]  # 絕對振幅 A_n = w_n²·G_n(0)
        # 歸一化: A/A₁ = A/(w₅²·G₅)
        A_rel = A / (wn2_sel[0] * Gs[4])  # A₁ = 1.0
        if A_rel <= 0: continue
        D_ell = D1 * A_rel
        C_ell = D_ell * 2*np.pi / (ells[i]*(ells[i]+1))
        vT = C_ell * (2*ells[i]+1) / (4*np.pi * Tcmb**2)
        D2 = (2*ells[i]**2)**2 * vT
        s8sq += D2 * Ws[i]**2
    return np.sqrt(s8sq), s8sq

# 多個場景
for f, label in [(0.0, "0% (無 beat)"), (0.05, "5%"), (0.1, "10%"), (0.15, "15%"), (0.2, "20%"), (0.3, "30%"), (0.5, "50%"), (1.0, "100% (全可見)")]:
    s8, s8sq = compute_sigma8(f)
    s8_9 = compute_sigma8(0.0)[0]
    print(f"  f={f:.1f} ({label}): σ8 = {s8:.4f}  (beat 佔 {100*(1-s8_9**2/s8sq):.1f}%)  vs 0.81: Δ={100*(s8/0.81-1):+.1f}%")

# 最佳場景: f = 0.15  (基於 Planck 峰間/包絡比 ~0.6 嘅保守估計)
s8_best, s8sq_best = compute_sigma8(0.15)
s8_9, s8sq_9 = compute_sigma8(0.0)
print(f"\n最佳估計 f=0.15:")
print(f"  9 峰 σ8 = {s8_9:.4f}  (σ8²={s8sq_9:.4f})")
print(f"  beat 背景 σ8 = {np.sqrt(s8sq_best - s8sq_9):.4f}  (σ8²={s8sq_best-s8sq_9:.4f})")
print(f"  總 σ8 = {s8_best:.4f}")
print(f"  vs 目標 0.81: Δ={100*(s8_best/0.81-1):+.1f}%")
print(f"  vs BOSS 0.783: Δ={100*(s8_best/0.783-1):+.1f}%")

# 對比: 需要 f = ? 先達到 0.81
for f_test in np.linspace(0, 1, 1001):
    s8, _ = compute_sigma8(f_test)
    if s8 >= 0.81:
        print(f"\n需要 f = {f_test:.3f} 先達到 σ8=0.81 (vs 0.81 目標)")
        print(f"  對應非選中 mode w_n² = {w2_avg*f_test:.3f}")
        print(f"  對比選中 mode w_n² 平均 = {w2_avg:.3f}")
        print(f"  比 = {f_test:.3f} (即非選中 mode 振幅為選中 mode 嘅 {100*f_test:.1f}%)")
        break