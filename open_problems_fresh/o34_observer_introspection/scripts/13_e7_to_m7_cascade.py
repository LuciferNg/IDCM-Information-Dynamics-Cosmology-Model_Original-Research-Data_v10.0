#!/usr/bin/env python3
"""
O34 — E_kchain → m_7 級聯推導 (scripts/13)
================================================
調律者指定三步驟:
[1] 定義級聯算符: 利用 K-Chain 拓撲算符, 建立 E_kchain 到 m_7 嘅降維算式
[2] 導入 CY₃/45² 幾何因子: 驗證 45 階對稱群在階梯算符中的衰減係數
[3] 驗證質量階梯比值: m_7/M_0 是否精確匹配代數閉合條件
"""

import numpy as np
from decimal import Decimal, getcontext

getcontext().prec = 100

N = 44
phi = (1 + np.sqrt(5)) / 2
phi_inv = phi - 1
eps = phi_inv / 4

# 基礎常數
M_P = 1.220890e22  # MeV (Planck 質量)
H0 = 72.59  # km/s/Mpc
hbar = 6.582119569e-16  # eV·s
c = 299792.458  # km/s
Mpc_to_km = 3.085677581e19

# 導出量
H0_per_s = H0 * 1000 / (3.085677581e22)  # s⁻¹
E_H = hbar * H0_per_s  # eV (ħ·H₀)
E_H_MeV = E_H * 1e-6  # MeV

# E_kchain (O34 閉合)
CY3 = 3 * N + 2  # 134
sq_MP_hbar_H0 = np.sqrt(M_P * E_H_MeV)  # √(M_P·ħ·H₀) in MeV
correction = 1 - CY3 / (N + 1)**2  # 1 - 134/45² = 1891/2025
E_kchain = sq_MP_hbar_H0 * correction  # MeV
E_kchain_meV = E_kchain * 1e9  # meV (1 MeV = 1e9 meV)

# m_7
m_7 = 13.8  # MeV (第 7 模 DM 質量)
gamma_7 = 4 * np.sin(np.pi * 7 / 88)**2

# 基礎質量標度 M₀ = m_7 / √γ_7
M0 = m_7 / np.sqrt(gamma_7)

print("=" * 67)
print("  O34 — E_kchain → m_7 級聯推導")
print("=" * 67)
print(f"\n  E_kchain = {E_kchain_meV:.6f} meV (O34 閉合)")
print(f"  m_7 = {m_7:.4f} MeV (第 7 模)")
print(f"  γ_7 = {gamma_7:.6f}")
print(f"  √γ_7 = {np.sqrt(gamma_7):.6f}")
print(f"  M₀ = m_7/√γ_7 = {M0:.4f} MeV")
print(f"  CY₃ = {CY3}, N_d+1 = 45, correction = {correction:.10f}")

# ═══════════════════════════════════════════════════════════════
# 步驟 1: 級聯算符分析
# ═══════════════════════════════════════════════════════════════
print(f"\n{'═'*67}")
print("  [1] 級聯算符分析")
print(f"{'═'*67}")

# 1a. 直接比率
ratio_m7_Ek = m_7 / E_kchain
ratio_M0_Ek = M0 / E_kchain
log_phi_m7 = np.log(ratio_m7_Ek) / np.log(phi)
log_phi_M0 = np.log(ratio_M0_Ek) / np.log(phi)

print(f"\n  m_7/E_kchain = {ratio_m7_Ek:.6e}")
print(f"  log_φ(m_7/E_kchain) = {log_phi_m7:.6f}")
print(f"  M₀/E_kchain = {ratio_M0_Ek:.6e}")
print(f"  log_φ(M₀/E_kchain) = {log_phi_M0:.6f}")

# 1b. 最近整數分析
for logphi, name in [(log_phi_m7, "m_7"), (log_phi_M0, "M₀")]:
    print(f"\n  === {name} log_φ = {logphi:.6f} ===")
    for k in range(40, 55):
        ratio = phi**k
        dev = abs(ratio - np.exp(logphi * np.log(phi))) / np.exp(logphi * np.log(phi))
        if dev < 0.05:
            print(f"    φ^{k} = {ratio:.4e}, 偏差 = {dev*100:.2f}%")
    # 半整數
    for k in [45, 45.5, 46, 46.5, 47, 47.5]:
        ratio = phi**k
        print(f"    φ^{k:.1f} = {ratio:.4e}, 偏差 = {abs(ratio - np.exp(logphi*np.log(phi)))/np.exp(logphi*np.log(phi))*100:.4f}%")

