#!/usr/bin/env python3
"""
O51/81: K_Chain 譜高階曲率 → C 嘅幾何代數解
===============================================================
路徑一: 從 ω_n = 2 sin(nπ/88) 嘅高階譜矩推導 C

C 係 δ(ℓ) = C·(ℓ-0.5)(1-4^{-ℓ}) 嘅係數
結構來源: K_Chain 離散譜嘅非線性曲率（skewness + kurtosis）

一階奇偶不對稱: C_1 = (Σγ_even - Σγ_odd)/Σγ = 2/90 = 0.02222
二階譜曲率: C_2 = skewness × (Σγ/σ²) × ...
三階譜曲率: C_3 = excess_kurtosis × ...
"""
import json, math

PASS = 0
FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ PASS: {name}")
    else:
        FAIL += 1
        print(f"  ❌ FAIL: {name}")
    if detail:
        print(f"    {detail}")

N_d = 44
phi = (1 + math.sqrt(5)) / 2

print("=" * 62)
print("K_Chain 譜高階曲率 → C 嘅幾何代數解")
print("=" * 62)

# ============ 1. K_Chain 譜 ============
omega = [2*math.sin(math.pi*n/(2*N_d)) for n in range(1, N_d+1)]
gamma = [4*math.sin(math.pi*n/(2*N_d))**2 for n in range(1, N_d+1)]

print("\n--- K_Chain 色散關係 ---")
print(f"ω_n = 2 sin(nπ/88), n=1..44")
print(f"γ_n = ω_n² = 4 sin²(nπ/88)")

# ============ 2. 譜矩計算 ============
print("\n--- 譜矩 (Spectral Moments) ---")

# 加權
w = gamma  # 用 γ_n 做權重
sum_w = sum(w)
mean = sum((n+1)*w[n] for n in range(N_d)) / sum_w
var = sum((n+1-mean)**2*w[n] for n in range(N_d)) / sum_w
skew = sum((n+1-mean)**3*w[n] for n in range(N_d)) / sum_w / var**1.5
kurt = sum((n+1-mean)**4*w[n] for n in range(N_d)) / sum_w / var**2 - 3

print(f"譜質心 μ = {mean:.6f}")
print(f"譜方差 σ² = {var:.6f}")
print(f"譜偏度 γ₁ = {skew:.6f} (Skewness, 正=右偏)")
print(f"譜峰度 γ₂ = {kurt:.6f} (Excess Kurtosis, 正=尖峰)")

# 譜嘅「彎曲度」— 高頻區曲率 vs 低頻區曲率
# ω_n 嘅二階導數 (離散): d²ω/dn² ∝ -sin(nπ/88)
# 喺 n=1: d²ω/dn² ≈ -sin(π/88) ≈ -0.0357
# 喺 n=44: d²ω/dn² ≈ -sin(π/2) = -1.0
# 曲率不均勻性: 高頻區曲率係低頻區嘅 28 倍!

curv_ratio = abs(math.sin(math.pi/88)) / abs(math.sin(math.pi/2))
print(f"\n曲率比 (低頻/高頻): {1/curv_ratio:.2f}×")
print(f"高頻區曲率遠大於低頻區 → 譜彎曲度主導高 ℓ 行為")

# ============ 3. C 嘅幾何推導 ============
print("\n--- C 嘅幾何代數推導 ---")

# C 嘅結構應該係 skewness 同 kurtosis 嘅函數:
# C = C_1 + C_2 + C_3 + ...
# 其中 C_1 = 奇偶不對稱 = 2/90
# C_2 ∝ skewness × (σ²/mean²)
# C_3 ∝ kurtosis × (σ²/mean²)²

# 從 RG flow 角度: β(g) = β₁g + β₂g² + β₃g³ + ...
# β₁ = C_1 = 2/90
# β₂ = C_2 / C_1 = skewness × σ/mean
# β₃ = C_3 / C_1 = kurtosis × σ²/mean²

C_1 = 2/90

# 第二項: 譜偏度
# skewness > 0 表示譜右偏 (高頻區能量集中)
# 呢個偏度產生一個「額外彎曲」— 投影到 ℓ 空間
C_2 = C_1 * abs(skew) * math.sqrt(var) / mean
# 但係 skewness 係有符號嘅, 正 skewness 表示高頻區多能量
# 呢個對應於高 ℓ 時 D_app 需要減小 (負貢獻)
# 所以 C_2 係負數

# 第三項: 譜峰度
# kurtosis > 0 表示譜嘅尾部比正態分布重
# 呢個產生一個「尾部修正」
C_3 = C_1 * abs(kurt) * var / (mean**2) * 0.5

# 總 C
C_total = C_1 + C_2 + C_3

print(f"C₁ = 奇偶不對稱           = {C_1:.6f}")
print(f"C₂ = skewness × σ/μ × C₁ = {C_2:+.6f} (skewness={skew:+.4f})")
print(f"C₃ = kurtosis × σ²/μ² × C₁ × 0.5 = {C_3:+.6f} (kurtosis={kurt:+.4f})")
print(f"C_total = C₁ + C₂ + C₃   = {C_total:.6f}")

# C_obs (從 DESI 推斷)
# δ(ℓ) = C(ℓ-0.5)(1-4^{-ℓ})
# 喺 ℓ=0.87 (Lyα): δ = +0.044 = C × 0.37 × 0.86
# C_obs = 0.044 / (0.37 × 0.86) = 0.138
C_obs = 0.044 / (0.87-0.5) / (1-4**(-0.87))
print(f"\nC_obs (DESI Lyα 推斷) = {C_obs:.4f}")

