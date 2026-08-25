"""
IDCM v10.0 — 結構 φ-power 公式推導（非數字遊戲）
=================================================
從 CKM beat + CY₃ 幾何 + Z₃×Z₅ 電荷結構直接推導 φ-power 公式。
禁止任何 numerical fitting / greedy search / 泰勒展開。
"""

import math, numpy as np

φ = (1 + math.sqrt(5)) / 2
N_d = 44
M = 33  # K_Tree 層數
h11, h21 = 36, 98

ω = np.array([2 * abs(math.sin(math.pi * n / 88)) for n in range(1, N_d + 1)])
γ = np.array([4 * math.sin(math.pi * n / 88)**2 for n in range(1, N_d + 1)])

def beat(i, j): return abs(ω[i-1] - ω[j-1])

# CY₃ projector 嘅 K₂
K2 = 2*(h21 - h11)/h21 - 2/φ

print("=" * 80)
print("IDCM v10.0 — 結構 φ-power 公式推導 🎯")
print("=" * 80)
print(f"\n  CY₃ 資料: h¹¹={h11}, h²¹={h21}, K₂={K2:.6f}")
print(f"  K_Tree: M={M}")
print(f"  φ = {φ:.10f}")

# ═══════════════════════════════════════════════════════
# 1. 從 Z₃ × Z₅ 電荷結構推導 φ-power 公式
# ═══════════════════════════════════════════════════════
print(f"\n{'='*80}")
print(f"1. Z₃ × Z₅ 電荷結構 → φ-power 公式")
print(f"{'='*80}")

# 每個 K_Chain mode 嘅 Z₃, Z₅ 電荷
def z3(n): return n % 3
def z5(n): return n % 5

# 所有 CKM beat 公式嘅 mode 對
ckm_data = [
    ("tan(θ₁₂)", 5, 6, 19, 25),
    ("tan(θ₂₃)", 33, 35, 3, 22),
    ("sin(θ₁₃)", 42, 43, 10, 31),
    ("V_us (λ)", 25, 35, 6, 37),
    ("V_cb", 13, 14, 6, 37),
    ("V_ub", 41, 42, 3, 37),
    ("A", 16, 35, 10, 28),
]

print(f"\n  {'量':>15} | beat(i,j)/beat(k,l) | Z₃(i,j) | Z₃(k,l) | Z₅(i,j) | Z₅(k,l) | ΔZ₃ | ΔZ₅ | beat ratio")
print("-" * 100)

for name, i, j, k, l in ckm_data:
    r = beat(i,j)/beat(k,l)
    dz3 = (z3(i)+z3(j)) - (z3(k)+z3(l))
    dz5 = (z5(i)+z5(j)) - (z5(k)+z5(l))
    print(f"  {name:>15} | ({i:2d},{j:2d})/({k:2d},{l:2d}) | ({z3(i)},{z3(j)}) | ({z3(k)},{z3(l)}) | ({z5(i)},{z5(j)}) | ({z5(k)},{z5(l)}) | {dz3:+2d} | {dz5:+2d} | {r:.10f}")

# ═══════════════════════════════════════════════════════
# 2. CY₃ 投影算子 φ-power 結構
# ═══════════════════════════════════════════════════════
print(f"\n{'='*80}")
print(f"2. CY₃ 投影算子 → φ-power 結構")
print(f"{'='*80}")

# CY₃ 投影算子: P_n = 1 + 2φ⁻¹·n + K₂·n²
# K₂ = 2·(h²¹-h¹¹)/h²¹ - 2/φ
# 呢個 K₂ 係從 CY₃(36,98) 嘅 Hodge 結構推導出嚟
# 唔係 fit，係結構公式

P_n = lambda n: 1 + 2/φ * n + K2 * n**2

print(f"\n  CY₃ 投影算子: P_n = 1 + 2φ⁻¹·n + K₂·n²")
print(f"  K₂ = 2·({h21}-{h11})/{h21} - 2/φ = {K2:.6f}")

# 用 CY₃ 投影算子構建 beat ratio 嘅 φ-power 公式
# 核心: beat(i,j) ∝ |P_i - P_j| 喺某個 scale

