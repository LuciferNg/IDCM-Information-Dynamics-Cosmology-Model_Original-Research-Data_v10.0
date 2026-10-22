#!/usr/bin/env python3
"""
O34 — 方向 B 世代跳躍精確閉合 (scripts/20)
====================================================
已知: k(e→μ) = log_φ(m_μ/m_e) = 11.0795 (偏差 0.72% vs 11 = L₅)
線索: 0.0795 ≈ 7/88 = 0.079545 (7 = L₄!)

驗證: k(e→μ) = 11 + 7/88 = L₅ + L₄/(2N_d)?
       k(μ→τ), k(e→τ) 嘅精確形式?
       t 夸克方向 B 修正?
"""

import numpy as np
from decimal import Decimal, getcontext

getcontext().prec = 100

N = 44
phi = (1 + np.sqrt(5)) / 2
phi_inv = phi - 1

# PDG 2024
m_e = 0.511
m_mu = 105.658
m_tau = 1776.93
m_t = 172.76e3
m_b = 4.18e3

def log_phi(x):
    return np.log(x) / np.log(phi)

print("=" * 67)
print("  O34 — 方向 B 世代跳躍精確閉合")
print("=" * 67)

# ═══════════════════════════════════════════════════════════════
# k(e→μ) 精確形式
# ═══════════════════════════════════════════════════════════════
k12 = log_phi(m_mu / m_e)
print(f"\n─── k(e→μ) = log_φ(m_μ/m_e) = {k12:.10f} ───")
print(f"  11 + 7/88 = {11 + 7/88:.10f}")
print(f"  偏差 = {abs(k12 - (11+7/88))/(11+7/88)*100:.6f}%")

# 驗證 m_μ/m_e = φ^(11+7/88)?
ratio_cand = phi**(11 + 7/88)
ratio_obs = m_mu / m_e
print(f"  φ^(11+7/88) = {ratio_cand:.6f}")
print(f"  m_μ/m_e = {ratio_obs:.6f}")
print(f"  偏差 = {abs(ratio_cand - ratio_obs)/ratio_obs*100:.6f}%")
print(f"  7 = L₄ (Lucas), 88 = 2N_d")
print(f"  → k(e→μ) = L₅ + L₄/88? L₅ = 11")

# 其他候選: 11 + 1/φ⁵?
print(f"\n  其他候選:")
print(f"  7/88 = {7/88:.8f}, log_φ(f) 需要 = {k12 - 11:.8f}")
print(f"  1/φ⁵ = {phi**(-5):.8f}")
print(f"  1/12 = {1/12:.8f}")
print(f"  1/13 = {1/13:.8f}")
print(f"  7/88 vs 需要: {abs(7/88 - (k12-11))/(k12-11)*100:.6f}%")

# ═══════════════════════════════════════════════════════════════
# k(μ→τ) 精確形式
# ═══════════════════════════════════════════════════════════════
k23 = log_phi(m_tau / m_mu)
print(f"\n─── k(μ→τ) = log_φ(m_τ/m_μ) = {k23:.10f} ───")
print(f"  6 + ? : 需要修正 = {k23 - 6:.8f}")
print(f"  6 = C(4,2)")
print(f"  修正 × 88 = {(k23-6)*88:.6f}")
print(f"  修正 × 44 = {(k23-6)*44:.6f}")

# 候選: 6 - 1/88? 6 - 0.25/88?
for cand in [6 - 1/88, 6 + 7/88, 6 - 7/88, 6 - 1/44, 6 + 1/88, 6 - 2/88]:
    err = abs(k23 - cand)/k23*100
    print(f"  候選 {cand:.8f} (= {cand}): 偏差 {err:.4f}%")

# ═══════════════════════════════════════════════════════════════
# k(e→τ) 精確形式
# ═══════════════════════════════════════════════════════════════
k13 = log_phi(m_tau / m_e)
print(f"\n─── k(e→τ) = log_φ(m_τ/m_e) = {k13:.10f} ───")
print(f"  17 + ? : 需要修正 = {k13 - 17:.8f}")
print(f"  修正 × 88 = {(k13-17)*88:.6f}")

# 如果 k(e→τ) = k(e→μ) + k(μ→τ):
print(f"  k12 + k23 = {k12+k23:.10f} (應 = k13 = {k13:.10f})")
print(f"  加法一致性: {abs(k12+k23-k13):.2e}")

# 候選組合: k13 = L₅ + C(4,2) + 修正?
# = 11 + 6 + ?
for cand in [17 + 7/88, 17 - 7/88, 17 - 1/88, 17 + 5/88, 17 - 6/88]:
    err = abs(k13 - cand)/k13*100
    print(f"  候選 {cand:.8f} (= {cand}): 偏差 {err:.4f}%")

# ═══════════════════════════════════════════════════════════════
# 精確系統搜尋: k(g) = a + b/88 形式
# ═══════════════════════════════════════════════════════════════
print(f"\n{'═'*67}")
print("  系統搜尋: k = a + b/88")
print(f"{'═'*67}")

targets = {"k(e→μ)": k12, "k(μ→τ)": k23, "k(e→τ)": k13}

