#!/usr/bin/env python3
"""
O32-20: 插值函數嘅微觀推導 — 從 K_Chain 諧波疊加
==================================================
問題: 點解 μ(x) = x/(1+x) 而唔係其他函數?

思路: μ(x) 應該由 K_Chain 所有模式嘅集體貢獻決定。
每個模式 n 有頻率 ω_n ∝ sin(πn/88), 對應「共振強度」。

關鍵猜想: μ(x) = Σ_n w_n·x/(x + κ_n), 其中 κ_n = γ_n/4 ∈ [0,1]
      = 並聯通道嘅「模式分解」

之前 Lorentzian fit 失敗 (residual 0.765)。原因: 用錯核函數。
正確嘅核: 每個模式對「臨界加速度」貢獻 s_n·γ_n/a₀?

另一條路: 由統計力學推導!
- W-field = K_Chain 模式嘅熱浴
- 每個模式係二能級 (on/off)
- 佔有率: p_n = 1/(1 + exp(E_n/kT))  ← Fermi-Dirac!
- E_n = γ_n·E₀ (模式能量), kT ↔ g_bar·a₀ 標度?

μ(x) = x/(1+x) = 1/(1 + 1/x) ← 形式同 Fermi-Dirac 1/(1+e^x) 一樣!

如果 1/x = exp(E₀/kT) → E₀/kT = ln(1/x) → kT = E₀/ln(1/x)

但 μ(x) = x/(1+x) 唔係 e 嘅函數... 除非 1/x 本身係 e^{...}
1/x = e^{ln(1/x)} → μ = 1/(1 + e^{ln(1/x)}) ← Fermi-Dirac with βE = ln(1/x)!

即: μ(x) = f_FD(ln(1/x)), f_FD(ε) = 1/(1+e^ε)

ε = ln(1/x) = ln(a₀/g_bar) ← W-field 嘅「化學勢」!

深 MOND (x<<1): ε >> 1 → μ ≈ e^{-ε} = x (Fermi tail!)... 但深 MOND 應該 μ ≈ √x!
唔啱! 深 MOND μ ≈ √x 而唔係 x → 單一 Fermi 模式唔夠。

需要 2 個模式 (或連續譜):
μ(x) = √x/(1+√x)?? 但呢個係 standard interpolation, 唔係 simple!

simple: μ = x/(1+x) = 1/(1+1/x) → 1/x 扮演「能量」
standard: μ = x/√(1+x²) → ?

關鍵: 我哋 fit 出 simple interpolation 最好 (Lelli+2017 用 simple!)
simple 嘅結構: μ = 1/(1+1/x) — 並聯電路 (之前發現)
"""
import numpy as np
import json

# ============ 1. Fermi-Dirac 形式 ============
print("=" * 65)
print("1. μ(x) 嘅統計力學形式")
print("=" * 65)

# simple interpolation: μ(x) = x/(1+x)
# 設 ε ≡ ln(1/x) = ln(a₀/g_bar)  (W-field 化學勢標度)
# μ = 1/(1 + e^ε)  ← Fermi-Dirac!

print("""
simple interpolation:
  μ(x) = x/(1+x) = 1/(1 + 1/x) = 1/(1 + e^ε),  ε = ln(1/x)

即 μ(x) = Fermi-Dirac 佔有率, 能量 ε = ln(a₀/g_bar)!

物理詮釋:
  W-field 模式嘅佔有率由「化學勢」ε 決定
  g_bar >> a₀ (x>>1): ε << 0 → μ → 1 (通道全開? 唔啱, μ→1 係對)
  g_bar << a₀ (x<<1): ε >> 0 → μ → e^{-ε} = x (Fermi tail)
  
⚠️ 但深 MOND 應該 μ ≈ √x 而唔係 x!
   μ ≈ x 會導致 g_obs ≈ g_bar + a₀x = g_bar + a₀·g_bar/a₀ = 2g_bar (錯!)
   正確深 MOND: g_obs = √(g_bar·a₀), μ = g_bar/g_obs = √(g_bar/a₀) = √x

→ 單一 Fermi 模式唔得! 需要模式疊加。
""")

# ============ 2. 模式疊加: 每個模式貢獻 √x 形式 ============
print("=" * 65)
print("2. 多模式疊加")
print("=" * 65)

# 假設: μ(x) = Σ_n w_n·√(x/(x+γ_n))... 或者
# 每個模式: μ_n(x) = √(x/(x+κ_n)), κ_n = γ_n/4
# 集體: μ(x) = Σ w_n·μ_n(x)

Nd = 44
gamma = np.array([4*np.sin(np.pi*n/88)**2 for n in range(1, Nd+1)])
kappa = gamma/4  # ∈ [0,1]

