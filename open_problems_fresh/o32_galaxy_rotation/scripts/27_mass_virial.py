#!/usr/bin/env python3
"""
O32-27: 質量函數 virial 修正 — 崩塌密度閉合
============================================
問題: script 26 用 ρ_m 計 M_c = 4.2e22 (宇宙尺度) — 錯!
正確: 崩塌時密度 = virial overdensity Δ_vir ≈ 18π² ≈ 177 (ΛCDM)
     但 IDCM 冇膨脹 → 崩塌密度由 W-field 決定!

關鍵洞察: 崩塌 = g_bar 到 a₀ 嘅過渡
R_c 由「深 MOND 區域開始」決定:
  g_bar(R) = a₀ → R_c = √(GM(R_c)/a₀)

但更基本: 星系形成嘅「崩塌質量」應該由 BTFR 反推!
  V⁴ = G·M·a₀ → M = V⁴/(G·a₀)
  觀測: 銀河系 V ≈ 180 km/s → M_bar ≈ ?

另一條路: 質量階梯同崩塌尺度嘅一致性
  M_d = M₀/64^d (K_Tree 階梯)
  R_d = √(GM_d/a₀) (崩塌半徑)
  → R_d 應該 = λ_d = λ_sync/4^d?
"""
import numpy as np
import json

G = 6.674e-11
Msun = 1.989e30
c = 299792.458e3
R_H = 4129.94*3.085677581e22
H0 = c/R_H
a0 = c**2/(2*np.pi*R_H)
rho_c = 3*H0**2/(8*np.pi*G)
phi = (1+np.sqrt(5))/2

print("="*70)
print("質量函數 virial 修正")
print("="*70)

# ===== 1. 質量階梯 + 崩塌半徑一致性 =====
print("\n--- 1. 質量階梯 M_d ↔ 崩塌半徑 R_c = √(GM/a₀) ---")
M_0 = 1.1859e18  # Msun (λ_sync 尺度質量, script 26)
print(f"{'d':>3} {'M_d (Msun)':>12} {'R_c = √(GM/a₀)':>14} {'λ_d (kpc)':>10} {'R_c/λ_d':>8}")
for d in range(3, 8):
    M_d = M_0/64**d
    R_c = np.sqrt(G*M_d*Msun/a0)/3.0857e19  # kpc
    lam_d = 294.88*1e3/4**d  # kpc
    ratio = R_c/lam_d
    print(f"{d:>3} {M_d:>12.3e} {R_c:>14.2f} {lam_d:>10.2f} {ratio:>8.3f}")

# ===== 2. R_c = λ_d 嘅解 =====
print("\n--- 2. 解 R_c = λ_d ---")
# √(GM_d/a₀) = λ_sync/4^d, M_d = M₀/64^d
# 兩邊平方: GM₀·64^(-d)/a₀ = (λ_sync·4^(-d))²
# GM₀·64^(-d)/a₀ = λ_sync²·16^(-d)
# GM₀/a₀·64^(-d) = λ_sync²·16^(-d)
# GM₀/(a₀·λ_sync²) = 16^(-d)/64^(-d) = 64^d/16^d = 4^d
# d = log₄(GM₀/(a₀λ_sync²))
lhs = G*M_0*Msun/(a0*(294.88*3.0857e22)**2)
d_star = np.log(lhs)/np.log(4)
print(f"GM₀/(a₀λ_sync²) = {lhs:.4f}")
print(f"d* = log₄(GM₀/(a₀λ_sync²)) = {d_star:.4f}")
print(f"→ 質量階梯同崩塌半徑喺 d* ≈ {d_star:.1f} 一致")

# 如果 d* 應該 = 4 (銀河系): GM₀/(a₀λ²) = 4⁴ = 256
print(f"4⁴ = 256 vs 實際 {lhs:.4f} — 比例 {lhs/256:.4f}")