for name, k in targets.items():
    best = None
    best_err = float('inf')
    for a in range(1, 40):
        for b in range(-20, 21):
            cand = a + b/88
            err = abs(cand - k)/k*100
            if err < best_err:
                best_err = err
                best = (a, b, cand)
    print(f"  {name}: k = {best[0]} + {best[1]}/88 = {best[2]:.8f}, 偏差 {best_err:.4f}%")

# ═══════════════════════════════════════════════════════════════
# 半整數/其他形式搜尋
# ═══════════════════════════════════════════════════════════════
print(f"\n{'═'*67}")
print("  系統搜尋: k = a + b/(2N_d) 同 a + b/N_d²")
print(f"{'═'*67}")

for name, k in targets.items():
    best = None
    best_err = float('inf')
    for a in range(1, 40):
        for b in range(-30, 31):
            for denom_name, denom in [("88", 88), ("1936", 44**2), ("90", 90), ("528", 528)]:
                cand = a + b/denom
                err = abs(cand - k)/k*100
                if err < best_err:
                    best_err = err
                    best = (a, b, denom_name, cand)
    print(f"  {name}: k = {best[0]} + {best[1]}/{best[2]} = {best[3]:.8f}, 偏差 {best_err:.4f}%")

# ═══════════════════════════════════════════════════════════════
# t 夸克方向 B 修正
# ═══════════════════════════════════════════════════════════════
print(f"\n{'═'*67}")
print("  t 夸克: m_t/m_b 方向 B 修正")
print(f"{'═'*67}")

# 如果 t 用 n=19, b 用 n=33: sin(19)/sin(33) = 0.679
r_tb_obs = m_t / m_b
sin_tb = np.sin(19*np.pi/88) / np.sin(33*np.pi/88)
print(f"  m_t/m_b = {r_tb_obs:.6f}")
print(f"  sin(19)/sin(33) = {sin_tb:.6f}")
print(f"  剩餘因子 = m_t/m_b ÷ sin(19)/sin(33) = {r_tb_obs/sin_tb:.6f}")
k_tb = log_phi(r_tb_obs / sin_tb)
print(f"  log_φ(剩餘) = {k_tb:.6f}")
print(f"  k_tb ≈ ? {k_tb:.4f}")
print(f"  8.5 = 17/2? {k_tb:.4f} vs 8.5: 偏差 {abs(k_tb-8.5)/k_tb*100:.4f}%")

# 如果 t 用 n=44 (Nyquist): sin(44)/sin(33) = 3.33
sin_tb44 = np.sin(44*np.pi/88) / np.sin(33*np.pi/88)
print(f"\n  sin(44)/sin(33) = {sin_tb44:.6f}")
print(f"  剩餘 = {r_tb_obs/sin_tb44:.6f}")
k_tb44 = log_phi(r_tb_obs / sin_tb44)
print(f"  log_φ(剩餘) = {k_tb44:.6f}")
print(f"  {k_tb44:.4f} ≈ ?")
print(f"  12.2 = L₆ + 0.2?")
print(f"  12 = 3×4 = dim_ℂ×B?")

# 全譜搜尋: 搵 (n_t, n_b, φ^k) 組合
print(f"\n  全譜搜尋 (n_t, n_b) + φ^k 修正:")
best = None
best_err = float('inf')
for nt in range(1, N+1):
    for nb in range(1, N+1):
        if nt == nb: continue
        s = np.sin(nt*np.pi/88) / np.sin(nb*np.pi/88)
        k = log_phi(r_tb_obs / s)
        # 檢查 k 係咪接近半整數或整數
        for kh in [k, round(k*2)/2]:
            err = abs(kh - k)/k*100
            if err < 1.0 and err < best_err:
                best_err = err
                best = (nt, nb, kh, s, k)
if best:
    print(f"  最佳: n_t={best[0]}, n_b={best[1]}, φ^{best[2]:.1f} × sin({best[0]})/sin({best[1]})")
    print(f"    sin 部分 = {best[3]:.6f}, 需要 φ^k = {r_tb_obs/best[3]:.4f}, k = {best[4]:.4f}")
    print(f"    偏差 = {best_err:.4f}%")

# ═══════════════════════════════════════════════════════════════
# 儲存
# ═══════════════════════════════════════════════════════════════
with open("data/generation_ladder_closure.txt", "w") as f:
    f.write("O34 — Direction B Generation Ladder Closure\n")
    f.write("=" * 67 + "\n")
    f.write(f"k(e->mu) = {k12:.10f}\n")
    f.write(f"k(mu->tau) = {k23:.10f}\n")
    f.write(f"k(e->tau) = {k13:.10f}\n")
    f.write(f"k12 + k23 = {k12+k23:.10f} (additivity {abs(k12+k23-k13):.2e})\n")
    f.write(f"k(e->mu) = 11 + 7/88 candidate: err {abs(k12-(11+7/88))/(11+7/88)*100:.6f}%\n")
    f.write(f"m_mu/m_e = phi^(11+7/88): err {abs(ratio_cand-ratio_obs)/ratio_obs*100:.6f}%\n")
    f.write(f"t quark: m_t/m_b = {r_tb_obs:.4f}, needs phi^k correction\n")
    f.write(f"Status: 🟡 k(e->mu) = 11+7/88 strong candidate\n")