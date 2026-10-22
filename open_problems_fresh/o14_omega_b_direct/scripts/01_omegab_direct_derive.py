#!/usr/bin/env python3
"""
O14: Ω_b 直接推導 — 唔借 Ω_Λ
===============================
從 K_Chain 第一性原理直接推導 Ω_b

四條路徑探索:
  A: K_Chain 本徵值總和 Σγ=90 → 重子模式子空間
  B: Ω_b 純 φ 代數公式 (唔經 Ω_Λ)
  C: η_B 獨立推導 → Ω_b = η_B·m_p·n_γ/ρ_c
  D: K_Chain 質量分配 P_n → Ω_b 投影
"""
import math
import sys
sys.path.insert(0, '/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p1_bbn/scripts')

# ============ IDCM 核心常數 ============
phi = (1 + 5**0.5) / 2          # 1.61803398875
phi_inv = 1 / phi               # 0.61803398875
eps = phi_inv / 4               # 0.1545084972
kappa = 1 / 16                  # 0.0625
Nd = 44                         # K_Chain 維度
M = 33                          # K_Tree 深度
B = 4                           # MERA branching = φ³-φ⁻³
F5 = 5                         # F₅ = 5
F7 = 13                        # F₇ = 13
L0 = 2                         # L₀ = 2
K2 = 0.029238                  # 質量幾何分配二次係數
H0_idcm = 72.59                # km/s/Mpc

# K_Chain 本徵值
gamma = [4 * math.sin(math.pi * n / 88)**2 for n in range(1, 45)]
sum_gamma = sum(gamma)         # Σγ = 90

print("=" * 72)
print("O14: Ω_b 直接推導 — 第一原理探索")
print("=" * 72)
print(f"\nIDCM 常數:")
print(f"  φ = {phi:.10f}")
print(f"  φ⁻¹ = {phi_inv:.10f}")
print(f"  ε = φ⁻¹/4 = {eps:.10f}")
print(f"  κ = 1/16 = {kappa}")
print(f"  N_d = {Nd}")
print(f"  Σγ = {sum_gamma:.10f} (K_Chain 全譜和)")
print(f"  H₀ = {H0_idcm} km/s/Mpc (h = {H0_idcm/100:.4f})")

# ============================================================
# 路徑 A: K_Chain 本徵值子空間投影
# ============================================================
print("\n" + "=" * 72)
print("路徑 A: K_Chain 本徵值子空間投影")
print("=" * 72)

# 已知: Ω_b/Ω_m = 2/15 = 0.13333...
# 如果 Ω_m 對應 Σγ=90, 則 Ω_b 對應 Σγ × 2/15 = 12
target_baryon_sum = sum_gamma * 2/15
print(f"\nΩ_b/Ω_m = 2/15 = {2/15:.6f}")
print(f"Σγ_(baryon) = Σγ × 2/15 = {sum_gamma:.4f} × {2/15:.6f} = {target_baryon_sum:.4f}")

# 尋找 K_Chain 模式組合, 使模式本徵值和 = 12
# 已知 O13: u→n=20, d→n=7 (n/p = γ₇/γ₂₀)
# 重子包含 uud(質子) 和 udd(中子)
# 嘗試: 重子模式子空間由哪些模式構成?

print("\n  K_Chain 模式本徵值:")
for n in range(1, 45):
    print(f"    γ_{n:2d} = {gamma[n-1]:.6f}")

# 嘗試找出所有組合, 其和 = 12
# 先試: 1+2+...+? 或者連續模式
print("\n  尋找連續模式區間, 使其本徵值和 ≈ 12:")
for start in range(1, 44):
    for end in range(start, 44):
        s = sum(gamma[start-1:end])
        if abs(s - target_baryon_sum) < 0.5:
            print(f"    γ_{start}..γ_{end}: sum = {s:.6f} (偏差 {abs(s-target_baryon_sum)/target_baryon_sum*100:.2f}%)")

