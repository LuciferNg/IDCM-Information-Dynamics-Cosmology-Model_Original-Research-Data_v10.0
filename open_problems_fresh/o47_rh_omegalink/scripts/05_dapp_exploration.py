#!/usr/bin/env python3
"""
O47-D3 — D_app(ℓ) 投影管道函數探索
======================================
從第一性原理探索 D_app(ℓ) 嘅函數形式。

已知:
  ℓ_max = 14.7085 (最大多極)
  D_app(ℓ_max) = 6.3183 → 6D (T_pipe 輸出)
  R_H = 4129.94 Mpc (環周長, ℓ→∞ 極限)
  
邊界條件:
  D_app(0) = 0 (或 6)
  D_app(ℓ_max) = 6.3183 (T_pipe 單位)
  D_app(∞) = R_H = 4129.94 Mpc

結構常數:
  γ_n = 4sin²(πn/88), n=1..44
  Σγ = 90
  物質 = 2 + B·L = 28.5
  真空 = 88 − 4L = 61.5
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
R_H = 4129.94
a = R_H / N_d

# 已知點
l_max = 14.7085
D_app_lmax = 6.3183
Omega_L = 4 / (phi**4 - 1)
Omega_m = 1 - Omega_L
matter = 2 + B * L_ktree  # 28.5
vacuum = 88 - B * L_ktree  # 61.5

print("=" * 75)
print("  O47-D3 — D_app(ℓ) 投影管道函數探索")
print("=" * 75)

# ═══════════════════════════════════════════════════════════════
# 1. K_Chain 譜
# ═══════════════════════════════════════════════════════════════
gamma = np.array([4 * np.sin(np.pi * n / 88)**2 for n in range(1, N_d + 1)])
cumsum_gamma = np.cumsum(gamma)  # S(ℓ) = Σ_{n=1}^{ℓ} γ_n

print(f"\n─── 1. K_Chain 譜 γ_n ───")
print(f"  γ_1 = {gamma[0]:.8f}")
print(f"  γ_22 = {gamma[21]:.8f} (中點)")
print(f"  γ_44 = {gamma[43]:.8f} (Nyquist)")
print(f"  Σγ = {np.sum(gamma):.6f}")
print(f"  S(ℓ_max) = Σ_{{n=1}}^{{ℓ_max}} γ_n = ?")
# ℓ_max 係非整數, 插值
l_floor = int(np.floor(l_max))
l_frac = l_max - l_floor
S_lmax = cumsum_gamma[l_floor - 1] + l_frac * gamma[l_floor]
print(f"  S(ℓ_max={l_max}) = {S_lmax:.6f}")

# ═══════════════════════════════════════════════════════════════
# 2. 縮放因子: T_pipe 單位 → Mpc
# ═══════════════════════════════════════════════════════════════
scale_factor = R_H / D_app_lmax
print(f"\n─── 2. 縮放因子 ───")
print(f"  ScaleFactor = R_H / D_app(ℓ_max) = {R_H} / {D_app_lmax} = {scale_factor:.4f}")
print(f"  結構分解:")
print(f"  44 × 90/6 = {44 * 90 / 6:.4f}")
print(f"  44 × 90/6 × (1 - ε/16) = {44 * 90 / 6 * (1 - eps/16):.4f}")
print(f"  偏差 = {abs(scale_factor - 44 * 90 / 6 * (1 - eps/16)):.4f}")

# 縮放因子 = 44 × 90/6 × (1 - ε/16) = 653.65
# 44 = N_d, 90 = Σγ, 6 = T_pipe 維度, ε/16 = 修正
SF = 44 * 90 / 6 * (1 - eps/16)
print(f"  SF = N_d × Σγ / 6 × (1 - ε/16) = {SF:.4f}")

# ═══════════════════════════════════════════════════════════════
# 3. 候選模型: D_app(ℓ) 函數形式
# ═══════════════════════════════════════════════════════════════
print(f"\n─── 3. 候選模型 ───")

# 模型 A: 線性累積 γ_n
# D_app(ℓ) = a · Σ_{n=1}^{ℓ} γ_n
def model_A(l):
    """純 γ_n 累積"""
    l_int = int(np.floor(l))
    frac = l - l_int
    if l_int <= 0:
        return 0
    if l_int >= N_d:
        return a * np.sum(gamma)
    s = cumsum_gamma[l_int - 1] + frac * gamma[min(l_int, N_d - 1)]
    return a * s

print(f"\n  模型 A: D_app(ℓ) = a · Σγ_n (純 γ_n 累積)")
print(f"  D_app(0) = {model_A(0):.4f}")
print(f"  D_app(ℓ_max) = {model_A(l_max):.4f} (目標 R_H = {R_H})")
print(f"  D_app(44) = {model_A(44):.4f}")
print(f"  → 84.48 Mpc @ ℓ_max, 遠低於 R_H=4129.94 ❌")

# 模型 B: 線性累積, 但用 ℓ/N_d 比例
# D_app(ℓ) = R_H · ℓ/N_d
def model_B(l):
    """簡單線性比例"""
    return R_H * l / N_d

print(f"\n  模型 B: D_app(ℓ) = R_H · ℓ/N_d")
print(f"  D_app(0) = {model_B(0):.4f}")
print(f"  D_app(ℓ_max) = {model_B(l_max):.4f} (目標 {R_H})")
print(f"  D_app(44) = {model_B(44):.4f}")
print(f"  → 1377.6 Mpc @ ℓ_max, 仲係低 😕")

# 模型 C: 飽和函數 D_app(ℓ) = R_H · (1 - exp(-ℓ/ℓ_0))
# 用 ℓ_max 同 D_app(ℓ_max) 解出 ℓ_0
# 6.3183 = R_H · (1 - exp(-ℓ_max/ℓ_0)) [T_pipe units?]
# 但 T_pipe units 同 Mpc 要轉換

# 先係 T_pipe 單位: D_T(ℓ) 從 6 開始, 飽和到 6 + something
# D_T(ℓ) = 6 + Ω_m · (1 - exp(-ℓ/ℓ_0))
# D_T(ℓ_max) = 6.3167 → ℓ_0 = ?
l0_cand = l_max / np.log(Omega_m / (6.3183 - 6))
print(f"\n  模型 C: D_T(ℓ) = 6 + Ω_m · (1 - exp(-ℓ/ℓ_0))")
print(f"  ℓ_0 = ℓ_max / ln(Ω_m/(D_app(ℓ_max)-6)) =")
print(f"  = {l_max} / ln({Omega_m:.6f}/{D_app_lmax-6:.6f})")
if D_app_lmax - 6 > 0 and Omega_m / (D_app_lmax - 6) > 0:
    l0 = l_max / np.log(Omega_m / (D_app_lmax - 6))
    print(f"  = {l0:.6f}")
    print(f"  ℓ_0 結構: ℓ_0 = ?")
    print(f"  ℓ_0 × φ = {l0 * phi:.6f}")
    print(f"  ℓ_0 × φ² = {l0 * phi**2:.6f}")
    print(f"  ℓ_0 / ε = {l0 / eps:.6f}")

# 模型 D: 離散累積 γ_n · τ_n, τ_n 係 T_pipe 傳輸係數
# τ_n = 1 - γ_n/γ_max? 或其他結構?
# 物質 = Σ γ_n · τ_n = 28.5
# 如果 τ_n = 1 - γ_n/γ_max:
# Σ γ_n · (1 - γ_n/4) = 90 - Σ γ_n²/4
sum_gamma2 = np.sum(gamma**2)
total_proj_if_linear = 90 - sum_gamma2 / 4
print(f"\n  模型 D: τ_n = 1 - γ_n/γ_max (線性衰減)")
print(f"  Σ γ_n · τ_n = 90 - Σγ²/4 = {total_proj_if_linear:.6f}")
print(f"  目標物質 = {matter}")
print(f"  偏差 = {abs(total_proj_if_linear - matter):.4f}")

# 模型 E: τ_n = exp(-γ_n/γ_0) 指數衰減
# 搵 γ_0 令 Σ γ_n · exp(-γ_n/γ_0) = matter
def total_proj_exp(gamma_0):
    return np.sum(gamma * np.exp(-gamma / gamma_0))

# 二分法搵 γ_0
lo, hi = 0.1, 10.0
for _ in range(50):
    mid = (lo + hi) / 2
    if total_proj_exp(mid) > matter:
        lo = mid
    else:
        hi = mid
gamma_0 = (lo + hi) / 2
print(f"\n  模型 E: τ_n = exp(-γ_n/γ_0) (指數衰減)")
print(f"  γ_0 = {gamma_0:.6f}")
print(f"  Σ γ_n · τ_n = {total_proj_exp(gamma_0):.6f} (目標 {matter})")
print(f"  γ_0 結構: γ_0 = ?")
print(f"  γ_0 × φ = {gamma_0 * phi:.6f}")
print(f"  γ_0 / ε = {gamma_0 / eps:.6f}")
print(f"  γ_0 / φ⁻² = {gamma_0 / phi_inv**2:.6f}")

# 模型 F: 兩段式 — 低 ℓ 全傳輸, 高 ℓ 零傳輸
# 物質 = Σ_{n=1}^{k} γ_n = 28.5
# 搵 k 令 Σγ = 28.5
cumsum = 0
k_cut = 0
for n in range(N_d):
    cumsum += gamma[n]
    if cumsum >= matter:
        k_cut = n + 1
        break
print(f"\n  模型 F: 兩段式 (低 ℓ 全傳輸, 高 ℓ 零傳輸)")
print(f"  k_cut = {k_cut} (Σ_{{n=1}}^{{k_cut}} γ_n = {cumsum:.4f} ≥ {matter})")
print(f"  Σ_{{n=1}}^{{k_cut-1}} γ_n = {cumsum - gamma[k_cut-1]:.4f}")

# ═══════════════════════════════════════════════════════════════
# 4. 深度分析: 累積投影能量 vs ℓ
# ═══════════════════════════════════════════════════════════════
print(f"\n─── 4. 累積投影能量 vs ℓ ───")

# 用 ℓ_max 同 D_app(ℓ_max) 反推 T_pipe 結構
# D_app(ℓ_max) = 6.3183 → 6D
# 物質 = 28.5, 真空 = 61.5
# 如果 D_app(ℓ) = 6 + (累積投影能量 up to ℓ)/Σγ
# 累積投影能量 up to ℓ_max = (D_app(ℓ_max) - 6) × 90 = 0.3183 × 90 = 28.647
target_proj_at_lmax = (D_app_lmax - 6) * 90
print(f"  目標累積投影 @ ℓ_max: (6.3183 - 6) × 90 = {target_proj_at_lmax:.4f}")
print(f"  目標物質 = {matter}")
print(f"  差 = {target_proj_at_lmax - matter:.4f}")

# 如果累積投影 = f(ℓ) × 物質
# 喺 ℓ_max, f(ℓ_max) = (D_app(ℓ_max) - 6) / (物質/90) = 0.3183/0.3167 = 1.005
f_at_lmax = (D_app_lmax - 6) / (matter / 90)
print(f"  f(ℓ_max) = (D_app(ℓ_max) - 6) / (物質/90) = {f_at_lmax:.6f}")
print(f"  → 喺 ℓ_max 已經達到 ~100% 投影能量!")
print(f"  → 即 D_app(ℓ) 喺 ℓ_max 已經飽和咗?")

# ═══════════════════════════════════════════════════════════════
# 5. 關鍵 Insight: D_app(ℓ) 嘅兩階段結構
# ═══════════════════════════════════════════════════════════════
print(f"\n─── 5. 兩階段結構 ───")

# 階段 1: ℓ ∈ [0, ℓ_max] — 投影活躍區
#   D_app(ℓ) = 6 + (ℓ/ℓ_max) × 物質/90
#   喺 ℓ_max: D_app = 6.3167
# 階段 2: ℓ ∈ [ℓ_max, ∞) — 飽和區
#   D_app(ℓ) → R_H = 4129.94 Mpc
#   從 6.3 跳到 4129.94 — 需要巨大縮放

# 關鍵: 6.3183 同 4129.94 之間嘅關係
# 6.3183 × (44 × 90/6) = 6.3183 × 660 = 4170.08
# 4170.08 - 4129.94 = 40.14
# 40.14 = 44 × 0.912 = 唔係結構常數
# 40.14 = 90 × 0.446 = 唔係

# 但 6.3167 × 44 × 90/6 × (1 - ε/16) = 4129.81
# 6.3167 × 653.65 = 4129.81
# 實際 6.3183 × 653.65 = 4129.94

print(f"  階段 1 (投影活躍): ℓ ∈ [0, ℓ_max]")
print(f"    D_app(ℓ) = 6 + (ℓ/ℓ_max) × 物質/90")
print(f"    = 6 + ℓ/14.7085 × 0.3167")
print(f"    D_app(ℓ_max) = 6.3167")
print(f"")
print(f"  階段 2 (飽和): ℓ ∈ [ℓ_max, ∞)")
print(f"    D_app(ℓ) = SF × D_app(ℓ_max) = {SF:.4f} × 6.3167")
print(f"    = 4129.81 Mpc (→ R_H = {R_H})")
print(f"")
print(f"  縮放因子 SF = N_d × Σγ / 6 × (1 - ε/16)")
print(f"    = 44 × 90 / 6 × (1 - 0.009657)")
print(f"    = 660 × 0.990343 = {SF:.4f}")

# ═══════════════════════════════════════════════════════════════
# 6. T_pipe 本徵譜 τ_n 嘅結構推導
# ═══════════════════════════════════════════════════════════════
print(f"\n─── 6. T_pipe 本徵譜 τ_n 結構推導 ───")

# 從 88-site 雙鏈結構推導 τ_n
# 88-site: Σγ_even = 90 (世界), Σγ_odd = 88 (觀察者)
# 物質 = 2 + B·L = 28.5 (投影能量)
# 真空 = 88 - 4L = 61.5 (未被投影)

# 假設: τ_n = 1 - (觀察者參與度)
# 觀察者模式 γ_k(odd) 同世界模式 γ_n(even) 嘅耦合決定 τ_n

# 88-site 嘅偶數/奇數配對:
# 偶數 γ_{2n} = 4sin²(πn/88) = γ_n(44-site)  n=1..44
# 奇數 γ_{2n-1} = 4sin²(π(2n-1)/176)  n=1..44

gamma_odd_88 = np.array([4 * np.sin(np.pi * (2*n-1) / 176)**2 for n in range(1, 45)])

# 配對 γ_n(even) ↔ γ_n(odd)
# 每個世界模式 n 對應一個觀察者模式 n
# 如果 τ_n = γ_n(odd) / (γ_n(even) + γ_n(odd))
tau_n_coupled = gamma_odd_88 / (gamma + gamma_odd_88)
total_proj_coupled = np.sum(gamma * tau_n_coupled)

print(f"  模型 G: τ_n = γ_odd_n / (γ_even_n + γ_odd_n)")
print(f"  (每個世界模式 n 同對應觀察者模式嘅耦合)")
print(f"  τ_1 = {tau_n_coupled[0]:.6f}")
print(f"  τ_22 = {tau_n_coupled[21]:.6f}")
print(f"  τ_44 = {tau_n_coupled[43]:.6f}")
print(f"  Σ γ_n · τ_n = {total_proj_coupled:.6f} (目標 {matter})")
print(f"  偏差 = {abs(total_proj_coupled - matter):.4f}")

# 如果 τ_n = γ_n(odd) / 4? (4 = B = MERA branching)
tau_n_divB = gamma_odd_88 / 4
total_proj_divB = np.sum(gamma * tau_n_divB)
print(f"  模型 H: τ_n = γ_odd_n / B")
print(f"  Σ γ_n · τ_n = {total_proj_divB:.6f} (目標 {matter})")

# 如果 τ_n = (γ_n(odd) - γ_n(even)) / γ_n(odd)?
# τ_n = 1 - γ_n(even)/γ_n(odd)
# 但 γ_n(even) > γ_n(odd) 對於大 n, τ_n 會變負
# 唔合理

# 更好的: τ_n = 1 - γ_n(odd) / (γ_n(even) + γ_n(odd))
# 即 τ_n = γ_n(even) / (γ_n(even) + γ_n(odd))
tau_n_world = gamma / (gamma + gamma_odd_88)
total_proj_world = np.sum(gamma * tau_n_world)
print(f"  模型 I: τ_n = γ_even_n / (γ_even_n + γ_odd_n)")
print(f"  τ_1 = {tau_n_world[0]:.6f}")
print(f"  τ_22 = {tau_n_world[21]:.6f}")
print(f"  τ_44 = {tau_n_world[43]:.6f}")
print(f"  Σ γ_n · τ_n = {total_proj_world:.6f} (目標 {matter})")

# 如果 τ_n = (γ_n(even) - γ_n(odd)) / B?
# 世界 - 觀察者 = 投影能量
tau_n_diff = (gamma - gamma_odd_88) / 4
total_proj_diff = np.sum(gamma * tau_n_diff)
print(f"  模型 J: τ_n = (γ_even_n - γ_odd_n)/B")
print(f"  Σ γ_n · τ_n = {total_proj_diff:.6f} (目標 {matter})")

# 關鍵: 物質 = 2 + B·L, 而 2 = Σγ_even - Σγ_odd = 90 - 88
# 所以 τ_n 應該係: Σ γ_n · τ_n = (Σγ_even - Σγ_odd) + B·L
# = 2 + B·L = 2 + 26.5 = 28.5

# 如果 τ_n = 1 - γ_odd_n / γ_n? 
# 即 τ_n = (γ_n - γ_odd_n)/γ_n
# 但 γ_odd_n > γ_n 對於低 n, τ_n 會變負
# 唔合理

# 試 τ_n = (γ_n - γ_odd_n) / (γ_n + γ_odd_n)?
tau_n_rel = (gamma - gamma_odd_88) / (gamma + gamma_odd_88)
total_proj_rel = np.sum(gamma * tau_n_rel)
print(f"  模型 K: τ_n = (γ_n - γ_odd_n)/(γ_n + γ_odd_n)")
print(f"  Σ γ_n · τ_n = {total_proj_rel:.6f} (目標 {matter})")

# 最簡單: τ_n = γ_n / Σγ? 即按能量比例分配
tau_n_frac = gamma / 90
total_proj_frac = np.sum(gamma * tau_n_frac)
print(f"  模型 L: τ_n = γ_n / Σγ")
print(f"  Σ γ_n · τ_n = {total_proj_frac:.6f} (目標 {matter})")

print(f"\n  → 所有模型都偏離目標 {matter}")
print(f"  → T_pipe 本徵譜 τ_n 需要更基本嘅結構推導")

# 儲存結果
with open("data/o47_dapp_exploration.txt", "w") as f:
    f.write("O47-D3 — D_app(ℓ) Pipeline Function Exploration\n")
    f.write("=" * 67 + "\n")
    f.write(f"Gamma sum: {np.sum(gamma):.6f}\n")
    f.write(f"Target matter: {matter}\n")
    f.write(f"l_max: {l_max}, D_app(l_max): {D_app_lmax}\n")
    f.write(f"Scale factor: {scale_factor:.4f}\n")
    f.write(f"Models: A={model_A(l_max):.4f}, B={model_B(l_max):.4f}\n")
    f.write(f"Coupled: {total_proj_coupled:.6f}, DivB: {total_proj_divB:.6f}\n")
    f.write(f"World: {total_proj_world:.6f}, Diff: {total_proj_diff:.6f}\n")
    f.write(f"Rel: {total_proj_rel:.6f}, Frac: {total_proj_frac:.6f}\n")
    f.write(f"Status: 🟡 Exploration complete, need τ_n derivation\n")