# ===== 3. 由 BTFR 反推崩塌質量 =====
print("\n--- 3. BTFR 反推 M_c ---")
# 銀河系: V = 180 km/s, V_flat = 200 km/s
# M_bar = V⁴/(G·a₀)
for V in [50, 100, 180, 200, 300]:
    M = (V*1e3)**4/(G*a0)/Msun
    R = np.sqrt(G*M*Msun/a0)/3.0857e19
    print(f"V = {V:>3} km/s: M_bar = {M:>10.3e} Msun, R_c = {R:>7.1f} kpc")

# ===== 4. virial 密度 =====
print("\n--- 4. virial 密度修正 ---")
# ΛCDM: Δ_vir ≈ 18π² ≈ 177.6 (Einstien-de Sitter)
# IDCM: 冇膨脹, 冇 Λ → 用 W-field 過渡
# 崩塌密度: ρ_coll = M_c/((4π/3)R_c³)
# 但 M_c, R_c 由 a₀ 鎖死: GM/R² = a₀ → ρ_coll = M/(4πR³/3) = 3a₀/(4πGR)
# → ρ_coll·R = 3a₀/(4πG) = const!

print(f"ρ_coll·R_c = 3a₀/(4πG) = {3*a0/(4*np.pi*G):.4e} kg/m²·kpc⁻¹... 等我算")
print(f"3a₀/(4πG) = {3*a0/(4*np.pi*G):.4e} kg/m³·m = {3*a0/(4*np.pi*G)/3.0857e19:.4e} kg/m²")

# 密度-半徑關係: ρ ∝ 1/R (唔係 const!)
print(f"\n→ ρ_coll ∝ 1/R_c — 細星系密度高 (冇 cusp!)")
print(f"→ 對比 NFW: ρ ∝ 1/(r(1+r)²) — 中心 ∝ 1/r")

# 檢查: R = 20 kpc 時
R20 = 20*3.0857e19
rho20 = 3*a0/(4*np.pi*G*R20)
print(f"R = 20 kpc: ρ_coll = {rho20:.4e} kg/m³ = {rho20/Msun*3.0857e19**3:.2f} Msun/kpc³")
print(f"對比 ρ_c (宇宙臨界) = {rho_c:.4e} kg/m³")
print(f"overdensity = {rho20/rho_c:.1f}×")

# ===== 5. 質量函數完整形式 =====
print("\n--- 5. 質量函數完整形式 ---")
# dN/dM ∝ M^(-4/3)·exp(-(M/M_c))  (K_Tree 量子化 + 崩塌閾值)
# M_c 由「最後崩塌嘅尺度」決定 = 而家仲喺 a₀ 過渡嘅尺度
# g_bar(R) = a₀: R_c = √(GM(R_c)/a₀), M(R_c) = ρ_coll·(4π/3)R_c³
# ρ_coll = 3a₀/(4πGR_c) → M = 3a₀/(4πGR_c)·(4π/3)R_c³ = a₀R_c²/G (一致!)
# → 冇閉合解 (R_c 自由) — 需要更多物理

# 用 BTFR: 質量函數 ↔ 速度函數
# VF: dN/dV ∝ dN/dM·dM/dV, M ∝ V⁴ → dM/dV ∝ V³
# dN/dM ∝ M^(-4/3) → dN/dV ∝ V^(-16/3)·V³ = V^(-7/3)
alpha_V = 7/3
print(f"速度函數: dN/dV ∝ V^(-7/3) = V^(-{alpha_V:.4f})")
print(f"ΛCDM 對照: VF 低速度端 α ≈ 2-3 (Schechter)")
print(f"觀測 (SDSS): 低質量端 α_V ≈ 2.5-3.0")

# 高速度 cutoff: V_c 由崩塌
# V_c = (G·M_c·a₀)^(1/4), M_c 需要確定