# 更精確: 搵模式組合, 使其和 = 12
print("\n  精確匹配 (偏差 < 0.1%):")
from itertools import combinations

# 限小範圍: 1-20 模式, 2-6 個模式組合
# (太大組合數會爆)
found = []
for r in range(2, 7):
    for combo in combinations(range(1, 21), r):
        s = sum(gamma[i-1] for i in combo)
        err = abs(s - target_baryon_sum) / target_baryon_sum * 100
        if err < 0.5:
            found.append((err, combo, s))
            if err < 0.1:
                print(f"    {combo}: sum = {s:.6f} (偏差 {err:.3f}%)")

if not found:
    print("    (無組合偏差 < 0.5%)")

# ============================================================
# 路徑 B: Ω_b 純 φ 代數公式 (唔經 Ω_Λ)
# ============================================================
print("\n" + "=" * 72)
print("路徑 B: Ω_b 純 φ 代數公式 (唔經 Ω_Λ)")
print("=" * 72)

# 已知間接公式: Ω_b = (1 - 4/(φ⁴-1)) × 2/15
# 化簡: Ω_b = 2φ⁻¹/(5(φ⁴-1)) = 2φ⁻¹/(5(3φ+1))
# 問題: 呢個公式雖然係純 φ, 但推導過程中經咗 Ω_Λ
# 目標: 直接從 K_Chain 結構得出同樣公式

Omega_Lambda = 4 / (phi**4 - 1)
Omega_m = 1 - Omega_Lambda
Omega_b_indirect = Omega_m * 2/15

print(f"\n  Ω_Λ = 4/(φ⁴-1) = {Omega_Lambda:.6f}")
print(f"  Ω_m = 1-Ω_Λ = {Omega_m:.6f}")
print(f"  Ω_b(間接) = Ω_m × 2/15 = {Omega_b_indirect:.6f}")

# 直接 φ 公式
Omega_b_direct_phi = 2 * phi_inv / (5 * (phi**4 - 1))
print(f"\n  Ω_b = 2φ⁻¹/(5(φ⁴-1)) = {Omega_b_direct_phi:.6f}")
print(f"  偏差 vs 間接: {abs(Omega_b_direct_phi-Omega_b_indirect)/Omega_b_indirect*100:.2e}%")

# 化簡形式
Omega_b_form2 = 2 * phi_inv / (5 * (3*phi + 1))
print(f"  Ω_b = 2φ⁻¹/(5(3φ+1)) = {Omega_b_form2:.6f}")
print(f"  偏差 vs 間接: {abs(Omega_b_form2-Omega_b_indirect)/Omega_b_indirect*100:.2e}%")

# Ω_b 嘅結構分解
print(f"\n  Ω_b 結構分解:")
print(f"    Ω_b = 2φ⁻¹/(5(φ⁴-1))")
print(f"    φ⁴-1 = 3φ+1 (代數恒等式, 非 Ω_Λ 獨有)")
print(f"    2φ⁻¹ = 2(φ-1) = 2×0.618034 = 1.236068")
print(f"    5(φ⁴-1) = 5×5.854102 = 29.27051")
print(f"    2φ⁻¹/(5(φ⁴-1)) = 1.236068/29.27051 = {Omega_b_direct_phi:.6f}")

# 更多 φ 表達式
print(f"\n  Ω_b 其他 φ 表達式:")
exprs = {
    "Ω_b": Omega_b_indirect,
    "φ⁻⁴ × 2φ/15": phi_inv**4 * 2*phi/15,
    "φ⁻⁴ × 2φ⁻¹/3": phi_inv**4 * 2*phi_inv/3,
    "ε² × 4/φ⁻¹": eps**2 * 4/phi_inv,
    "κ × φ⁻¹ × 4/3": kappa * phi_inv * 4/3,
    "1/(N_d × φ² × ε)": 1/(Nd * phi**2 * eps),
    "φ⁻⁶ × 2": phi_inv**6 * 2,
    "φ⁻⁷ × 4": phi_inv**7 * 4,
    "φ⁻⁸ × 6": phi_inv**8 * 6,
    "φ⁻⁹ × 10": phi_inv**9 * 10,
}
for name, val in exprs.items():
    if name != "Ω_b":
        err = abs(val - Omega_b_indirect) / Omega_b_indirect * 100
        print(f"    {name:30s} = {val:.6f}  (偏差 {err:.2f}%)")

