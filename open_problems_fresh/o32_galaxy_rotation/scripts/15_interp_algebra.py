#!/usr/bin/env python3
"""
O32-15: RAR 插值函數嘅代數結構 — ν(ν-1) = a₀/g_bar
=====================================================
關鍵恆等式 (來自 simple interpolation):

g_obs = (g_bar/2)(1 + √(1 + 4a₀/g_bar))
設 ν ≡ g_obs/g_bar, 則:

  ν(ν-1) = a₀/g_bar    ← 核心代數恆等式!

證明: (2ν-1)² = 1+4a₀/g_bar → 4ν²-4ν = 4a₀/g_bar → ν(ν-1) = a₀/g_bar

呢個恆等式揭示插值函數嘅 K_Chain 結構:
1. ν 同 1-ν 都係解 (Z₂ 對偶, 類比 γ_n + γ_{44-n} = 4)
2. ν(ν-1) 係「雙曲」結構 — 同 γ_n = 4sin²(πn/88) 嘅倍角公式有聯繫:
   γ_{2n} = γ_n(4-γ_n) → 歸一化 u_n = γ_n/4: u_{2n} = 4u_n(1-u_n) (Logistic!)
3. 深 MOND 極限 (g_bar → 0): ν → √(a₀/g_bar), ν-1 ≈ ν → ν² ≈ a₀/g_bar ✅

目標: 證明 ν(ν-1) = a₀/g_bar 同 K_Chain 模式結構嘅同構
"""
import numpy as np
import json

# ============ K_Chain 常數 ============
Nd = 44
phi = (1 + np.sqrt(5)) / 2
gamma = np.array([4 * np.sin(np.pi * n / 88) ** 2 for n in range(1, Nd + 1)])
u = gamma / 4  # 歸一化到 [0, 1]

# ============ 1. 核心恆等式 ============
print("=" * 65)
print("1. ν(ν-1) = a₀/g_bar 恆等式")
print("=" * 65)

# 驗證: 對任意 g_bar/a₀, ν(ν-1)·(g_bar/a₀) = 1
for x in [1e-3, 1e-1, 1.0, 10.0, 1e3]:
    gbar = x  # 單位 a₀
    nu = (1 + np.sqrt(1 + 4 / x)) / 2
    lhs = nu * (nu - 1) * x
    print(f"g_bar/a₀ = {x:>8.3f}: ν = {nu:>8.4f}, ν(ν-1)·(g_bar/a₀) = {lhs:.10f} "
          f"{'✅' if abs(lhs-1) < 1e-9 else '❌'}")

print("\n核心恆等式: ν(ν-1) = a₀/g_bar ⟺ g_obs(g_obs - g_bar) = g_bar·a₀")
print("物理意義: 額外加速度 (g_obs - g_bar) × 總加速度 g_obs = 常數 × g_bar")
print("即: 額外加速度 ∝ 1/g_obs — W-field 修正隨加速度遞減!")

# ============ 2. 同 Logistic map 嘅聯繫 ============
print("\n" + "=" * 65)
print("2. K_Chain 模式歸一化 u_n = γ_n/4 嘅 Logistic 結構")
print("=" * 65)

# γ_{2n} = γ_n(4-γ_n) → u_{2n} = 4u_n(1-u_n) (Logistic map r=4!)
print("倍角公式: γ_{2n} = γ_n(4-γ_n)")
print("歸一化:   u_{2n} = 4u_n(1-u_n)  (Logistic map, r = 4 = B!)")
print()
print(f"{'n':>3} {'γ_n':>8} {'u_n':>8} {'γ_{2n}':>8} {'γ_n(4-γ_n)':>10} {'match':>6}")
for n in [1, 2, 3, 4, 5, 10, 11]:
    if 2 * n > Nd:
        continue
    g2n = gamma[2 * n - 1]
    gprod = gamma[n - 1] * (4 - gamma[n - 1])
    ok = abs(g2n - gprod) < 1e-12
    print(f"{n:>3} {gamma[n-1]:>8.5f} {u[n-1]:>8.5f} {g2n:>8.5f} {gprod:>10.5f} "
          f"{'✅' if ok else '❌'}")

print("\nB = 4 = φ³ - φ⁻³ 出現喺 Logistic 參數! K_Chain 模式自相似:")
print("u_{2n} = 4u_n(1-u_n) — 倍頻結構由 B=4 分支強迫")

# ============ 3. 插值函數嘅模式分解 ============
print("\n" + "=" * 65)
print("3. 插值函數 ν(x) 嘅級數展開 vs K_Chain 諧波")
print("=" * 65)

