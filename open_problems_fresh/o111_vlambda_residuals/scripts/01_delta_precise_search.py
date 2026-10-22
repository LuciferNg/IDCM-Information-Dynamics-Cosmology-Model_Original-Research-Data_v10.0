#!/usr/bin/env python3
"""
O111 攻堅 1: Δ = F(γ)−264 精確閉合形式 — 高精度搜索
====================================================
Δ = 0.082129232580245 (50位)
1/Δ = 12.1759325953

攻擊路線:
  1. κ-block 分解: 邊個 block 出分數部分?
  2. Δ vs γ_n 精確組合 (高精度 PSLQ)
  3. 1/Δ 嘅連分數結構
  4. Δ × 整數嘅近整數結構
  5. Δ = γ_29/36 + 修正項 嘅精確形式
  6. Δ 同 Lucas/φ 嘅關係
"""
import sys, os, math, json, itertools
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O111 攻堅 1: Δ 精確閉合形式 — 高精度搜索")
print("=" * 72)

passed = 0; failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1; print(f"  ✅ {name} {detail}")
    else:
        failed += 1; print(f"  ❌ {name} {detail}")

# ─── 載入 κ 數據 ───
d = json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))
kappa = np.array(d["kappa"])  # 整數!
gamma36 = 4 * np.sin(np.pi * np.arange(1, 37) / 88) ** 2
gamma44 = 4 * np.sin(np.pi * np.arange(1, 45) / 88) ** 2

# 高精度 F(γ)
Fg = np.einsum("ijk,i,j,k", kappa, gamma36, gamma36, gamma36) / 6.0
delta = Fg - 264
print(f"\n[基準] F(γ) = {Fg:.15f}")
print(f"  Δ = F(γ) − 264 = {delta:.15f}")
print(f"  1/Δ = {1/delta:.10f}")
print(f"  1/Δ − 12 = {1/delta - 12:.10f}")

# ─── 1. κ-block 分解 ───
print("\n[1] κ-block 分解: 邊個 block 出分數部分?")
# 按 generation 分組: gen0=0-11, gen1=12-23, gen2=24-35
gen = np.array([0]*12 + [1]*12 + [2]*12)
F_total = 0
F_by_gen = {}
for g0, g1, g2 in itertools.product([0,1,2], repeat=3):
    mask = (gen == g0)[:, None, None] & (gen == g1)[None, :, None] & (gen == g2)[None, None, :]
    F_block = np.einsum("ijk,i,j,k", kappa * mask, gamma36, gamma36, gamma36) / 6.0
    label = f"({g0},{g1},{g2})"
    F_by_gen[label] = float(F_block)
    print(f"  F{label} = {F_block:.8f}")

print(f"\n  F_total = {sum(F_by_gen.values()):.8f} (應 = {Fg:.8f})")
check("block 總和 = F(γ)", abs(sum(F_by_gen.values()) - Fg) < 1e-10)

# 邊個 block 貢獻分數部分?
for label, val in sorted(F_by_gen.items()):
    frac = val - round(val)
    if abs(frac) > 1e-10:
        print(f"  F{label} = {val:.8f} (分數部分 {frac:+.8f})")

# ─── 2. γ_29/36 修正 ───
print("\n[2] γ_29/36 修正項")
g29_36 = gamma44[28] / 36  # γ_29/36 (0-index: 28)
print(f"  γ_29/36 = {g29_36:.15f}")
print(f"  Δ = {delta:.15f}")
print(f"  Δ − γ_29/36 = {delta - g29_36:.15f}")
diff = delta - g29_36
print(f"  diff/Δ = {diff/delta*100:.6f}%")

# 求 diff 嘅結構: diff = -5.1267e-5
# 試: diff = -γ_1/36?  γ_1 = 4sin²(π/88)
g1_36 = gamma44[0] / 36
print(f"  γ_1/36 = {g1_36:.15f}")
print(f"  diff + γ_1/36 = {diff + g1_36:.15f}")
print(f"  diff / (-γ_1) = {diff/(-gamma44[0]):.6f}")

# 更一般: diff = a·γ_i + b·γ_j
print("\n  diff 線性組合搜索 (γ_i 係數):")
for i in range(1, 45):
    for j in range(i, 45):
        for ci in range(-5, 6):
            for cj in range(-5, 6):
                if ci == 0 and cj == 0:
                    continue
                val = ci*gamma44[i-1] + cj*gamma44[j-1]
                err = abs(val - diff)
                if err < 5e-7:  # < 0.00005%
                    print(f"    {ci}γ_{i}+{cj}γ_{j} = {val:.10f} (err {err:.2e})")

# ─── 3. 連分數展開 ───
print("\n[3] 連分數展開")
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

cf_delta = cf(delta, 20)
print(f"  Δ 連分數: {cf_delta}")
print(f"  = {cf_delta[0]} + 1/({cf_delta[1]} + 1/({cf_delta[2]} + ...))")

# 睇有理逼近
from fractions import Fraction
for max_den in [100, 1000, 10000, 100000]:
    f = Fraction(delta).limit_denominator(max_den)
    err = abs(float(f) - delta)/delta
    print(f"  有理逼近 (den≤{max_den:6d}): {f.numerator:6d}/{f.denominator:6d} = {float(f):.12f} (err {err:.2e})")

# 1/Δ 嘅連分數
cf_inv = cf(1/delta, 20)
print(f"\n  1/Δ 連分數: {cf_inv}")
# 1522/125?
print(f"  1522/125 = {1522/125:.10f} (err {abs(1522/125 - 1/delta)/1/delta*100:.4f}%)")

