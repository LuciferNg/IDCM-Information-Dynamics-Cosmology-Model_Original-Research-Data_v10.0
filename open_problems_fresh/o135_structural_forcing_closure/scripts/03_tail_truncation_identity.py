#!/usr/bin/env python3
"""
O135 — scripts/03: v9.0 φ 近似 = v10.0 精確式嘅 Lucas 尾截斷 (Tail-truncation identity)
========================================================================================
發現: v9.0 嘅 φ-power 形式唔係隨機擬合 — 佢哋係 v10.0 精確有理式嘅 **Lucas 尾 (leading
      truncation)**: 精確值 − φ 形式 = (√5 φ⁻¹⁰)-級項。即 v9.0 = v10.0 嘅一階截斷。

驗證兩個已註冊恆等式 (O148 / O33):
  (T1) 41/60 − 4/(φ⁴−1)          = √5 φ⁻¹⁰ / [60(3φ+1)]
  (T2) 19/123 − φ⁻¹/4            = −√5 φ⁻¹⁰ / 492
並量度 v_SM 側 (T3: 246.2196 − (φ¹¹+φ⁸)) 係唔係同級尾項。
"""
import json, os
import mpmath as mp

mp.mp.dps = 50
phi = (1 + mp.sqrt(5)) / 2
results = []
def chk(name, cond, detail):
    results.append((name, bool(cond), detail))
    print(f"  [{'✔' if cond else '✘'}] {name}\n       {detail}")

print("=" * 80)
print("O135 scripts/03 — v9.0 φ 形式 = v10.0 精確式嘅 Lucas 尾截斷")
print("=" * 80)

# T1: Ω_Λ
lhs = mp.mpf(41)/60 - 4/(phi**4 - 1)
rhs = mp.sqrt(5) * phi**-10 / (60*(3*phi + 1))
dev1 = abs(lhs/rhs - 1)
chk("T1  Ω_Λ 尾: 41/60 − 4/(φ⁴−1) = √5φ⁻¹⁰/[60(3φ+1)]", dev1 < mp.mpf('1e-30'),
    f"LHS={mp.nstr(lhs,20)}  RHS={mp.nstr(rhs,20)}  dev={mp.nstr(dev1,3)} (O148)")

# T2: ε
lhs2 = mp.mpf(19)/123 - phi**-1/4
rhs2 = -mp.sqrt(5) * phi**-10 / 492
dev2 = abs(lhs2/rhs2 - 1)
chk("T2  ε 尾: 19/123 − φ⁻¹/4 = −√5φ⁻¹⁰/492", dev2 < mp.mpf('1e-30'),
    f"LHS={mp.nstr(lhs2,20)}  RHS={mp.nstr(rhs2,20)}  dev={mp.nstr(dev2,3)} (O33)")

# T3: V_EW 側 — 檢定 v9.0 φ 形係唔係同級 Lucas 尾截斷 (發現: 唔係)
tail3 = mp.mpf('246.2196') - (phi**11 + phi**8)
scale = mp.sqrt(5) * phi**-10
ratio3 = tail3 / scale
chk("T3  V_EW 側: v_SM − (φ¹¹+φ⁸) **唔係** Lucas 尾截斷",
    abs(ratio3) > mp.mpf(10),
    f"v_SM−(φ¹¹+φ⁸)={mp.nstr(tail3,6)}  vs Lucas 尾 √5φ⁻¹⁰={mp.nstr(scale,6)}  "
    f"比值={mp.nstr(ratio3,6)} ≫ 1 ⟹ V_EW φ 形 **唔係** 精確式嘅一階截斷, 係獨立 φ 巧合 "
    f"(區別於 ε/Ω_Λ: 佢哋係真 Lucas 尾)")

# T4: φ⁻¹⁰ = 1/(L₁₀·φ... ) 身份 — φ⁻¹⁰ 同 1/123 嘅關係 (L₁₀=123)
chk("T4  Lucas 尾標度 = φ⁻¹⁰ 階", abs(phi**-10*123 - 1) < mp.mpf('1e-2'),
    f"φ⁻¹⁰={mp.nstr(phi**-10,10)}, 123φ⁻¹⁰={mp.nstr(123*phi**-10,10)} "
    f"(≈1 ⟹ φ⁻¹⁰ ≈ 1/L₁₀=1/123, 尾項天然係 Lucas 階)")

npass = sum(1 for r in results if r[1])
print(f"\n{'='*80}\nRESULT: {npass}/{len(results)} PASS — 尾截斷恆等式確認\n{'='*80}")
print("結論: ε / Ω_Λ 嘅 v9.0 φ 形式 = v10.0 精確式嘅**一階 (Lucas 尾) 截斷** (EXACT 恆等式);")
print("      V_EW 嘅 v9.0 φ 形式**唔係**尾截斷 (比值 13×) = 獨立 φ 巧合 ⟹ 更強烈 🔴。")

out = {"T1_dev": mp.nstr(dev1,3), "T2_dev": mp.nstr(dev2,3), "T3_ratio": mp.nstr(ratio3,6),
       "result": f"{npass}/{len(results)} PASS"}
os.makedirs("data", exist_ok=True)
with open("data/03_tail_truncation.json", "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("→ data/03_tail_truncation.json")
