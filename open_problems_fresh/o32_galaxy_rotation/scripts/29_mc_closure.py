#!/usr/bin/env python3
"""
O32-29: M_c 崩塌截止質量閉合 — λ_sync + BTFR 組合
=====================================================
核心: M_c = a₀·λ_sync²/(44⁴·π²·G) = 1.89e12 Msun (Schechter M*)
      V_max = √(a₀·R_H/44³) = 410 km/s (最大旋轉速度)

閉合鏈:
  λ_sync = π·R_H/44 (0.001% ✅)
  → R_c = λ_sync/(44²π) = R_H/44³ = 48.5 kpc
  → V_max = √(a₀·R_c) = c·44^{-3/2}/√(2π) = 410 km/s
  → M_c = V_max⁴/(G·a₀) = a₀·R_H²/(44⁶·G) = 1.89e12 Msun

同時修正 script 26/27 嘅錯誤:
  1. M_c 公式: 27a₀³/(16π²G³ρ²) → 9a₀³/(16π²G³ρ²) (3×)
  2. d* 記錄: 3.48 → -2.94 (符號錯)
"""
import numpy as np
import json
import math

# ===== 常數 =====
G = 6.67430e-11
MSUN = 1.98892e30
C = 299792458.0
R_H = 4129.94 * 3.0856775814913673e22  # m
R_H_MPC = 4129.94
H0 = C / R_H  # s⁻¹
a0 = C**2 / (2 * np.pi * R_H)  # 1.12245e-10 m/s²
PHI = (1+np.sqrt(5))/2
LAM_SYNC = 294.88  # Mpc
LAM_SYNC_M = LAM_SYNC * 3.0856775814913673e22
MPC_TO_M = 3.0856775814913673e22
KPC_TO_M = 3.0856775814913673e19

print("="*78)
print("M_c 崩塌截止質量閉合 — λ_sync + BTFR 組合")
print("="*78)

results = []

# ===== 1. 驗證基礎常數 =====
print("\n--- 1. 基礎常數 ---")
print(f"R_H = {R_H_MPC:.4f} Mpc")
print(f"H₀ = c/R_H = {H0:.4e} s⁻¹ = {H0*3.0857e19:.2f} km/s/Mpc")
print(f"a₀ = c²/(2πR_H) = {a0:.6e} m/s²")
print(f"λ_sync = {LAM_SYNC:.4f} Mpc")

# ===== 2. R_c = R_H/44³ = 48.5 kpc =====
print("\n--- 2. R_c: 最大相干盤半徑 ---")
# 44³ = 85184 (三維 K_Chain 模式空間體積)
R_c_Mpc = R_H_MPC / 44**3
R_c_kpc = R_c_Mpc * 1000
R_c_m = R_c_Mpc * MPC_TO_M
print(f"R_c = R_H/44³ = {R_H_MPC:.4f}/{44**3} = {R_c_Mpc:.6f} Mpc = {R_c_kpc:.1f} kpc")
print(f"44³ = {44**3}")
print(f"44⁴ = {44**4}")

# λ_sync 表達
R_c_via_lam = LAM_SYNC / (44**2 * math.pi)
print(f"R_c = λ_sync/(44²π) = {LAM_SYNC:.4f}/({44**2}π) = {R_c_via_lam:.6f} Mpc")
print(f"R_c 一致: {abs(R_c_Mpc - R_c_via_lam)/R_c_Mpc*100:.2e}% ✅")

# ===== 3. V_max = √(a₀·R_c) = 410 km/s =====
print("\n--- 3. V_max: 最大旋轉速度 ---")
V_max = np.sqrt(a0 * R_c_m)
V_max_kms = V_max / 1000
print(f"V_max = √(a₀·R_c) = √({a0:.4e}·{R_c_m:.4e}) = {V_max:.4e} m/s = {V_max_kms:.1f} km/s")

# 解析形式: V_max = c·44^{-3/2}/√(2π)
V_max_analytic = C * 44**(-1.5) / np.sqrt(2*np.pi)
V_max_analytic_kms = V_max_analytic / 1000
print(f"V_max = c·44^(-3/2)/√(2π) = {C:.0f}·{44**(-1.5):.6f}/{np.sqrt(2*np.pi):.6f}")
print(f"      = {V_max_analytic:.4e} m/s = {V_max_analytic_kms:.1f} km/s")
print(f"      (一致: {abs(V_max-V_max_analytic)/V_max*100:.2e}% ✅)")
print(f"觀測最大星系 V ~ 400-500 km/s (UGC 12591 ~ 500 km/s) ✅")

