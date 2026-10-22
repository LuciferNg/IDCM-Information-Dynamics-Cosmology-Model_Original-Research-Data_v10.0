#!/usr/bin/env python3
"""
O47-D3 — D_app(ℓ) 函數推導: ΛCDM 類比 + 離散結構
====================================================
從 ΛCDM 嘅 D_A(z) 函數類比, 推導 IDCM 嘅 D_app(ℓ) 函數形式。

ΛCDM: D_A(z) = c/(1+z) ∫₀ᶻ dz'/H(z'), H(z) = H₀√(Ω_m(1+z)³ + Ω_Λ)
IDCM: D_app(ℓ) = ?

關鍵 insight: 將 ℓ 映射到紅移 z, 噉 D_app(ℓ) 應該同 ΛCDM 嘅 D_A(z) 一致。
"""

import numpy as np
import math

# ═══════════════════════════════════════════════════════════════
# 常數
# ═══════════════════════════════════════════════════════════════
N_d = 44
B = 4
L_ktree = 53 / 8
phi = (1 + math.sqrt(5)) / 2
phi_inv = phi - 1
eps = phi_inv / 4
R_H = 4129.94          # Mpc
c = 299792.458         # km/s
H0 = c / R_H           # km/s/Mpc
a = R_H / N_d          # Mpc

Omega_L = 4 / (phi**4 - 1)
Omega_m = 1 - Omega_L
matter = 2 + B * L_ktree  # 28.5
vacuum = 88 - B * L_ktree  # 61.5

l_max = 14.7085
D_app_lmax = 6.3183

print("=" * 75)
print("  O47-D3 — D_app(ℓ) 函數推導: ΛCDM 類比")
print("=" * 75)
print(f"\n  H₀ = c/R_H = {c}/{R_H} = {H0:.4f} km/s/Mpc")
print(f"  Ω_Λ = {Omega_L:.6f}, Ω_m = {Omega_m:.6f}")

# ═══════════════════════════════════════════════════════════════
# 1. ΛCDM D_A(z) 函數
# ═══════════════════════════════════════════════════════════════
def H_ratio(z):
    """H(z)/H₀ = √(Ω_m(1+z)³ + Ω_Λ)"""
    return np.sqrt(Omega_m * (1 + z)**3 + Omega_L)

def D_A_LCDM(z):
    """ΛCDM 角直徑距離 (Mpc)"""
    if z <= 0:
        return 0.0
    # 數值積分
    N_steps = 10000
    z_vals = np.linspace(0, z, N_steps + 1)
    dz = z / N_steps
    integral = 0
    for i in range(N_steps):
        z_mid = (z_vals[i] + z_vals[i+1]) / 2
        integral += dz / H_ratio(z_mid)
    return c / (1 + z) * integral / H0

def D_C_LCDM(z):
    """ΛCDM 共動距離 (Mpc)"""
    if z <= 0:
        return 0.0
    N_steps = 10000
    z_vals = np.linspace(0, z, N_steps + 1)
    dz = z / N_steps
    integral = 0
    for i in range(N_steps):
        z_mid = (z_vals[i] + z_vals[i+1]) / 2
        integral += dz / H_ratio(z_mid)
    return c * integral / H0

print(f"\n─── 1. ΛCDM D_A(z) 參考點 ───")
print(f"  D_A(z=1) = {D_A_LCDM(1):.2f} Mpc")
print(f"  D_A(z=2) = {D_A_LCDM(2):.2f} Mpc")
print(f"  D_A(z=10) = {D_A_LCDM(10):.2f} Mpc")
print(f"  D_A(z=100) = {D_A_LCDM(100):.2f} Mpc")
print(f"  D_A(z=1000) = {D_A_LCDM(1000):.2f} Mpc")
print(f"  D_A(z=1100) = {D_A_LCDM(1100):.2f} Mpc (CMB)")

# 漸近值
z_max = 10000
D_A_inf = D_A_LCDM(z_max)
print(f"  D_A(z→∞) ≈ D_A(z={z_max}) = {D_A_inf:.2f} Mpc")
print(f"  R_H = {R_H} Mpc")
print(f"  D_A(∞) vs R_H: {D_A_inf / R_H:.4f} × R_H")