# ν(x) = (1+√(1+4/x))/2, x = g_bar/a₀
# 高 x 展開: ν = 1 + x⁻¹ - x⁻² + 2x⁻³ - 5x⁻⁴ + 14x⁻⁵ - ...
# 係數: 1, -1, 2, -5, 14 = (-1)^k·Catalan_k?
# C_0=1, C_1=1, C_2=2, C_3=5, C_4=14 → 係數 = (-1)^k·C_k!
print("高 x 展開: ν(x) = 1 + C₀x⁻¹ - C₁x⁻² + C₂x⁻³ - C₃x⁻⁴ + C₄x⁻⁵ - ...")
print("C_k = Catalan 數: 1, 1, 2, 5, 14, 42, 132, ...")
print()

# 驗證
from math import comb
def catalan(k):
    return comb(2*k, k) // (k+1)

x = 10.0
nu_exact = (1 + np.sqrt(1 + 4/x)) / 2
# 展開到 8 階
nu_series = 1.0
for k in range(1, 9):
    nu_series += (-1)**k * catalan(k) * x**(-k)
print(f"x = 10: ν_exact = {nu_exact:.10f}")
print(f"        ν_series (8 階) = {nu_series:.10f}")
print(f"        Catalan 展開誤差: {abs(nu_exact - nu_series):.2e}")

# ============ 4. 關鍵: Catalan 數同 44 嘅關係 ============
print("\n" + "=" * 65)
print("4. Catalan 數嘅 K_Chain 對應")
print("=" * 65)

# Catalan C_k = (1/(k+1))·C(2k,k)
# C_5 = 42, C_6 = 132, C_7 = 429, C_8 = 1430, C_9 = 4862, C_10 = 16796
print("Catalan 數列: 1, 1, 2, 5, 14, 42, 132, 429, 1430, 4862, 16796, ...")
print()
print("K_Chain 結構: 44 sites, 88 = 2×44, Σγ = 90")
print()

# 檢查: Σγ = 90 同 Catalan 有咩關係?
print(f"Σγ_n = {gamma.sum():.6f} (應為 90)")
print(f"44 = 4·11 = (φ³-φ⁻³)(φ⁵-φ⁻⁵)")
print(f"88 = 2·44, 90 = 2·44 + 2 = 2(N+1)")

# Catalan C_k 同 44: C_6 = 132 = 3·44! 
print(f"\nC₆ = 132 = 3×44 !!!")
print(f"C₆/44 = {132/44} = 3 (三代!)")
print(f"C₇ = 429 = 44·9.75 (無直接)")
print(f"C₈ = 1430 = 44·32.5")
print(f"C₉ = 4862 = 44·110.5")

# 更深入: Catalan 生成函數 C(x) = (1-√(1-4x))/(2x)
# 我哋嘅 √(1+4/x) = √(1+4x⁻¹) → Catalan 自然出現!
print("\n生成函數: C(x) = (1-√(1-4x))/(2x) = Σ C_k·x^k")
print("我哋嘅:  ν(x) = (1+√(1+4x⁻¹))/2 — 同 Catalan 生成函數同構!")
print("        √(1-4y) 出現喺 C(y), 我哋有 √(1+4x⁻¹)")
print("        y = -x⁻¹: C(-x⁻¹) = (1-√(1+4x⁻¹))/(-2x⁻¹) = (x/2)(√(1+4x⁻¹)-1)")
print("        → ν(x) = 1 + x·C(-x⁻¹)... 檢查:")
# ν = (1+√(1+4/x))/2, x·C(-1/x) = x·(1-√(1+4/x))/(-2/x) = -(x²/2)(1-√(1+4/x))
# = (x²/2)(√(1+4/x)-1)
# ν = 1 + (1/x)·(x²/2)(√(1+4/x)-1)·... 唔係, 計錯
# 直接: ν-1 = (√(1+4/x)-1)/2 = √(1+4/x)·(1-1/√(1+4/x))/2... 唔簡潔
# 用 (√(1+4/x)-1)/2 = (4/x)/(2(√(1+4/x)+1)) = (2/x)/(√(1+4/x)+1)
# ν-1 = 2/(x(√(1+4/x)+1)) = 2/(x·2ν) = 1/(x·ν) ← 另一個恆等式!
nu_test = (1 + np.sqrt(1 + 4/5.0)) / 2
print(f"ν-1 = 1/(x·ν) 驗證 (x=5): {nu_test-1:.6f} vs {1/(5*nu_test):.6f}")

# ============ 5. 插值函數嘅諧波疊加表示 ============
print("\n" + "=" * 65)
print("5. 插值函數嘅諧波疊加 (K_Chain 44 模式)")
print("=" * 65)

