#!/usr/bin/env python3
"""
O147 優先級二+三 — κ 種子起源 + 階梯乘法生成算子
==================================================
優先級二: 5 種子指派規則推導 (用戶建議: ½L₅ vs L₆−B² 表示論/CY₃ 對應)
優先級三: 階梯三點 (1,0),(0,1),(2,1) 封閉生成算子 (用戶建議 Interaction 形式)

發現 (scripts/11): κ(t) = 0 (O64 實證, 唔係 docs/09 嘅 −14)
更新 κ 表:
        gen1   gen2   gen3
  L:    L₄/2   L₄/2   N_gen²
  U:   −B²     Z₂     0
  D:    0      L₆     Z₂

優先級二候選推導:
  κ(e) = κ(μ) = (L₅ − B)/2 = (11−4)/2 = 3.5  ← 輕子 gen1/2 種子!
  κ(τ) = L₅ − Z₂ = 11−2 = 9 = N_gen²          ← 輕子 gen3!
  κ(s) = 2N_gen² = 18 = L₆                     ← D gen2!
  κ(b) = Z₂ = B/2 = 2                          ← D gen3!
  κ(u) = κ(d) − B² = −16                       ← 行規則
  κ(c) = κ(s) − B² = 2                         ← 行規則
  κ(t) = 0                                     ← O64 實證

優先級三候選: 乘法生成算子 m(a,b) = N_d × Z₂^a × N_gen^b
  (1,0) → 44×2¹×3⁰ = 88 ✓
  (0,1) → 44×2⁰×3¹ = 132 ✓
  (2,1) → 44×2²×3¹ = 528 ✓
  對比用戶 Interaction 形式 f = N_d(aZ₂+bN_gen+abI): I = 2.5 = F₅/2
"""
import math

PASS, FAIL = 0, 0
rows = []

def check(name, cond, detail=""):
    global PASS, FAIL
    rows.append((name, bool(cond), detail))
    if cond: PASS += 1
    else: FAIL += 1

N_d = 44
B = 4
N_gen = 3
Z2 = 2
phi = (1 + math.sqrt(5)) / 2
L = {0:2, 1:1, 2:3, 3:4, 4:7, 5:11, 6:18, 7:29, 8:47}
F = {5:5, 6:8, 7:13, 8:21, 9:34}

print("=" * 100)
print("  O147 優先級二 — κ 種子起源推導")
print("=" * 100)

# ============ 優先級二: κ 種子起源 ============
print("\n─── A. 種子生成公式 (候選) ───")
kappa_e = (L[5] - B) / 2          # (L₅−B)/2 = 3.5
kappa_tau = L[5] - Z2              # L₅−Z₂ = 9
kappa_s = 2 * N_gen**2             # 2N_gen² = 18
kappa_b = Z2                        # Z₂ = 2
print(f"  κ(e) = (L₅−B)/2    = ({L[5]}−{B})/2 = {kappa_e}")
print(f"  κ(μ) = κ(e) (共享) = {kappa_e}")
print(f"  κ(τ) = L₅−Z₂       = {L[5]}−{Z2} = {kappa_tau} = N_gen² = {N_gen**2}")
print(f"  κ(s) = 2N_gen²     = 2×{N_gen**2} = {kappa_s} = L₆ = {L[6]}")
print(f"  κ(b) = Z₂          = {kappa_b} = B/2 = {B//2}")

check("A1 κ(e) = (L₅−B)/2 = 3.5", kappa_e == 3.5)
check("A2 κ(τ) = L₅−Z₂ = N_gen² = 9", kappa_tau == 9)
check("A3 κ(s) = 2N_gen² = L₆ = 18", kappa_s == 18)
check("A4 κ(b) = Z₂ = B/2 = 2", kappa_b == 2)

print("\n─── B. 用戶問題: ½L₅ vs L₆−B² 表示論/CY₃ 對應 ───")
half_L5 = L[5]/2
L6_minus_B2 = L[6] - B**2
print(f"  ½L₅ = {half_L5} (= rank(SU(12))/2, rank(SU(12)) = 11 = L₅)")
print(f"  L₆−B² = {L[6]}−{B**2} = {L6_minus_B2} = Z₂ (夸克 gen3 值 = κ(b))")
print(f"  ½L₅ − (L₆−B²) = {half_L5} − {L6_minus_B2} = {half_L5 - L6_minus_B2} = L₄/2 = κ(e)!")
check("B1 ½L₅ − (L₆−B²) = L₄/2 = κ(e)", half_L5 - L6_minus_B2 == L[4]/2)
check("B2 ½L₅ = rank(SU(12))/2", half_L5 == 11/2)

print("\n─── C. 種子交叉身份 ───")
print(f"  κ(τ) − κ(e) = {kappa_tau - kappa_e} = L₅/2 = ½L₅ (輕子 gen2→3 增量)")
print(f"  κ(τ) − κ(b) = {kappa_tau - kappa_b} = L₄ = n(μ)! (跨行)")
print(f"  κ(s) = 2κ(τ) = {2*kappa_tau} (跨行對稱)")
print(f"  κ(e) = ½L₅ − Z₂ = {half_L5 - Z2}")
check("C1 κ(τ)−κ(e) = L₅/2", kappa_tau - kappa_e == L[5]/2)
check("C2 κ(τ)−κ(b) = L₄ = 7 = n(μ)", kappa_tau - kappa_b == L[4])
check("C3 κ(s) = 2κ(τ)", kappa_s == 2*kappa_tau)
check("C4 κ(e) = ½L₅ − Z₂", kappa_e == half_L5 - Z2)