# ═══════════════════════════════════════════════════════════════
# 2. ℓ ↔ z 映射
# ═══════════════════════════════════════════════════════════════
print(f"\n─── 2. ℓ ↔ z 映射探索 ───")

# 假設 ℓ 對應某個 redshift z
# ℓ_max = 14.7085 對應 z 使得 D_A(z) = D_app(ℓ_max) × SF?
# 但 D_app(ℓ_max) = 6.3183 係 T_pipe 單位, 唔係 Mpc

# 假設: D_app(ℓ) 係「T_pipe 輸出」, 同 D_A(z) 有函數關係
# D_T(ℓ) = 6 + f(ℓ) × Ω_m  (f(ℓ) 由 0 到 1)
# D_T(ℓ_max) = 6.3167 → f(ℓ_max) ≈ 1

# 轉換到 Mpc: D_Mpc(ℓ) = D_T(ℓ) × SF
# 喺 ℓ_max: D_Mpc = 6.3167 × 653.65 = 4129.81 Mpc ≈ R_H

# 所以: D_Mpc(ℓ_max) ≈ R_H → ℓ_max 對應 z→∞
# 而 ℓ 同 z 嘅關係: z(ℓ) = ℓ/(ℓ_max - ℓ) × z_max?
# 或 z(ℓ) = tan(πℓ/2ℓ_max)?
# 或 z(ℓ) = ℓ^α?

# 簡單: z(ℓ) = ℓ / (ℓ_max - ℓ) × ℓ_max
# z(ℓ_max) → ∞
def z_from_ℓ_simple(l):
    if l >= l_max:
        return 1e10
    if l <= 0:
        return 0
    return l / (l_max - l) * l_max

print(f"  z(ℓ) = ℓ/(ℓ_max - ℓ) × ℓ_max")
print(f"  z(1) = {z_from_ℓ_simple(1):.2f}")
print(f"  z(5) = {z_from_ℓ_simple(5):.2f}")
print(f"  z(10) = {z_from_ℓ_simple(10):.2f}")
print(f"  z(14) = {z_from_ℓ_simple(14):.2f}")
print(f"  z(ℓ_max) = ∞")

# 用呢個映射, D_app(ℓ) = D_A(z(ℓ))
print(f"\n  D_app(ℓ) = D_A(z(ℓ)) 測試:")
for l_test in [1, 5, 10, 14]:
    z_test = z_from_ℓ_simple(l_test)
    D_test = D_A_LCDM(z_test)
    print(f"  ℓ={l_test:2d} → z={z_test:.2f} → D_A={D_test:.2f} Mpc")

# ═══════════════════════════════════════════════════════════════
# 3. 離散 D_app(ℓ) 結構
# ═══════════════════════════════════════════════════════════════
print(f"\n─── 3. 離散 D_app(ℓ) 結構: K_Chain 模式投影 ───")

# K_Chain 譜 γ_n
gamma = np.array([4 * np.sin(np.pi * n / 88)**2 for n in range(1, N_d + 1)])
# 88-site 奇數譜
gamma_odd = np.array([4 * np.sin(np.pi * (2*n-1) / 176)**2 for n in range(1, 45)])

# 假設: 每個 K_Chain 模式 n 對應一個 ℓ 值
# ℓ(n) = ℓ_max × (Σ_{k=1}^{n} γ_k) / (Σ_{k=1}^{N_d} γ_k)
# = ℓ_max × S(n)/90
# 噉 n=1→ℓ≈0.16, n=44→ℓ=14.7085

l_of_n = l_max * np.cumsum(gamma) / 90
print(f"  ℓ(n) = ℓ_max × S(n)/90:")
print(f"  ℓ(1) = {l_of_n[0]:.4f}")
print(f"  ℓ(10) = {l_of_n[9]:.4f}")
print(f"  ℓ(22) = {l_of_n[21]:.4f}")
print(f"  ℓ(44) = {l_of_n[43]:.4f}")