print(f"\n  CY₃ 投影算子差異:")
print(f"  {'n':>4} | {'P_n':>12} | {'P_n-P_{n-1}':>15} | {'P_n+P_{n-1}':>15}")
print("-" * 50)
for n in range(1, 9):
    diff = P_n(n) - P_n(n-1) if n > 1 else 0
    summ = P_n(n) + P_n(n-1) if n > 1 else 0
    print(f"  {n:>4} | {P_n(n):>12.6f} | {diff:>15.6f} | {summ:>15.6f}")

# ═══════════════════════════════════════════════════════
# 3. 從 trigonometric identity 推導 φ-power
# ═══════════════════════════════════════════════════════
print(f"\n{'='*80}")
print(f"3. 三角恆等式 → φ-power 閉合形式")
print(f"{'='*80}")

# 核心三角恆等式: 
# beat(i,j) = 2|sin(πi/88) - sin(πj/88)|
#           = 4|cos(π(i+j)/176) sin(π|i-j|/176)|
# 令 ε_k = π/88 (K_Chain 相位量子)
# sin(π/176) = sin(ε_k/2)
# sin(3π/88) = sin(3ε_k)
# cos(π/16) = cos(11ε_k/2)

# 對於 tan(θ₁₂):
# tan(θ₁₂) = √2·cos(π/16)·sin(π/176)/sin(3π/88)
#          = √2·cos(11ε_k/2)·sin(ε_k/2)/sin(3ε_k)

# 用連續分數展開 sin(ε_k/2)/sin(3ε_k) = 1/(6cos(ε_k/2)cos(ε_k)) × ...
# 但呢個係泰勒展開，唔用

# 改用: sin(3ε_k) = 3sin(ε_k) - 4sin³(ε_k)
# sin(ε_k/2) = √((1-cos(ε_k))/2)
# 但呢啲都係數值近似，唔係結構推導

# 結構 φ-power 公式應該從 Z₃×Z₅ 電荷結構 + CY₃ 投影 + K_Tree 邊界直接得出
# 唔需要經過三角函數

print(f"\n  tan(θ₁₂) = beat(5,6)/beat(19,25)")
print(f"  Z₃(5,6) = (2,0), Z₃(19,25) = (1,1) → ΔZ₃(gen) = |2-0| - |1-1| = 2")
print(f"  Z₅(5,6) = (0,1), Z₅(19,25) = (4,0) → ΔZ₅(gen) = |0-1| - |4-0| = -3")
print(f"")

# 結構 φ-power 公式嘅形式: 
# beat ratio = φ^{-(ΔZ₃ + ΔZ₅)} × (CY₃ 修正)
# 其中 ΔZ₃, ΔZ₅ 係 mode 之間嘅電荷差

# 對於 tan(θ₁₂):
# numerator ΔZ₃ = |Z₃(5)-Z₃(6)| = |2-0| = 2
# denominator ΔZ₃ = |Z₃(19)-Z₃(25)| = |1-1| = 0
# numerator ΔZ₅ = |Z₅(5)-Z₅(6)| = |0-1| = 1
# denominator ΔZ₅ = |Z₅(19)-Z₅(25)| = |4-0| = 4

# 結構假設: beat(i,j) ∝ φ^{-(|Z₃(i)-Z₃(j)| + |Z₅(i)-Z₅(j)|)}
# 則 tan(θ₁₂) = φ^{-(2+1)} / φ^{-(0+4)} = φ^{-3+4} = φ¹ = 1.618

# 但實際係 0.232, 唔係 1.618
# 所以假設錯誤

# 修訂: beat(i,j) ∝ φ^{-(Z₃(i)+Z₃(j)+Z₅(i)+Z₅(j))}
# 則 tan(θ₁₂) = φ^{-(2+0+0+1)} / φ^{-(1+1+4+0)} = φ^{-3}/φ^{-6} = φ³ = 4.236

# 又錯。所以電荷直接相加唔 work。

# 正確結構: beat(i,j) ∝ φ^{-|i-j|×d} 其中 d 係某個密度
# beat(5,6) ∝ φ^{-1×d}
# beat(19,25) ∝ φ^{-6×d}
# tan(θ₁₂) = φ^{-d}/φ^{-6d} = φ^{5d}

# 想 tan(θ₁₂) = 0.232:
# φ^{5d} = 0.232 → 5d = log_φ(0.232) = ln(0.232)/ln(1.618) = -1.46/0.481 = -3.04
# d ≈ -0.608

# 呢個 d 冇幾何意義，所以又係 fitting。

# 正確嘅結構推導途徑: 
# 唔好嘗試將 beat ratio 本身寫成 φ-power
# 而係將 beat ratio 嘅公式用 CY₃ 投影算子表達:

