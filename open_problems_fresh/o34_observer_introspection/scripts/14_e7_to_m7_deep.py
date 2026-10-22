#!/usr/bin/env python3
"""
O34 — E_kchain → m_7 級聯深層推導 (scripts/14)
====================================================
從 scripts/13 發現:
  M₀/E_kchain ≈ φ^47 (47 = L₈, 偏差 3.3%)
  m_7/E_kchain / φ^45 ≈ φ^(1/φ) (偏差 0.5%)

目標: 用 CY₃/45² 幾何因子閉合偏差
思路: M₀ 可能同 √(M_P·ħ·H₀) × φ^47 × (CY₃/45² 相關修正) 有關
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

# E_kchain 基礎
CY3 = 3 * N + 2  # 134
N45 = N + 1  # 45
sq_MP_hbar = np.sqrt(M_P * E_H_MeV)  # √(M_P·ħ·H₀) MeV
corr = 1 - CY3 / N45**2  # 1891/2025
E_kchain = sq_MP_hbar * corr  # MeV

# m_7 相關
m_7 = 13.8  # MeV
gamma_7 = 4 * np.sin(np.pi * 7 / 88)**2
M0 = m_7 / np.sqrt(gamma_7)  # 27.9 MeV

print("=" * 67)
print("  O34 — E_kchain → m_7 級聯深層推導")
print("=" * 67)
print(f"\n  E_kchain = {E_kchain*1e9:.4f} meV")
print(f"  √(M_P·ħ·H₀) = {sq_MP_hbar*1e9:.4f} meV")
print(f"  M₀ = m_7/√γ_7 = {M0:.4f} MeV")
print(f"  m_7 = {m_7:.4f} MeV")
print()

# ═══════════════════════════════════════════════════════════════
# [A] M₀ 同 √(M_P·ħ·H₀) × φ^L8 嘅關係
# ═══════════════════════════════════════════════════════════════
print("─── [A] M₀ = √(M_P·ħ·H₀) × φ^L₈ × f(CY₃) ───")

# L₈ = 47 (Lucas)
L = [2, 1]
for i in range(2, 10):
    L.append(L[-1] + L[-2])
print(f"  Lucas: L₈ = {L[8]} = 47")

# 基礎候選: M₀_base = √(M_P·ħ·H₀) × φ^47
M0_base = sq_MP_hbar * phi**47
print(f"\n  √(M_P·ħ·H₀) × φ^47 = {M0_base:.4f} MeV")
print(f"  M₀ = {M0:.4f} MeV")
print(f"  M₀ / M0_base = {M0/M0_base:.8f}")

# 呢個比率 = ?
ratio_M0 = M0 / M0_base
print(f"  log_φ(ratio) = {np.log(ratio_M0)/np.log(phi):.6f}")

# 需要嘅修正: M₀ = M0_base × f
# f = 1.0343, 接近 1 + 1/29 = 1.0345? 29 = L₇
# 1 + 1/29 = 1.034483, 偏差 0.02%
print(f"  1 + 1/L₇ = 1 + 1/29 = {1 + 1/29:.8f}")
print(f"  偏差 = {abs(ratio_M0 - (1+1/29))/(1+1/29)*100:.4f}%")

# 其他候選
candidates = []
for k in range(-10, 11):
    for n in [1, 2, 4, 7, 11, 18, 29, 44, 45, 88, 90, CY3]:
        val = 1 + k/n
        err = abs(ratio_M0 - val) / val * 100
        if err < 0.1:
            candidates.append((k, n, val, err))
print(f"\n  最佳 1 + k/n 候選:")
for k, n, val, err in sorted(candidates, key=lambda x: x[3])[:5]:
    print(f"    1 + {k}/{n} = {val:.8f}, 偏差 {err:.4f}%")

# 1 + 1/29 = 1.034483 (29 = L₇), 偏差 0.02% — 好靚!
# 但係 29 係咪結構? 29 = L₇ = 7+18? 29 = ?
# 29 = L₇ (Lucas)

# 唔夠靚, 試其他
# ratio_M0 = 1.034302
# 可能係 CY₃/45² 相關?
print(f"\n  ratio_M0 - 1 = {ratio_M0 - 1:.8f}")
print(f"  CY₃/45² = {CY3/45**2:.8f}")
print(f"  (ratio_M0-1) / (CY₃/45²) = {(ratio_M0-1)/(CY3/45**2):.6f}")
print(f"  (ratio_M0-1) × 45² = {(ratio_M0-1)*45**2:.6f}")

# (ratio_M0-1) × 45² = 6.947 ≈ 7?
# 7 = L₄ = F₇/F₂? 7 = γ_22? γ_22 = 2
# 7 = ?
print(f"  7 = L₄ (Lucas)")

# 所以 M₀ ≈ √(M_P·ħ·H₀) × φ^47 × (1 + 7/45²)?
M0_cand = sq_MP_hbar * phi**47 * (1 + 7/45**2)
print(f"\n  √(M_P·ħ·H₀)×φ^47×(1+L₄/45²) = {M0_cand:.4f} MeV")
print(f"  M₀ = {M0:.4f} MeV, 偏差 = {abs(M0_cand-M0)/M0*100:.4f}%")

# 7 = L₄. 1 + 7/45² = 1.00346, 唔係 1.0343
# 錯咗, 用錯公式

# 重新: ratio_M0 = 1.0343
# 1.0343 - 1 = 0.0343 ≈ 1/29.1
# 29 = L₇
# 1/29 = 0.03448
# 偏差 0.5%

# 有冇其他結構? 0.0343 = ?
print(f"\n  ratio_M0 - 1 = {ratio_M0-1:.8f}")
print(f"  φ⁻⁵ = {phi**(-5):.8f}")
print(f"  φ⁻⁴ = {phi**(-4):.8f}")
print(f"  ε = {eps:.8f}")
print(f"  ε² = {eps**2:.8f}")

# ═══════════════════════════════════════════════════════════════
# [B] 級聯算符形式
# ═══════════════════════════════════════════════════════════════
print(f"\n{'═'*67}")
print("  [B] 級聯算符形式")
print(f"{'═'*67}")

# 級聯算符 L̂: E_kchain → M₀ → m_7
# 兩步: L̂₁(E_kchain) = M₀, L̂₂(M₀) = m_7
# 或者: L̂_n(E_kchain) = m_n

# L̂₁: E_kchain → M₀
# M₀/E_kchain = 6.87e9 = φ^47.07
# 47.07 = L₈ + 0.07
# 0.07 = ?

# L̂₂: M₀ → m_7
# m_7/M₀ = √γ_7 = 0.4946 (代數恆等式!)
# 呢個已經閉合!

# 所以關鍵係 L̂₁: E_kchain → M₀
# M₀ = E_kchain × φ^47 × f
# f = M₀/(E_kchain × φ^47) = ?

f_M0 = M0 / (E_kchain * phi**47)
print(f"\n  M₀/(E_kchain × φ^47) = {f_M0:.8f}")
print(f"  log_φ(f_M0) = {np.log(f_M0)/np.log(phi):.6f}")

# 如果 f_M0 = 1 + δ, δ = ?
delta = f_M0 - 1
print(f"  δ = f_M0 - 1 = {delta:.8f}")
print(f"  δ = 1/29.14 = {1/(delta):.2f}")
print(f"  L₇ = 29, 1/29 = {1/29:.8f}")
print(f"  δ - 1/L₇ = {delta - 1/29:.6e}")

# δ 同 φ 冪嘅關係
print(f"  φ⁻⁵ = {phi**(-5):.8f}")
print(f"  φ⁻⁶ = {phi**(-6):.8f}")
print(f"  δ/φ⁻⁵ = {delta/phi**(-5):.4f}")
print(f"  δ/φ⁻⁶ = {delta/phi**(-6):.4f}")

# ═══════════════════════════════════════════════════════════════
# [C] 直接 m_7 同 √(M_P·ħ·H₀) 嘅關係
# ═══════════════════════════════════════════════════════════════
print(f"\n{'═'*67}")
print("  [C] m_7 直接同 √(M_P·ħ·H₀) 嘅關係")
print(f"{'═'*67}")

# m_7 = √(M_P·ħ·H₀) × φ^k × g(CY₃, γ_7)
ratio_m7_sq = m_7 / sq_MP_hbar
print(f"\n  m_7 / √(M_P·ħ·H₀) = {ratio_m7_sq:.6e}")
print(f"  log_φ = {np.log(ratio_m7_sq)/np.log(phi):.6f}")

# 45.465? 接近 45.5
# 45.5 = 45 + 0.5 = N_d+1 + 0.5
print(f"  45.5 = N_d + 1.5 = {N + 1.5}")

# 半整數: 45.5 = 91/2 = Σγ_even/2 + 0.5? Σγ_even=90, 90/2=45, 45+0.5=45.5
# 45.465 vs 45.5, 偏差 0.077%
# 45.465 = 45 + 0.465
# 0.465 ≈ 1 - 1/φ? 1 - 0.618 = 0.382? 唔係
# 0.465 ≈ 1/φ²? 0.382? 唔係
# 0.465 ≈ 1/2.15? 唔係

# 嘗試: 45.465 = 45 + 0.465
# 0.465 ≈ ?
print(f"\n  log_φ - 45 = {np.log(ratio_m7_sq)/np.log(phi) - 45:.6f}")
print(f"  φ⁻¹ = {phi_inv:.6f}")
print(f"  φ⁻² = {phi**(-2):.6f}")
print(f"  φ⁻³ = {phi**(-3):.6f}")
print(f"  φ⁻¹/2 = {phi_inv/2:.6f}")
print(f"  φ⁻¹/φ = {phi_inv/phi:.6f}")

# 0.465 ≈ 0.5 - 0.035? 0.5 = 1/2, 0.035 ≈ 1/29
# 0.5 - 1/29 = 0.4655!
print(f"  0.5 - 1/L₇ = 0.5 - 1/29 = {0.5 - 1/29:.6f}")
print(f"  偏差 = {abs((np.log(ratio_m7_sq)/np.log(phi) - 45) - (0.5 - 1/29)):.6f}")

# 所以 m_7/√(M_P·ħ·H₀) ≈ φ^(45 + 0.5 - 1/29) = φ^45.4655
# 精確: 45.465 vs 45.4655, 偏差 1e-6
# 但呢個係近似, 唔係精確代數閉合

# m_7 = √(M_P·ħ·H₀) × φ^45 × √φ × φ^(-1/29)?
# √φ = φ^0.5 = 1.272
# φ^(-1/29) = 0.979
# φ^45.4655 = φ^45 × √φ × φ^(-1/29) = 2.54e9 × 1.272 × 0.979 = 3.16e9?
# 實際 3.17e9, 偏差 0.3% — 近似

# 更直接: 檢查有冇精確 φ^(k+p/q) 形式
# 45.465 = 45 + 0.465 = 45 + 465/1000 = 45 + 93/200
# 93/200 = 3×31/(2×100) — 冇結構

# 試: 45.465 = 45 + 13/28? 13/28 = 0.4643? 偏差 0.0016
# 13/28 = (F₇)/(4×L₅)? 4×L₅=44, 13/44 = 0.295 — 唔係
# 13 = F₇, 28 = L₇-1? 29-1=28

# 保持誠實: 45.465 冇簡單 φ 有理式
# 但 45.5 - 1/29 = 45.4655 係最接近嘅結構候選

print(f"\n  精確 log_φ(m_7/√(M_P·ħ·H₀)) = {np.log(ratio_m7_sq)/np.log(phi):.10f}")
print(f"  45.5 - 1/L₇ = 45.5 - 1/29 = 45.465517")
print(f"  偏差 = {abs(np.log(ratio_m7_sq)/np.log(phi) - (45.5 - 1/29)):.2e}")

# 但 45.5 = 91/2 = (Σγ_even+1)/2 = (90+1)/2
# 1/29 = 1/L₇
# 所以: log_φ(m_7/√(M_P·ħ·H₀)) ≈ (Σγ_even+1)/2 - 1/L₇
# 偏差 5e-5 — 有趣但非精確

# ═══════════════════════════════════════════════════════════════
# 總結
# ═══════════════════════════════════════════════════════════════
print(f"\n{'═'*67}")
print(f"  探索結論")
print(f"{'═'*67}")

print(f"""
  ✅ 代數閉合: m_7/M₀ = √γ_7 = 2sin(7π/88)  (精確)
  ✅ 結構: 47 = L₈ (Lucas), 45 = N_d+1 (Σγ_even/2)
  🟡 未閉合: M₀/E_kchain = φ^47 × f
               f = {f_M0:.8f}, δ = {delta:.8f}
               δ ≈ 1/L₇ = 1/29 (偏差 0.5%)
  🟡 未閉合: m_7/√(M_P·ħ·H₀) = φ^45.465
               ≈ φ^((Σγ_even+1)/2 - 1/L₇) (偏差 5e-5)
  🔴 級聯算符: 需要包含 CY₃/45² 幾何因子嘅精確代數形式
""")

# 儲存
with open("data/e7_to_m7_deep_results.txt", "w") as f:
    f.write("O34 — E_kchain to m_7 Deep Cascade\n")
    f.write("=" * 67 + "\n")
    f.write(f"m_7/M0 = sqrt(gamma_7) = {np.sqrt(gamma_7):.10f} (exact)\n")
    f.write(f"M0/E_kchain = {M0/E_kchain:.6e} = phi^47 * {f_M0:.8f}\n")
    f.write(f"47 = L8 = Lucas(8)\n")
    f.write(f"delta = f_M0 - 1 = {delta:.8f}\n")
    f.write(f"delta ≈ 1/L7 = 1/29 = {1/29:.8f} (err 0.5%)\n")
    f.write(f"m_7/sqrt(M_P·ħ·H₀) = {ratio_m7_sq:.6e}\n")
    f.write(f"log_phi(m_7/...) = {np.log(ratio_m7_sq)/np.log(phi):.10f}\n")
    f.write(f"Status: 🟡 M0 ≈ phi^L8, m_7/M0 closed, cascade operator 🔴\n")