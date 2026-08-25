#!/usr/bin/env python3
"""
GZK 推導結構檢驗 + 精確化
==========================
問題: 2.18% 偏差 (E_GZK vs 5e19) 係咪結構性? 定係巧合?

檢查:
1. λ_min = L_P·φ⁴⁴ 嘅結構來源 (44 = N_d)
2. 用完整 MERA 深度公式 D_H/L_P = φ^(N_d·L + ε²-ε³-ε⁴) 會唔會更好
3. E_max = 4φ·E_GZK 嘅 4φ 來源 (MERA 分支 × φ)
4. 備選: E_GZK = E_Pl × φ⁻⁴⁴? 定係其他?
"""
import math

phi = (1 + 5**0.5) / 2
inv_phi = 1/phi
eps = inv_phi / 4
N_d = 44
L = 53/8

h = 6.62607015e-34
c = 2.99792458e8
L_P = 1.616255e-35
eV_J = 1.602176634e-19
# 注意: 用 non-reduced Planck 能量 E_Pl^h = hc/L_P (唔係 ħc/G 嘅 reduced 版本!)
# reduced: E_Pl = sqrt(ħc⁵/G) = 1.22e28 eV (錯嘅參照)
# non-reduced: E_Pl^h = hc/L_P = 7.68e28 eV (核心公式用嘅)
E_Pl_h = h * c / L_P  # J — non-reduced Planck 能量
print(f"E_Pl^h = hc/L_P = {E_Pl_h/eV_J:.3e} eV (non-reduced)")
print(f"E_Pl(reduced) = {math.sqrt(h*c**5/(2*math.pi*6.67430e-11))/eV_J:.3e} eV (唔用呢個!)")
print(f"ratio = 2π = {2*math.pi:.6f}")

# ============ 1. λ_min = L_P·φ^44 ============
lam1 = L_P * phi**44
E1 = h*c/lam1 / eV_J
print(f"\n1. λ_min = L_P·φ^44 = {lam1:.4e} m")
print(f"   E_GZK = {E1:.4e} eV  (vs 5e19, 偏差 {abs(E1/5e19-1)*100:.3f}%)")

# ============ 2. 完整 MERA 深度 ============
# D_H/L_P = φ^(N_d·L + ε²-ε³-ε⁴)  →  λ_min = L_P × φ^(-(N_d·L + ...))?
# 唔係 — 完整深度係最大尺度。λ_min 應該係「一個站點」嘅尺度
# 站點尺度 = R_H/44 = c/(44H₀)? 
# 試: λ_min = L_P × φ^N_d (44 層縮放, 唔含 L)
# 但 λ_min 要係「最細」→ φ^44 由 L_P 放大 44 次?
# 真正問題: φ^44 = 1.57e9 → λ_min = 2.53e-26 m
# 呢個係「44 步之後嘅尺度」— 但 L_P×φ^44 係放大, 唔係縮細!
print(f"\n2. 結構來源檢查:")
print(f"   φ^44 = {phi**44:.4e} (放大)")
print(f"   φ^-44 = {phi**-44:.4e} (縮細)")
print(f"   L_P×φ^44 = {lam1:.3e} m")
print(f"   L_P×φ^-44 = {L_P*phi**-44:.3e} m")

# λ_min 應該係幾細? E_GZK=5e19 eV → λ = hc/E
lam_gzk = h*c/(5e19*eV_J)
print(f"   λ(GZK 5e19 eV) = {lam_gzk:.4e} m")
print(f"   L_P×φ^44 = {lam1:.4e} m")
print(f"   ratio = {lam_gzk/lam1:.6f}")

# ============ 3. 用縮細版本: L_P×φ^-44 ============
lam2 = L_P * phi**-44
E2 = h*c/lam2 / eV_J
print(f"\n3. L_P×φ^-44: E = {E2:.3e} eV — 太巨大, 唔啱 GZK")

# ============ 4. 備選: 用 Compton/Planck 關係 ============
# E_GZK = E_Pl^h × φ^-44 (non-reduced Planck 能量)
E3 = E_Pl_h/eV_J * phi**-44
print(f"\n4. E_Pl^h×φ^-44 = {E3:.4e} eV  (vs 5e19, 偏差 {abs(E3/5e19-1)*100:.3f}%)")
# E_Pl^h×φ^-44 = hc/(L_P·φ^44) — 同核心公式完全一樣 ✅
print(f"   (同核心公式 hc/(L_P·φ^44) 一致: {abs(E3/E1-1)*100:.6f}%)")

# ============ 5. 真正嘅結構詮釋 ============
print(f"\n5. 結構詮釋:")
print(f"   E_GZK = E_Pl^h × φ^-44 = hc/(L_P·φ^44) = {E1:.4e} eV")
print(f"   E_max = 4φ × E_GZK = 4·E_Pl^h·φ^-43 = {4*E_Pl_h/eV_J*phi**-43:.4e} eV")
print(f"   (4φ·φ^-44 = 4·φ^-43, 指數結構一致)")
print(f"   Oh-My-God = 3.2e20 → 偏差 {abs(4*E_Pl_h/eV_J*phi**-43/3.2e20-1)*100:.3f}%")

# ============ 6. 更精確: 用完整 D_H/L_P 深度 ============
# D_H/L_P = φ^(291.5 + ε²-ε³-ε⁴) = φ^(583/2 + 0.0239-0.0037-0.00057)
exp_full = N_d*L + eps**2 - eps**3 - eps**4
print(f"\n6. 完整 MERA 深度指數: {exp_full:.6f}")
print(f"   291.5 + {eps**2-eps**3-eps**4:.6f} = {exp_full:.6f}")

# 如果 λ_min = L_P × φ^(N_d·L - 44·L)? 冇意義
# 真正問題: φ^44 係咪 N_d 步?
# 44 = N_d 本身 → φ^N_d = φ^44 ✅ 結構成立

# ============ 7. 敏感度分析 ============
print(f"\n7. 敏感度: 如果指數唔係 44:")
for exp in [43, 43.5, 44, 44.5, 45]:
    E = E_Pl_h/eV_J * phi**(-exp)
    print(f"   φ^-{exp}: E = {E:.4e} eV, GZK 偏差 {abs(E/5e19-1)*100:6.2f}%")

# ============ 8. 驗證 4φ 結構 ============
print(f"\n8. 4φ = (φ³-φ⁻³)×φ 驗證:")
print(f"   φ³-φ⁻³ = {phi**3 - phi**-3:.6f} (應該 = 4)")
print(f"   (φ³-φ⁻³)×φ = {4*phi:.6f} (應該 = 4φ = 6.472)")
print(f"   E_max/E_GZK = {4*phi:.6f}")

# ============ 總結 ============
print(f"\n{'='*60}")
print(f"總結:")
print(f"  E_GZK = hc/(L_P·φ^44) = {E1:.4e} eV  (2.18% vs 5e19)")
print(f"  E_max = 4φ·E_GZK = 4·hc/(L_P·φ^43) = {4*E_Pl_h/eV_J*phi**-43:.4e} eV  (1.08% vs 3.2e20)")
print(f"  結構: N_d=44 步黃金層級, MERA 分支 4, φ 乘數")
print(f"  零自由參數 — 全部來自 x²+x-1=0")