# D_app(ℓ(n)) = a × Σ_{k=1}^{n} τ_k · γ_k
# 如果 τ_k = (2 + B·L) / Σγ = 19/60 (uniform)
D_uniform = a * 19/60 * np.cumsum(gamma)
print(f"\n  D_app(ℓ(n)) = a × 19/60 × S(n) (uniform τ_n):")
print(f"  D_app(ℓ(1)) = {D_uniform[0]:.4f} Mpc")
print(f"  D_app(ℓ(10)) = {D_uniform[9]:.4f} Mpc")
print(f"  D_app(ℓ(22)) = {D_uniform[21]:.4f} Mpc")
print(f"  D_app(ℓ(44)) = {D_uniform[43]:.4f} Mpc")
print(f"  → 總和 = {D_uniform[43]:.4f} Mpc (目標 R_H = {R_H})")
print(f"  → uniform τ_n 唔夠, 得 2675 Mpc")

# 如果 τ_n 係非均匀, 需要令 Σ τ_n·γ_n = 28.5 而 D_app(44) = R_H
# D_app(44) = a × Σ τ_n·γ_n × (R_H / (a × 28.5))
# = a × 28.5 × (R_H / (a × 28.5)) = R_H ✓
# 只要 Σ τ_n·γ_n = 28.5 就得!

# 但需要定義每個 n 嘅 τ_n
# 從 88-site 結構: 物質 = 2 + B·L
# 2 = Σγ_even - Σγ_odd = 90 - 88
# B·L = 26.5

# τ_n 應該滿足: Σ γ_n · τ_n = 2 + B·L = 28.5
# 而且 τ_n 應該同 γ_n 有關

# 假設: τ_n = 1 - γ_n/γ_max + δ_n
# 其中 δ_n 係修正使得 Σ γ_n·δ_n = 6.5
# (因為 1 - γ_n/4 給出 22, 需要額外 6.5)

# 或者: τ_n = (2 + B·L) / (44 × γ_n)?
# Σ γ_n × (2+B·L)/(44×γ_n) = 44 × (2+B·L)/44 = 28.5
# 但 τ_n = 28.5/(44×γ_n) = 0.6477/γ_n
# 對於 γ_1 = 0.0051: τ_1 = 127.1 > 1! 唔合理

# 最簡單: τ_n = 1 for n ≤ k_cut, 0 for n > k_cut
# k_cut = 27 (Σγ_{1..27} = 29.12 > 28.5)
# 但 Σγ_{1..26} = 26.42 < 28.5
# 所以 k_cut = 27, 但最後一個要 partial
remainder = 28.5 - 26.4165
tau_27 = remainder / gamma[26]
print(f"\n  兩段式 τ_n:")
print(f"  τ_n = 1 for n ≤ 26, τ_27 = {tau_27:.6f}, τ_n = 0 for n > 27")
print(f"  Σ γ_n·τ_n = 26.4165 + {tau_27:.6f} × {gamma[26]:.6f} = {26.4165 + tau_27 * gamma[26]:.4f}")

# 累積 D_app
D_two_stage = np.zeros(N_d)
cum = 0
for n in range(N_d):
    if n < 26:
        tau = 1.0
    elif n == 26:
        tau = tau_27
    else:
        tau = 0.0
    cum += a * tau * gamma[n]
    D_two_stage[n] = cum

print(f"  D_app(ℓ(26)) = {D_two_stage[25]:.4f} Mpc")
print(f"  D_app(ℓ(27)) = {D_two_stage[26]:.4f} Mpc")
print(f"  D_app(ℓ(44)) = {D_two_stage[43]:.4f} Mpc")
print(f"  → 總和 = {D_two_stage[43]:.4f} Mpc (目標 R_H={R_H})")

# ═══════════════════════════════════════════════════════════════
# 4. 完整 D_app(ℓ) 函數: 連續形式
# ═══════════════════════════════════════════════════════════════
print(f"\n─── 4. 完整 D_app(ℓ) 函數 ───")

# 從 ΛCDM 類比: D_app(ℓ) = R_H · (1 - (1 + ℓ/ℓ_max)^(-Ω_m/Ω_Λ))?
# 或: D_app(ℓ) = R_H · (1 - exp(-ℓ/ℓ_max · Ω_m/Ω_Λ))?
# 或: D_app(ℓ) = R_H · ℓ/(ℓ + ℓ_0)?