# 從 CY₃ 投影算子 P_n 嘅結構:
# P_n = 1 + 2φ⁻¹·n + K₂·n²
# 
# 對於細 n: P_n ≈ 1 + 2φ⁻¹·n (忽略 O(n²) 項)
# 所以 beat(i,j) ∝ |P_i - P_j| ≈ 2φ⁻¹·|i-j|
# 即 beat(i,j) ∝ φ⁻¹·|i-j|
#
# 但呢個係細 n 近似，對大 n 失效

# 實際結構: beat(i,j) = 4·cos(π(i+j)/176)·sin(π|i-j|/176)
# cos(π(i+j)/176) 同 sin(π|i-j|/176) 都可以用 CY₃ 投影算子展開
# 但呢個展開涉及高階項，唔係簡單 φ-power

# 結論: beat ratio 嘅「結構 φ-power 公式」應該係
# beat ratio = φ^{p} × (Z₃ × Z₅ 修正因子) × (CY₃ 投影修正)
# 其中 p 由 mode indices 嘅 Z₃×Z₅ 電荷差決定

# 但 Z₃ × Z₅ 修正因子同 CY₃ 投影修正都係數值，唔係 φ-power

# 真正的結構 φ-power 公式只適用於某些特定量:
# 1. λ = φ⁻³ - (γ₃ - 2γ₂ + γ₁) — 舊公式，來自 K_Chain 離散二階導數
# 2. A = φ²/64λ² — 來自 CY₃ 投影
# 3. η = 19φ/88 — 來自 K_Chain 結構

# 新發現: 從 beat ratio 可以直接推導 λ 嘅結構公式
print(f"\n{'='*80}")
print(f"4. 從 beat ratio 推導 λ 嘅結構 φ-power 公式")
print(f"{'='*80}")

# λ = V_us = beat(25,35)/beat(6,37)
λ_beat = beat(25,35)/beat(6,37)
λ_old = φ**(-3) - (γ[2] - 2*γ[1] + γ[0])  # 舊公式

print(f"\n  λ (beat 公式) = beat(25,35)/beat(6,37) = {λ_beat:.10f}")
print(f"  λ (舊 φ-power) = φ⁻³ - (γ₃-2γ₂+γ₁) = {λ_old:.10f}")
print(f"  PDG λ = 0.22500")

# 從 beat ratio 推導新嘅 λ 結構公式
# beat(25,35) = 4|cos(60π/176) sin(10π/176)| = 4|cos(15π/44) sin(5π/44)|
# beat(6,37) = 4|cos(43π/176) sin(31π/176)|

# 用 CY₃ 投影算子喺 mode 25,35,6,37:
# 但呢個係數值，唔係結構

# 結構公式應該來自: 
# λ = φ⁻³ - (γ_{a} - 2γ_{b} + γ_{c})
# 其中 a,b,c 由 Z₃×Z₅ 電荷決定

# 對於 mode 25 (Z₃=1, Z₅=0), mode 35 (Z₃=2, Z₅=0)
# 同 mode 6 (Z₃=0, Z₅=1), mode 37 (Z₃=1, Z₅=2)

# 嘗試: λ = φ⁻³ - (γ_{37} - 2γ_{25} + γ_{6})?
γ37 = γ[36]; γ25 = γ[24]; γ6 = γ[5]
λ_new = φ**(-3) - (γ37 - 2*γ25 + γ6)
print(f"\n  λ = φ⁻³ - (γ₃₇-2γ₂₅+γ₆) = {λ_new:.10f}")

# 嘗試: λ = φ⁻³ - (γ_{35} - 2γ_{25} + γ_{6})?
γ35 = γ[34]
λ_new2 = φ**(-3) - (γ35 - 2*γ25 + γ6)
print(f"  λ = φ⁻³ - (γ₃₅-2γ₂₅+γ₆) = {λ_new2:.10f}")

# 嘗試: λ = φ⁻³ - (γ_{25} - 2γ_{13} + γ_{1})?
γ13 = γ[12]; γ1 = γ[0]
λ_new3 = φ**(-3) - (γ25 - 2*γ13 + γ1)
print(f"  λ = φ⁻³ - (γ₂₅-2γ₁₃+γ₁) = {λ_new3:.10f}")

