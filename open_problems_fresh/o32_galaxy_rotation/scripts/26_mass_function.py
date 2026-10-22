#!/usr/bin/env python3
"""
O32-26: 星系質量函數 — K_Tree 深度量子化
==========================================
方向 3: 放棄 Press-Schechter, 改用有限譜量子化

核心假設:
1. 星系形成 = K_Tree (33 層, B=4) 特定深度嘅共振崩塌
2. 崩塌閾值 = K_Chain 模式能量標度
3. 質量階梯 = Fibonacci/Lucas 結構

推導:
- 質量標度: M_d = M₀·4^d? (K_Tree B=4)
- 對應速度: V = (G·M·a₀)^(1/4) (BTFR!)
- 崩塌質量: 由 a₀ 臨界加速度 + 宇宙學密度決定

經典崩塌質量 (ΛCDM 對照):
M_PS = (4π/3)ρ_m·(3σ(R)/δ_c)^3...

IDCM 版本:
- 崩塌尺度 R_c: a(R_c) = a₀ → R_c = √(GM(R_c)/a₀)
- 但 M(R) 由 K_Tree 量子化: M = M_0·4^d
"""
import numpy as np
import json

G = 6.674e-11
Msun = 1.989e30
c = 299792.458e3
R_H = 4129.94*3.085677581e22
H0 = c/R_H
a0 = c**2/(2*np.pi*R_H)
phi = (1+np.sqrt(5))/2

# 宇宙學密度 (IDCM)
Omega_m = 0.3167  # IDCM: Ω_b+Ω_DM
rho_c = 3*H0**2/(8*np.pi*G)
rho_m = Omega_m*rho_c

print("="*70)
print("星系質量函數: K_Tree 量子化")
print("="*70)

# ===== 1. 質量階梯 =====
print("\n--- 1. K_Tree 質量階梯 ---")
# K_Tree: 33 層, B=4, λ_sync = 294.88 Mpc
# 尺度階梯: λ_sync/4^d
# 質量階梯: M ∝ ρ·λ³ ∝ λ³ (固定 ρ)
lam_sync = 294.88  # Mpc
M_0 = rho_m*(lam_sync*3.0857e22)**3/Msun  # λ_sync 尺度質量
print(f"ρ_m = {rho_m:.4e} kg/m³")
print(f"λ_sync = 294.88 Mpc 質量: M = {M_0:.3e} Msun")

# 每層: λ_d = λ_sync/4^d, M_d = M_0/64^d
print(f"\n質量階梯 M_d = M₀/64^d (每層 ÷64, 因為 4³):")
for d in range(0, 12):
    M_d = M_0/64**d
    lam_d = lam_sync/4**d
    if M_d > 1e6:
        print(f"  d={d:>2}: λ = {lam_d:>10.1f} kpc, M = {M_d:>10.3e} Msun")

# ===== 2. 找星系質量範圍 =====
print("\n--- 2. 星系質量範圍 (1e9-1e12 Msun) ---")
print("對應深度:")
for M_target in [1e9, 1e10, 1e11, 1e12]:
    d = np.log(M_0/M_target)/np.log(64)
    lam = lam_sync/4**d
    print(f"  M = {M_target:.0e} Msun: d = {d:.2f}, λ = {lam:.1f} kpc")

# ===== 3. 崩塌閾值: a(R) = a₀ =====
print("\n--- 3. 崩塌閾值 a(R_c) = a₀ ---")
# 密度漲落 δ ~ 1: g_bar(R) = GM(R)/R²
# 崩塌當 g_bar ~ a₀ → R_c² = GM/a₀ → R_c = √(GM/a₀)
# 但 M 本身由 R 決定 (均勻密度): M = (4π/3)ρR³
# 崩塌質量: GM/R² = a₀ 且 M = (4π/3)ρR³
# → G(4π/3)ρR³/R² = a₀ → (4π/3)GρR = a₀ → R_c = 3a₀/(4πGρ)
# → M_c = (4π/3)ρ·(3a₀/(4πGρ))³ = (4π/3)ρ·27a₀³/(64π³G³ρ³)
#       = 9a₀³/(16π²G³ρ²)  (⚠️ 修正: 之前錯寫 27, 正確係 9)
M_c = 9*a0**3/(16*np.pi**2*G**3*rho_m**2)
print(f"崩塌半徑 R_c = 3a₀/(4πGρ) = {3*a0/(4*np.pi*G*rho_m)/3.0857e19:.1f} kpc")
print(f"崩塌質量 M_c = 9a₀³/(16π²G³ρ²) = {M_c/Msun:.3e} Msun")
print(f"(ΛCDM 對照: Press-Schechter M* ≈ 1e13 Msun)")

