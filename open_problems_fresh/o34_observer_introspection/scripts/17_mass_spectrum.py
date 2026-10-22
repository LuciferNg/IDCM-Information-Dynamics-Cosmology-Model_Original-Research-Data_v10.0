#!/usr/bin/env python3
"""
O34 — m_n 全質量階梯幾何譜推導 (scripts/17)
====================================================
從級聯閉合形式推廣:
  m_n = E_kchain × φ^(47 + 37/528) × √γ_n
      = 13.8 × sin(nπ/88)/sin(7π/88) MeV

檢驗 n=1..44 模式質量對應已知粒子/特徵標度。
"""

import numpy as np
from decimal import Decimal, getcontext

getcontext().prec = 100

N = 44
phi = (1 + np.sqrt(5)) / 2
phi_inv = phi - 1

# 基礎常數
M_P = 1.220890e22  # MeV
H0 = 72.59
hbar = 6.582119569e-16
H0_per_s = H0 * 1000 / (3.085677581e22)
E_H = hbar * H0_per_s
E_H_MeV = E_H * 1e-6

CY3 = 3 * N + 2
N45 = N + 1
sq_MP_hbar = np.sqrt(M_P * E_H_MeV)
corr = 1 - CY3 / N45**2
E_kchain = sq_MP_hbar * corr  # MeV

# 級聯閉合
m_7_closed = 13.8  # MeV
gamma_7 = 4 * np.sin(np.pi * 7 / 88)**2
sqrt_gamma_7 = np.sqrt(gamma_7)

# 通用算式: m_n = 13.8 × sin(nπ/88)/sin(7π/88)
def m_n(n):
    """模式 n 嘅質量 (MeV)"""
    return 13.8 * np.sin(np.pi * n / 88) / np.sin(np.pi * 7 / 88)

print("=" * 67)
print("  O34 — m_n 全質量階梯幾何譜")
print("=" * 67)
print(f"\n  通用算式: m_n = 13.8 × sin(nπ/88)/sin(7π/88) MeV")
print(f"  528 = CY₃ × B × N_d = {CY3} × 4 × {N} = {CY3*4*N}")
print(f"  47 = N_d + dim_ℂ(CY₃) = {N} + 3")
print()

# ═══════════════════════════════════════════════════════════════
# 全譜計算
# ═══════════════════════════════════════════════════════════════
print("─── 全質量譜 (n=1..44, MeV) ───")
print(f"{'n':>3} | {'m_n(MeV)':>10} | {'ln(m_n)':>10} | {'特徵標度':>20}")
print("-" * 50)

modes = []
for n in range(1, N + 1):
    mass = m_n(n)
    log_m = np.log(mass) if mass > 0 else float('-inf')
    modes.append((n, mass, log_m))

# 分組顯示
for n, mass, log_m in modes:
    label = ""
    if n == 1: label = "基礎模式"
    elif n == 2: label = "第一對偶"
    elif n == 3: label = "第三諧波"
    elif n == 4: label = "第四諧波"
    elif n == 5: label = "第五諧波"
    elif n == 6: label = "第六諧波 (ν?)"
    elif n == 7: label = "DM 質量 (閉合)"
    elif n == 11: label = "L₅ 諧波"
    elif n == 13: label = "F₇ 諧波"
    elif n == 22: label = "Z₂ 對稱 (γ=2)"
    elif n == 33: label = "K_Tree 深度"
    elif n == 44: label = "Nyquist (v_g=0)"
    print(f"  {n:3d} | {mass:10.4f} | {log_m:10.4f} | {label:>20}")

# ═══════════════════════════════════════════════════════════════
# 已知粒子質量對比
# ═══════════════════════════════════════════════════════════════
print(f"\n{'═'*67}")
print("  已知粒子質量對比")
print(f"{'═'*67}")

# 已知粒子質量 (MeV)
particles = [
    ("ν₁ (輕)", 0.001e-3, 1e-6),  # 中微子 ~1 meV
    ("ν₂ (中)", 0.008e-3, 1e-6),  # ~8 meV
    ("ν₃ (重)", 0.05e-3, 1e-5),  # ~50 meV
    ("電子", 0.511, 0.01),
    ("μ子", 105.66, 0.5),
    ("τ子", 1776.86, 5),
    ("上夸克", 2.16, 0.5),
    ("下夸克", 4.67, 0.5),
    ("奇夸克", 93.5, 5),
    ("粲夸克", 1270, 30),
    ("底夸克", 4180, 50),
    ("頂夸克", 172760, 500),
    ("質子", 938.27, 0.5),
    ("中子", 939.57, 0.5),
    ("π⁰", 134.98, 0.5),
    ("π⁺", 139.57, 0.5),
    ("Δm²₂₁ (ν)", 7.5e-5, 1e-6),  # eV²
    ("Δm²₃₁ (ν)", 2.5e-3, 1e-5),  # eV²
]

