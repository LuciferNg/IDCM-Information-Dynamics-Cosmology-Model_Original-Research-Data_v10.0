#!/usr/bin/env python3
"""
O100-P3+P4 閉合探索: 968/1291 ↔ O83 partition function ↔ T_CMB
==============================================================
目標: 從 O83 已建立嘅 partition function 結構，推導 
  P3: 968/322.75 = 3-1/1291 嘅結構意義
  P4: 968 ↔ T_CMB 交叉驗證
"""
import numpy as np

# ===== K_Chain 譜 =====
N_d = 44
phi = (1 + np.sqrt(5))/2

# 88-site chain
omega_88 = np.array([2*np.sin(np.pi*k/176) for k in range(1, 89)])
gamma_88 = omega_88**2  # 4sin²(kπ/176)

# 奇偶分解
gamma_odd = gamma_88[::2]   # k=1,3,5,...,87 (odd indices)
gamma_even = gamma_88[1::2] # k=2,4,6,...,88 (even indices = 44-site)

# 44-site chain (even 子集, 確認相等)
omega_44 = np.array([2*np.sin(np.pi*n/88) for n in range(1, 45)])

print("=" * 70)
print("  P3: 968/322.75 = 3-1/1291 結構分析")
print("=" * 70)

# 基本量
S1_gamma_odd = np.sum(1/gamma_odd)
S1_gamma_even = np.sum(1/gamma_even)
S1_gamma_44 = np.sum(1/omega_44**2)

print(f"  Σ1/γ_odd  = {S1_gamma_odd:.10f} = {S1_gamma_odd:.0f} (整數!)")
print(f"  Σ1/γ_even = {S1_gamma_even:.10f} = {S1_gamma_even:.4f}")
print(f"  Σ1/γ_44   = {S1_gamma_44:.10f} (= even, 驗證)")
print(f"  44 × 22   = {44*22}")
print(f"  1291/4    = {1291/4}")
print(f"  比        = {S1_gamma_odd/S1_gamma_even:.10f}")
print(f"  3 - 1/1291 = {3 - 1/1291:.10f}")
print(f"  差        = {S1_gamma_odd/S1_gamma_even - (3 - 1/1291):.2e}")

# ===== P3: 968 = 44×22 嘅結構分解 =====
print("\n" + "=" * 70)
print("  P3: 968 = 44×22 結構分解")
print("=" * 70)

# 44 = N_d, 22 = 88/4 = 2L₅
print(f"  968 = 44 × 22")
print(f"    = N_d × (88/4)")
print(f"    = N_d × 2L₅  (L₅=11)")
print(f"    = 88 × 11")
print(f"    = 8 × 121 = 2³ × 11²")

# 從 O83 partition function 角度
# Z(β) = Π e^{-βω_n/2}/(1-e^{-βω_n})
# 高溫極限: ⟨φ_n²⟩_T → 1/(βω_n²) = 1/(βγ_n)
# 所以 Σ1/γ_n = β·Σ⟨φ_n²⟩_T (高溫極限)

# 但更關鍵: 968 = 44×22, 而 44 = N_d, 22 = 88/4
# 呢個係結構數乘積, 唔係封閉和

print("\n  O83 配分函數角度:")
print(f"  Z(β=0) 高溫極限: ⟨φ²⟩_T → 1/(βγ)")
print(f"  Σ1/γ_odd = {S1_gamma_odd:.0f} = 44×22")
print(f"  Σ1/γ_even = {S1_gamma_even:.4f} = 1291/4")

# 1291 質數分析
print(f"\n  1291 = 1291 (質數)")
print(f"  1291 - 968 = 323 = 17×19")
print(f"  1291 = 3×430 + 1, 430 = 44×9.77...")
print(f"  1291 = 11×117.36... 唔乾淨")

# ===== 嘗試: 968 = 44×22 從 O83 出 =====
# O83: G_n(0) = 1/(4sin(nπ/88)) = 1/(2ω_n)
# ΣG_even = Σ_{n=1}^{44} 1/(4sin(nπ/88)) = 32.35863
# ΣG_odd = Σ_{k odd} 1/(4sin(kπ/176)) = 41.94179

G_even = np.sum(1/(4*np.sin(np.pi*np.arange(1,45)/88)))
G_odd = np.sum(1/(4*np.sin(np.pi*np.arange(1,89,2)/176)))
G_44 = np.sum(1/(4*np.sin(np.pi*np.arange(1,45)/88)))

print(f"\n  ΣG_even (44-site) = {G_even:.10f}")
print(f"  ΣG_odd  (88-site) = {G_odd:.10f}")
print(f"  G_odd/G_even = {G_odd/G_even:.6f}")

# 但 968 = Σ1/γ, 唔係 ΣG
# 1/γ = 1/(4sin²(kπ/176)) = 4/(2ω)² = 1/ω²
# G = 1/(2ω)
# 1/γ = G² × 4ω? No: 1/γ = 1/ω², G = 1/(2ω), so G² = 1/(4ω²) = 1/(4γ)
# 所以 Σ1/γ = 4×ΣG²