# ===== 6. 嘗試: M_c 由 T_sync 尺度 =====
print("\n--- 6. M_c 候選 ---")
# 宇宙一生內完成崩塌: t_coll = T_sync/2π = 1/H₀
# 自由落體時間: t_ff = √(3π/(32Gρ)) → ρ_coll = 3π/(32G·t_ff²)
# t_ff = 1/H₀ → ρ = 3πH₀²/(32G) = 3π/32·ρ_c·8/3·... 
# ρ_c = 3H₀²/(8πG) → ρ_coll = 3πH₀²/(32G) = (3π/32)·8πρ_c/3·... 
# ρ_coll = 3π/(32G)·H₀² = 3πH₀²/(32G) = (3π/(32G))·(8πGρ_c/3) = π²ρ_c/4
rho_ff = np.pi**2*rho_c/4
print(f"t_ff = 1/H₀ → ρ_coll = π²ρ_c/4 = {rho_ff/rho_c:.4f} ρ_c")
print(f"(ΛCDM Δ_vir = 18π² ≈ 177.6, 我哋 π²/4 ≈ 2.47 — 差好遠)")

# 用 T_sync = 84.64 Gyr (2π/H₀): t_ff = T_sync/2π = 1/H₀ 同上
# 用 t_ff = T_sync = 2π/H₀: ρ = 3π/(32G)·H₀²/(4π²)·... 
rho_ff2 = 3*np.pi/(32*G*(2*np.pi/H0)**2)
print(f"t_ff = 2π/H₀ → ρ_coll = {rho_ff2/rho_c:.4f} ρ_c")

# 用 t_ff = T_sync/4 (K_Tree 一層)? 
rho_ff4 = 3*np.pi/(32*G*(2*np.pi/H0/4)**2)
print(f"t_ff = (2π/H₀)/4 → ρ_coll = {rho_ff4/rho_c:.4f} ρ_c")

# ===== 7. 另一角度: 質量階梯同 44 嘅關係 =====
print("\n--- 7. 質量階梯 ↔ 44-site ---")
# M_0 = ρ_m·λ_sync³, λ_sync = R_H·(44-44/4^3)/... 
# λ_sync 喺 D_app 公式: D_app(ℓ) = (44-44/4^ℓ)(R_H/44)(1+2φ⁻¹ℓ)
# ℓ=3: D_app(3) = (44-44/64)(R_H/44)(1+2φ⁻³) = 43.31·93.86·1.472 = 5983 Mpc? 
# 唔啱 — D_app 係視距。λ_sync = 294.88 Mpc = R_H/14.0?
R_H_Mpc = 4129.94
print(f"R_H/λ_sync = {R_H_Mpc/294.88:.4f}")
print(f"R_H/λ_sync ≈ 14 = 2×7? {14}")
print(f"44/(R_H/λ_sync) = {44/(R_H_Mpc/294.88):.4f} ≈ 3.14 = π!?")

# ===== 總結 =====
print("\n" + "="*70)
print("★ 質量函數閉合狀態")
print("="*70)
print("""
已閉合:
1. 質量階梯 M_d = M₀/64^d (K_Tree B=4)
2. d=4 ↔ 銀河系 (7e10 Msun, 180 km/s)
3. dN/dM ∝ M^(-4/3) (觀測 1.3-1.5 ✅)
4. 速度函數 dN/dV ∝ V^(-7/3)
5. ρ_coll ∝ 1/R (W-field 過渡, 冇 cusp)

未閉合:
1. M_c 嘅確定值 (崩塌截止質量)
2. virial 密度嘅 IDCM 推導
3. 觀測驗證 (SDSS/GAMA 質量函數)

下一步: 用 SPARC/觀測質量函數數據直接 fit 質量階梯!
""")

with open('data/mass_function_virial.json', 'w') as f:
    json.dump({
        'd_star': float(d_star),
        'rho_coll_R': '3a0/(4πGR) — ρ ∝ 1/R',
        'alpha_V': float(alpha_V),
        'R_H_over_lambda': float(R_H_Mpc/294.88),
        'tff_rho': float(rho_ff/rho_c),
        'status': 'ladder ✅, M_c 🔴'
    }, f, indent=2)
print("結果已存: data/mass_function_virial.json")
