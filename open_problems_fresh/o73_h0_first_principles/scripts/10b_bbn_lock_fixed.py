"""
O73 攻堅 10b: ★★★ BBN 鎖定 — 修正版 (區分循環 vs 真鎖定)
=====================================================================
反幻覺核查發現:
  BBN 記錄 §2.1: IDCM η_B = 6.062e-10 係用 ρ_c = 3H₀²/8πG 計出嚟!
  → 直接用 IDCM η_B 反推 ω_ring 係「循環」(用返 ω_ring 計出嘅 η_B)

正確鎖定鏈 (冇循環):
  觀測 η_B(obs) = 6.104e-10  ← BBN 豐度 (D/H) fit, 完全冇 H₀/ω_ring!
     標準 BBN: D/H = 2.527e-5 → η_B ≈ 6.10e-10 (核物理 + 觀測)
  T_CMB(obs) = 2.72548 K      ← 直接觀測 (COBE/FIRAS)
  Ω_b(結構) = 0.04221         ← IDCM 質量分配 (冇 ω_ring)
  m_p, G, k_B, ħ              ← 物理常數

  η_B = Ω_b·ρ_c/(m_p·n_γ),  ρ_c = 3ω_ring²/8πG
  → ω_ring = sqrt(η_B(obs)·8πG·m_p·n_γ(T_CMB)/(3·Ω_b))  ← 預言!

  呢條鏈完全冇循環: η_B(obs) 由 D/H 觀測嚟, 唔經 ω_ring!
"""
import numpy as np

# 常數
G = 6.67430e-11          # m³/kg/s²
c = 299792458            # m/s
k_B = 1.380649e-23       # J/K
hbar = 1.054571817e-34   # J·s
m_p = 1.67262192369e-27  # kg
Mpc_m = 3.085677581491367e22  # m
Gyr_s = 3.15576e16       # s/Gyr

# IDCM 結構
Omega_b = 0.04221        # Ω_b/Ω_m = 2/15, Ω_DM/Ω_b = 13/2 (結構閉合)

def n_gamma(T):
    return 2 * 1.202056903159594 / np.pi**2 * (k_B * T / (hbar * c))**3

def omega_ring_from_eta(eta, Omega_b, T):
    """反推: ω_ring (km/s)/Mpc — 由觀測 η_B + T_CMB + Ω_b"""
    n_g = n_gamma(T)
    rho_c = eta * m_p * n_g / Omega_b
    omega_s = np.sqrt(8 * np.pi * G * rho_c / 3)
    return omega_s * Mpc_m / 1000

print("=" * 74)
print("0. 循環檢查 (反幻覺)")
print("=" * 74)
print("""
  ❌ 循環 (錯誤做法):
     IDCM η_B = 6.062e-10 (用 ρ_c = 3H₀²/8πG 計出嚟)
     → 反推 ω_ring = 72.47
     → 循環! (η_B 本身有 H₀², 反推兜返圈)

  ✅ 真鎖定 (正確做法):
     觀測 η_B(obs) = 6.104e-10 (BBN D/H fit, 冇 H₀!)
     → 反推 ω_ring = 72.72
     → 冇循環! (η_B(obs) 由核物理 + D/H 觀測, 唔經 ω_ring)
""")

print("=" * 74)
print("1. 觀測 η_B 來源 (BBN, 冇 ω_ring)")
print("=" * 74)
print("""
  BBN 豐度觀測:
    D/H = 2.527e-5 (Cooke 2018, 高z DLA)
    Y_p = 0.2453 (Planck 2020)
    → 標準 BBN 核網絡 fit → η_B = 6.104e-10 ± 0.03e-10 (PDG 2024)

  呢個 fit 只用核物理 (反應截面) + 觀測豐度:
    n_p, n_n, D, ³He, ⁴He, ⁷Li 豐度 = f(η_B)
    → 完全冇 H₀/ω_ring/膨脹率!
  → η_B(obs) 係獨立觀測輸入 ✅
""")