x_grid = np.logspace(-3, 3, 300)
mu_target = x_grid/(1+x_grid)

# 模型 A: μ = Σ w_n·x/(x+κ_n)  (並聯模式)
A = np.array([x_grid/(x_grid+k) for k in kappa]).T
wA, resA, _, _ = np.linalg.lstsq(A, mu_target, rcond=None)
muA = A @ wA
print(f"模型 A (x/(x+κ_n) 疊加): max residual = {np.max(np.abs(muA-mu_target)):.2e}")
print(f"  w_n 範圍: [{wA.min():.3f}, {wA.max():.3f}]")

# 模型 B: μ = Σ w_n·√(x/(x+κ_n))
B = np.array([np.sqrt(x_grid/(x_grid+k)) for k in kappa]).T
wB, resB, _, _ = np.linalg.lstsq(B, mu_target, rcond=None)
muB = B @ wB
print(f"模型 B (√(x/(x+κ_n)) 疊加): max residual = {np.max(np.abs(muB-mu_target)):.2e}")
print(f"  w_n 範圍: [{wB.min():.3f}, {wB.max():.3f}]")

# 模型 C: 連續譜 μ = ∫ w(κ)·x/(x+κ) dκ, w(κ) = ?
# 如果 w(κ) = δ(κ-1) → μ = x/(x+1) ✓!!! 單一模式 κ=1!
print(f"\n模型 C (單一模式 κ=1): μ = x/(x+1) = 目標 — 平凡!")

# 模型 D: μ = x/(x+1) 嘅「模式詮釋」:
# x/(x+1) = 1/(1+1/x), 1/x = a₀/g_bar
# 如果 a₀ = Σ_n a₀^{(n)} (模式分攤), 每個模式 μ_n = g_bar/(g_bar + a₀^{(n)})
# 集體: 1/μ = Σ_n 1/μ_n? 唔係並聯...
# 串聯: 1/μ = 1 + 1/x = 1 + Σ_n (1/x_n), 1/x_n = a₀^{(n)}/g_bar
# → a₀ = Σ a₀^{(n)} 分解!

print("""
★ 新詮釋: 串聯通道!
  1/μ(x) = 1 + 1/x = 1 + Σ_n a₀^{(n)}/g_bar
  
  即 a₀ 分解成模式貢獻: a₀ = Σ_n a₀^{(n)}
  
  每個模式 n 貢獻「臨界加速度」a₀^{(n)}, 全部加埋 = a₀
  呢個對應 K_Chain 模式嘅「串聯共振」!
""")

# ============ 3. a₀ 嘅模式分解 ============
print("=" * 65)
print("3. a₀ 嘅模式分解")
print("=" * 65)

# a₀ = c²/(2πR_H), R_H = 44·dx
# a₀ 對應 mode 1? 定係所有模式總和?
# 自然分解: a₀^{(n)} = a₀·w_n, Σw_n = 1
# 候選: w_n = γ_n/Σγ = γ_n/90 (能量權重)
# 或者 w_n = 1/44 (均勻)
# 或者 w_n = sin²(πn/88)·(2/44)... 等我試

w_uniform = np.ones(Nd)/Nd
w_energy = gamma/gamma.sum()
w_sin = np.sin(np.pi*np.arange(1, Nd+1)/88)**2
w_sin /= w_sin.sum()

# 邊個分解最自然? 檢查 Σ 1/(x + γ_n/...) 
# 其實最自然: a₀^{(n)} 對應模式頻率 ω_n 嘅「向心加速度」
# a₀^{(n)} = c·ω_n/(2π) ? 
c = 299792.458e3
R_H = 4129.94*3.085677581e22
omega_n = (88*c/R_H)*np.sin(np.pi*np.arange(1, Nd+1)/88)
a0n = c*omega_n/(2*np.pi)
print(f"a₀^(n) = c·ω_n/2π 分解:")
print(f"  Σ a₀^(n) = {a0n.sum():.6e}")
print(f"  a₀ (單獨) = {c**2/(2*np.pi*R_H):.6e}")
print(f"  比例 = {a0n.sum()/(c**2/(2*np.pi*R_H)):.4f}")
# Σ a₀^(n) = Σ c·(88c/R_H)sin(πn/88)/(2π) = (88c²/(2πR_H))Σsin(πn/88)
# Σ_{n=1}^{44} sin(πn/88) = ?
Sn = np.sum(np.sin(np.pi*np.arange(1, Nd+1)/88))
print(f"  Σ sin(πn/88) = {Sn:.6f}")
print(f"  理論: cot(π/176) ≈ {1/np.tan(np.pi/176):.6f} (88/π ≈ 28.0)")
print(f"  88/π = {88/np.pi:.4f}")
# Σ_{n=1}^{N} sin(πn/(2N)) = (1/2)cot(π/(4N)), N=44
print(f"  (1/2)cot(π/(4·44)) = {0.5/np.tan(np.pi/176):.6f}")