# 1c. 級聯步數: 7 步? (m_7 係第 7 模)
# 如果級聯算符 L: E → E × φ^α, 7 步後: E_kchain × φ^(7α) = m_7
alpha_m7 = log_phi_m7 / 7
alpha_M0 = log_phi_M0 / 7
print(f"\n  7 步級聯: α = log_φ(m_7/E_kchain)/7 = {alpha_m7:.4f}")
print(f"  7 步級聯: α = log_φ(M₀/E_kchain)/7 = {alpha_M0:.4f}")
print(f"  6 步級聯: α(m_7) = {log_phi_m7/6:.4f}, α(M₀) = {log_phi_M0/6:.4f}")
print(f"  8 步級聯: α(m_7) = {log_phi_m7/8:.4f}, α(M₀) = {log_phi_M0/8:.4f}")

# 1d. 結構候選: 級聯算符 = φ^7? φ^6.5? φ^6.5×γ_7^0.5?
# φ^6.5 = 15.4, φ^7 = 29.0, φ^6 = 17.9
# (m_7/E_kchain)^(1/7) = (3.4e9)^(1/7) = 23.0
step_factor = ratio_m7_Ek ** (1/7)
print(f"\n  每步增長因子 = (m_7/E_kchain)^(1/7) = {step_factor:.4f}")
print(f"  log_φ(step) = {np.log(step_factor)/np.log(phi):.4f}")
print(f"  φ^6 = {phi**6:.4f}")
print(f"  φ^6.5 = {phi**6.5:.4f}")
print(f"  φ^7 = {phi**7:.4f}")
print(f"  step_factor / φ^6.5 = {step_factor/phi**6.5:.4f}")
print(f"  step_factor / φ^6.5 ≈ 1/√γ_7? √γ_7 = {np.sqrt(gamma_7):.4f}")
print(f"  step_factor × √γ_7 = {step_factor * np.sqrt(gamma_7):.4f}")
print(f"  step_factor × √γ_7 / φ^6.5 = {step_factor * np.sqrt(gamma_7) / phi**6.5:.4f}")

# ═══════════════════════════════════════════════════════════════
# 步驟 2: CY₃/45² 幾何因子
# ═══════════════════════════════════════════════════════════════
print(f"\n{'═'*67}")
print("  [2] CY₃/45² 幾何因子")
print(f"{'═'*67}")

# E_kchain 嘅 correction = 1 - CY₃/45² = 1891/2025
# 45 = N_d+1 = Σγ_even/2
# 呢個 correction 係「世界能量減去 CY₃ 佔用」= 未被投影嘅能量比例
# m_7 係第 7 模 (DM), 應該同 γ_7 有關

# 2a. m_7 同 √(M_P·ħ·H₀) 嘅關係 (未加 correction)
ratio_sq = m_7 / sq_MP_hbar_H0
print(f"\n  m_7 / √(M_P·ħ·H₀) = {ratio_sq:.6e}")
print(f"  log_φ(m_7/√(M_P·ħ·H₀)) = {np.log(ratio_sq)/np.log(phi):.6f}")

# m_7_uncorr = m_7 / correction? 如果 correction 係投影因子
m_7_proj = m_7 / correction
print(f"\n  m_7 / correction = {m_7_proj:.4f} MeV")
print(f"  m_7_proj / √(M_P·ħ·H₀) = {m_7_proj/sq_MP_hbar_H0:.6e}")
print(f"  log_φ = {np.log(m_7_proj/sq_MP_hbar_H0)/np.log(phi):.6f}")

# 2b. 45 階對稱群: 45 = N_d+1 = Σγ_even/2
# 45 階: 可能係 45 = 5×9 = F₅×F₆? 5×9=45
# 或者 45 = 3×15 = 3×F₇? 3×15=45
print(f"\n  45 = N_d+1 = {N}+1 = 45")
print(f"  45 = 5×9 = F₅×F₆ = 5×9")
print(f"  45² = 2025")

# 2c. correction 嘅結構: 1891/2025
# 1891 = ? 2025 - 134 = 1891
# 1891 = 17×111.2? 1891 = 31×61?
print(f"  1891 = 2025 - CY₃ = {2025 - CY3}")
print(f"  1891 = 17×111.2? 1891 = 31×61? 31×61 = {31*61}")
print(f"  1891 = 1891 (質因數分解: 1891 = 31×61 = {31*61})")

# 2d. 如果 m_7 都有 CY₃ 修正?
# m_7_corr = m_7 × (1 + CY₃/N²)? 或者 m_7 = m_base × (1 - CY₃/45²)?
# 如果 m_7 係「未被投影」嘅質量, 咁應該同 61.5/90 有關
Omega_L_exact = 4 / (phi**4 - 1)
unproj_ratio = 61.5 / 90
print(f"\n  Ω_Λ = {Omega_L_exact:.6f}")
print(f"  未被投影比例 = 61.5/90 = {unproj_ratio:.6f}")
print(f"  m_7 × 61.5/90 = {m_7 * unproj_ratio:.4f} MeV")
print(f"  m_7 × Ω_Λ = {m_7 * Omega_L_exact:.4f} MeV")