# 用 ΛCDM D_A(z) 嘅形式
# D_A(z) = c/(1+z) ∫₀ᶻ dz'/H(z')
# 對於大 z: D_A(z) ≈ c/H₀ × (1/z) × const
# 對於小 z: D_A(z) ≈ c/H₀ × z

# 如果 ℓ = z (簡單映射):
# D_app(ℓ) = c/H₀ × ℓ  for ℓ << 1
# D_app(ℓ) → R_H for ℓ → ∞

# 最簡單匹配: D_app(ℓ) = R_H × ℓ / (ℓ + ℓ_0)
# D_app(ℓ_max) = R_H × ℓ_max / (ℓ_max + ℓ_0) = ?
# 但 D_app(ℓ_max) 係 6.3183 (T_pipe), 唔係 Mpc

# 直接用 Mpc: D_app_Mpc(ℓ_max) ≈ R_H = 4129.94
# D_app_Mpc(ℓ) = R_H × ℓ / (ℓ + ℓ_0)
# D_app_Mpc(ℓ_max) = R_H × ℓ_max / (ℓ_max + ℓ_0) = R_H
# → ℓ_max / (ℓ_max + ℓ_0) = 1 → ℓ_0 = 0
# 不合理

# D_app_Mpc(ℓ) = R_H × (1 - exp(-ℓ/ℓ_0))
# D_app(ℓ_max) = R_H × (1 - exp(-ℓ_max/ℓ_0)) = R_H
# → exp(-ℓ_max/ℓ_0) = 0 → ℓ_0 = 0
# 又唔合理

# 所以 D_app_Mpc(ℓ_max) ≠ R_H!
# D_app_Mpc(ℓ_max) = 6.3183 × SF = 4129.81 ≈ R_H
# 所以 D_app_Mpc(ℓ) 喺 ℓ_max 已經接近 R_H

# 換句話說: ℓ_max 係飽和點, ℓ > ℓ_max 時 D_app 維持 ≈ R_H
# 對於 ℓ < ℓ_max: D_app 由 0 增長到 R_H

# 最簡單: D_app(ℓ) = R_H × (ℓ/ℓ_max)^α
# 用 ℓ 小嘅行為: D_app(ℓ) ≈ R_H × (ℓ/ℓ_max)  (線性)
# 用 ℓ=ℓ_max: D_app = R_H

# 檢查: D_app(0) = 0 ✓
# D_app(ℓ_max) = R_H ✓
# 但係咪連續可微?

# 其實, 如果 D_app(ℓ) = R_H × (ℓ/ℓ_max) 線性, 噉:
# D_app(ℓ) = 4129.94 × ℓ/14.7085 = 280.7 × ℓ Mpc
# D_app(1) = 280.7 Mpc
# 呢個同 ΛCDM D_A(z) 比較: D_A(z=1) = ?

def D_A_LCDM_inv(D_target):
    """Inverse D_A(z) — 搵 z 令 D_A(z) ≈ D_target"""
    lo, hi = 0.0, 10000.0
    for _ in range(50):
        mid = (lo + hi) / 2
        if D_A_LCDM(mid) > D_target:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2

D_A_1 = D_A_LCDM(1)
print(f"  D_A(z=1) = {D_A_1:.2f} Mpc (ΛCDM)")
print(f"  D_app(ℓ=1) = 280.7 Mpc (線性模型)")
print(f"  ℓ=1 對應 z ≈ {D_A_LCDM_inv(280.7):.2f}")

z_at_l1 = D_A_LCDM_inv(280.7)
print(f"  z(ℓ=1) ≈ {z_at_l1:.2f}")
print(f"  ℓ ↔ z 映射: ℓ=1 ↔ z≈{z_at_l1:.2f}")

# 搵 ℓ=14.7085 對應嘅 z
z_at_lmax = D_A_LCDM_inv(R_H * 0.99)  # 接近 R_H
print(f"  z(ℓ=ℓ_max) ≈ ∞ (D_A→R_H 需要 z→∞)")

