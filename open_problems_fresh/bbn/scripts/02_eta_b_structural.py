#!/usr/bin/env python3
"""
IDCM BBN 元素豐度 — 首個結構推導
==================================
從 0,1 → φ → K_Chain → 重子密度 → η_B → 元素豐度

方法（第一原理，零自由參數）：
1. K_Chain 質量幾何分配: Ω_DM/Ω_b = 6.5030 (P_n = 1 + 2φ⁻¹n + K₂n²)
2. IDCM 重子密度 Ω_b 從 K_Chain 結構推導
3. η_B = n_B/n_γ 結構公式
4. D/H, Y_p (⁴He) 預測

對比觀測: D/H = 2.527±0.030×10⁻⁵, Y_p = 0.2453±0.0034, ⁷Li/H = 1.58×10⁻¹⁰
"""
import math

# ============ IDCM 核心常數 ============
phi = (1 + 5**0.5) / 2          # 1.61803398875
phi_inv = 1 / phi               # 0.61803398875
eps = phi_inv / 4               # 0.1545084972
kappa = 1 / 16                  # 0.0625
Nd = 44                         # K_Chain 維度
M = 33                          # K_Tree 深度
B = 4                           # MERA branching factor
CY3 = 134                       # h11=36, h21=98
lambda_sync = 294.88            # Mpc
BAO = lambda_sync / 2           # 147.44 Mpc
H0_idcm = 72.59                 # km/s/Mpc
R_H = 4129.94                   # Mpc
K2 = 0.029238                   # 質量幾何分配二次係數
Omega_DM_Ob = 6.5030            # Ω_DM/Ω_b 幾何分配

# ============ 物理常數 ============
c = 299792.458                  # km/s
m_p_MeV = 938.27208816          # MeV/c²
m_p = m_p_MeV * 1.78266192e-30  # kg (!! 單位修正: MeV → kg)
m_n = 939.56542052              # MeV/c²
m_e = 0.51099895000             # MeV/c²
G = 6.67430e-11                 # m³ kg⁻¹ s⁻²
Mpc_to_m = 3.0856775814913673e22
Msun_to_kg = 1.98892e30
MeV_to_kg = 1.78266192e-30

# 臨界密度 ρ_c = 3H₀²/8πG  (SI: kg/m³)
H0_si = H0_idcm * 1000 / Mpc_to_m   # s⁻¹
rho_c = 3 * H0_si**2 / (8 * math.pi * G)   # kg/m³

# 光子數密度 (T = 2.7284 K)
T_cmb = 2.7284
k_B = 1.380649e-23
h_planck = 6.62607015e-34
hbar = h_planck / (2*math.pi)
c_si = 299792458.0
# n_γ = 2ζ(3)/π² × (k_B T/ħc)³
zeta3 = 1.2020569031595942
n_gamma = 2 * zeta3 / math.pi**2 * (k_B * T_cmb / (hbar * c_si))**3   # m⁻³

print("=" * 72)
print("IDCM BBN 元素豐度 — 首個結構推導")
print("=" * 72)

# ============ 1. 重子密度結構推導 ============
# IDCM: Ω_b 從 K_Chain 質量分配 + 已知 Ω_DM/Ω_b
# ΛCDM: Ω_b h² = 0.02237 (Planck) → Ω_b = 0.0493 (h=0.674)
# IDCM: 總物質密度 Ω_m = ? 需要結構推導
# 
# 路徑 A: Ω_Λ = 4/(φ⁴-1) = 0.68328 (已閉合)
#         Ω_m = 1 - Ω_Λ = 0.31672 (曲率 = 0? 需要假設)
#         但 IDCM 非 FLRW — 密度參數係投影量
#
# 路徑 B: 質量幾何分配 P_n 直接給 Ω_DM/Ω_b = 6.5030
#         Ω_b 需要另外嘅結構來源

print("\n[1] 重子密度 Ω_b")
print("-" * 72)

# 嘗試 1: Ω_Λ 閉合 → Ω_m
Omega_Lambda = 4 / (phi**4 - 1)   # 0.68328
Omega_m = 1 - Omega_Lambda        # 0.31672
print(f"Ω_Λ = 4/(φ⁴-1) = {Omega_Lambda:.5f}  (已閉合 ✅)")
print(f"Ω_m = 1 - Ω_Λ = {Omega_m:.5f}")

# Ω_b 從 Ω_m 同 Ω_DM/Ω_b:
# Ω_m = Ω_b + Ω_DM = Ω_b(1 + Ω_DM/Ω_b)
Omega_b = Omega_m / (1 + Omega_DM_Ob)
print(f"Ω_b = Ω_m/(1+Ω_DM/Ω_b) = {Omega_b:.5f}")
print(f"  → Ω_b h² = {Omega_b * (H0_idcm/100)**2:.5f} (IDCM h={H0_idcm/100:.3f})")
print(f"  vs Planck Ω_b h² = 0.02237 ± 0.00015")
print(f"  偏差 = {abs(Omega_b*(H0_idcm/100)**2 - 0.02237)/0.02237*100:.2f}%")