print(f"\n  {'粒子':>15} | {'質量(MeV)':>12} | {'最近模式':>10} | {'偏差':>10}")
print("-" * 55)

for name, mass, tol in particles:
    if 'Δm²' in name:
        continue  # 平方差另計
    # 搵最近模式
    best_n = 1
    best_err = float('inf')
    for n, m_n_val, _ in modes:
        if m_n_val > 0:
            err = abs(m_n_val - mass) / mass * 100
            if err < best_err:
                best_err = err
                best_n = n
    if best_err < 50:
        status = f"n={best_n:2d}"
        print(f"  {name:>15} | {mass:12.4f} | {status:>10} | {best_err:8.2f}%")
    else:
        print(f"  {name:>15} | {mass:12.4f} | {'—':>10} | {'>50%':>8}")

# ═══════════════════════════════════════════════════════════════
# 對數間距分析
# ═══════════════════════════════════════════════════════════════
print(f"\n{'═'*67}")
print("  對數間距分析")
print(f"{'═'*67}")

# 模式間嘅 log 間距
log_gaps = []
for i in range(1, len(modes)):
    gap = modes[i][2] - modes[i-1][2]
    log_gaps.append(gap)

print(f"\n  log 間距統計:")
print(f"    平均: {np.mean(log_gaps):.4f}")
print(f"    標準差: {np.std(log_gaps):.4f}")
print(f"    最小: {min(log_gaps):.4f} (n={np.argmin(log_gaps)+2}-{np.argmin(log_gaps)+1})")
print(f"    最大: {max(log_gaps):.4f} (n={np.argmax(log_gaps)+2}-{np.argmax(log_gaps)+1})")
print(f"    ln(φ) = {np.log(phi):.4f}")

# 係咪等間距?
print(f"\n  log_φ 間距檢查:")
for i in range(1, len(modes)):
    gap = modes[i][2] - modes[i-1][2]
    log_phi_gap = gap / np.log(phi)
    if i <= 5 or i % 10 == 0:
        print(f"    n={i+1}-{i}: log_φ間距 = {log_phi_gap:.4f}")

# ═══════════════════════════════════════════════════════════════
# 關鍵模式分析
# ═══════════════════════════════════════════════════════════════
print(f"\n{'═'*67}")
print("  關鍵拓撲模式")
print(f"{'═'*67}")

key_modes = [1, 2, 3, 4, 5, 6, 7, 11, 13, 22, 33, 44]
print(f"\n  {'n':>3} | {'m_n(MeV)':>10} | {'√γ_n':>8} | {'γ_n':>8} | {'v_g/c':>8}")
print("-" * 45)
for n in key_modes:
    mass = m_n(n)
    sqrt_g = np.sqrt(4 * np.sin(np.pi * n / 88)**2)
    gamma = 4 * np.sin(np.pi * n / 88)**2
    vg = np.cos(np.pi * n / 88)
    print(f"  {n:3d} | {mass:10.4f} | {sqrt_g:8.4f} | {gamma:8.4f} | {vg:8.4f}")

# ═══════════════════════════════════════════════════════════════
# 同 m_7 嘅比例
# ═══════════════════════════════════════════════════════════════
print(f"\n{'═'*67}")
print("  模式比例 (m_n/m_7)")
print(f"{'═'*67}")

for n in key_modes:
    ratio = m_n(n) / 13.8
    print(f"  n={n:2d}: m_n/m_7 = {ratio:.6f} = sin({n}π/88)/sin(7π/88)")

# 儲存
with open("data/mass_spectrum_results.txt", "w") as f:
    f.write("O34 — m_n Mass Spectrum\n")
    f.write("=" * 67 + "\n")
    f.write(f"m_n = 13.8 * sin(n*pi/88)/sin(7*pi/88) MeV\n")
    f.write(f"\n{'n':>3} {'m_n(MeV)':>12}\n")
    for n, mass, _ in modes:
        f.write(f"{n:3d} {mass:12.4f}\n")
    f.write(f"\nLog gap stats: mean={np.mean(log_gaps):.4f}, std={np.std(log_gaps):.4f}\n")
    f.write(f"Status: 🟢 spectrum derived, particle matching 🟡\n")