# ═══════════════════════════════════════════════════════════════
# 步驟 3: m_7/M_0 代數閉合
# ═══════════════════════════════════════════════════════════════
print(f"\n{'═'*67}")
print("  [3] 質量階梯比值 — m_7/M₀ 代數閉合")
print(f"{'═'*67}")

# M₀ = m_7/√γ_7 = 基礎質量標度
# 應該檢查 M₀ 同 √(M_P·ħ·H₀) 嘅關係
print(f"\n  M₀ = m_7/√γ_7 = {M0:.4f} MeV")
print(f"  √(M_P·ħ·H₀) = {sq_MP_hbar_H0*1000:.6f} meV, correction = {correction:.10f}")
print(f"  M₀ / √(M_P·ħ·H₀) = {M0/sq_MP_hbar_H0:.6f}")
print(f"  log_φ(M₀/√(M_P·ħ·H₀)) = {np.log(M0/sq_MP_hbar_H0)/np.log(phi):.6f}")

# 3a. M₀ 同 ħ·H₀ 嘅關係 (Planck 量級)
# M₀ = 27.9 MeV, ħ·H₀ = 2.2e-31 eV
# M₀/(ħ·H₀) = 1.27e38
ratio_M0_EH = M0 / E_H_MeV
print(f"\n  M₀/(ħ·H₀) = {ratio_M0_EH:.6e}")
print(f"  log_φ(M₀/(ħ·H₀)) = {np.log(ratio_M0_EH)/np.log(phi):.6f}")

# 3b. 代數閉合檢查: M₀ × correction = ?
M0_corr = M0 * correction
print(f"\n  M₀ × correction = {M0_corr:.4f} MeV")
print(f"  m_7 = {m_7:.4f} MeV")
print(f"  M₀ × correction / m_7 = {M0_corr/m_7:.6f}")
print(f"  √γ_7 = {np.sqrt(gamma_7):.6f}")
print(f"  correction × √γ_7 = {correction * np.sqrt(gamma_7):.6f}")

# 3c. 關鍵比率: m_7 / √(M_P·ħ·H₀) × correction
# = m_7 / √(M_P·ħ·H₀) × (1 - CY₃/45²)
# = m_7 / E_kchain × correction / correction... 即係 E_kchain 本身
# m_7 / E_kchain = 3.4e9
# 如果 m_7 = E_kchain × φ^45 × γ_7^0.5?
try_val = E_kchain * phi**45 * np.sqrt(gamma_7)
print(f"\n  E_kchain × φ^45 × √γ_7 = {try_val:.4f} MeV")
print(f"  m_7 = {m_7:.4f} MeV")
print(f"  偏差 = {abs(try_val-m_7)/m_7*100:.4f}%")

# 各種候選
candidates = []
for k in range(44, 50):
    for g_pow in [-1, -0.5, 0, 0.5, 1]:
        val = E_kchain * phi**k * (gamma_7)**(g_pow)
        err = abs(val - m_7) / m_7 * 100
        if err < 5:
            candidates.append((k, g_pow, val, err))

candidates.sort(key=lambda x: x[3])
print(f"\n  最佳候選 (E_kchain × φ^k × γ_7^p ≈ m_7):")
for k, g_pow, val, err in candidates[:10]:
    print(f"    φ^{k} × γ_7^{g_pow:+.1f} = {val:.4f} MeV, 偏差 {err:.4f}%")

# 3d. 用 φ^45 同 correction
# correction = 1 - CY₃/45² = 1891/2025
# 如果 m_7 = √(M_P·ħ·H₀) × correction × φ^45 × γ_7^p?
val2 = sq_MP_hbar_H0 * correction * phi**45 * np.sqrt(gamma_7)
print(f"\n  √(M_P·ħ·H₀) × correction × φ^45 × √γ_7 = {val2:.4f} MeV")
print(f"  m_7 = {m_7:.4f} MeV, 偏差 = {abs(val2-m_7)/m_7*100:.4f}%")

# 3e. 直接用 E_kchain × φ^45 × γ_7^0.5 × (CY₃/45²)?
val3 = E_kchain * phi**45 * np.sqrt(gamma_7) * (1 + CY3/45**2)
print(f"\n  E_kchain × φ^45 × √γ_7 × (1+CY₃/45²) = {val3:.4f} MeV")
print(f"  偏差 = {abs(val3-m_7)/m_7*100:.4f}%")