# 嘗試: 1/(x·ν) = ν-1 → 1/ν = x(ν-1) → ν = 1/(1-x+xν)... 循環
# 另一條路: 用連分數!
# ν = 1 + 1/(x·ν) → ν = 1 + 1/(x(1 + 1/(xν))) → 連分數!
# ν(x) = 1 + 1/(x + 1/(x + 1/(x + ...)))  ← 週期連分數!
print("ν = 1 + 1/(xν) → 連分數表示:")
print("ν(x) = 1 + 1/(x + 1/(x + 1/(x + ...)))")
print("→ 呢個係「週期 1」嘅連分數, 對應 K_Chain 嘅自相似結構!")
print()

# 驗證連分數收斂
x = 3.0
nu_exact = (1 + np.sqrt(1 + 4/x)) / 2
cf = 1.0
for _ in range(50):
    cf = 1 + 1/(x + 0)  # 第一項
# 正確連分數: ν = 1 + 1/(x·ν) → 迭代 ν_{k+1} = 1 + 1/(x·ν_k)
nu_iter = 1.0
for _ in range(30):
    nu_iter = 1 + 1/(x*nu_iter)
print(f"x = 3: ν_exact = {nu_exact:.10f}, 迭代 30 次 = {nu_iter:.10f}")

# ============ 6. K_Chain 模式作為「閾值」分解 ============
print("\n" + "=" * 65)
print("6. 模式閾值分解: g_obs = g_bar + Σ 模式修正")
print("=" * 65)

# 假設: 每個 K_Chain 模式 n 貢獻修正 Δg_n = a₀·w_n·g_bar/(g_bar + γ_n·a₀)
# 即 g_obs/g_bar = 1 + Σ w_n·γ_n·a₀/(g_bar + γ_n·a₀)... 等我試 fit
# 簡單版: g_obs/g_bar = 1 + a₀·Σ w_n/(g_bar·(1+γ_n·a₀/g_bar)...)
# 目標: 1 + Σ_n w_n·x/(x + γ_n) ≈ ν(x·...) 形式

# 用 least squares fit 搵 w_n
x_grid = np.logspace(-3, 3, 500)
nu_target = (1 + np.sqrt(1 + 4/x_grid)) / 2
# 模型: nu_model = 1 + Σ w_n·x_grid/(x_grid + gamma_n)  (唔啱, 應該係 1/x 項)
# 模型2: nu_model = 1 + Σ w_n/(x_grid + gamma_n)  — 每模式一個 Lorentzian
A = np.array([1/(x_grid + g) for g in gamma]).T  # (500, 44)
b = nu_target - 1
w, res, rank, sv = np.linalg.lstsq(A, b, rcond=None)
print(f"Lorentzian 疊加 fit: max|residual| = {np.max(np.abs(A@w - b)):.2e}")
print(f"權重 w_n (頭 10): {w[:10]}")
print(f"權重 w_n (尾 10): {w[-10:]}")

# 檢查權重結構
w_abs = np.abs(w)
w_sorted = np.sort(w_abs)[::-1]
print(f"最大權重: {w_sorted[0]:.4f}, 第二大: {w_sorted[1]:.4f}, 前5: {w_sorted[:5]}")
print(f"Σ|w| = {w_abs.sum():.4f}")

# 用 γ_n 作為「模式」嘅 Lorentzian 疊加效果
print(f"\nγ_n 範圍: [{gamma.min():.4f}, {gamma.max():.4f}]")
print(f"γ₁ = {gamma[0]:.5f} (基態), γ₂₂ = {gamma[21]:.4f} (對偶中心), γ₄₄ = {gamma[43]:.4f} (Nyquist)")

# 如果權重集中喺低模式 → W-field 修正由低頻模式主導
low_modes = np.sum(w_abs[:11]) / w_abs.sum()
print(f"低 11 模式權重佔比: {low_modes*100:.1f}%")

# ============ 保存 ============
with open('data/interp_algebra.json', 'w') as f:
    json.dump({
        'identity': 'nu(nu-1) = a0/g_bar',
        'logistic': 'u_{2n} = 4u_n(1-u_n), B=4',
        'catalan': 'nu(x) = 1 + C0/x - C1/x^2 + C2/x^3 - ...',
        'continued_fraction': 'nu = 1 + 1/(x·nu)',
        'gamma_sum': float(gamma.sum()),
        'gamma_1': float(gamma[0]),
        'gamma_22': float(gamma[21]),
        'gamma_44': float(gamma[43]),
        'lorentz_fit_max_resid': float(np.max(np.abs(A@w - b))),
        'weights': w.tolist()
    }, f, indent=2)
print("\n結果已存: data/interp_algebra.json")
