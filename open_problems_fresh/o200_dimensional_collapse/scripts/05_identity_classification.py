#!/usr/bin/env python3
"""
O200 script 05 — ③ 代數恆等式 vs 匹配 分類
==============================================
三類分清（本 O 方法論核心）:
  (a) 恆等式 IDENTITY  — 由定義精確導出, 唔受密度檢定
  (b) 預言殘差 RESIDUAL — 導出量 vs 獨立量度, 檢定 = 量度誤差
  (c) 池子匹配 MATCH    — 公式搜索命中目標, 檢定 = 密度/null

Run: /usr/bin/python3 scripts/05_identity_classification.py
"""
import sympy as sp

print("="*84)
print("O200 ③ 代數恆等式 vs 匹配 分類 (sympy 符號驗證)")
print("="*84)

# 符號
R, om, c, lP, tP, TR, a0 = sp.symbols('R omega c l_Pl t_Pl T_ring a0', positive=True)

# ---------- (a) 恆等式候選 ----------
print("\n[(a) 恆等式 — 由定義精確導出]")
print("-"*84)

# I1: N_world/N_ring = c_W/(2πc)
# 定義: l_Pl = c·t_Pl ; T_ring = 2π/ω ; c_W = R·ω
lhs1 = (R/(c*tP))/((2*sp.pi/om)/tP)
rhs1 = (R*om)/(2*sp.pi*c)
d1 = sp.simplify(lhs1 - rhs1)
print(f"\nI1. N_world/N_ring = c_W/(2πc)")
print(f"    LHS = {sp.simplify(lhs1)}")
print(f"    RHS = {sp.simplify(rhs1)}")
print(f"    差 = {d1}   →  {'✅ 恆等式' if d1 == 0 else '❌'}")

# I2: a₀/(c²/R) = 1/(2π)   (a₀ ≡ c²/2πR)
lhs2 = (c**2/(2*sp.pi*R))/(c**2/R)
d2 = sp.simplify(lhs2 - 1/(2*sp.pi))
print(f"\nI2. a₀/(c²/R) = 1/(2π)   [a₀ ≡ c²/2πR 定義式]")
print(f"    LHS = {sp.simplify(lhs2)}")
print(f"    差 = {d2}   →  {'✅ 恆等式 (定義式)' if d2 == 0 else '❌'}")

# I3: T_ring = 2π/ω ⟹ T_ring/τ = 2π
lhs3 = (2*sp.pi/om)/(1/om)
d3 = sp.simplify(lhs3 - 2*sp.pi)
print(f"\nI3. T_ring/τ = 2π   [τ ≡ 1/ω]")
print(f"    LHS = {sp.simplify(lhs3)}")
print(f"    差 = {d3}   →  {'✅ 恆等式' if d3 == 0 else '❌'}")

# I4: R/a = 88  (a ≡ R/88)
a_sym = sp.Symbol('a', positive=True)
lhs4 = R/(R/88)
d4 = sp.simplify(lhs4 - 88)
print(f"\nI4. R_world/a = 88   [a ≡ R_world/88 定義式]")
print(f"    LHS = {sp.simplify(lhs4)}")
print(f"    差 = {d4}   →  {'✅ 恆等式 (定義式)' if d4 == 0 else '❌'}")

# ---------- (b) 預言殘差候選 ----------
print("\n[(b) 預言殘差 — 導出量 vs 獨立量度]")
print("-"*84)
print("""
R1. c_W/c = R_world·ω_ring/c
    導出 = 1.0019283 ; 量度 = 1 (SI 精確定義 c)
    殘差 = 0.1928%  ← 真殘差（c 精確, 冇量度誤差可推卸）
    ⚠️ 唔受池子密度檢定 — 呢個係【預言 vs 定義值】, 唔係【搜索命中】
    判定: 🟡 結構關係 c_W = R_world·ω_ring 成立到 0.19%

R2. R_world/(c/ω_ring) = c_W/c   (同上, 同一個殘差)
    O73 H1 聲稱 R_world = c/ω_ring ⟹ 殘差 = 0.1928%
    判定: 🟡 同上

R3. E_kchain = M₀/φ^e (e = 47+37/528)
    O204 U4: 37/528 係有理近似, 差 1.3e-12 → 對數比 e = ln(M₀/E_kchain)/ln φ = 47.0701
    判定: 🟢 對數比精確（但 37/528 係近似）
""")

# ---------- (c) 池子匹配候選 ----------
print("\n[(c) 池子匹配 — 公式搜索命中目標, 受密度檢定]")
print("-"*84)
print("""
M1. M₀/m₇ = 2.0217827 ≈ 93/46 (dev 0.0022%)
    null P = 0.163  → 🔴 唔超越隨機

M2. R_world/r_d = 28.078021 ≈ 197/7 (dev 0.2309%)
    null P = 0.766  → 🔴 唔超越隨機

M3. M₀/E_kchain = 6940.5468 ≈ φ^18 (dev 16.75%)
    null P = 0.789  → 🔴 唔超越隨機

M4. T_CMB/A = 20309.091 ≈ φ^21 (dev 20.52%)
    null P = 0.883  → 🔴 唔超越隨機
""")

print("="*84)
print("[分類總結]")
print("="*84)
print("""
┌─────────────┬──────────────────────────┬─────────────────────┬──────────┐
│ 類別        │ 判準                     │ 檢定方法            │ 本 O 結果│
├─────────────┼──────────────────────────┼─────────────────────┼──────────┤
│ (a) 恆等式  │ 由定義精確導出 (差 = 0)  │ sympy 符號化簡      │ 4/4 ✅   │
│ (b) 預言殘差│ 導出量 vs 獨立量度       │ 量度誤差            │ 3 項 🟡  │
│ (c) 池子匹配│ 公式搜索命中目標         │ 密度/null test      │ 4/4 🔴   │
└─────────────┴──────────────────────────┴─────────────────────┴──────────┘

★★ 核心鐵律: 
   (a) 恆等式唔受密度檢定（唔係匹配）
   (b) 預言殘差唔受池子檢定（用誤差預算）
   (c) 只有池子匹配受密度檢定
   ⟹ 混淆三者 = 方法論錯誤（O136 密度效應嘅根源）
""")
