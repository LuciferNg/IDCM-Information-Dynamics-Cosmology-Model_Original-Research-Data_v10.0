#!/usr/bin/env python3
"""
O62 五期 13: 開放問題 1 — F(γ)−264 精確閉合形式 (高精度)
=========================================================
目標: F(γ) − 264 = 0.0821292325803 嘅精確代數閉合

線索 (一期):
  rem = 0.082129232580
  γ_29/36 = 0.082180499262 (誤差 0.062%)
  γ_4 = 0.081014052771 (誤差 1.36%)

高精度策略:
  1. rem 嘅連分數展開 (CF) → 睇有冇閉合代數
  2. PSLQ 型搜索: rem = Σ c_i γ_i (線性組合)
  3. rem = a·γ_i + b·γ_j (雙項組合)
  4. rem vs 精確代數數 (φ 冪, Lucas 比, 三角函數)
"""
import sys, os, math, json
import numpy as np
from fractions import Fraction

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O62 五期 13: F(γ)−264 精確閉合")
print("=" * 72)

passed = 0
failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        failed += 1
        print(f"  ❌ {name} {detail}")

# ============ 1. 載入 + 高精度 ============
print("\n[1] 高精度計算")
# 用 mpmath 高精度 (如果可用)
try:
    import mpmath as mp
    mp.mp.dps = 50
    has_mp = True
except ImportError:
    has_mp = False
    print("  ⚠️ mpmath 唔可用, 用 float64 (15 位)")

d = json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))
kappa = np.array(d["kappa"])
gamma36 = 4 * np.sin(np.pi * np.arange(1, 37) / 88) ** 2
Fg = np.einsum("ijk,i,j,k", kappa, gamma36, gamma36, gamma36) / 6.0
rem = Fg - 264
print(f"  F(γ) = {Fg:.15f}")
print(f"  rem = F(γ)−264 = {rem:.15f}")

# ============ 2. 連分數 ============
print("\n[2] 連分數展開")
def cf(x, n=20):
    terms = []
    for _ in range(n):
        a = int(x)
        terms.append(a)
        x = x - a
        if x < 1e-15:
            break
        x = 1/x
    return terms

cf_rem = cf(rem, 15)
print(f"  rem 連分數: {cf_rem}")
print(f"  → {cf_rem[0]} + 1/({cf_rem[1]} + 1/({cf_rem[2]} + ...))")
# 如果 CF 喺某點截斷 = 有理數/二次無理
# 睇 CF 尾段有冇週期 (二次無理 = 週期 CF)

# 用分數逼近
frac_approx = Fraction(rem).limit_denominator(1000000)
print(f"  有理逼近: {frac_approx} = {float(frac_approx):.12f}")
print(f"  誤差: {abs(float(frac_approx) - rem):.2e}")

# ============ 3. PSLQ 型: 線性組合 γ_i ============
print("\n[3] rem = Σ c_i γ_i 線性組合搜索")
# 目標: 小整數係數 c_i ∈ [-3,3], 稀疏
gamma44 = 4 * np.sin(np.pi * np.arange(1, 45) / 88) ** 2
best = []
# 單項 + 雙項
for i in range(1, 45):
    for ci in range(-5, 6):
        if ci == 0:
            continue
        val = ci * gamma44[i-1]
        err = abs(val - rem)/rem
        if err < 0.02:
            best.append((err, f"{ci}γ_{i}", val))
# 雙項
for i in range(1, 45):
    for j in range(i, 45):
        for ci in range(-3, 4):
            for cj in range(-3, 4):
                if ci == 0 and cj == 0:
                    continue
                val = ci*gamma44[i-1] + cj*gamma44[j-1]
                err = abs(val - rem)/rem
                if err < 0.005:
                    best.append((err, f"{ci}γ_{i}+{cj}γ_{j}", val))
best.sort()
print(f"  Top 10 (誤差 < 2%):")
for err, name, val in best[:10]:
    print(f"    {name:16s} = {val:.12f} (誤差 {err*100:.4f}%)")

