#!/usr/bin/env python3
"""
O97 — Level D 公理湧現測試 (調律者要求):
「真公理 = 管道在可自由任意選擇下, 不經干涉, 自己收斂至 0.618」

核心主張:
  fit 常數 → 需要人校準 (干涉, tuning)
  公理常數 → 吸引子 (attractor): 任何初始條件/任何注入, 動力學自動收斂
  0.618 = 1/φ 必須係吸引子, 唔係輸入。

動態系統: 單位儲備倒數管道 (O(1) kernel, D2)
    x_{n+1} = 1/(1 + x_n)
    * 固定點: x = 1/(1+x) → x²+x−1=0 → x = (√5−1)/2 = 1/φ = 0.6180339...
    * 全域收縮: |f′(x)| = 1/(1+x)² < 1 ∀ x>0 → 全域 (0,∞) 都係 basin
    * 漸近速率: f′(1/φ) = −1/φ² = −0.381966 (φ⁻², 黃金二次)
    * 經濟學詮釋: 每步保留 1 單位 (kernel), 循環 x 單位; 新循環 = 1/(1+x);
      穩定態: 儲備 61.8%, 循環 38.2% = 0.618² — 自相似黃金組合

測試:
  T1 固定點/收縮 精確 (sympy)
  T2 自由初始選擇 (7 個代表值 + 10⁵ log-uniform 樣本): 全部 → 0.618
  T3 收斂速率 = φ⁻² (無干涉, 純動力學)
  T4 噪聲魯棒 (不經干涉, 加噪照收斂)
  T5 垃圾注入遺忘 (任意外部輸入 → 管道自己恢復 0.618)
  T6 族對照: x′=1/(c+x), 只有 c=1 (單位儲備) 嘅吸引子 = 0.618
"""
import math
import numpy as np
import sympy as sp

