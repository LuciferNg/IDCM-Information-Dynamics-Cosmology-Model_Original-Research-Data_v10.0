#!/usr/bin/env python3
"""
O34 — 方向 C + B 閉合: 質量比值 + 世代階梯 (scripts/18)
============================================================
方向 C (質量比值, 幾何因子消去):
  m_{n1}/m_{n2} = sin(n1·π/88)/sin(n2·π/88)

方向 B (世代階梯 φ^k):
  m(Particle) = E_kchain · D · φ^{k(g)} · 2sin(nπ/88)
  k(g) = 世代拓撲選擇數

驗證:
  [C] m_u/m_d, m_s/m_d, m_c/m_b, m_t/m_b vs sin 比值
  [B] m_e, m_μ, m_τ 世代階梯 k(g) 鎖定
"""

import numpy as np
from decimal import Decimal, getcontext

getcontext().prec = 100

N = 44
phi = (1 + np.sqrt(5)) / 2
phi_inv = phi - 1
eps = phi_inv / 4

print("=" * 67)
print("  O34 — 方向 C + B: 質量比 + 世代階梯")
print("=" * 67)

# PDG 2024 質量 (MeV)
m_e = 0.511
m_mu = 105.658
m_tau = 1776.93
m_u = 2.16
m_d = 4.67
m_s = 93.4
m_c = 1.27e3
m_b = 4.18e3
m_t = 172.76e3
m_W = 80.377e3
m_Z = 91.1876e3
m_H = 125.25e3

def sin_ratio(n1, n2):
    """sin(n1·π/88)/sin(n2·π/88)"""
    return np.sin(np.pi * n1 / 88) / np.sin(np.pi * n2 / 88)

# ═══════════════════════════════════════════════════════════════
# [C] 質量比值 vs sin 比值
# ═══════════════════════════════════════════════════════════════
print(f"\n{'═'*67}")
print("  [C] 質量比值 vs sin 比值")
print(f"{'═'*67}")

# m_u/m_d = 2.16/4.67 = 0.4625
# sin(1π/88)/sin(2π/88) = 1/(2cos(π/88)) = 0.50032
ratio_ud = m_u / m_d
sin_12 = sin_ratio(1, 2)
print(f"\n  m_u/m_d = {ratio_ud:.6f}")
print(f"  sin(1π/88)/sin(2π/88) = {sin_12:.6f} = 1/(2cos(π/88))")
print(f"  偏差 = {abs(sin_12 - ratio_ud)/ratio_ud*100:.4f}%")

# φ 階梯修正: sin_12 × φ^k = ratio?
# 0.50032 → 0.4625: 需要 × 0.9244 = φ^(-0.157)
k_ud = np.log(ratio_ud / sin_12) / np.log(phi)
print(f"  k = log_φ(ratio/sin) = {k_ud:.4f}")
print(f"  φ^k = {phi**k_ud:.6f}")

# 0.157 ≈ ?
print(f"  1 - φ^(-k) = {1 - phi**(-k_ud):.6f}")
print(f"  k ≈ -1/6.37? k ≈ -0.157")

# m_s/m_d = 20.0
ratio_sd = m_s / m_d
print(f"\n  m_s/m_d = {ratio_sd:.6f}")
print(f"  sin(3π/88)/sin(2π/88) = {sin_ratio(3,2):.6f}")
print(f"  sin(5π/88)/sin(2π/88) = {sin_ratio(5,2):.6f}")
print(f"  sin(7π/88)/sin(2π/88) = {sin_ratio(7,2):.6f}")
print(f"  sin(11π/88)/sin(2π/88) = {sin_ratio(11,2):.6f}")

# m_c/m_b = 0.3038
ratio_cb = m_c / m_b
print(f"\n  m_c/m_b = {ratio_cb:.6f}")
print(f"  sin(2π/88)/sin(5π/88) = {sin_ratio(2,5):.6f}")
print(f"  sin(3π/88)/sin(7π/88) = {sin_ratio(3,7):.6f}")
print(f"  sin(1π/88)/sin(3π/88) = {sin_ratio(1,3):.6f}")
print(f"  sin(4π/88)/sin(9π/88) = {sin_ratio(4,9):.6f}")