# 最簡單嘅 ℓ ↔ z 映射: z(ℓ) = ℓ / (ℓ_max - ℓ) × z_0
# 其中 z_0 係某個常數
# 用 ℓ=1, z=0.3 校準: z_0 = 0.3 × (14.7085-1)/1 = 4.11
z0 = z_at_l1 * (l_max - 1) / 1
print(f"\n  z(ℓ) = ℓ/(ℓ_max - ℓ) × z_0")
print(f"  用 ℓ=1, z={z_at_l1:.2f} 校準: z_0 = {z0:.4f}")

# 檢查: z(ℓ) = ℓ/(ℓ_max - ℓ) × z_0 嘅結構
# z_0 = 4.11 ≈ ?
print(f"  z_0 = {z0:.4f}")
print(f"  z_0 / Ω_m = {z0 / Omega_m:.4f}")
print(f"  z_0 / Ω_Λ = {z0 / Omega_L:.4f}")
print(f"  z_0 × φ⁻¹ = {z0 * phi_inv:.4f}")
print(f"  z_0 × ε = {z0 * eps:.4f}")
print(f"  z_0 / (B·L) = {z0 / (B * L_ktree):.4f}")

# ═══════════════════════════════════════════════════════════════
# 5. 結構推導: D_app(ℓ) = R_H · (1 - exp(-ℓ/ℓ_0))?
# ═══════════════════════════════════════════════════════════════
print(f"\n─── 5. D_app(ℓ) 結構候選 ───")

# 從 ΛCDM 類比, D_A(z) 嘅形式對於小 z 係線性, 大 z 飽和
# 最簡單嘅 IDCM 形式: D_app(ℓ) = R_H · (1 - exp(-ℓ/ℓ_0))
# 
# 但 ℓ_0 需要使 D_app(ℓ_max) ≈ R_H
# 即 ℓ_max >> ℓ_0
# ℓ_0 = ℓ_max / 5 = 2.94? 噉 D_app(ℓ_max) = R_H(1-e^{-5}) = 0.993R_H

# 更自然: D_app(ℓ) = R_H · (1 - (1 + ℓ/ℓ_0)^{-α})
# 其中 α = Ω_m/Ω_Λ = 3ε ≈ 0.464

alpha = Omega_m / Omega_L
print(f"  α = Ω_m/Ω_Λ = 3ε = {alpha:.6f}")

# 對於 D_app(ℓ) = R_H · (1 - (1 + ℓ/ℓ_0)^{-α})
# 需要 D_app(ℓ_max) ≈ R_H → (1 + ℓ_max/ℓ_0)^{-α} ≈ 0 → ℓ_max >> ℓ_0
# D_app(ℓ) ≈ R_H · α · ℓ/ℓ_0 for ℓ << ℓ_0

# 改用: D_app(ℓ) = R_H · (1 - exp(-α · ℓ/ℓ_0))
# ℓ_0 係特徵尺度

# 或者 D_app(ℓ) = D_A(z(ℓ)) 直接用 ΛCDM
# 其中 z(ℓ) = ℓ / (ℓ_max - ℓ) × z_0

print(f"\n  候選 A: D_app(ℓ) = D_A(z(ℓ)), z(ℓ) = ℓ/(ℓ_max-ℓ) × z_0")
print(f"  z_0 = {z0:.4f} (由 ℓ=1, z={z_at_l1:.2f} 校準)")
print(f"  但 z_0 嘅結構來源未明 🔴")

# 候選 B: D_app(ℓ) = R_H · (ℓ/ℓ_max)^α 其中 α = Ω_m/Ω_Λ?
print(f"\n  候選 B: D_app(ℓ) = R_H · (ℓ/ℓ_max)^(Ω_m/Ω_Λ)")
print(f"  D_app(1) = {R_H * (1/l_max)**alpha:.2f} Mpc")
print(f"  (ΛCDM D_A(z=1) = {D_A_1:.2f} Mpc)")

