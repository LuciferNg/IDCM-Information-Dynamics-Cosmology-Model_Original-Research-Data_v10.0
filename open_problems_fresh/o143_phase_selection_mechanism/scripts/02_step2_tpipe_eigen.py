#!/usr/bin/env python3
"""
O143 Step 2 — 求解 T_pipe 算子嘅本徵相位態
============================================
目標: T_pipe 係 88-site 管道轉移算子，其本徵態展開決定相位場：
  T_pipe |ψ_m⟩ = λ_m |ψ_m⟩
  Φ_m(x_k) = A_m cos(k·ω_m + θ_0^(m))

理論基礎:
- T_pipe = 88-site 週期鏈嘅轉移矩陣
- 本徵值 λ_m = 2cos(πm/88) (離散 cos 譜)
- 本徵向量 = 離散 Fourier 模態
- 拓撲相角 θ_0^(m) 由奇偶不對稱性鎖定 (Σγ_odd=88 vs Σγ_even=90)
"""

import numpy as np
import json, os

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
O143 = f'{BASE}/open_problems_fresh/o143_phase_selection_mechanism'
OUTDIR = f'{O143}/data'
os.makedirs(OUTDIR, exist_ok=True)

print("=" * 72)
print("  O143 Step 2: T_pipe 算子本徵相位態")
print("=" * 72)

N = 88

# ══════════════════════════════════════════════════════════════
# 1. 構建 T_pipe 矩陣
# ══════════════════════════════════════════════════════════════
# T_pipe 係 88×88 週期三對角矩陣 (nearest-neighbor hopping)
# T_ij = 1 if |i-j| = 1 (mod 88), 0 otherwise
T = np.zeros((N, N))
for i in range(N):
    T[i, (i+1) % N] = 1.0
    T[i, (i-1) % N] = 1.0

# ══════════════════════════════════════════════════════════════
# 2. 對角化
# ══════════════════════════════════════════════════════════════
eigvals, eigvecs = np.linalg.eigh(T)

# 排序 (由小到大)
idx = np.argsort(eigvals)
eigvals = eigvals[idx]
eigvecs = eigvecs[:, idx]

print(f"\nT_pipe 對角化:")
print(f"  本徵值範圍: [{eigvals.min():.6f}, {eigvals.max():.6f}]")
print(f"  理論: λ_m = 2cos(πm/88), m=0..87")

# 驗證: 本徵值 vs 理論 (週期邊界: λ_m = 2cos(2πm/88))
m = np.arange(N)
theory_vals = 2 * np.cos(2 * np.pi * m / N)
print(f"  Max dev from theory: {np.max(np.abs(np.sort(eigvals) - np.sort(theory_vals))):.2e}")

# ══════════════════════════════════════════════════════════════
# 3. 基態本徵向量 (m=0: 最低頻模式)
# ══════════════════════════════════════════════════════════════
# m=0: λ_0 = 2cos(0) = 2 (uniform mode)
# m=1: λ_1 = 2cos(π/88) ≈ 1.9987 (longest wavelength)
# m=44: λ_44 = 2cos(π/2) = 0 (Nyquist)

# 基態相位: Φ_0(x_k) = cos(π·k/44) (n=1 mode, 半週期)
# 呢個係最長波長嘅非均勻模式
k = np.arange(N)
phi_base = np.cos(np.pi * k / (N/2))  # cos(πk/44)

# 第一激發態: Φ_1(x_k) = cos(π·k/44 + π/88)
phi_excited = np.cos(np.pi * k / (N/2) + np.pi / N)

print(f"\n基態相位場 Φ_base:")
print(f"  Φ_base(x_k) = cos(πk/44), k=0..87")
print(f"  range: [{phi_base.min():.6f}, {phi_base.max():.6f}]")

# ══════════════════════════════════════════════════════════════
# 4. 拓撲相角 θ_0^(m) 鎖定
# ══════════════════════════════════════════════════════════════
# 88-site 雙鏈嘅奇偶不對稱性:
# - 偶數鏈 Σγ_even = 90 (世界)
# - 奇數鏈 Σγ_odd = 88 (觀察者)
# 差 = 2 = B/2 (B=4)