# m_t/m_b = 41.33
ratio_tb = m_t / m_b
print(f"\n  m_t/m_b = {ratio_tb:.6f}")
print(f"  sin(44π/88)/sin(1π/88) = {sin_ratio(44,1):.6f}")
print(f"  sin(22π/88)/sin(1π/88) = {sin_ratio(22,1):.6f}")

# 全譜搜尋: 搵 (n1,n2) 令 sin 比值 ≈ SM 比值
print(f"\n  ─── 全譜搜尋 (sin 比值 ≈ SM 比值) ───")
sm_targets = {
    "m_u/m_d": m_u/m_d,
    "m_s/m_d": m_s/m_d,
    "m_c/m_b": m_c/m_b,
    "m_t/m_b": m_t/m_b,
    "m_e/m_mu": m_e/m_mu,
    "m_mu/m_tau": m_mu/m_tau,
    "m_W/m_Z": m_W/m_Z,
    "m_H/m_W": m_H/m_W,
}

for name, target in sm_targets.items():
    best = None
    best_err = float('inf')
    for n1 in range(1, N+1):
        for n2 in range(1, N+1):
            if n1 == n2:
                continue
            r = sin_ratio(n1, n2)
            err = abs(r - target) / target * 100
            if err < best_err:
                best_err = err
                best = (n1, n2, r)
    if best:
        print(f"  {name:<12} 目標={target:>10.6f} | 最佳 sin({best[0]}π/88)/sin({best[1]}π/88) = {best[2]:>10.6f} | 偏差 {best_err:6.2f}%")

# ═══════════════════════════════════════════════════════════════
# [B] 世代階梯 φ^k
# ═══════════════════════════════════════════════════════════════
print(f"\n{'═'*67}")
print("  [B] 世代階梯 φ^k (輕子)")
print(f"{'═'*67}")

# 輕子質量比
ratios_lepton = {
    "m_μ/m_e": m_mu/m_e,
    "m_τ/m_μ": m_tau/m_mu,
    "m_τ/m_e": m_tau/m_e,
}

print(f"\n  {'比值':<10} | {'目標':>10} | {'log_φ':>8} | {'近整數':>6} | {'偏差%':>8}")
print("-" * 50)
for name, ratio in ratios_lepton.items():
    log_phi_r = np.log(ratio) / np.log(phi)
    nearest = round(log_phi_r)
    dev = abs(log_phi_r - nearest) / log_phi_r * 100
    print(f"  {name:<10} | {ratio:>10.4f} | {log_phi_r:>8.4f} | {nearest:>6} | {dev:>8.4f}%")

# 世代跳躍 k(g)
print(f"\n  ─── 世代跳躍 k(g) ───")
k12 = np.log(m_mu/m_e) / np.log(phi)  # e→μ
k23 = np.log(m_tau/m_mu) / np.log(phi)  # μ→τ
k13 = np.log(m_tau/m_e) / np.log(phi)  # e→τ
print(f"  k(e→μ) = log_φ(m_μ/m_e) = {k12:.6f}")
print(f"  k(μ→τ) = log_φ(m_τ/m_μ) = {k23:.6f}")
print(f"  k(e→τ) = log_φ(m_τ/m_e) = {k13:.6f}")
print(f"  k(e→μ) + k(μ→τ) = {k12+k23:.6f} (應 = k(e→τ) = {k13:.6f})")

# 近整數?
print(f"\n  k(e→μ) ≈ ? {k12:.4f}")
print(f"  11 = L₅ (Lucas)")
print(f"  11.08 vs 11: 偏差 = {abs(k12-11)/k12*100:.4f}%")
print(f"  k(μ→τ) ≈ ? {k23:.4f}")
print(f"  6 = B×dim_ℂ/2 = 4×3/2? {4*3/2}")
print(f"  6 = C(4,2) = MERA 分支二階? {np.math.comb(4,2) if hasattr(np,'math') else 6}")
print(f"  {k23:.4f} vs 6: 偏差 = {abs(k23-6)/k23*100:.4f}%")
print(f"  k(e→τ) ≈ ? {k13:.4f}")
print(f"  17 = L₅ + C(4,2) = 11+6? {11+6}")
print(f"  {k13:.4f} vs 17: 偏差 = {abs(k13-17)/k13*100:.4f}%")