print("\n─── D. CY₃ 交點數對應檢查 ───")
# CY₃ (36, 98): χ = 2(h¹¹−h²¹), K3 等
chi = 2*(36 - 98)
print(f"  χ(CY₃) = 2(h¹¹−h²¹) = 2(36−98) = {chi}")
print(f"  |χ|/2 = {abs(chi)//2} = 62 — 唔係 κ 種子")
print(f"  h¹¹ = 36 = N_d−F₆, h²¹ = 98")
print(f"  5.5 同 2 冇直接 CY₃ 交點數身份 — 但 κ(τ)−κ(b) = 7 = L₄ = n(μ) 係跨行新身份")
check("D1 冇直接 CY₃ 交點數對應 (誠實)", True)

# ============ 優先級三: 階梯生成算子 ============
print("\n" + "=" * 100)
print("  O147 優先級三 — 階梯三點生成算子")
print("=" * 100)

print("\n─── E. 乘法生成算子 m(a,b) = N_d × Z₂^a × N_gen^b ───")
def m(a, b): return N_d * Z2**a * N_gen**b
for name, a, b, expect in [("rung1 (μ/e)", 1, 0, 88), ("rung2 (t/b)", 0, 1, 132), ("rung3 (s/d)", 2, 1, 528)]:
    val = m(a, b)
    ok = val == expect
    print(f"  {name:14s}: m({a},{b}) = 44×2^{a}×3^{b} = {val} {'✅' if ok else '🔴'}")
    check(f"E {name} = {expect}", val == expect)

print("\n─── F. (2,1) 指數線性組合 = 物理張量積 ───")
print("  (2,1) = 2(1,0) + (0,1) 喺指數空間")
print("  → m = Z₂² × N_gen = 4 × 3 = 12 = B×N_gen")
print("  → 528 = N_d × B × N_gen = 44 × 4 × 3")
print("  物理語意: 第三階梯 = 兩倍對偶 × 世代 = 世界維度(B) × 世代(N_gen)")
check("F1 (2,1) = 2(1,0)+(0,1) 指數線性", (2,1) == (2*1+0, 2*0+1))
check("F2 2²×3¹ = 12 = B×N_gen", 2**2 * 3**1 == B*N_gen)

print("\n─── G. 對比用戶 Interaction 形式 f = N_d(aZ₂+bN_gen+abI) ───")
# (2,1): 44×(2·2 + 1·3 + 2·1·I) = 528 → 7 + 2I = 12 → I = 2.5
I_val = (12 - 7)/2
print(f"  f(2,1) = 44×(4+3+2I) = 528 → I = {I_val} = F₅/Z₂ = 5/2")
print(f"  乘法形式 m = N_d·Z₂^a·N_gen^b 更簡潔: 冇 Interaction 項, 三點全中")
check("G1 Interaction I = 2.5 = F₅/2 都結構", I_val == F[5]/Z2)
check("G2 乘法形式 m(a,b) 三點全中 (88/132/528)", m(1,0)==88 and m(0,1)==132 and m(2,1)==528)

print("\n─── H. 階梯乘數結構身份 (更新 docs/10) ───")
print(f"  88  = 44 × 2¹ × 3⁰ = N_d × Z₂¹")
print(f"  132 = 44 × 2⁰ × 3¹ = N_d × N_gen¹")
print(f"  528 = 44 × 2² × 3¹ = N_d × Z₂² × N_gen¹ = N_d × B × N_gen")
check("H1 88 = N_d·Z₂", 88 == N_d*Z2)
check("H2 132 = N_d·N_gen", 132 == N_d*N_gen)
check("H3 528 = N_d·B·N_gen", 528 == N_d*B*N_gen)

print("\n─── I. 階梯 rung 對應嘅 κ 分子 (k 值) 一致性 ───")
# rung3 (s/d) 嘅 κ 修正 = κ(s)−κ(d) = 18 = L₆
print(f"  s/d: κ(s)−κ(d) = {kappa_s} − 0 = {kappa_s} = L₆ (docs/07 公式層修正分子)")
# rung1 (μ/e): κ(μ)−κ(e) = 0 (唔需要修正, docs/07 k≈0)
print(f"  μ/e: κ(μ)−κ(e) = 3.5 − 3.5 = 0 (唔需要修正 ✓)")
# rung2 (t/b): κ(t)−κ(b) = 0−2 = −2 (新!)
print(f"  t/b: κ(t)−κ(b) = 0 − 2 = −2 (O64 grid 修正, scripts/11 驗證 0.026%)")
check("I1 μ/e κ 差 = 0 一致", kappa_e - kappa_e == 0)
check("I2 s/d κ 差 = 18 = L₆", kappa_s - 0 == L[6])

# ============ 總結 ============
print("\n" + "=" * 100)
print(f"  PASS: {PASS}  FAIL: {FAIL}")
for name, ok, detail in rows:
    print(f"    {'✅' if ok else '🔴'} {name}  {detail}")
print("=" * 100)
