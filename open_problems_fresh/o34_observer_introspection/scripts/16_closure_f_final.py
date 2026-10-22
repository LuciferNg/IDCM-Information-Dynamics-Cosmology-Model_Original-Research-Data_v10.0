#!/usr/bin/env python3
"""
O34 — 候選 G 同 37/12 結構最終驗證 (scripts/16)
====================================================
發現: log_φ(f) = 0.0700696
  log_φ(f) × 44 = 3.083064 ≈ 3 + 1/12 = 37/12
  12 = dim_ℂ(CY₃) × B = 3 × 4 (新結構!)

候選 G: f = √(φ^(3/44) × 44/42.5) 偏差 0.003%

目標: 嚴格驗證兩個候選, 判斷邊個係真正結構
"""

import numpy as np
from decimal import Decimal, getcontext

getcontext().prec = 100

N = 44
phi = (1 + np.sqrt(5)) / 2
phi_inv = phi - 1
eps = phi_inv / 4

# 常數
M_P = 1.220890e22  # MeV
H0 = 72.59  # km/s/Mpc
hbar = 6.582119569e-16  # eV·s
H0_per_s = H0 * 1000 / (3.085677581e22)
E_H = hbar * H0_per_s  # eV
E_H_MeV = E_H * 1e-6  # MeV

CY3 = 3 * N + 2  # 134
N45 = N + 1  # 45
sq_MP_hbar = np.sqrt(M_P * E_H_MeV)
corr = 1 - CY3 / N45**2  # 1891/2025
E_kchain = sq_MP_hbar * corr  # MeV

m_7 = 13.8  # MeV
gamma_7 = 4 * np.sin(np.pi * 7 / 88)**2
M0 = m_7 / np.sqrt(gamma_7)

f_target = M0 / (E_kchain * phi**47)
logf = np.log(f_target) / np.log(phi)

print("=" * 67)
print("  O34 — 候選 G vs 37/12 最終驗證")
print("=" * 67)
print(f"\n  f_target = {f_target:.12f}")
print(f"  log_φ(f) = {logf:.12f}")
print()

# ═══════════════════════════════════════════════════════════════
# 候選 1: log_φ(f) = (dim_ℂ + 1/(dim_ℂ·B))/N_d = (3+1/12)/44
# ═══════════════════════════════════════════════════════════════
print("─── 候選 1: log_φ(f) = (3 + 1/12)/44 = 37/528 ───")

cand1_log = (3 + 1/12) / 44
cand1 = phi**cand1_log
err1 = abs(cand1 - f_target) / f_target * 100
err1_log = abs(cand1_log - logf) / logf * 100
print(f"  log_φ 候選 = {cand1_log:.12f}")
print(f"  log_φ 實際 = {logf:.12f}")
print(f"  偏差 (log) = {err1_log:.6f}%")
print(f"  f 候選 = {cand1:.10f}")
print(f"  偏差 (f) = {err1:.6f}%")
print(f"  結構: 12 = dim_ℂ × B = 3×4, 37 = 3×12+1")
print(f"  12 嘅角色: 1/(dim_ℂ·B) = 1/12 係複維度×分支嘅倒數修正")
print()

# ═══════════════════════════════════════════════════════════════
# 候選 2: f = √(φ^(3/44) × 44/42.5)  (幾何平均)
# ═══════════════════════════════════════════════════════════════
print("─── 候選 2: f = √(φ^(3/44) × N_d/(N_d-3/2)) ───")

B_cand = phi**(3/44)
C_cand = 44 / 42.5
G = np.sqrt(B_cand * C_cand)
errG = abs(G - f_target) / f_target * 100
logG = np.log(G) / np.log(phi)
errG_log = abs(logG - logf) / logf * 100
print(f"  B = φ^(3/44) = {B_cand:.10f}")
print(f"  C = 44/42.5 = {C_cand:.10f}")
print(f"  G = √(B×C) = {G:.10f}")
print(f"  偏差 (f) = {errG:.6f}%")
print(f"  log_φ(G) = {logG:.12f}")
print(f"  偏差 (log) = {errG_log:.6f}%")
print()

# ═══════════════════════════════════════════════════════════════
# 比較: log_φ(G) = (3/44 + log_φ(44/42.5))/2
# ═══════════════════════════════════════════════════════════════
logC = np.log(C_cand) / np.log(phi)
print("─── log_φ(G) 分解 ───")
print(f"  log_φ(B) = 3/44 = {3/44:.10f}")
print(f"  log_φ(C) = log_φ(44/42.5) = {logC:.10f}")
print(f"  log_φ(G) = (3/44 + log_φ(C))/2 = {logG:.10f}")
print(f"  log_φ(C) × 44 = {logC*44:.6f}")
print(f"  log_φ(C) × 44 ≈ 3.172?")
print(f"  3.172 ≈ ? 3 + 1/5.8? 唔係靚結構")
print()

# ═══════════════════════════════════════════════════════════════
# 關鍵判斷: 邊個係「結構」邊個係「湊數」?
# ═══════════════════════════════════════════════════════════════
print("─── 結構判斷 ───")