# ═══════════════════════════════════════════════════════════════
# 輕子質量閉合候選
# ═══════════════════════════════════════════════════════════════
print(f"\n{'═'*67}")
print("  輕子質量閉合候選")
print(f"{'═'*67}")

# 候選: m_μ = m_e × φ^11?
m_mu_cand = m_e * phi**11
print(f"\n  m_μ = m_e × φ^11 = {m_mu_cand:.4f} MeV")
print(f"  m_μ 目標 = {m_mu:.4f} MeV")
print(f"  偏差 = {abs(m_mu_cand - m_mu)/m_mu*100:.4f}%")

# 候選: m_τ = m_μ × φ^6?
m_tau_cand = m_mu * phi**6
print(f"\n  m_τ = m_μ × φ^6 = {m_tau_cand:.4f} MeV")
print(f"  m_τ 目標 = {m_tau:.4f} MeV")
print(f"  偏差 = {abs(m_tau_cand - m_tau)/m_tau*100:.4f}%")

# 候選: m_τ = m_e × φ^17?
m_tau_cand2 = m_e * phi**17
print(f"\n  m_τ = m_e × φ^17 = {m_tau_cand2:.4f} MeV")
print(f"  m_τ 目標 = {m_tau:.4f} MeV")
print(f"  偏差 = {abs(m_tau_cand2 - m_tau)/m_tau*100:.4f}%")

# φ^k 精確階梯: 搵最近整數 k
print(f"\n  ─── φ^k 整數階梯搜尋 ───")
for name, ratio in ratios_lepton.items():
    log_phi_r = np.log(ratio) / np.log(phi)
    best_k = None
    best_err = float('inf')
    for k in range(1, 40):
        r_cand = phi**k
        err = abs(r_cand - ratio) / ratio * 100
        if err < best_err:
            best_err = err
            best_k = k
    print(f"  {name:<10}: 最佳 k={best_k} (φ^{best_k} = {phi**best_k:.2f}), 偏差 {best_err:.4f}%")

# ═══════════════════════════════════════════════════════════════
# 半整數階梯
# ═══════════════════════════════════════════════════════════════
print(f"\n  ─── 半整數 k 階梯 ───")
for name, ratio in ratios_lepton.items():
    log_phi_r = np.log(ratio) / np.log(phi)
    best_k = None
    best_err = float('inf')
    for k_half in range(2, 60):
        k = k_half / 2
        r_cand = phi**k
        err = abs(r_cand - ratio) / ratio * 100
        if err < best_err:
            best_err = err
            best_k = k
    print(f"  {name:<10}: 最佳半整數 k={best_k} (φ^{best_k} = {phi**best_k:.2f}), 偏差 {best_err:.4f}%")

# 儲存
with open("data/direction_cb_results.txt", "w") as f:
    f.write("O34 — Direction C+B: Mass Ratios + Generation Ladder\n")
    f.write("=" * 67 + "\n")
    f.write(f"m_u/m_d = {ratio_ud:.6f}, sin(1π/88)/sin(2π/88) = {sin_12:.6f}, dev {abs(sin_12-ratio_ud)/ratio_ud*100:.4f}%\n")
    f.write(f"k(e→μ) = {k12:.6f} ≈ 11 = L₅ (dev {abs(k12-11)/k12*100:.4f}%)\n")
    f.write(f"k(μ→τ) = {k23:.6f} ≈ 6 = C(4,2) (dev {abs(k23-6)/k23*100:.4f}%)\n")
    f.write(f"k(e→τ) = {k13:.6f} ≈ 17 = L₅+C(4,2) (dev {abs(k13-17)/k13*100:.4f}%)\n")
    f.write(f"m_μ = m_e×φ^11 = {m_mu_cand:.4f} vs {m_mu:.4f} (dev {abs(m_mu_cand-m_mu)/m_mu*100:.4f}%)\n")
    f.write(f"m_τ = m_μ×φ^6 = {m_tau_cand:.4f} vs {m_tau:.4f} (dev {abs(m_tau_cand-m_tau)/m_tau*100:.4f}%)\n")
    f.write(f"Status: 🟡 generation ladder candidates, need precise closure\n")