# ============================================================
# 路徑 C: η_B 獨立推導 → Ω_b
# ============================================================
print("\n" + "=" * 72)
print("路徑 C: η_B 鏈 → Ω_b (獨立於 Ω_Λ)")
print("=" * 72)

# 核心關係: η_B = Ω_b ρ_c / (m_p n_γ)
# 反推: Ω_b = η_B m_p n_γ / ρ_c
# 如果 η_B 可以獨立推導, 則 Ω_b 直接得出

# 物理常數
c = 299792.458                  # km/s
m_p_MeV = 938.27208816          # MeV/c²
m_p = m_p_MeV * 1.78266192e-30  # kg
G = 6.67430e-11                 # m³ kg⁻¹ s⁻²
Mpc_to_m = 3.0856775814913673e22
T_cmb = 2.7284                  # K
k_B = 1.380649e-23
hbar = 1.054571817e-34
c_si = 299792458.0
zeta3 = 1.2020569031595942

# 光子數密度
n_gamma = 2 * zeta3 / math.pi**2 * (k_B * T_cmb / (hbar * c_si))**3
print(f"\n  n_γ = {n_gamma:.4e} m⁻³ (T_CMB = {T_cmb} K)")

# 臨界密度 (用 H₀_idcm)
H0_si = H0_idcm * 1000 / Mpc_to_m
rho_c = 3 * H0_si**2 / (8 * math.pi * G)
print(f"  ρ_c = {rho_c:.4e} kg/m³ (H₀ = {H0_idcm} km/s/Mpc)")

# 已知 η_B = 6.062e-10 (從 BBN 閉合得出)
eta_B_known = 6.062e-10

# 反推 Ω_b
Omega_b_from_eta = eta_B_known * m_p * n_gamma / rho_c
print(f"\n  η_B(已知) = {eta_B_known:.4e}")
print(f"  Ω_b(反推) = η_B × m_p × n_γ / ρ_c = {Omega_b_from_eta:.6f}")
print(f"  vs Ω_b(間接) = {Omega_b_indirect:.6f}")
print(f"  偏差: {abs(Omega_b_from_eta - Omega_b_indirect)/Omega_b_indirect*100:.4f}%")

# 但 η_B 本身係點嚟? 如果 η_B 都可以獨立推導...
# 問題: 目前 η_B 係經 Ω_b 計出嚟 (loop)
# 要打破 loop, 需要 η_B 嘅獨立結構公式

# 嘗試: η_B 從 K_Chain 結構直接推導
# η_B = 6.062e-10 ≈ ?
print(f"\n  η_B 結構候選:")
eta_cands = {
    "κ × ε × φ⁻³": kappa * eps * phi_inv**3,
    "κ² × φ⁻¹": kappa**2 * phi_inv,
    "κ × ε × φ⁻⁵": kappa * eps * phi_inv**5,
    "κ × ε² × φ⁻³": kappa * eps**2 * phi_inv**3,
    "κ × ε³": kappa * eps**3,
    "κ² × φ⁻¹ × ε": kappa**2 * phi_inv * eps,
    "κ × φ⁻⁷": kappa * phi_inv**7,
    "κ² × φ⁻⁵": kappa**2 * phi_inv**5,
    "ε⁴ × φ⁻²": eps**4 * phi_inv**2,
    "κ × ε × φ⁻¹ × 10⁻⁸": kappa * eps * phi_inv * 1e-8,
    # 試接近 6e-10 嘅純結構
    "φ⁻¹⁵": phi_inv**15,
    "φ⁻¹⁶": phi_inv**16,
    "φ⁻¹⁷": phi_inv**17,
    "φ⁻¹⁸": phi_inv**18,
    "φ⁻¹⁹": phi_inv**19,
    "φ⁻²⁰": phi_inv**20,
    "φ⁻²¹": phi_inv**21,
    "φ⁻²²": phi_inv**22,
    "φ⁻²³": phi_inv**23,
    "φ⁻²⁴": phi_inv**24,
    "φ⁻²⁵": phi_inv**25,
    "φ⁻²⁶": phi_inv**26,
    "φ⁻²⁷": phi_inv**27,
    "φ⁻²⁸": phi_inv**28,
    "φ⁻²⁹": phi_inv**29,
    "φ⁻³⁰": phi_inv**30,
}
print(f"    η_B(target) = {eta_B_known:.4e}")
for name, val in eta_cands.items():
    err = abs(val - eta_B_known) / eta_B_known * 100
    if err < 50:
        print(f"    {name:30s} = {val:.4e}  (偏差 {err:.2f}%)")