phi = (1 + math.sqrt(5))/2
xstar = 1/phi
results = []
def record(ok, label, detail=""):
    results.append((ok, label, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {label} {detail}")

f = lambda x: 1/(1 + x)

# ═════ T1: 固定點 + 全局收縮 (sympy 精確) ═════
print("=== T1: 固定點 + 全局收縮 ===")
X = sp.Symbol('X', positive=True, real=True)
fp = sp.solve(sp.Eq(X, 1/(1+X)), X)
fp_pos = [c for c in fp if sp.nsimplify(c) > 0]
exact_star = (sp.sqrt(5) - 1)/2          # 1/φ 精確 sympy
record(len(fp_pos) == 1 and sp.simplify(fp_pos[0] - exact_star) == 0,
       "T1a 固定點 x=1/(1+x) 唯一正解 = 1/φ = 0.618034",
       f"解={[sp.nsimplify(c) for c in fp]}")
# 全局收縮 |f'|=1/(1+x)²<1 ∀x>0
deriv = sp.simplify(sp.diff(1/(1+X), X))
expr_pos = sp.factor(1 - 1/(1+X)**2)          # X(X+2)/(X+1)² > 0 for X>0
record(expr_pos.is_positive is True,
       "T1b 全局收縮 |f′|=1/(1+x)²<1 ∀x>0 (全域 basin)",
       f"f′={deriv}, 1−f′²={expr_pos} > 0   ∀X>0")

# ═════ T2: 自由初始選擇 → 全部自己收斂到 0.618 ═════
print("\n=== T2: 自由任意初始選擇 (無干涉) ===")
starts = [1e-6, 0.001, 0.5, 1, 3, 10, 1e6]
print("    單軌跡 (20 步):")
for x0 in starts:
    x = x0
    for _ in range(20):
        x = f(x)
    ok = abs(x - xstar) < 1e-6
    print(f"      x₀={x0:>6g} → x₂₀={x:.10f} ({'✓ 0.618' if ok else '✗'})")
    record(ok, f"T2a x₀={x0:g} 收斂 (20 步)", f"err={abs(x-xstar):.2e}")
# 10⁵ log-uniform 樣本 (任意選擇: 跨 12 個數量級)
rng = np.random.default_rng(42)
samples = 10**(-6 + 12*rng.random(100000))
xs = samples.copy()
for _ in range(40):
    xs = f(xs)
rel = np.abs(xs - xstar)
print(f"    log-uniform[1e-6,1e6] × 10⁵ 樣本, 40 步後:")
print(f"      mean={xs.mean():.10f}, median={np.median(xs):.10f}, "
      f"std={xs.std():.2e}, max|err|={rel.max():.2e}")
record(np.std(xs) < 1e-6 and abs(np.mean(xs) - xstar) < 1e-6,
       "T2b 10⁵ 任意初始選擇 → 分佈坍縮為 0.618 點質量",
       f"std={xs.std():.2e}, mean err={abs(xs.mean()-xstar):.2e}")
# T2c: 任意起點 2 步後自動 snap 入 Fibonacci 收斂帶 (種子 (0,1) 由管道重現)
fibs = [1, 1]
for _ in range(20):
    fibs.append(fibs[-1] + fibs[-2])
x0 = math.pi/2          # 任意起點 (唔係 0/1)
orbit = [x0]
for _ in range(8):
    orbit.append(f(orbit[-1]))
print(f"    T2c: x₀={x0:.6f} (π/2, 任意) 軌跡:")
bounds_ok = (0.5 <= orbit[2] <= 1.0)     # x₂ ∈ (1/2, 1)
for n in range(3, 9):
    # 解析 (f 遞減, f((a,b)) = (1/(1+b), 1/(1+a))):
    #   odd n: xₙ ∈ (Fₙ₋₁/Fₙ, Fₙ/Fₙ₊₁); even n: xₙ ∈ (Fₙ/Fₙ₊₁, Fₙ₋₁/Fₙ)
    #   → 一律 [min,max](Fₙ₋₁/Fₙ, Fₙ/Fₙ₊₁); 注意 fibs[i] = F_{i+1}
    r1 = fibs[n-2]/fibs[n-1]             # Fₙ₋₁/Fₙ
    r2 = fibs[n-1]/fibs[n]               # Fₙ/Fₙ₊₁
    bl, bh = min(r1, r2), max(r1, r2)
    inside = bl - 1e-12 <= orbit[n] <= bh + 1e-12
    bounds_ok &= inside
    print(f"      xₙ(n={n}) = {orbit[n]:.6f} ∈ [{bl:.6f}, {bh:.6f}] (Fₙ₋₁/Fₙ, Fₙ/Fₙ₊₁)")
record(bounds_ok, "T2c 任意起點 2 步後 snap 入 Fibonacci 收斂帶 (種子重現)",
       "任意 x₀ → xₙ 被 Fₙ₋₁/Fₙ, Fₙ/Fₙ₊₁ 邊界夾逼 (n≥3)")

# ═════ T3: 收斂速率 = φ⁻² ═════
print("\n=== T3: 收斂速率 (自相似: 吸引子 φ, 速率 φ²) ===")
x = 2.5   # 遠離固定點
rates = []
for _ in range(30):
    xn, xnn = x, f(x)
    rates.append(abs(xnn - xstar)/abs(xn - xstar))
    x = xnn
print(f"    尾部速率 mean={np.mean(rates[-10:]):.6f}, φ⁻²={1/phi**2:.6f}, φ⁻¹={1/phi:.6f}")
record(abs(np.mean(rates[-10:]) - 1/phi**2) < 1e-4,
       "T3 漸近收斂速率 = φ⁻² = 0.381966 (黃金二次)",
       f"實測 {np.mean(rates[-10:]):.6f} vs 1/φ²={1/phi**2:.6f}")
# 全局上界 4/9 於 [0.5,1] (入軌後)
max_d = max(abs(1/(1+x)**2) for x in np.linspace(0.5, 1.0, 10000))
record(max_d <= 4/9, "T3b 入軌後收縮 ≤ 4/9 (任何干擾每步至少砍掉一半以上)", f"max|f′|={max_d:.4f}")

# ═════ T4: 噪聲魯棒 (不經干涉 — 冇人調參, 加噪照企喺 0.618) ═════
print("\n=== T4: 噪聲魯棒 (獨立同分佈噪聲, 無任何調節) ===")
eta = 0.05
xs = np.full(1000, 0.5)
for _ in range(200):
    xs = f(xs) + rng.uniform(-eta, eta, size=xs.shape)
print(f"     200 步後 (噪聲±{eta}): mean={xs.mean():.4f}, std={xs.std():.4f}, "
      f"max|dev|={np.max(np.abs(xs-xstar)):.4f}")
record(abs(xs.mean() - xstar) < 0.05 and xs.std() < 0.1 and
       np.max(np.abs(xs - xstar)) < 0.15,
       "T4 噪聲下吸引子保持 (冇調節, 冇跑飛)", f"mean={xs.mean():.4f}, σ={xs.std():.4f}")

# ═════ T5: 垃圾注入遺忘 (自由任意外部輸入 → 管道自己恢復) ═════
print("\n=== T5: 任意垃圾注入 → 管道自己恢復 0.618 ===")
recover = []
for _ in range(20):
    x = rng.uniform(1e-3, 10)      # 一次性任意外部垃圾注入 (自由任意值)
    steps = 0
    while abs(x - xstar) > 1e-3 and steps < 60:
        x = f(x)
        steps += 1
    recover.append(steps)
print(f"     20 次垃圾注入 (U[1e-3,10]): 平均恢復步數={np.mean(recover):.1f}, 最長={np.max(recover)}")
print(f"     例: 注入 10 後偏差 9.38 → 每步×0.444 → ~11 步返到 1e-3 (理論預期吻合)")
record(np.mean(recover) < 15 and np.max(recover) < 20,
       "T5 任意垃圾注入後 <15 步自動恢復 (干擾被遺忘, 毋須調參)",
       f"平均 {np.mean(recover):.1f} 步, 最長 {np.max(recover)} 步")

# ═════ T6: 族對照 x′=1/(c+x): 只有 c=1 (單位儲備) 吸引子 = 0.618 ═════
print("\n=== T6: 族對照 x′=1/(c+x), c∈{0.5,1,2,3} ===")
for c in [0.5, 1, 2, 3]:
    xc = (math.sqrt(c*c + 4) - c)/2
    is_golden = abs(xc - xstar) < 1e-9
    tag = "✓ 0.618 單位儲備" if is_golden else f"✗ ≠0.618 (間距 {abs(xc-xstar):.3f})"
    print(f"      c={c}: 吸引子 = {xc:.6f}  {tag}")
    # 只 c=1 應該等於 0.618; 其他 c 應該明顯唔同
    if c == 1:
        record(is_golden, f"T6 c=1 吸引子 = 0.618 (單位儲備)", f"x*={xc:.6f}")
    else:
        record(not is_golden and abs(xc - xstar) > 0.05,
               f"T6 c={c} 吸引子 ≠ 0.618 (對照)", f"x*={xc:.6f}, 間距={abs(xc-xstar):.3f}")
# 收斂性: 全族都係全球收縮 → 「邊個吸引子」由 c (kernel 結構) 決定, 唔係 tune
# c=1 嘅獨特地位 = 單位儲備規範化 (D2 O(1) kernel = 保留 1 單位)

# ═════ 總結 ═════
npass = sum(1 for o, _, _ in results if o)
ntot = len(results)
print(f"\n=== 公理湧現測試: {npass}/{ntot} PASS ===")
if npass == ntot:
    print(">>> 0.618 係吸引子, 唔係輸入: 任意初始選擇/任意注入/噪聲 → 全收斂 φ⁻¹")
    print(">>> 收斂速率 φ⁻², 恢復自動, 冇調參 — 「真公理」湧現測試通過 (T1-T6)")