# 呢個 M_c 同 BTFR 有咩關係?
V_c = (G*M_c*a0)**0.25
print(f"V_c = (G·M_c·a₀)^(1/4) = {V_c/1e3:.1f} km/s")

# ===== 4. 質量函數 =====
print("\n--- 4. 質量函數形式 ---")
# 量子化: 質量階梯 M_d = M₀/64^d
# 每個階級嘅豐度: 由 K_Tree 分支數決定
# 層 d 有 4^d 個節點 → 每個節點一個星系
# → dN/dM ∝ 4^d / (dM_d/dd)
# M_d = M₀·4^(-3d) → dM/dd = -3ln4·M_d
# dN/dM = 4^d/(3ln4·M_d) ∝ 4^d/M_d = 4^d/(M₀·4^(-3d)) = 4^(4d)/M₀

# 冪律: dN/dM ∝ M^(-α)
# M ∝ 4^(-3d) → d ∝ -log₄(M/M₀)/3
# dN/dM ∝ 4^(4d) = (4^(-3d))^(-4/3) = M^(-4/3)
alpha = 4/3
print(f"量子化質量函數: dN/dM ∝ M^(-{alpha:.3f})")
print(f"ΛCDM 對照 (低質量端): α ≈ 1.9-2.0 (Schechter α)")
print(f"觀測: 星系質量函數低質量端 α ≈ 1.3-1.5")

# 高質量端 cutoff: 由崩塌閾值 M_c
print(f"\n高質量 cutoff: M > M_c = {M_c/Msun:.2e} Msun 唔崩塌 (g < a₀)")
print(f"→ 質量函數: dN/dM ∝ M^(-4/3)·exp(-(M/M_c))")

# ===== 5. Fibonacci 修正 =====
print("\n--- 5. Fibonacci/Lucas 質量階梯 ---")
# 純 B=4 階梯太粗糙, 用 Fibonacci 組合?
# 記憶: N_d = 44 = φ級聯 199-76-29-4, F₇ = 13
# Lucas: L₇ = 29
print("Fibonacci: 1, 1, 2, 3, 5, 8, 13, 21, 34, ...")
print("Lucas:     2, 1, 3, 4, 7, 11, 18, 29, 47, ...")
print(f"F₇ = 13, L₇ = 29, F₆+F₇ = 21, L₆ = 18")

# 質量比候選
print(f"\n質量比候選 (相鄰階級):")
print(f"  φ³ = {phi**3:.3f} ≈ 4.236")
print(f"  φ⁴ = {phi**4:.3f} ≈ 6.854")
print(f"  4 = B (K_Tree)")
print(f"  64 = B³ (質量維度)")

# ===== 6. BTFR 質量-速度 =====
print("\n--- 6. BTFR 連接 ---")
# 每個質量階級 M_d → V_d = (GM_d·a₀)^(1/4)
print(f"{'d':>3} {'M (Msun)':>12} {'V (km/s)':>10} {'λ (kpc)':>10}")
for d in range(0, 12):
    M_d = M_0/64**d
    if M_d < 1e7 or M_d > 1e14:
        continue
    V_d = (G*M_d*Msun*a0)**0.25/1e3
    lam_d = lam_sync/4**d*1e3  # kpc
    print(f"{d:>3} {M_d:>12.3e} {V_d:>10.1f} {lam_d:>10.1f}")

with open('data/mass_function.json', 'w') as f:
    json.dump({
        'M_c': float(M_c/Msun),
        'V_c': float(V_c/1e3),
        'alpha': float(alpha),
        'ladder': 'M_d = M₀/64^d',
        'lambda_sync': 294.88,
        'mass_range': '1e9-1e12 Msun ↔ d = 4-6'
    }, f, indent=2)
print("結果已存: data/mass_function.json")