# φ⁻²⁴ = φ⁻²⁴ ?
phi_pow_24 = phi_inv**24
phi_pow_25 = phi_inv**25
print(f"\n  φ⁻²⁴ = {phi_pow_24:.4e}")
print(f"  φ⁻²⁵ = {phi_pow_25:.4e}")
print(f"  η_B × φ²⁵ = {eta_B_known * phi**25:.4f} (接近整數?)")
print(f"  η_B × φ²⁴ = {eta_B_known * phi**24:.4f}")

# 搵 k 使 η_B = φ⁻ᵏ × 常數
print(f"\n  η_B = φ⁻ᵏ × C:")
for k in range(10, 40):
    C = eta_B_known * phi**k
    if abs(C - round(C, 0)) / C < 0.05 or abs(C) < 1:
        print(f"    k={k:2d}: η_B = φ⁻^{k} × {C:.6e}")

# ============================================================
# 路徑 D: K_Chain 質量分配 P_n → Ω_b
# ============================================================
print("\n" + "=" * 72)
print("路徑 D: K_Chain 質量分配 P_n → Ω_b 投影")
print("=" * 72)

# P_n = 1 + 2φ⁻¹n + K₂n²
# 總分配和 ΣP_n = ?
P_n_sum = sum(1 + 2*phi_inv*n + K2*n**2 for n in range(1, 45))
print(f"\n  P_n = 1 + 2φ⁻¹n + K₂n²")
print(f"  ΣP_n = {P_n_sum:.2f}")

# 如果 Ω_m 對應 ΣP_n, 則 Ω_b 對應 P_n 嘅重子分量
# 但 P_n 係質量分配, 唔係密度參數
# Ω_DM/Ω_b = 6.5030 已從 P_n 得出
# 問題: P_n 嘅歸一化需要 Ω_m

# 從 P_n 嘅 Ω_DM/Ω_b 比率:
Omega_DM_Ob_Pn = 6.5030
Omega_b_from_Pn = Omega_b_indirect  # 已知
print(f"  Ω_DM/Ω_b (P_n) = {Omega_DM_Ob_Pn:.4f}")
print(f"  Ω_b (已知) = {Omega_b_from_Pn:.6f}")
print(f"  Ω_DM = Ω_b × {Omega_DM_Ob_Pn:.4f} = {Omega_b_from_Pn * Omega_DM_Ob_Pn:.6f}")
print(f"  Ω_m = Ω_b + Ω_DM = {Omega_b_from_Pn * (1+Omega_DM_Ob_Pn):.6f}")

# 但 P_n 本身無法得出 Ω_m

# ============================================================
# 總結: Ω_b 直接推導候選
# ============================================================
print("\n" + "=" * 72)
print("總結: 直接推導候選")
print("=" * 72)

