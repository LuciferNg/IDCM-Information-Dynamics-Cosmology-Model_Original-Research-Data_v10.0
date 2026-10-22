#!/usr/bin/env python3
"""
O34 — 世代跳躍 Lucas 閉合最終驗證 (scripts/21)
====================================================
發現 (scripts/20):
  k(e→μ) = 11 + 7/88 = L₅ + L₄/(2N_d)         偏差 0.0003%
  k(μ→τ) = 6 - 12/88 = C(4,2) - dim_ℂ·B/(2N_d) 偏差 0.0278%
  k(e→τ) = 17 - 5/88 = L₅+C(4,2) - F₅/(2N_d)   偏差 0.0094%

新候選 (528 結構):
  k(e→τ) = 17 - 29/528 = L₅+C(4,2) - L₇/(dim_ℂ·B·N_d) 偏差 0.0018%
  k(μ→τ) = 6 - 71/528 = C(4,2) - (L₇+L₄·6)/(...) 偏差 ?

目標: 嚴格驗證所有候選, 鎖定最靚形式
"""

import numpy as np
from decimal import Decimal, getcontext

getcontext().prec = 100

N = 44
phi = (1 + np.sqrt(5)) / 2
B = 4
dimC = 3

m_e = 0.511
m_mu = 105.658
m_tau = 1776.93
m_t = 172.76e3
m_b = 4.18e3

def log_phi(x):
    return np.log(x) / np.log(phi)

k12 = log_phi(m_mu / m_e)
k23 = log_phi(m_tau / m_mu)
k13 = log_phi(m_tau / m_e)

print("=" * 67)
print("  O34 — 世代跳躍 Lucas 閉合最終驗證")
print("=" * 67)

print(f"\n  目標值:")
print(f"  k(e→μ) = {k12:.10f}")
print(f"  k(μ→τ) = {k23:.10f}")
print(f"  k(e→τ) = {k13:.10f}")
print(f"  加法: {k12+k23:.10f} = k13 ✓")

# ═══════════════════════════════════════════════════════════════
# 候選 1: k = a + b/88 形式
# ═══════════════════════════════════════════════════════════════
print(f"\n{'═'*67}")
print("  候選 1: k = a + b/88 (a, b 結構)")
print(f"{'═'*67}")

cands_88 = {
    "k(e→μ)": (k12, 11, 7, "L₅ + L₄/88"),
    "k(μ→τ)": (k23, 6, -12, "C(4,2) - (dim_ℂ·B)/88"),
    "k(e→τ)": (k13, 17, -5, "L₅+C(4,2) - F₅/88"),
}

for name, (k, a, b, desc) in cands_88.items():
    cand = a + b/88
    err = abs(cand - k)/k*100
    print(f"  {name}: {a} + {b}/88 = {cand:.10f}, 偏差 {err:.6f}%")
    print(f"    {desc}")

# ═══════════════════════════════════════════════════════════════
# 候選 2: k(e→τ) = 17 - 29/528 (L₇/528)
# ═══════════════════════════════════════════════════════════════
print(f"\n{'═'*67}")
print("  候選 2: k = a - b/528 (528 = dim_ℂ·B·N_d)")
print(f"{'═'*67}")

# k(e→τ) = 17 - 29/528
cand = 17 - 29/528
print(f"  k(e→τ) = 17 - 29/528 = {cand:.10f}")
print(f"  偏差 = {abs(cand-k13)/k13*100:.6f}%")
print(f"  29 = L₇, 528 = dim_ℂ·B·N_d = 3·4·44")
print(f"  17 = L₅ + C(4,2) = 11+6")

# k(μ→τ) = k(e→τ) - k(e→μ) = 17 - 29/528 - 11 - 7/88
# = 6 - 29/528 - 42/528 = 6 - 71/528
cand23 = 6 - 71/528
print(f"\n  k(μ→τ) = 6 - 71/528 = {cand23:.10f}")
print(f"  偏差 = {abs(cand23-k23)/k23*100:.6f}%")
print(f"  71 = L₇ + L₄·6 = 29 + 42? {29 + 7*6}")
print(f"  71 = 2·L₅ + L₇ + L₄ = 22+29+7 = 58? 唔係")
print(f"  71 = 528·(6 - k23)/1? 直接: 71 = 528×(6-k23)")

# 71 有冇結構? 71 = 質數, 71 = 44+27? 27=3³
print(f"  71 = 2·N_d - 17 = 88-17 = 71 ✓ (17 = L₅+C(4,2))")
print(f"  71 = 88 - 17, 17 = L₅ + C(4,2)")
print(f"  → 71 = 2N_d - (L₅ + C(4,2))")

# ═══════════════════════════════════════════════════════════════
# 候選 3: 統一 Lucas 形式
# ═══════════════════════════════════════════════════════════════
print(f"\n{'═'*67}")
print("  候選 3: 統一 Lucas 結構")
print(f"{'═'*67}")

# 嘗試: k(g) = L_a - L_b/528 或者 k(g) = C(4,2)·g + ...
# 搜尋 k = a - b/528 形式 (a ∈ 1..30, b ∈ 1..60)
for name, k in [("k(e→μ)", k12), ("k(μ→τ)", k23), ("k(e→τ)", k13)]:
    best = None
    best_err = float('inf')
    for a in range(1, 31):
        for b in range(1, 61):
            cand = a - b/528
            err = abs(cand - k)/k*100
            if err < best_err:
                best_err = err
                best = (a, b, cand)
    print(f"  {name}: k = {best[0]} - {best[1]}/528 = {best[2]:.10f}, 偏差 {best_err:.6f}%")
    print(f"    {best[0]} = ?, {best[1]} = ?")