# 拓撲相角 θ_0: 由離散譜嘅奇偶加權決定
# 每個模式 m 嘅拓撲相角 = 奇偶能量差嘅 Fourier 對偶
gamma_k = 4 * np.sin(np.pi * np.arange(1, N+1) / (2*N))**2
gamma_even = gamma_k[::2]  # k=2,4,...,88 (0-indexed: 1,3,...,87)
gamma_odd = gamma_k[1::2]  # k=1,3,...,87 (0-indexed: 0,2,...,86)

# 每個模式 m 嘅奇偶加權
theta_0 = np.zeros(N)
for m_idx in range(N):
    # 模式 m 喺奇數 site 嘅投影權重
    w_odd = np.sum(eigvecs[1::2, m_idx])  # 奇數 site
    w_even = np.sum(eigvecs[::2, m_idx])  # 偶數 site
    # 拓撲相角 = 奇偶權重比嘅相位
    if abs(w_even) > 1e-15:
        theta_0[m_idx] = np.arctan2(w_odd, w_even)
    else:
        theta_0[m_idx] = np.pi/2

print(f"\n拓撲相角 θ_0^(m):")
print(f"  基態 (m=0): θ_0 = {theta_0[0]:.6f} rad = {np.degrees(theta_0[0]):.2f}°")
print(f"  m=1: θ_0 = {theta_0[1]:.6f} rad = {np.degrees(theta_0[1]):.2f}°")
print(f"  m=44 (Nyquist): θ_0 = {theta_0[44]:.6f} rad = {np.degrees(theta_0[44]):.2f}°")

# ══════════════════════════════════════════════════════════════
# 5. 構建完整 T_pipe 相位場
# ══════════════════════════════════════════════════════════════
# Φ_m(x_k) = A_m cos(k·ω_m + θ_0^(m))
# ω_m = πm/44 (88-site 週期性)
# A_m = 1/√N (歸一化)

omega_m = np.pi * m / (N/2)  # = πm/44
Phi_m = np.zeros((N, N))
for m_idx in range(N):
    Phi_m[m_idx, :] = np.cos(k * omega_m[m_idx] + theta_0[m_idx])

# 真空態: 用 γ_k 譜加權, 確保奇偶比例 88:90
# 偶數 site 權重: γ_even / Σγ_even
# 奇數 site 權重: γ_odd / Σγ_odd
weight_even = gamma_even / gamma_even.sum()
weight_odd = gamma_odd / gamma_odd.sum()

# 構建加權真空態: 每個 site 嘅振幅按 γ_k 比例
psi_vac = np.zeros(N)
psi_vac[::2] = weight_even  # 偶數 site
psi_vac[1::2] = weight_odd  # 奇數 site
psi_vac = psi_vac / np.sqrt(np.sum(psi_vac**2))  # 歸一化

print(f"\n真空態 |ψ_vac⟩ (γ_k 加權):")
print(f"  norm: {np.sqrt(np.sum(psi_vac**2)):.6f}")

# 真空態嘅奇偶分解
vac_even = np.sum(psi_vac[::2]**2)
vac_odd = np.sum(psi_vac[1::2]**2)
print(f"  偶數 (世界) 能量: {vac_even:.6f}")
print(f"  奇數 (觀察者) 能量: {vac_odd:.6f}")
print(f"  比例: {vac_odd/vac_even:.6f} (理論 88/90 = {88/90:.6f})")

# ══════════════════════════════════════════════════════════════
# 6. 儲存
# ══════════════════════════════════════════════════════════════
results = {
    'N_sites': N,
    'eigval_range': [float(eigvals.min()), float(eigvals.max())],
    'theory_range': [float(theory_vals.min()), float(theory_vals.max())],
    'max_eigval_dev': float(np.max(np.abs(np.sort(eigvals) - np.sort(theory_vals)))),
    'theta_0_m0_rad': float(theta_0[0]),
    'theta_0_m0_deg': float(np.degrees(theta_0[0])),
    'theta_0_m1_rad': float(theta_0[1]),
    'theta_0_m44_rad': float(theta_0[44]),
    'vac_norm': float(np.sqrt(np.sum(psi_vac**2))),
    'vac_even_energy': float(vac_even),
    'vac_odd_energy': float(vac_odd),
    'vac_odd_even_ratio': float(vac_odd/vac_even),
    'theory_ratio': 88/90,
}

outpath = f'{OUTDIR}/step2_tpipe_eigenstates.json'
with open(outpath, 'w') as f:
    json.dump(results, f, indent=2, default=float)
print(f"\n✅ 結果已存: {outpath}")