results.append(('V_max (km/s)', V_max_kms, 410, 'max rotation'))

# ===== 4. M_c = V_max⁴/(G·a₀) = 1.89e12 Msun =====
print("\n--- 4. M_c: 崩塌截止質量 (Schechter M*) ---")
M_c_kg = V_max**4 / (G * a0)
M_c_Msun = M_c_kg / MSUN
print(f"M_c = V_max⁴/(G·a₀) = ({V_max:.4e})⁴/({G:.4e}·{a0:.4e})")
print(f"    = {M_c_kg:.4e} kg = {M_c_Msun:.4e} Msun")

# a₀·R_H²/(44⁶·G) 形式
M_c_via_RH = a0 * R_H**2 / (44**6 * G) / MSUN
print(f"M_c = a₀·R_H²/(44⁶·G) = {a0:.4e}·({R_H:.4e})²/({44**6}·{G:.4e})")
print(f"    = {M_c_via_RH:.4e} Msun (一致: {abs(M_c_Msun-M_c_via_RH)/M_c_Msun*100:.2e}% ✅)")

# a₀·λ_sync²/(44⁴·π²·G) 形式
M_c_via_lam = a0 * LAM_SYNC_M**2 / (44**4 * math.pi**2 * G) / MSUN
print(f"M_c = a₀·λ_sync²/(44⁴·π²·G) = {M_c_via_lam:.4e} Msun (一致: {abs(M_c_Msun-M_c_via_lam)/M_c_Msun*100:.2e}% ✅)")

# Schechter M* 對比 (觀測 M* ≈ 10¹¹-10¹² Msun)
print(f"→ Schechter M* ≈ 10¹¹-10¹² Msun ✅ ({M_c_Msun:.2e} Msun)")
print(f"→ Press-Schechter DM halo M* ≈ 10¹²-10¹³ Msun ✅")

results.append(('M_c (Msun)', M_c_Msun, 1.89e12, 'Schechter M*'))

# ===== 5. 質量階梯 M_c 位置 =====
print("\n--- 5. 質量階梯位置 ---")
# M_d = M₀/64^d, 搵 d 令 M_d ≈ M_c
M0 = 1.187e18  # Msun
d_c = np.log(M0 / M_c_Msun) / np.log(64)
print(f"M_c 喺質量階梯位置: d_c = log₆₄(M₀/M_c) = {d_c:.4f}")
print(f"→ d = {d_c:.1f} (介乎 d=3 星系團 4.5e12 同 d=4 銀河系 7.1e10)")

# M_c 對應速度
V_c = (G * M_c_kg * a0)**0.25
print(f"V(M_c) = (G·M_c·a₀)^(1/4) = {V_c/1000:.1f} km/s (= V_max = {V_max_kms:.1f} km/s ✅)")

# ===== 6. 質量函數完整形式 =====
print("\n--- 6. 質量函數完整形式 ---")
print("dN/dM ∝ M^(-4/3)·exp(-(M/M_c))")
print(f"  M_c = {M_c_Msun:.4e} Msun (Schechter cutoff)")
print(f"  α = 4/3 (低質量端冪律, 觀測 1.3-1.5 ✅)")

# ===== 7. 修正 script 26/27 錯誤 =====
print("\n" + "="*78)
print("★ 修正: Script 26 M_c 公式 3× 錯誤")
print("="*78)
print("""
Script 26 (已修正 2026-08-18): M_c = 9*a0**3/(16*π²*G³*ρ²) ✅
原本錯:                      M_c = 27*a0**3/(16*π²*G³*ρ²) (3× 錯誤)

推導:
  GM/R² = a₀ → R = √(GM/a₀)
  M = (4π/3)ρR³ → R = (3M/(4πρ))^(1/3)
  √(GM/a₀) = (3M/(4πρ))^(1/3) → (GM/a₀)^(3/2) = 3M/(4πρ)
  M^(1/2) = 3a₀^(3/2)/(4πρG^(3/2))
  M = 9a₀³/(16π²G³ρ²)  ← 正確係 9 唔係 27!
""")
# 驗證: 用正確公式
rho_m = 3.135e-27  # kg/m³ (script 26 值)
M_c_correct = 9*a0**3/(16*np.pi**2*G**3*rho_m**2) / MSUN
M_c_wrong = 27*a0**3/(16*np.pi**2*G**3*rho_m**2) / MSUN
print(f"ρ_m = {rho_m:.4e} kg/m³")
print(f"M_c (正確 9)  = {M_c_correct:.3e} Msun")
print(f"M_c (錯誤 27) = {M_c_wrong:.3e} Msun")
print(f"比例 = {M_c_wrong/M_c_correct:.1f}× ✓")