# 候選 C: D_app(ℓ) = R_H · (ℓ/ℓ_max) / (1 + (ℓ/ℓ_max) × (1-Ω_m))
print(f"\n  候選 C: D_app(ℓ) = R_H · (ℓ/ℓ_max) / (1 + (1-Ω_Λ)·(ℓ/ℓ_max))")
print(f"  = R_H · (ℓ/ℓ_max) / (1 + Ω_m·(ℓ/ℓ_max))")
print(f"  D_app(ℓ_max) = {R_H / (1 + Omega_m):.2f} Mpc (目標 R_H = {R_H})")
print(f"  → 唔飽和到 R_H ❌")

# 候選 D: D_app(ℓ) = R_H · (1 - (1 + ℓ/ℓ_max * Ω_m/Ω_Λ)^{-1})
# 其中 ℓ_max 係飽和點
# D_app(ℓ_max) = R_H · (1 - (1 + Ω_m/Ω_Λ)^{-1})
# = R_H · (1 - (1 + 3ε)^{-1})
# = R_H · (1 - 1/(1+3ε))
# = R_H · 3ε/(1+3ε) = R_H · Ω_m = 1308 Mpc
# 唔夠! ❌

print(f"\n  候選 D: D_app(ℓ) = R_H · (1 - (1 + ℓ/ℓ_0·Ω_m/Ω_Λ)^{-1})")
print(f"  D_app(ℓ_max) at ℓ_0=ℓ_max: = R_H · Ω_m = {R_H * Omega_m:.2f} Mpc ❌")

# 候選 E: 直接用 ℓ_max 決定飽和
# D_app(ℓ) = R_H · (1 - exp(-ℓ/ℓ_0))
# ℓ_0 = ℓ_max / ln(R_H/(R_H - D_app(ℓ_max)))
# D_app(ℓ_max) = 6.3183 × 653.65 = 4129.81
# ℓ_0 = l_max / ln(R_H/(R_H - 4129.81))
# = 14.7085 / ln(4129.94/0.13) = 14.7085 / 10.36 = 1.42
l0 = l_max / np.log(R_H / (R_H - 4129.81))
print(f"\n  候選 E: D_app(ℓ) = R_H · (1 - exp(-ℓ/ℓ_0))")
print(f"  ℓ_0 = ℓ_max / ln(R_H/(R_H - D_app(ℓ_max)))")
print(f"  = {l_max} / ln({R_H}/{R_H - 4129.81:.2f})")
print(f"  = {l0:.4f}")
print(f"  ℓ_0 結構: ℓ_0 × φ = {l0 * phi:.4f}")
print(f"  ℓ_0 / ε = {l0 / eps:.4f}")
print(f"  ℓ_0 = N_d / {N_d / l0:.2f}")

# 如果 ℓ_0 = B? 4? ℓ_0/N_gen = 4/3 = 1.33
print(f"  ℓ_0 / B = {l0 / B:.4f}")
print(f"  ℓ_0 / (B·L) = {l0 / (B * L_ktree):.4f}")
print(f"  ℓ_0 = 4L/26.5? = {4*l0/26.5:.4f}")

# ℓ_0 嘅結構: ℓ_0 = 44/31 = 1.419? 31 = ? 31 = 29+2 = L₇+2
print(f"  N_d / {N_d / l0:.4f} = 44 / 31.0? 44/31 = {44/31:.4f}")
print(f"  ℓ_0 = 44/31.0 = {44/31:.4f}")
print(f"  31 = L₇ + 2 = 29 + 2 = 31 (Lucas 7 + 2)")
print(f"  31 = N_d - 13? 44 - 13 = 31 (F₇ = 13)")

# 儲存
with open("data/o47_dapp_lcdm_analogy.txt", "w") as f:
    f.write("O47-D3 — D_app(ℓ) LCDM Analogy\n")
    f.write("=" * 67 + "\n")
    f.write(f"H0 = {H0:.4f}, Omega_L = {Omega_L:.6f}, Omega_m = {Omega_m:.6f}\n")
    f.write(f"DA(z=1) = {D_A_LCDM(1):.2f}, DA(z=1100) = {D_A_LCDM(1100):.2f}\n")
    f.write(f"DA(inf) = {D_A_inf:.2f}\n")
    f.write(f"z0 (from l=1 cal) = {z0:.4f}\n")
    f.write(f"l0 (exponential) = {l0:.4f}\n")
    f.write(f"Status: 🟡 Exploration complete\n")