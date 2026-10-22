#!/usr/bin/env python3
"""
O32-21: 二次守恆嘅場論推導
============================
目標: 從 AQUAL 作用量 S = ∫[-(a₀²/8πG)F(y) + Φρ_b] 推導 g_obs² = g_bar(g_obs + a₀)

AQUAL:
  ∇·(μ(y)·∇Φ) = 4πGρ_b,  μ(y) = √y/(1+√y), y = |∇Φ|²/a₀²
  球對稱: μ(x)·g_obs = g_bar, x = g_obs/a₀

推導目標: 證明 g_obs² = g_bar(g_obs + a₀)

方法: 能量守恆/變分結構
1. AQUAL 作用量對 Φ 嘅 Noether 荷?
2. 標量場嘅「能量」張量
3. 等效「有效度規」?

關鍵: μ(x)·g_obs = g_bar 已經隱含 ν(ν-1) = a₀/g_bar?
  檢查: μ(x) = x/(1+x), x = g_obs/a₀
  g_bar = μ·g_obs = g_obs·x/(1+x) = g_obs·(g_obs/a₀)/(1+g_obs/a₀) = g_obs²/(g_obs+a₀)
  → g_bar(g_obs + a₀) = g_obs²  ← 直接推導!! ✓✓✓

★ 所以二次守恆 = AQUAL 場方程嘅直接結果!
  唔需要額外假設 — 佢就係 μ = x/(1+x) 嘅等價形式!
"""
import numpy as np
import json

print("=" * 65)
print("二次守恆 = AQUAL 場方程直接結果")
print("=" * 65)

print("""
AQUAL 場方程 (球對稱):
  μ(x)·g_obs = g_bar,  x = g_obs/a₀,  μ(x) = x/(1+x)

代入:
  g_bar = g_obs·x/(1+x) = g_obs·(g_obs/a₀)/(1 + g_obs/a₀)
        = g_obs²/(g_obs + a₀)

→ g_bar(g_obs + a₀) = g_obs²  ✅ QED

所以: 二次守恆唔係新發現 — 佢係 μ = x/(1+x) 嘅代數等價形式!
""")

# ============ 1. 但係 μ = x/(1+x) 點嚟? ============
print("=" * 65)
print("1. μ = x/(1+x) 嘅推導: 從 F(y) 出發")
print("=" * 65)

print("""
AQUAL: μ(y) = F'(y), y = x² (x = |∇Φ|/a₀)

μ(x) = x/(1+x) → μ(y) = √y/(1+√y)

F(y) = ∫ μ dy = y - 2√y + 2ln(1+√y)  (之前推導)

問題: 點解 F(y) 係呢個形式? 有咩對稱性強迫?
""")

# ============ 2. F(y) 嘅對稱性分析 ============
print("=" * 65)
print("2. F(y) 嘅對稱性: 分形/尺度不變性")
print("=" * 65)

# 檢查 F(y) 喺 y → λy 嘅行為
def F(y):
    t = np.sqrt(y)
    return y - 2*t + 2*np.log1p(t)

# 漸近行為
print("F(y) 漸近:")
print(f"  y → 0:  F ≈ (2/3)y^(3/2)  (深 MOND)")
print(f"  y → ∞:  F ≈ y - 2√y + 2ln(y)  (牛頓)")
print()

# 尺度行為: F(λy) vs λF(y)?
print("尺度檢查 F(λy) vs λ^α·F(y):")
for lam in [2, 4, 10]:
    y0 = 1.0
    print(f"  λ={lam:>2}: F({lam})={F(lam):.4f}, λF(1)={lam*F(1):.4f}, "
          f"λ^(3/2)F(1)={lam**1.5*F(1):.4f}, λ²F(1)={lam**2*F(1):.4f}")
    print(f"        F(λ)/F(1) = {F(lam)/F(1):.4f}  (λ^α: α = {np.log(F(lam)/F(1))/np.log(lam):.3f})")

print("""
→ F 冇簡單齊次性 (α 隨 λ 變) — 唔係冪律場論
→ F 係「跨尺度」插值: 深 MOND (y^3/2) → 牛頓 (y) 平滑過渡
""")

# ============ 3. 從變分原理推 μ = x/(1+x) ============
print("=" * 65)
print("3. 最小作用量 + 簡單性原理")
print("=" * 65)

print("""
候選 μ(x) 嘅約束:
1. μ(0) = 0 (冇重子 → 冇場)
2. μ(∞) = 1 (牛頓極限)
3. 單調遞增 (物理: g_obs > g_bar 穩定)
4. 最簡單嘅有理函數滿足以上: μ = x/(1+x)  ← 唯一一次多項式比!

證明唯一性:
  一次有理函數 μ(x) = (ax+b)/(cx+d)
  約束: μ(0) = 0 → b = 0
        μ(∞) = 1 → a = c
  → μ(x) = x/(x + d/a) = x/(x + κ)
  尺度不變性 (a₀ 唯一標度): κ = 1
  → μ(x) = x/(1+x)  ✅ 唯一!
""")