# 咁 a₀ = c²/(2πR_H) 對應邊個模式?
# a₀ = c·ω₁/(2π·88·sin(π/88)) (之前發現) — mode 1 相關!
# 但係 Σ a₀^(n) 好大 (28×a₀) → 唔係簡單總和

# 真正嘅結構: a₀ 係「單一模式」嘅投影?
# a₀ = c·ω₁/(2π·88sin(π/88)) = c·ω₁/(2π·3.1409)
# 88sin(π/88) ≈ π → a₀ ≈ c·ω₁/(2π²)

print(f"""
★ 關鍵: a₀ 由 mode 1 鎖死 (唔係模式總和):
  a₀ = c·ω₁/(2π·88·sin(π/88)) = c·ω₁/(2π·3.1409)
  
  但 μ(x) = x/(1+x) 嘅「1/x」項:
  1/x = a₀/g_bar = c·ω₁/(2π·88sin(π/88)·g_bar)
  
  W-field 通道電導 = 1/x = a₀/g_bar ∝ ω₁/g_bar
  → 只有 mode 1 參與! 其他模式唔貢獻星系尺度!
  
  呢個合理: 星系尺度 (kpc) 對應 K_Chain 長波長 mode,
  只有 mode 1 (λ=R_H) 喺星系尺度有非零投影!
  (高 mode λ_n = R_H·88/(2n·88)... 等我算 λ_n)
""")

# 模式波長: λ_n = 2R_H/n? 定係 R_H·88/(2n)?
# K_Chain: 88 sites, 周長 R_H, site 間距 dx = R_H/88
# mode n 波長: λ_n = 88·dx/n = R_H/n? 定係 2R_H/n?
# 駐波: λ_n = 2·R_H/n (n 個半波長)
# 行波: λ_n = R_H/n
# 用 K_Chain 標準: γ_n = 4sin²(πn/88) → ω ∝ sin(πn/88)
# 波數 k_n = πn/88 (rad/site) → λ_n = 2π/k_n = 176/n (sites) = R_H·176/(88n) = 2R_H/n
lambda_n = 2*R_H/np.arange(1, Nd+1)  # m
print(f"模式波長 λ_n = 2R_H/n:")
for n in [1, 2, 5, 10, 22, 44]:
    print(f"  n={n:>2}: λ = {lambda_n[n-1]/3.085677581e22:.2f} Mpc")
print(f"\n星系尺度 (kpc) << λ₁ (4129 Mpc) → 只有長波長模式有投影")
print(f"但 μ(x) 嘅結構: 單一「有效模式」決定 μ = x/(1+x)")
print(f"→ 模式 1 嘅 W-field 喺星系尺度 = 均勻場 (λ >> 星系)")
print(f"→ 均勻場 → 常數修正 a₀ → μ = g_bar/(g_bar+a₀) = x/(1+x) ✓✓✓")