# ============ 2. η_B 結構公式 ============
print("\n[2] 重子-光子比 η_B")
print("-" * 72)
# η_B = n_B/n_γ = Ω_b ρ_c / (m_p n_γ)
n_b = Omega_b * rho_c / m_p     # m⁻³
eta_B = n_b / n_gamma
print(f"ρ_c = {rho_c:.4e} kg/m³")
print(f"n_γ = {n_gamma:.4e} m⁻³ (T={T_cmb}K)")
print(f"n_b = {n_b:.4e} m⁻³")
print(f"η_B = {eta_B:.4e}")
print(f"vs 觀測 (BBN 擬合) η_B = 6.1×10⁻¹⁰")
print(f"  比率 = {eta_B/6.1e-10:.3f}")

# ============ 3. D/H 預測 ============
print("\n[3] D/H 預測")
print("-" * 72)
# ΛCDM: D/H ≈ 2.53×10⁻⁵ × (η_B/6.1×10⁻¹⁰)^(-1.6)  (經驗冪律)
# IDCM: 如果 η_B 結構推導正確, D/H 直接得出
D_H_obs = 2.527e-5
if eta_B > 0:
    D_H_pred = 2.53e-5 * (eta_B / 6.1e-10) ** (-1.6)
    print(f"D/H_pred = 2.53e-5 × (η_B/6.1e-10)^(-1.6) = {D_H_pred:.4e}")
    print(f"D/H_obs  = {D_H_obs:.4e}")
    print(f"  偏差 = {abs(D_H_pred - D_H_obs)/D_H_obs*100:.2f}%")

# ============ 4. Y_p (⁴He) 預測 ============
print("\n[4] ⁴He 質量分數 Y_p")
print("-" * 72)
# Y_p 由 n/p 比決定:
# Y_p = 2(n/p) / (1 + n/p)
# ΛCDM: n/p = 1/7 (weak freeze-out @ T≈0.8 MeV) → Y_p ≈ 0.25
# IDCM 結構: n/p 比由 K_Chain 模式截止決定?
# 
# 嘗試: n/p = 質量比 m_n/m_p 嘅投影修正
# m_n/m_p = 939.565/938.272 = 1.001378
# 但 freeze-out 比 ~ 1/7 = 0.143 遠大於質量比
# 
# IDCM 線索: n/p 由 weak 反應率 = 結構閾值?
# κ = 1/16 = 0.0625 → n/p ~ κ⁻¹?
np_ratio_obs = 1/7.0   # ≈ 0.143

# 嘗試 A: n/p = κ⁻¹ × φ⁻ᵏ?
for k in [1, 2, 3, 4]:
    np_k = (1/kappa) * phi_inv**k
    Yp_k = 2*np_k/(1+np_k)
    print(f"  n/p = κ⁻¹·φ⁻^{k} = {np_k:.4f} → Y_p = {Yp_k:.4f}")

# 嘗試 B: n/p 從 K_Chain 模式
# γ_n = 4sin²(πn/88), Σγ = 90
# n/p 可能 = γ_n / γ_m 某組合?
gamma = [4*math.sin(math.pi*n/88)**2 for n in range(1, 45)]
# 找 γ_i/γ_j ≈ 1/7
print("\n  K_Chain 模式比 γ_i/γ_j ≈ 1/7:")
for i in range(44):
    for j in range(i+1, 44):
        r = gamma[i]/gamma[j]
        if 0.13 < r < 0.16:
            print(f"    γ_{i+1}/γ_{j+1} = {r:.4f} (n/p=1/7={1/7:.4f})")

# ============ 5. ⁷Li 問題 ============
print("\n[5] ⁷Li 問題")
print("-" * 72)
Li_H_obs = 1.58e-10
Li_H_bbn = 4.9e-10   # ΛCDM BBN 預測 (η_B=6.1e-10)
print(f"⁷Li/H BBN 預測 = {Li_H_bbn:.2e}")
print(f"⁷Li/H 觀測 (Spite) = {Li_H_obs:.2e}")
print(f"ΛCDM 張力 = {Li_H_bbn/Li_H_obs:.1f}×")
print(f"IDCM 機會: 結構機制 (非恆星耗盡) 可解釋")
print(f"  IDCM 預測: ⁷Li 產量受 K_Chain 模式結構抑制 → 待推導")

# ============ 總結 ============
print("\n" + "=" * 72)
print("總結")
print("=" * 72)
print(f"η_B(IDCM)   = {eta_B:.3e}  (vs 6.1e-10, 比 {eta_B/6.1e-10:.2f}×)")
print(f"D/H(IDCM)   = 待 η_B 修正")
print(f"Y_p(IDCM)   = 待 n/p 結構公式")
print(f"⁷Li(IDCM)   = 待結構機制")
print()
print("狀態: 🟡 部分推導 — η_B 依賴 Ω_b 結構來源")
print("下一步: Ω_b 需要獨立結構公式 (唔借用 Ω_Λ/Ω_m)")