# ─── 4. Δ × N 近整數 ───
print("\n[4] Δ × N 近整數")
for N in [44, 88, 90, 134, 946, 36, 66, 178, 264, 283, 484, 462, 124, 133, 98, 73, 198, 350, 904]:
    val = delta * N
    near = abs(val - round(val))
    marker = " ★" if near < 0.01 else ""
    if near < 0.1:
        print(f"  Δ×{N:4d} = {val:.10f} (近整數 {round(val)}, 差 {near:.6f}){marker}")

# ─── 5. 1/Δ 嘅結構身份 ───
print("\n[5] 1/Δ 結構身份")
inv = 1/delta
checks = {
    "12 + 44/250": 12 + 44/250,
    "12 + 22/125": 12 + 22/125,
    "12 + γ₁": 12 + gamma44[0],
    "12 + γ₄": 12 + gamma44[3],
    "12 + γ₆/φ": 12 + gamma44[5]/phi,
    "12 + 2γ₆": 12 + 2*gamma44[5],
    "12 + 1/5.68": 12 + 1/5.68,
    "h¹¹/3 + 22/125": 36/3 + 22/125,
    "44/φ⁴": 44/phi**4,
    "90/φ⁵": 90/phi**5,
    "88/φ⁵": 88/phi**5,
    "134/φ⁶": 134/phi**6,
    "946/φ⁸": 946/phi**8,
    "283/φ⁷": 283/phi**7,
    "44/γ₁₃": 44/gamma44[12],
    "88/γ₂₉": 88/gamma44[28],
    "90/γ₂₉": 90/gamma44[28],
    "12 + γ₂₉/γ₃₆": 12 + gamma44[28]/gamma44[35],
    "12 + 1/5.680": 12 + 1/5.680,
    "12 + 1/(5+γ₄)": 12 + 1/(5+gamma44[3]),
    "12 + 1/(L₅+L₆)": 12 + 1/(11+18),
    "12 + 1/(L₇+γ₁)": 12 + 1/(7+gamma44[0]),
    "12 + γ₁/γ₂₉": 12 + gamma44[0]/gamma44[28],
    "12 + γ₄/γ₂₉": 12 + gamma44[3]/gamma44[28],
}
print(f"  1/Δ = {inv:.10f}")
for name, val in sorted(checks.items(), key=lambda x: abs(x[1]-inv)):
    err = abs(val - inv)/inv*100
    marker = " ★" if err < 0.01 else (" ◈" if err < 0.1 else "")
    print(f"    {name:24s} = {val:.10f} (err {err:.4f}%){marker}")

# ─── 6. Δ = 1/(12 + 1/(5 + ...)) 連分數逼近 ───
print("\n[6] 連分數逼近")
# 1/Δ = 12 + 1/(5 + 1/(1 + 1/(...)))
# 所以 Δ = 1/(12 + 1/(5 + 1/(1 + ...)))
# 各層截斷:
conv = []
a = cf_inv
for n in range(1, min(8, len(a))):
    # 計算第 n 層 convergent
    num, den = 1, a[n-1]
    for k in range(n-2, -1, -1):
        num, den = den, a[k]*den + num
    # 倒返: 1/(first + 1/(...))
    num, den = den, num  # 取倒數
    # 加番第一項
    num, den = a[0]*den + num, den
    val = num/den
    err = abs(val - delta)/delta*100
    print(f"  convergent {n}: {num}/{den} = {val:.12f} (err {err:.4f}%)")
    conv.append((n, num, den, val, err))

# ─── 7. Δ 同 κ 譜嘅關係 ───
print("\n[7] Δ 同 κ 譜")
# Σκ(2,2,2) = 88 (O62 發現)
# 264 = −2(Σκ + χ), χ = −124
# Δ = F(γ) − 264. 可能 Δ = f(κ 譜, γ 譜)
# 嘗試: Δ = (Σκ_i γ_i) / (Σγ × something)?

# 每個 κ 嘅貢獻分佈
print("  κ 非零數: 1341")
print(f"  Σκ = {kappa.sum():.0f}")
print(f"  Σκ(2,2,2) = {kappa[24:,24:,24:].sum():.0f}")

# 每個 index 嘅 κ 和
kappa_sum_i = kappa.sum(axis=(1,2))
print(f"  κ 行和 (max 5): {np.sort(kappa_sum_i)[-5:]}")
print(f"  κ 行和 (min 5): {np.sort(kappa_sum_i)[:5]}")

# ─── 8. 總結: 最佳候選 ───
print("\n" + "=" * 72)
print("攻堅 1 總結: Δ 最佳候選")
print("=" * 72)
print(f"""
  Δ = {delta:.15f}
  1/Δ = {1/delta:.10f}
  
  1. γ_29/36 = {g29_36:.15f} (err {abs(g29_36-delta)/delta*100:.4f}%)
  2. 125/1522 = {125/1522:.15f} (err {abs(125/1522-delta)/delta*100:.4f}%)
  3. Δ + γ_1/36 = {delta + gamma44[0]/36:.15f} (e.g. Δ = γ_29/36 - γ_1/36 + ...)
  
  連分數 convergent:
""")
for n, num, den, val, err in conv[:3]:
    print(f"    {n}: {num}/{den} = {val:.12f} (err {err:.4f}%)")

out = {
    "delta": float(delta),
    "inv_delta": float(1/delta),
    "cf_delta": cf_delta,
    "cf_inv": cf_inv,
    "gamma29_over_36": float(g29_36),
    "diff_g29": float(delta - g29_36),
    "block_decomp": F_by_gen,
    "convergents": [{"n": n, "num": int(num), "den": int(den), "val": float(val), "err_pct": float(err)} for n, num, den, val, err in conv],
    "passed": passed, "failed": failed,
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "01_delta_search.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")