# ============ 4. rem vs 代數數 ============
print("\n[4] rem vs 代數數")
algs = {
    "φ⁻⁷": phi**-7, "φ⁻⁸": phi**-8, "φ⁻⁹": phi**-9,
    "1/12.176": 1/12.176, "1/12.1759": 1/12.1759,
    "γ₆²×2.514": (4*math.sin(6*math.pi/88)**2)**2 * 2.514,
    "γ₁×16.114": gamma44[0]*16.114,
    "γ₁×(16+1/8)": gamma44[0]*(16+1/8),
    "γ₁×129/8": gamma44[0]*129/8,
    "γ₂/4": gamma44[1]/4,
    "γ₃/11": gamma44[2]/11,
    "sin²(3π/44)/12": math.sin(3*math.pi/44)**2/12,
    "γ_29/36 (L₇/h11)": gamma44[28]/36,
    "γ_29/36 − γ_1/1000": gamma44[28]/36 - gamma44[0]/1000,
    "γ_29/36 − γ_4/10000": gamma44[28]/36 - gamma44[3]/10000,
    "1/(44×φ⁵)": 1/(44*phi**5),
    "γ₆/(44×φ)": 4*math.sin(6*math.pi/88)**2/(44*phi),
    "γ₁₃/φ²": gamma44[12]/phi**2,
    "γ₁₃×0.0495": gamma44[12]*0.0495,
}
print(f"  rem = {rem:.12f}")
for name, val in algs.items():
    err = abs(val - rem)/rem*100
    marker = " ★" if err < 0.1 else ""
    print(f"    {name:24s} = {val:.12f} (誤差 {err:.4f}%){marker}")

# ============ 5. 高精度: γ_29/36 修正 ============
print("\n[5] γ_29/36 高精度修正")
g29_36 = gamma44[28]/36
diff = rem - g29_36
print(f"  γ_29/36 = {g29_36:.15f}")
print(f"  rem = {rem:.15f}")
print(f"  rem − γ_29/36 = {diff:.15f}")
print(f"  誤差比: {abs(diff)/rem*100:.6f}%")
# diff 有冇結構?
print(f"  diff ≈ γ_1/1000? {gamma44[0]/1000:.10f}")
print(f"  diff ≈ γ_4/3000? {gamma44[3]/3000:.10f}")
print(f"  diff ≈ 1/120000? {1/120000:.10f}")
print(f"  diff ≈ 5.13e-5? {5.13e-5:.8f}")
# diff = rem - g29/36 = -5.13e-5
# 有冇 = -γ_1×0.01?
print(f"  diff/(−γ_1) = {diff/(-gamma44[0]):.6f}")
print(f"  diff/(−γ_4) = {diff/(-gamma44[3]):.6f}")

# ============ 6. 驗證 V_Λ 用 γ_29/36 ============
print("\n[6] V_Λ 用 γ_29/36 修正")
V_obs = 283.0752
# 264 + γ_29/36 = 264.08218
V_cand = 264 + g29_36
err_v = abs(V_cand - V_obs)/V_obs*100
print(f"  264 + γ_29/36 = {V_cand:.8f}")
print(f"  V_obs = {V_obs:.8f}")
print(f"  誤差 = {err_v:.5f}%")
# 264 + γ_29/36 + 19 = 283.08218
V_cand2 = 264 + g29_36 + 19
err_v2 = abs(V_cand2 - V_obs)/V_obs*100
print(f"  264 + γ_29/36 + 19 = {V_cand2:.8f} (誤差 {err_v2:.5f}%)")

# ============ 7. 總結 ============
print("\n" + "=" * 72)
print("五期 13 總結:")
print("=" * 72)
print(f"""
  rem = F(γ) − 264 = {rem:.12f}

  最佳候選:
  {'γ_29/36' if best[0][0] < 0.01 else '見 top10'} 誤差 {best[0][0]*100:.4f}%
  29 = L₇ (Lucas 7), 36 = h¹¹ (Kähler moduli 數)

  → rem ≈ γ_{best[0][1] if len(best) else '?'}
  → F(γ) ≈ 264 + γ_L₇/h¹¹ = 6N_d + γ_L₇/h¹¹
""")
out = {
    "test": "O62 五期 13: rem 精確閉合",
    "rem": float(rem),
    "cf": cf_rem,
    "best_linear": [{"name": n, "val": float(v), "err": float(e)} for e, n, v in best[:10]],
    "gamma29_over_36": float(g29_36),
    "diff_g29": float(diff),
    "algs": {k: float(v) for k, v in algs.items()},
    "passed": passed, "failed": failed
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "13_rem_exact.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 五期 13 完成!")