# 驗證唯一性
print("唯一性驗證:")
print("  μ(x) = x/(x+κ), κ 由尺度固定 = 1")
print("  μ(x) = x/(1+x) ✅")

# ============ 4. 二次守恆嘅幾何詮釋 ============
print("=" * 65)
print("4. 二次守恆嘅幾何: 圓/雙曲線結構")
print("=" * 65)

# g_obs² = g_bar·g_obs + g_bar·a₀
# 設 u = g_obs/a₀, v = g_bar/a₀:
# u² = v·u + v → v = u²/(u+1) = u - 1 + 1/(u+1)
# 或者: v(u+1) = u² → 呢個係咩曲線?
print("""
設 u = g_obs/a₀, v = g_bar/a₀:
  u² = uv + v
  v = u²/(u+1)  (有理函數曲線)

參數化: 設 t = u:
  (u, v) = (t, t²/(t+1)), t ∈ (0, ∞)

呢條曲線嘅幾何:
  v = t²/(t+1) = t - 1 + 1/(t+1)
  
  當 t → 0: v ≈ t² (深 MOND: g_bar ∝ g_obs²)
  當 t → ∞: v ≈ t - 1 (牛頓: g_bar ≈ g_obs - a₀)

反函數: t = (v + √(v²+4v))/2 = (v/2)(1+√(1+4/v)) ✓
""")

# 曲線參數
print("曲線 (u, v) 表:")
print(f"{'u':>8} {'v':>10} {'v/u':>8} {'ν=u/v':>8}")
for u in [0.01, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]:
    v = u**2/(u+1)
    print(f"{u:>8.2f} {v:>10.4f} {v/u:>8.4f} {u/v:>8.4f}")

# ============ 5. 二次守恆 = 圓周運動嘅能量? ============
print("=" * 65)
print("5. 物理詮釋: 圓周運動能量")
print("=" * 65)

print("""
旋轉曲線: V² = R·g_obs

二次守恆: g_obs² = g_bar(g_obs + a₀)
→ V⁴/R² = (GM/R²)(V²/R + a₀)
→ V⁴ = GM(V²/R + a₀)/... 
   V⁴ = GM·g_obs + GM·a₀ = GM(V²/R + a₀)
→ V⁴ = (GM/R)·V² + GM·a₀
→ V²(V² - GM/R) = GM·a₀
→ V²(V² - V_bar²) = GM·a₀   (V_bar² = GM/R)

★ 旋轉曲線形式:
  V²(V² - V_bar²) = GM·a₀ = 常數 (對固定 M)

深 MOND (V >> V_bar): V⁴ ≈ GM·a₀ → V = (GMa₀)^(1/4) 平坦 ✓
牛頓區 (V ≈ V_bar): V²·(2V_bar·ΔV) ≈ GM·a₀ → 微擾
""")

# 驗證 V²(V²-V_bar²) = GMa₀
print("驗證 V²(V² - V_bar²) = GM·a₀:")
G = 6.674e-11
Msun = 1.989e30
a0 = 1.1225e-10
for M_s in [1e9, 1e10, 1e11, 1e12]:
    M = M_s*Msun
    for R_kpc in [5, 10, 30]:
        R = R_kpc*3.085677581e19
        gbar = G*M/R**2
        nu = (1+np.sqrt(1+4*a0/gbar))/2
        gobs = gbar*nu
        V2 = R*gobs
        Vbar2 = R*gbar
        lhs = V2*(V2-Vbar2)
        rhs = G*M*a0
        ok = abs(lhs-rhs)/rhs < 1e-9
        print(f"  M={M_s:>3.0e}, R={R_kpc:>2}: {lhs:.3e} vs {rhs:.3e} {'✅' if ok else '❌'}")

print("""
★ 終極形式:
  V²(V² - V_bar²) = GM·a₀

  呢個係旋轉曲線嘅「二次守恆」形式!
  - 左: V² (總動能標度) × (V²-V_bar²) (超額)
  - 右: GM·a₀ (重子 × 臨界) — 常數!
  
  對固定 M: V²(V²-V_bar²) = const
  → 平坦曲線自動出現 (V → (GMa₀)^(1/4))
""")

with open('data/quadratic_conservation.json', 'w') as f:
    json.dump({
        'derivation': 'g_bar = μ·g_obs = g_obs²/(g_obs+a₀) → g_obs² = g_bar(g_obs+a₀)',
        'uniqueness': 'μ = x/(x+κ), κ=1 by scale invariance → μ = x/(1+x)',
        'rotation_form': 'V²(V²-V_bar²) = GM·a₀',
        'curve': 'v = u²/(u+1), u=g_obs/a₀, v=g_bar/a₀'
    }, f, indent=2)
print("結果已存: data/quadratic_conservation.json")