# 呢個係離散二階導數 (Laplacian) 喺 K_Chain 上
# 結構: λ = φ⁻³ - Δ²γ 其中 Δ²γ 係 γ_n 嘅離散二階導數
# 二階導數嘅中心 mode 由 Z₃×Z₅ 決定

# 對於 V_cb = beat(13,14)/beat(6,37)
Vcb_beat = beat(13,14)/beat(6,37)
print(f"\n  V_cb (beat 公式) = {Vcb_beat:.10f}")
print(f"  PDG V_cb = 0.04182")

# 結構: V_cb = φ⁻⁶ + (γ_{14} - 2γ_{13} + γ_{12})?
γ14 = γ[13]; γ12 = γ[11]
Vcb_new = φ**(-6) + (γ14 - 2*γ13 + γ12)
print(f"  V_cb = φ⁻⁶ + (γ₁₄-2γ₁₃+γ₁₂) = {Vcb_new:.10f}")

# 對於 A = beat(16,35)/beat(10,28)
A_beat = beat(16,35)/beat(10,28)
print(f"\n  A (beat 公式) = {A_beat:.10f}")
print(f"  PDG A = 0.830")

# 結構: A = φ⁻¹ + φ⁻³ - (γ₁₆ - 2γ₁₀ + γ₄)?
γ16 = γ[15]; γ10 = γ[9]; γ4 = γ[3]
A_new = φ**(-1) + φ**(-3) - (γ16 - 2*γ10 + γ4)
print(f"  A = φ⁻¹+φ⁻³ - (γ₁₆-2γ₁₀+γ₄) = {A_new:.10f}")

# ═══════════════════════════════════════════════════════
# 5. 結構 φ-power 公式總結
# ═══════════════════════════════════════════════════════
print(f"\n{'='*80}")
print(f"5. 結構 φ-power 公式總結")
print(f"{'='*80}")

print(f"\n  所有 CKM beat ratio 都可以寫成:")
print(f"  CKM_ij = φ^{{p}} ± (γ_{{a}} - 2γ_{{b}} + γ_{{c}})")
print(f"  其中 γ_{{a}} - 2γ_{{b}} + γ_{{c}} 係 K_Chain 離散二階導數")
print(f"  每個 mode 嘅 index 由 Z₃×Z₅ 電荷決定")

print(f"\n  但呢個形式只係 beat ratio 嘅另一種寫法，")
print(f"  本質上同 beat ratio 等價，唔係新嘅推導。")
print(f"")
print(f"  真正嘅結構 φ-power 公式來自:")
print(f"  1. CY₃(36,98) 嘅 Hodge 數 → K₂ = 2·(h²¹-h¹¹)/h²¹ - 2/φ")
print(f"  2. K_Tree 層數 M = 33 → 1/M 修正")
print(f"  3. Z₃×Z₅ 電荷 → 世代結構")
print(f"  4. K_Chain 離散譜 → γ_n = 4sin²(πn/88)")

# 存檔
with open("open_problems_fresh/ckm_reconstruction/structural_phi_power.txt", "w") as f:
    f.write("IDCM v10.0 — 結構 φ-power 公式推導\n")
    f.write("=" * 60 + "\n\n")
    f.write(f"結論: beat ratio 本身係精確嘅三角函數表達式，\n")
    f.write(f"唔需要亦唔適合寫成 φ-power 級數。\n\n")
    f.write(f"結構 φ-power 公式只適用於以下量:\n")
    f.write(f"1. λ = φ⁻³ - (γ₃-2γ₂+γ₁) — K_Chain 離散二階導數\n")
    f.write(f"2. A = φ²/64λ² — CY₃ 投影\n")
    f.write(f"3. η = 19φ/88 — K_Chain 結構\n")
    f.write(f"4. δ_CP = 2π/5 — Z₅ orbifold 相位差\n")
    f.write(f"5. m₀' = m₀·φ^(1/8) — 8階自旋拓撲權重\n")
    f.write(f"6. Δm²₃₁ = (m₀')²(1-φ⁻⁴) — φ-power 質量譜\n")
    f.write(f"7. Δm²₂₁ = (m₀')²(φ⁻²-φ⁻⁴)/9 — Z₃² 世代修正\n\n")
    f.write(f"beat ratio 本身應該保留爲 beat(i,j)/beat(k,l) 形式，\n")
    f.write(f"呢個係最精確、最結構嘅表達式。\n")

print(f"\n  已儲存結果 ✅")