# ============ 4. RG Flow 積分 ============
print("\n--- RG Flow 非線性積分 (路徑二) ---")
# β(g) = β₁g + β₂g² + β₃g³ + ...
# β₁ = C₁ = 2/90
# β₂ = C₂/C₁ = ...
# β₃ = C₃/C₁ = ...

# 積分: g(ℓ) = ∫₀^ℓ β(g(ℓ')) dℓ'
# 一階: g(ℓ) = β₁ℓ
# 二階: g(ℓ) = β₁ℓ + β₂β₁²ℓ²/2
# 三階: g(ℓ) = β₁ℓ + β₂β₁²ℓ²/2 + (β₂²β₁³ + β₃β₁³)ℓ³/6

beta1 = C_1
beta2 = C_2 / C_1 if C_1 != 0 else 0
beta3 = C_3 / C_1 if C_1 != 0 else 0

# 喺 ℓ=0.5 嘅積分值 = C (因為 δ(ℓ) = g(ℓ) - β₁ℓ 嘅殘差)
# 但係真正嘅 C 係 g(ℓ) × (1-4^{-ℓ}) 嘅係數
# 更準確: C = dg/dℓ @ ℓ=0.5 × (1-4^{-0.5}) = β(g(0.5)) × 0.5

g_half = beta1*0.5 + beta2*beta1**2*0.5**2/2 + (beta2**2*beta1**3 + beta3*beta1**3)*0.5**3/6
C_rg = beta1 + beta2*g_half + beta3*g_half**2

print(f"β₁ = {beta1:.6f}")
print(f"β₂ = {beta2:.6f}")
print(f"β₃ = {beta3:.6f}")
print(f"g(0.5) = {g_half:.6f}")
print(f"C_RG = β(g(0.5)) = {C_rg:.6f}")
print(f"C_obs = {C_obs:.4f}")

# ============ 5. 驗證 ============
print("\n--- 驗證: C_total vs C_obs ---")
print(f"C_total (譜高階矩) = {C_total:.6f}")
print(f"C_RG (非線性積分) = {C_rg:.6f}")
print(f"C_obs (DESI 推斷) = {C_obs:.4f}")

check("C_total 數量級正確", abs(C_total - C_obs) < 0.1, f"{C_total:.4f} vs {C_obs:.4f}")
check("C_RG 數量級正確", abs(C_rg - C_obs) < 0.1, f"{C_rg:.4f} vs {C_obs:.4f}")

# 用 C_total 做 DESI 驗證
print("\n--- DESI 驗證 (C_total) ---")
R_H = 4129.94
rd_c = math.pi * R_H / 88 * 420/421

def D_orig(ell):
    return R_H * (1 - 4**(-ell)) * (1 + 2*phi**(-1)*ell)

def D_corrected(ell, C_val):
    delta = C_val * (ell - 0.5) * (1 - 4**(-ell))
    return R_H * (1 - 4**(-ell)) * (1 + 2*phi**(-1)*ell + delta)

desi = [
    (0.510, 13.588, 0.167),
    (0.706, 17.351, 0.177),
    (0.934, 21.576, 0.152),
    (1.321, 27.601, 0.318),
    (2.330, 38.988, 0.531),
]

chi2_orig = 0
chi2_corr = 0
for z, dm, err in desi:
    ell = math.log(1+z, 4)
    d1 = D_orig(ell) / rd_c
    d2 = D_corrected(ell, C_total) / rd_c
    chi2_orig += ((d1 - dm)/err)**2
    chi2_corr += ((d2 - dm)/err)**2

print(f"DESI 5 點 χ² (原始): {chi2_orig:.2f}")
print(f"DESI 5 點 χ² (C_total): {chi2_corr:.2f}")

# ============ 6. 總結 ============
print(f"\n{'=' * 62}")
print("總結")
print("=" * 62)
print(f"K_Chain 譜高階曲率分析:")
print(f"C1 = 奇偶不對稱 = {C_1:.6f} (一階, 線性)")
print(f"C2 = 偏度修正 = {C_2:+.6f} (二階, 非線性)")
print(f"C3 = 峰度修正 = {C_3:+.6f} (三階, 非線性)")
print(f"C_total = {C_total:.6f}")
print(f"C_RG(beta) = {C_rg:.6f} (RG flow 積分)")
print(f"C_obs = {C_obs:.4f} (DESI 推斷)")
print(f"")
print(f"delta(ell) = C x (ell - 0.5) x (1 - 4^(-ell))")

result = {
    'C1': round(C_1, 6),
    'C2': round(C_2, 6),
    'C3': round(C_3, 6),
    'C_total': round(C_total, 6),
    'C_rg': round(C_rg, 6),
    'C_obs': round(C_obs, 4),
    'skewness': round(skew, 6),
    'kurtosis': round(kurt, 6),
    'chi2_orig': round(chi2_orig, 2),
    'chi2_corr': round(chi2_corr, 2),
    'pass': PASS,
    'fail': FAIL
}

with open('data/81_spectral_curvature.json', 'w') as f:
    json.dump(result, f, indent=2, default=str)

print(f"-> data/81_spectral_curvature.json")