# ============ 4. 最終詮釋 ============
print("\n" + "=" * 65)
print("4. 微觀推導總結")
print("=" * 65)
print("""
★ 推導鏈:

1. K_Chain mode 1: λ₁ = R_H = 4129.94 Mpc (宇宙最大波長)
2. 喺星系尺度 (kpc << Mpc), mode 1 嘅 W-field 係「均勻場」
3. 均勻 W-field 提供常數額外加速度 a₀
4. 牛頓引力 g_bar 同 W-field 修正並聯:
   g_obs = g_bar + a₀·μ(x), μ(x) = g_bar/(g_bar+a₀) = x/(1+x)
5. μ = x/(1+x) 由「常數額外加速度」直接推出:
   Δg = a₀·(g_bar/(g_bar+a₀)) → 當 g_bar >> a₀: Δg → a₀ (飽和)
                                   當 g_bar << a₀: Δg → g_bar (跟隨)
   
⚠️ 等等, 咁 μ(x) 嘅深 MOND 極限係 μ → x (線性), 但正確係 √x!
   問題: 如果 Δg = a₀·x/(1+x), 深 MOND (x<<1) Δg ≈ a₀·x = g_bar
   咁 g_obs = g_bar + g_bar = 2g_bar → V² = 2GM/R → 唔係平坦!
   
   ❌ 呢個詮釋唔啱! simple interpolation 嘅深 MOND 係:
   g_obs = g_bar·(1+√(1+4/x))/2 ≈ g_bar·√(1/x)·... 
   x<<1: ν ≈ (1+2/√x)/2 ≈ 1/√x → g_obs ≈ g_bar/√x = √(g_bar·a₀) ✓
   μ = g_bar/g_obs ≈ √x (唔係 x!)
   
   所以 μ(x) = x/(1+x) 嘅「並聯電路」詮釋係:
   μ = g_bar/(g_bar + a₀) 唔啱! 因為深 MOND μ → √x
   
   正確: μ = 1/ν, ν(ν-1) = 1/x
   深 MOND: ν ≈ 1/√x → μ = √x
   牛頓區: ν ≈ 1 + 1/x → μ ≈ x/(1+x) ≈ 1 - 1/x

★ 修正詮釋: μ(x) = x/(1+x) 只係「插值公式」, 唔係微觀機制!
   微觀機制: ν(ν-1) = 1/x (代數恆等式) — 呢個先係本質!

   ν(ν-1) = a₀/g_bar:
   (g_obs/g_bar)(g_obs/g_bar - 1) = a₀/g_bar
   g_obs(g_obs - g_bar) = g_bar·a₀
   
   呢個係「二次式」結構 — 對應能量守恆?
   g_obs² - g_bar·g_obs - g_bar·a₀ = 0
   
   判別式: Δ = g_bar² + 4g_bar·a₀ = g_bar(g_bar + 4a₀)
   g_obs = (g_bar + √(g_bar²+4g_bar·a₀))/2
   
   呢個係 g_obs² = g_bar·g_obs + g_bar·a₀ — 二次守恆!
   
   物理: 能量守恆 g_obs² = g_bar·(g_obs + a₀)
   解釋: 總加速度平方 = 重子加速度 × (總 + 臨界)
   
   ★ 呢個「二次守恆」先係 W-field 嘅微觀本質!
""")

# ============ 5. 二次守恆嘅物理 ============
print("=" * 65)
print("5. 二次守恆 g_obs² = g_bar(g_obs + a₀)")
print("=" * 65)

# 驗證
print("驗證 g_obs² = g_bar(g_obs + a₀):")
for x in [0.01, 0.1, 1, 10, 100]:
    nu = (1+np.sqrt(1+4/x))/2
    lhs = nu**2  # (g_obs/g_bar)²
    rhs = 1*(nu + 1/x)  # (g_obs/g_bar + a₀/g_bar)
    print(f"  x={x:>6.2f}: ν² = {lhs:.6f}, ν+1/x = {rhs:.6f} {'✅' if abs(lhs-rhs)<1e-10 else '❌'}")

print("""
★ 二次守恆嘅意義:

  g_obs² = g_bar·g_obs + g_bar·a₀
  
  左手: g_obs² ∝ V⁴/R² (總加速度平方)
  右手: g_bar·g_obs (牛頓 × 總) + g_bar·a₀ (牛頓 × 臨界)
  
  能量密度形式: ρ_W = g_obs²/(8πG) = g_bar(g_obs+a₀)/(8πG)
  
  即: W-field 能量密度 = 牛頓場 × (總場 + 臨界場)
  
  呢個自然對應:
  - 牛頓場能量: g_bar²/(8πG)
  - 交互能量: g_bar·a₀/(8πG)
  - 臨界場: a₀²/(8πG) (常數, 可吸收)
  
  g_obs² = g_bar² + g_bar·a₀ + ... 
  實際: g_obs² = g_bar² + g_bar·a₀ (展開?)
  (g_bar+g_bar·a₀/g_bar)²... 
  
  檢查: ν² = 1 + 2/x + ... vs ν+1/x = 1 + 2/x + 1/x² - ...
  高 x: ν = 1+1/x-1/x²+2/x³-...
  ν² = 1 + 2/x + (1/x²-2/x²) + ... = 1+2/x-1/x²+...
  ν+1/x = 1+1/x-1/x²+... + 1/x = 1+2/x-1/x²+... ✓
""")

with open('data/microscopic_interp.json', 'w') as f:
    json.dump({
        'fermi_form': 'mu = 1/(1+e^eps), eps = ln(a0/g_bar)',
        'single_mode': 'a0 = c·omega_1/(2π·88·sin(π/88)) → mode 1 only',
        'quadratic': 'g_obs^2 = g_bar(g_obs + a0)',
        'quadratic_check': 'ν² = ν + 1/x 恆等',
        'lambda_1': float(lambda_n[0]/3.085677581e22),
        'lambda_n_Mpc': [float(l/3.085677581e22) for l in lambda_n[:5]]
    }, f, indent=2)
print("結果已存: data/microscopic_interp.json")