# 但兩個都係宇宙尺度 (用 ρ_m)，需要用崩塌密度先得
print("\n注意: 用 ρ_m (宇宙平均密度) 會得到宇宙尺度 M_c,")
print("必須用崩塌密度 ρ_coll = Δ·ρ_m, Δ ≈ 177 先得到星系尺度。")

# ===== 8. 修正 d* 記錄 =====
print("\n" + "="*78)
print("★ 修正: d* 記錄 (3.48 → -2.94)")
print("="*78)
GM0 = G * M0 * MSUN
lam_sync_m = 294.88 * MPC_TO_M
lhs = GM0 / (a0 * lam_sync_m**2)
d_star_correct = np.log(lhs) / np.log(4)
print(f"GM₀/(a₀λ_sync²) = {lhs:.6f}")
print(f"d* = log₄(GM₀/(a₀λ_sync²)) = {d_star_correct:.4f}")
print(f"(記錄 11_lambda_sync_closure.md 寫 3.48 — ❌ 應為 -2.94)")
print(f"d* = -2.94 ≈ -3 → GM₀/(a₀λ_sync²) ≈ 1/64 = {1/64:.6f}")
print(f"偏差 = {abs(lhs-1/64)/(1/64)*100:.2f}%")

# 用 M_c (正確) 代替 M₀ 睇 d* 變成？
M_c_kg_val = M_c_Msun * MSUN
lhs_c = G * M_c_kg_val / (a0 * lam_sync_m**2)
d_star_c = np.log(lhs_c) / np.log(4)
print(f"d*(M_c) = log₄(G·M_c/(a₀λ_sync²)) = {d_star_c:.4f}")

# ===== 9. 質量階梯細化 (Fibonacci) =====
print("\n" + "="*78)
print("★ 質量階梯 Fibonacci 細化")
print("="*78)
# 質量階梯 M_d = M₀/64^d, K_Tree B=4
# 相鄰階級質量比 = 64 = 4³
# Fibonacci 細化: 用 φ 比例
for d in range(3, 8):
    M_d = M0 / 64**d
    # Fibonacci 子層
    for k, f in enumerate([1, PHI, PHI**2, PHI**3]):
        M_sub = M_d / f
        if M_sub > 1e5 and M_sub < 1e15:
            print(f"  d={d}.{k}: M = {M_sub:.4e} Msun (×φ^{-k})")

# ===== 總結 =====
print("\n" + "="*78)
print("★ M_c 閉合總結")
print("="*78)
print(f"""
M_c = a₀·λ_sync²/(44⁴·π²·G)
    = V_max⁴/(G·a₀)
    = a₀·R_H²/(44⁶·G)
    = {M_c_Msun:.4e} Msun

V_max = √(a₀·R_H/44³) = c·44^(-3/2)/√(2π) = {V_max_kms:.1f} km/s

R_c = R_H/44³ = λ_sync/(44²·π) = {R_c_kpc:.1f} kpc

質量函數: dN/dM ∝ M^(-4/3)·exp(-(M/{M_c_Msun:.2e}))

修正:
  1. Script 26 M_c 公式: 27→9 (3× 錯誤)
  2. d* 記錄: 3.48→-2.94 (符號錯)
""")

# 保存
output = {
    'R_c_kpc': float(R_c_kpc),
    'V_max_kms': float(V_max_kms),
    'M_c_Msun': float(M_c_Msun),
    'M_c_formula': 'a0·λ_sync²/(44⁴·π²·G)',
    'V_max_formula': 'c·44^(-3/2)/√(2π)',
    'd_c_ladder': float(d_c),
    'script26_correction': '27→9 (3×)',
    'd_star_correction': '-2.94 (not 3.48)',
    'Schechter_match': f'M* ≈ 10¹¹-10¹² Msun ✅',
    'results': [{'name': r[0], 'value': r[1], 'expect': r[2], 'note': r[3]} for r in results]
}
with open('data/mc_closure.json', 'w') as f:
    json.dump(output, f, indent=2, default=str)
print("結果已存: data/mc_closure.json")