G2_odd = np.sum(1/(4*np.sin(np.pi*np.arange(1,89,2)/176))**2)
G2_even = np.sum(1/(4*np.sin(np.pi*np.arange(1,45)/88))**2)

print(f"\n  4×ΣG²_odd = {4*G2_odd:.10f} (vs 968)")
print(f"  4×ΣG²_even = {4*G2_even:.10f} (vs 322.75)")

# ===== P4: 968 ↔ T_CMB =====
print("\n" + "=" * 70)
print("  P4: 968 ↔ T_CMB = 2.7283 K 交叉驗證")
print("=" * 70)

# O83 T_CMB 公式: T_CMB = 2×T_Pl×exp(-74)×(CY₃/10²)×(1-φ⁻⁹)
T_Pl = 1.416784e32
T_cmb_idcm = 2*T_Pl*np.exp(-74)*(134/100)*(1-phi**(-9))
T_cmb_obs = 2.72548
print(f"  T_CMB (IDCM) = {T_cmb_idcm:.4f} K")
print(f"  T_CMB (FIRAS) = {T_cmb_obs:.4f} K")
print(f"  dev = {100*(T_cmb_idcm/T_cmb_obs-1):.3f}%")

# 968 = 44×22 同 T_CMB 嘅關係
# 嘗試: T_CMB × 968 = ?
print(f"\n  T_CMB × 968 = {T_cmb_idcm * 968:.4f} K")
print(f"  T_CMB × 44 = {T_cmb_idcm * 44:.4f} K")
print(f"  T_CMB × 22 = {T_cmb_idcm * 22:.4f} K")

# 嘗試: M₀ / (k_B·T_CMB) 同 968 嘅關係
M0 = 27.900915  # MeV
k_B_eV_K = 8.617333262e-5  # eV/K
kBT_cmb = T_cmb_idcm * k_B_eV_K  # eV
M0_eV = M0 * 1e6  # eV
print(f"\n  k_B·T_CMB = {kBT_cmb:.6e} eV")
print(f"  M₀ = {M0_eV:.6e} eV")
print(f"  M₀/(k_B·T_CMB) = {M0_eV/kBT_cmb:.4e}")

# 嘗試: 968 同 M₀/(k_B·T_CMB) 嘅對數關係
ratio = M0_eV/kBT_cmb
print(f"  log₁₀(M₀/(k_B·T_CMB)) = {np.log10(ratio):.4f}")
print(f"  log₁₀(968) = {np.log10(968):.4f}")
print(f"  ratio/968 = {ratio/968:.4e}")

# 嘗試: (M₀/(k_B·T_CMB)) / 968 = ?
print(f"\n  (M₀/(k_B·T_CMB)) / 968 = {ratio/968:.4f}")

# 嘗試: 968 = 44×22, 而 O83 嘅 T_CMB 公式有 exp(-74)
# 74 = 2×37, 37 係?
# 74 = 2×L₈? L₈=47, no.
# 74 = F₁₀? F₁₀=55, no.
# 74 = 44+30 = N_d + (Σγ_even-Σγ_odd) = 44+2? No.
print(f"\n  74 結構: 74 = 44 + 30 = N_d + 30")
print(f"  30 = 3×10 = N_gen × 10?")
print(f"  30 = ½×60 = (h²¹−h¹¹)/2? 62/2 = 31. No.")
print(f"  74 = 88 - 14 = 88 - (B²-2)")
print(f"  74 = 2×37, 37 係質數")

# 嘗試: 968 同 exp(-74) 嘅關係
print(f"\n  exp(-74) = {np.exp(-74):.4e}")
print(f"  968 × exp(-74) = {968 * np.exp(-74):.4e}")
print(f"  1/968 = {1/968:.4e}")
print(f"  exp(-74) / (1/968) = {np.exp(-74) * 968:.4e}")

# ===== 封閉形式探索 =====
print("\n" + "=" * 70)
print("  封閉形式探索: Σ1/γ_odd = 44×22")
print("=" * 70)

# 嘗試: 968 = 88×11, 88 = 2N_d, 11 = L₅
# 或 968 = 8×121 = 2³×11²
# 8 = 2B, 121 = L₅²

# 熱態連接: 如果 T_CMB 對應嘅 β = 1/(k_B T_CMB)
# 以 M₀ 為單位: β_eff = M₀/(k_B T_CMB)
beta_eff = M0_eV / kBT_cmb
print(f"  β_eff (以 M₀ 為單位) = {beta_eff:.4e}")