# 3f. 更精確: 直接用 E_kchain × φ^a 形式
# ratio_m7_Ek = 3.4e9, log_phi = 45.61
# 如果 m_7 = E_kchain × φ^45 × φ^0.61
# φ^0.61 = 1.34
# 1.34 ≈ 4/3? 4/3 = 1.333
# 1.34 ≈ √(γ_1)? γ_1 = 0.00127, √γ_1 = 0.0357... 唔係
# 1.34 ≈ 1/γ_44? γ_44 = 4, 1/4 = 0.25... 唔係
# 1.34 ≈ φ^0.5 = 1.272? 偏差 5.5%
# 1.34 ≈ φ^0.6 = 1.328? 偏差 0.9%
# 1.34 ≈ φ^0.61 = 1.337? 偏差 0.2%
# 所以 m_7/E_kchain = φ^45.61 = φ^45 × φ^0.61
# φ^0.61 ≈ 1.337, 而 1/γ_1 = 785... 唔係

# 0.61 有冇結構? 0.61 ≈ 1/φ? 1/φ = 0.618!
# φ^0.618 = 1.339!
print(f"\n  φ^0.618 = {phi**phi_inv:.6f} (φ^φ⁻¹)")
print(f"  φ^0.61 = {phi**0.61:.6f}")
print(f"  φ^φ⁻¹ = {phi**phi_inv:.6f}")
print(f"  m_7/E_kchain / φ^45 = {ratio_m7_Ek/phi**45:.6f}")
print(f"  = φ^0.618? {phi**phi_inv:.6f}")
print(f"  偏差 = {abs(ratio_m7_Ek/phi**45 - phi**phi_inv)/phi**phi_inv*100:.4f}%")

# phi^phi_inv = phi^(1/phi) = phi^(0.618) ≈ 1.339
# 1.339 vs 1.337? 偏差 0.15%
# 有意思! 但唔係精確

# 有冇其他結構? 0.61 = 7/11.5? 7/11.5 = 0.609
# 0.61 = 7/11.5? 唔係結構
# 0.61 = 1 - 1/φ + 1/φ³? 1 - 0.618 + 0.236 = 0.618? 唔係
# 0.61 ≈ 1 - 1/φ²? 1 - 0.382 = 0.618? 唔係

# 直接: φ^0.618 = φ^(1/φ) 有結構 (φ^φ⁻¹)
# 但呢個只係 0.15% 近似, 唔係精確

print(f"\n{'═'*67}")
print(f"  探索結論")
print(f"{'═'*67}")

# 總結最佳候選
best = candidates[0] if candidates else None
print(f"""
  m_7/E_kchain = {ratio_m7_Ek:.4e}
  log_φ(m_7/E_kchain) = {log_phi_m7:.4f}
  M₀/E_kchain = {ratio_M0_Ek:.4e}
  log_φ(M₀/E_kchain) = {log_phi_M0:.4f}

  級聯算符 (7 步): 每步增長因子 = {step_factor:.4f}
  log_φ(step) = {np.log(step_factor)/np.log(phi):.4f}

  最佳候選: {f'φ^{best[0]} × γ_7^{best[1]:+.1f} = {best[2]:.4f} MeV, 偏差 {best[3]:.4f}%' if best else '未找到'}

  ★ φ^0.618 = φ^(1/φ) = {phi**phi_inv:.6f} (結構!)
  m_7/E_kchain / φ^45 = {ratio_m7_Ek/phi**45:.6f} ≈ φ^(1/φ) (偏差 {abs(ratio_m7_Ek/phi**45 - phi**phi_inv)/phi**phi_inv*100:.4f}%)
""")

# 儲存
with open("data/e7_to_m7_cascade_results.txt", "w") as f:
    f.write("O34 — E_kchain to m_7 Cascade\n")
    f.write("=" * 67 + "\n")
    f.write(f"E_kchain = {E_kchain_meV:.4f} meV\n")
    f.write(f"m_7 = {m_7:.4f} MeV\n")
    f.write(f"M0 = m_7/sqrt(gamma_7) = {M0:.4f} MeV\n")
    f.write(f"ratio m_7/E_kchain = {ratio_m7_Ek:.4e}\n")
    f.write(f"log_phi(m_7/E_kchain) = {log_phi_m7:.4f}\n")
    f.write(f"step factor (7-step) = {step_factor:.4f}\n")
    f.write(f"phi^45 = {phi**45:.4e}\n")
    f.write(f"m_7/E_kchain / phi^45 = {ratio_m7_Ek/phi**45:.6f}\n")
    f.write(f"phi^(1/phi) = {phi**phi_inv:.6f}\n")
    if best:
        f.write(f"best candidate: phi^{best[0]} * gamma_7^{best[1]:+.1f} = {best[2]:.4f} MeV, err {best[3]:.4f}%\n")
    f.write(f"Status: 🔴 級聯算符未閉合 (exploration only)\n")