# ═══════════════════════════════════════════════════════════════
# t 夸克閉合
# ═══════════════════════════════════════════════════════════════
print(f"\n{'═'*67}")
print("  t 夸克: m_t/m_b 閉合")
print(f"{'═'*67}")

r_tb = m_t / m_b
print(f"  m_t/m_b = {r_tb:.6f}")
print(f"  log_φ(m_t/m_b) = {log_phi(r_tb):.6f}")

# 如果 t: n=19 (同位旋預測), b: n=33
sin_tb = np.sin(19*np.pi/88)/np.sin(33*np.pi/88)
k_tb = log_phi(r_tb / sin_tb)
print(f"\n  用 sin(19)/sin(33) = {sin_tb:.6f}:")
print(f"  剩餘 k = log_φ(m_t/m_b ÷ sin(19)/sin(33)) = {k_tb:.6f}")
print(f"  {k_tb:.4f} ≈ ?")

# 8.5378 ≈ 8.5 = 17/2? 偏差 0.44%
# 8.5378 = 8 + 0.5378? 0.5378 = 47.3/88?
# 8.5378 ≈ 8 + 0.54? 
# 8.5378 ≈ 6 + 2.5378? 唔靚
# 試: k_tb = 8.5 = 17/2 (L₅+C(4,2))/2?
print(f"  8.5 = 17/2 = (L₅+C(4,2))/2? 偏差 {abs(k_tb-8.5)/k_tb*100:.4f}%")
print(f"  8.5 = ? ")

# 其他 n_t 選擇: 全譜搜尋已做, 最佳 n_t=1,n_b=2 但 k=9.17 唔靚
# 考慮: m_t 可能唔係 b 嘅同世代, 而係有額外 φ 因子
# m_t/m_b = 41.33, log_φ = 8.5378
# 8.5378 ≈ 8.5 + 0.0378? 0.0378 = 3.3/88?
# 8.5378 ≈ 8 + 47/88 = 8.5341? 偏差 0.04%? 47 = L₈?
cand_tb = 8 + 47/88
print(f"\n  8 + 47/88 = {cand_tb:.6f} (47 = L₈ = N_d+3)")
print(f"  偏差 = {abs(cand_tb - k_tb)/k_tb*100:.4f}%")

# 47 = N_d + dim_ℂ! 同級聯閉合一致!
# k_tb = 8 + (N_d+dim_ℂ)/88?
# 8 = ? 8 = B×2? 8 = F₆?

# 驗證 m_t/m_b = φ^(8 + 47/88) × sin(19)/sin(33)?
r_cand = phi**(8 + 47/88) * sin_tb
print(f"\n  m_t/m_b = φ^(8+47/88) × sin(19)/sin(33) = {r_cand:.4f}")
print(f"  目標 = {r_tb:.4f}")
print(f"  偏差 = {abs(r_cand - r_tb)/r_tb*100:.6f}%")
print(f"  8 = 2·B = 2×4? 8 = F₆")
print(f"  47 = N_d + dim_ℂ = 44+3 (同級聯一致!)")

# 另一個選擇: m_t/m_b 直接用全 sin 比值?
# 全譜搜尋: 冇 (n_t,n_b) 直接匹配 41.33 (最佳 32%)
# → 需要 φ^k 修正, k_tb = 8 + 47/88?

# ═══════════════════════════════════════════════════════════════
# 完整質量公式驗證
# ═══════════════════════════════════════════════════════════════
print(f"\n{'═'*67}")
print("  完整質量公式 (方向 C + B 融合)")
print(f"{'═'*67}")

# 輕子: m_μ/m_e = φ^(L₅ + L₄/88)
# 夸克: m_t/m_b = φ^(8 + 47/88) × sin(19)/sin(33)

print(f"  輕子閉合: m_μ/m_e = φ^(11+7/88) = {phi**(11+7/88):.6f}")
print(f"            m_μ/m_e 目標 = {m_mu/m_e:.6f} (偏差 {abs(phi**(11+7/88)/(m_mu/m_e)-1)*100:.6f}%)")

# 儲存
with open("data/generation_lucas_closure.txt", "w") as f:
    f.write("O34 — Generation Ladder Lucas Closure\n")
    f.write("=" * 67 + "\n")
    f.write(f"k(e->mu) = {k12:.10f}, cand 11+7/88 = {11+7/88:.10f}, err {abs(k12-(11+7/88))/(11+7/88)*100:.6f}%\n")
    f.write(f"  7 = L4, 11 = L5, 88 = 2N_d\n")
    f.write(f"k(mu->tau) = {k23:.10f}, cand 6-71/528 = {cand23:.10f}, err {abs(k23-cand23)/k23*100:.6f}%\n")
    f.write(f"  71 = 2N_d - (L5+C(4,2)) = 88-17\n")
    f.write(f"k(e->tau) = {k13:.10f}, cand 17-29/528 = {17-29/528:.10f}, err {abs(k13-(17-29/528))/k13*100:.6f}%\n")
    f.write(f"  29 = L7, 528 = dim_C*B*N_d = 3*4*44\n")
    f.write(f"t quark: m_t/m_b = phi^(8+47/88)*sin(19)/sin(33), err {abs(r_cand-r_tb)/r_tb*100:.6f}%\n")
    f.write(f"  47 = N_d + dim_C = 44+3 (same as cascade!), 8 = F6 = 2B\n")
    f.write(f"Status: 🟢 k(e->mu) = L5+L4/88 closed 0.0003%\n")