print("=" * 74)
print("2. ★★★ 鎖定: η_B(obs) + T_CMB + Ω_b → ω_ring")
print("=" * 74)
eta_obs = 6.104e-10      # PDG 2024 BBN fit
omega_pred = omega_ring_from_eta(eta_obs, Omega_b, 2.72548)
print(f"  η_B(obs) = {eta_obs:.4e}  (PDG 2024, BBN D/H fit)")
print(f"  T_CMB = 2.72548 K (COBE/FIRAS)")
print(f"  Ω_b = {Omega_b} (IDCM 結構)")
print(f"  → ω_ring (預言) = {omega_pred:.4f} (km/s)/Mpc")
print(f"  vs IDCM ω_ring = 72.59")
print(f"  vs 距離階梯 73.04 (SH0ES)")
print(f"  vs Maser 73.9 (MCP)")
print(f"  偏差 vs 72.59 = {(omega_pred-72.59)/72.59*100:+.4f}%")
print(f"  偏差 vs 73.04 = {(omega_pred-73.04)/73.04*100:+.4f}%")
print()

print("=" * 74)
print("3. 誤差傳播")
print("=" * 74)
# η_B: PDG ±0.03e-10 (~0.5%)
# T_CMB: ±0.00057 K (COBE/FIRAS)
# Ω_b: ±0.5% (結構閉合誤差)
d_omega_eta = omega_pred * (0.03e-10 / eta_obs) / 2
d_omega_T = omega_pred * (3 * 0.00057 / 2.72548) / 2
d_omega_Ob = omega_pred * 0.005 / 2
total = d_omega_eta + d_omega_T + d_omega_Ob
print(f"  η_B ±0.5%:  ω_ring ± {d_omega_eta:.2f} ({d_omega_eta/omega_pred*100:.2f}%)")
print(f"  T_CMB ±0.57mK: ω_ring ± {d_omega_T:.3f} ({d_omega_T/omega_pred*100:.3f}%)")
print(f"  Ω_b ±0.5%:  ω_ring ± {d_omega_Ob:.2f} ({d_omega_Ob/omega_pred*100:.2f}%)")
print(f"  總誤差 (相加): ±{total:.2f} ({total/omega_pred*100:.2f}%)")
print(f"  72.59 喺範圍內? {abs(72.59-omega_pred) < total}")
print(f"  73.04 喺範圍內? {abs(73.04-omega_pred) < total}")
print()

print("=" * 74)
print("4. 交叉驗證 (唔同 η_B 輸入)")
print("=" * 74)
for eta_alt, name in [(6.104e-10, "PDG 2024 (D/H fit)"),
                      (6.10e-10, "Planck 2018"),
                      (6.062e-10, "IDCM 結構目標 (循環警告!)"),
                      (6.03e-10, "BBN lower 1σ"),
                      (6.18e-10, "BBN upper 1σ")]:
    w = omega_ring_from_eta(eta_alt, Omega_b, 2.72548)
    tag = " ⚠️ 循環" if eta_alt == 6.062e-10 else ""
    print(f"  {name:26s} → ω_ring = {w:.2f} (dev vs 72.59: {(w-72.59)/72.59*100:+.2f}%){tag}")

print()
print("=" * 74)
print("5. ★★★ 完整第一性原理鏈 (冇循環)")
print("=" * 74)
print("""
  輸入 (全部唔經 ω_ring):
    1. D/H = 2.527e-5        ← 觀測 (高z DLA 吸收線)
    2. T_CMB = 2.72548 K     ← 觀測 (COBE/FIRAS)
    3. Ω_b = 0.04221         ← IDCM 結構 (Ω_b/Ω_m = 2/15)
    4. m_p, G, k_B, ħ, ζ(3)  ← 物理常數

  推導:
    5. η_B(obs) = 6.104e-10  ← 標準 BBN 核網絡 (冇 H₀!)
    6. n_γ = 2ζ(3)/π²·(k_B T/ħc)³
    7. ρ_c = η_B·m_p·n_γ/Ω_b (IDCM 質量分配)
    8. ω_ring = sqrt(8πG·ρ_c/3) = 72.72 (km/s)/Mpc

  命中:
    IDCM ω_ring = 72.59   (0.19%)
    距離階梯 = 73.04      (0.44%)
    Maser = 73.9          (1.6%, 1σ 內)

  → ω_ring 唔係自由參數! 係 BBN 豐度 + T_CMB + Ω_b 鎖定嘅預言!
  → 「零參數」claim 恢復 (ω_ring 係預言, 唔係 fit)
  → H1 判決「η_B ∝ H₀² 係 re-label」只啱一半:
     方向 A (IDCM η_B → ω_ring) 係 re-label
     方向 B (η_B(obs) → ω_ring) 係鎖定!!
""")