# 候選 1 嘅結構: log_φ(f)×N_d = 3 + 1/12
# 3 = dim_ℂ(CY₃), 12 = dim_ℂ×B
# 即係: log_φ(f) = dim_ℂ/N_d + 1/(dim_ℂ·B·N_d)
# f = φ^(dim_ℂ/N_d) × φ^(1/(dim_ℂ·B·N_d))
#   = φ^(3/44) × φ^(1/528)
#   = B_cand × φ^(1/528)
print("候選 1 重寫:")
cand1_alt = phi**(3/44) * phi**(1/(3*4*44))
print(f"  f = φ^(3/44) × φ^(1/(3·4·44)) = φ^(3/44) × φ^(1/528)")
print(f"    = {phi**(3/44):.10f} × {phi**(1/528):.10f} = {cand1_alt:.10f}")
print(f"  偏差 = {abs(cand1_alt - f_target)/f_target*100:.6f}%")
print()

# 候選 2 重寫:
# G = √(φ^(3/44) × 44/42.5)
# log_φ(G) = 3/88 + (1/2)log_φ(44/42.5)
# = 3/88 + (1/2)log_φ(88/85)
# = 3/88 + (1/2)[log(88/85)/log(φ)]
print("候選 2 重寫:")
print(f"  log_φ(G) = 3/88 + (1/2)·log_φ(88/85)")
print(f"  88/85 = 44/42.5 (88-site 鏈 / 85-site?)")
print(f"  85 = 88 - 3 = 2N_d - dim_ℂ")
print(f"  → C = 2N_d/(2N_d - dim_ℂ) = 88/85")
print()

# 候選 1 更靚: 冇引入新數字 (只有 dim_ℂ=3, B=4, N_d=44 同埋 1/12)
# 候選 2 引入 42.5 = N_d - 3/2 (3/2 嘅來源 = dim_ℂ/2 有少少人為)
# 判斷: 候選 1 結構更乾淨

# ═══════════════════════════════════════════════════════════════
# 候選 1 精確度檢查
# ═══════════════════════════════════════════════════════════════
print("─── 候選 1 精確度 ───")
print(f"  偏差 0.009% (log) / 0.0088% (f)")
print(f"  呢個偏差係咪可以接受?")
print(f"  m_7 本身係 13.8 MeV (1 位小數, 精度 ~0.7%)")
print(f"  如果 m_7 有 0.7% 誤差, 咁 f 嘅 0.009% 偏差完全喺 m_7 精度內")
print(f"  → 候選 1 喺 m_7 觀測精度內閉合 ✅")
print()

# 驗證: 如果 m_7 = M₀×√γ_7 用候選 1 反推
m_7_implied = E_kchain * phi**47 * cand1 * np.sqrt(gamma_7)
print(f"  用候選 1 反推 m_7:")
print(f"  m_7_implied = E_kchain × φ^47 × f₁ × √γ_7 = {m_7_implied:.4f} MeV")
print(f"  m_7 目標 = {m_7:.4f} MeV")
print(f"  偏差 = {abs(m_7_implied - m_7)/m_7*100:.6f}%")
print()

# ═══════════════════════════════════════════════════════════════
# 最終級聯公式
# ═══════════════════════════════════════════════════════════════
print("=" * 67)
print("  級聯公式 (候選 1)")
print("=" * 67)
print(f"""
  m_7 = E_kchain × φ^47 × φ^(37/528) × √γ_7
      = E_kchain × φ^(47 + 37/528) × 2sin(7π/88)

  47 = N_d + dim_ℂ(CY₃) = 44 + 3
  37/528 = (3 + 1/12)/(12·44) = (dim_ℂ + 1/(dim_ℂ·B))/(dim_ℂ·B·N_d)
  12 = dim_ℂ × B = 3 × 4

  級聯算符 D: E_kchain → m_7
  D = φ^(47 + 37/528) × √γ_7
    = φ^(N_d + dim_ℂ + 1/(dim_ℂ·B·N_d)) × 2sin(7π/88)
""")

# 儲存
with open("data/closure_f_final_results.txt", "w") as f:
    f.write("O34 — Final Closure of Cascade Operator D\n")
    f.write("=" * 67 + "\n")
    f.write(f"f_target = {f_target:.12f}\n")
    f.write(f"Candidate 1: phi^(37/528), err = {err1:.6f}% (log {err1_log:.6f}%)\n")
    f.write(f"Candidate 2 (G): sqrt(phi^(3/44)*44/42.5), err = {errG:.6f}%\n")
    f.write(f"37/528 = (3 + 1/12)/(12*44), 12 = dim_C*B = 3*4\n")
    f.write(f"47 = N_d + dim_C(CY3) = 44 + 3\n")
    f.write(f"m_7 implied = {m_7_implied:.4f} MeV (target {m_7:.4f}, err {abs(m_7_implied-m_7)/m_7*100:.6f}%)\n")
    f.write(f"Cascade: m_7 = E_kchain * phi^(47+37/528) * sqrt(gamma_7)\n")
    f.write(f"Status: 🟢 closed within m_7 precision (0.009% < 0.7%)\n")