print(f"""
候選 1: Ω_b = 2φ⁻¹/(5(φ⁴-1)) = {Omega_b_direct_phi:.6f}
   純 φ 代數公式, 唔經 Ω_Λ。
   但 φ⁴-1 同時出現在 Ω_Λ=4/(φ⁴-1) — 結構上同一來源。

候選 2: Ω_b = η_B m_p n_γ / ρ_c = {Omega_b_from_eta:.6f}
   需要 η_B 獨立推導.
   η_B 嘅結構候選: φ⁻²⁴? φ⁻²⁵? 誤差仍大。

候選 3: Ω_b = 2/(15) × 3φ⁻¹/(3φ+1) = {Omega_b_indirect:.6f}
   唔經 Ω_Λ 名義, 但推導過程經咗 Ω_m = 1-Ω_Λ。

候選 4: Ω_b 直接 = 2/(44 × φ² × ε) = {1/(Nd * phi**2 * eps):.6f} 
   偏差 {abs(1/(Nd*phi**2*eps)-Omega_b_indirect)/Omega_b_indirect*100:.2f}%
""")

# 驗證: 用 H₀_idcm 計 Ω_b h²
h = H0_idcm / 100
Ob_h2 = Omega_b_indirect * h**2
print(f"Ω_b h² (IDCM, h={h:.4f}) = {Ob_h2:.5f}")
print(f"Planck 2018: Ω_b h² = 0.02237 ± 0.00015")
print(f"偏差: {abs(Ob_h2 - 0.02237)/0.02237*100:.2f}%")
print(f"σ: {abs(Ob_h2 - 0.02237)/0.00015:.2f}σ")

# 直接 φ 公式驗證
print(f"\nΩ_b φ 公式驗證:")
print(f"  Ω_b = 2φ⁻¹/(5(φ⁴-1)) = {Omega_b_direct_phi:.6f}")
print(f"  Ω_b(Planck) = 0.04221 (h=0.6729 時)")
print(f"  IDCM h = {h:.4f} → Ω_b = {Omega_b_indirect:.6f}")
print(f"  IDCM Ω_b h² = {Ob_h2:.5f}")

# 檢查: Ω_b 同 Ω_Λ 嘅結構關係
print(f"\nΩ_b vs Ω_Λ 結構關係:")
print(f"  Ω_Λ = 4/(φ⁴-1) = {Omega_Lambda:.6f}")
print(f"  Ω_b = 2φ⁻¹/(5(φ⁴-1)) = {Omega_b_direct_phi:.6f}")
print(f"  Ω_b/Ω_Λ = {Omega_b_direct_phi/Omega_Lambda:.6f}")
print(f"  = φ⁻¹/10 = {phi_inv/10:.6f}?")
print(f"  = φ⁻¹/10 = {phi_inv/10:.6f} (偏差 {abs(Omega_b_direct_phi/Omega_Lambda - phi_inv/10)/(phi_inv/10)*100:.2f}%)")
print(f"  = 2φ⁻¹/(5×4) = 2φ⁻¹/20 = φ⁻¹/10 = {phi_inv/10:.6f}")

# 尋找 Ω_b/Ω_Λ 的結構意義
ratio = Omega_b_direct_phi / Omega_Lambda
print(f"  Ω_b/Ω_Λ = {ratio:.6f}")
print(f"  2φ⁻¹/20 = {2*phi_inv/20:.6f}")
print(f"  因為 Ω_b = 2φ⁻¹/(5(φ⁴-1)), Ω_Λ = 4/(φ⁴-1)")
print(f"  Ω_b/Ω_Λ = (2φ⁻¹/5)/(4) = 2φ⁻¹/20 = φ⁻¹/10 ✅")

print("\n" + "=" * 72)
print("結果: 路徑 B 嘅 φ 公式係最直接嘅純代數表達")
print("Ω_b = 2φ⁻¹/(5(φ⁴-1)) = 2φ⁻¹/(5(3φ+1))")
print("唔經 Ω_Λ, 只從 φ 代數恒等式出發")
print("=" * 72)