# 熱 propagator 嘅高溫修正: ⟨φ²⟩_T = G_n(0)·(1 + 2/(e^{βω_n}−1))
# 對於 β_eff 極大 (低溫): 2/(e^{βω_n}−1) ≈ 0
# 所以 ⟨φ²⟩_T ≈ G_n(0) — 真空值
# 即係 T_CMB = 2.7K 對 K_Chain 而言係「低溫」, 唔係高溫
print(f"  β_eff × ω_min = {beta_eff * omega_44[0]:.4e} (>>1 = 低溫)")
print(f"  → CMB 溫度對 K_Chain 係極低溫, 唔係高溫極限")
print(f"  → Σ1/γ 嘅高溫解釋唔啱: T_CMB 對 K_Chain 係低溫")

# 所以 968 嘅結構意義唔係來自高溫熱態
# 而係來自 K_Chain 嘅固有幾何結構
print(f"\n  結論: 968 = 44×22 = N_d × 2L₅ 係 K_Chain 固有幾何")
print(f"  Σ1/γ_odd = 44×22 係精確整數閉合, 唔係熱態近似")
print(f"  → 968 嘅結構意義 = 觀察者鏈逆特徵值總和 = N_d × 2L₅")

# ===== 最終: 968/322.75 = 3-1/1291 嘅結構意義 =====
print("\n" + "=" * 70)
print("  最終分析: 968/322.75 = 3 - 1/1291")
print("=" * 70)

# 968 = 44×22, 322.75 = 1291/4
# 968/322.75 = (44×22)/(1291/4) = (44×22×4)/1291 = 3872/1291
# 3872/1291 = 3 - 1/1291

# 3872 = 44×88 = N_d × 2N_d = 2N_d²
print(f"  3872 = 44 × 88 = N_d × 2N_d = 2N_d²")
print(f"  1291 = 質數 (無結構分解)")
print(f"  所以 968/322.75 = 2N_d²/1291 = 3 - 1/1291")

# 但 1291 係質數, 呢個關係冇結構意義
# 重新檢查: 322.75 = Σ1/γ_even 係精確和?
# 或者 322.75 = 1291/4 係近似?
print(f"\n  Σ1/γ_even 精確值 = {S1_gamma_even}")
print(f"  1291/4 = {1291/4}")
print(f"  差 = {S1_gamma_even - 1291/4:.2e}")

# 如果 322.75 係近似 (浮點捨入), 咁 1291 可能係 artifact
# 精確檢查: Σ1/γ_even 嘅閉合形式
# 用 sympy 檢查精確有理數
try:
    from sympy import sin, pi, N, Rational, nsimplify, Integer
    # 嘗試有理近似
    n_sum = 0
    for n in range(1, 45):
        val = 1/(4*sin(n*pi/88)**2)
        n_sum += val
    print(f"\n  sympy 精確 Σ1/γ_even = {N(n_sum, 50)}")
    # 嘗試有理近似
    approx = nsimplify(n_sum, [Rational(1,4)])
    print(f"  有理近似: {approx} = {N(approx, 20)}")
except:
    print(f"  sympy 不可用, 使用 numpy 精確值 = {S1_gamma_even:.15f}")

# 檢查 322.75 是否精確 1291/4
print(f"\n  322.75 × 4 = {322.75*4}")
print(f"  1291 = {1291}")
print(f"  差 = {322.75*4 - 1291}")

# 結論
print("\n" + "=" * 70)
print("  P3+P4 判決")
print("=" * 70)
print("""
  P3: 968/322.75 = 3 - 1/1291

  ✅ 968 = 44×22 = N_d × 2L₅ 係精確整數 (Σ1/γ_odd)
  ✅ 這係 K_Chain 固有幾何, 非熱態近似
  ✅ 結構意義: 觀察者鏈逆特徵值總和 = N_d × 2L₅

  🟡 322.75 = Σ1/γ_even, 1291 係質數
     322.75 = 1291/4 但 1291 無結構分解
     這數值關係本身無結構意義

  ❌ 968/322.75 = 3 - 1/1291 係計算 artifact
     因為 1291 係質數, 3 - 1/1291 唔係結構閉合
     → 88/90 對偶唔需要經 968 入口

  P4: 968 ↔ T_CMB

  ✅ T_CMB = 2×T_Pl×exp(-74)×(CY₃/10²)×(1-φ⁻⁹) = 2.7283 K (O83 已閉合)
  ✅ 968 = 44×22 = Σ1/γ_odd (觀察者鏈幾何)
  ✅ 兩者各自獨立閉合, 冇直接數值關係
  🟡 T_CMB 對 K_Chain 係極低溫 (β_eff × ω_min >> 1)
  🟡 所以 968 唔經熱態進入 T_CMB

  核心判決:
  P3: 968/322.75 = 3-1/1291 係 artifact (1291 質數 = 無結構)
      → 88/90 → σ8 入口唔需要 968 做中介
      → 88/90 嘅 σ8 修正已由 BOSS data bracket 直接封口 (O100-A)
      
  P4: 968 ↔ T_CMB 各自獨立閉合, 不需要交叉驗證來閉合 O100
      → T_CMB 已在 O83 閉合 (17/17)
      → 968 係 K_Chain 幾何產物 (O34)
""")