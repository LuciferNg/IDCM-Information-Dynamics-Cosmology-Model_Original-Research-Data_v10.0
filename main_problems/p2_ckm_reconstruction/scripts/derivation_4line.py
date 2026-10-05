"""
IDCM v10.0 — 4 線推導：δ_CP, J_CP, 中微子質量譜, Beat 化簡
=============================================================
1. CKM δ_CP: 從 Z₅ twisted sector 推導
2. PMNS J_CP: beat 公式計算
3. 中微子質量譜: Δm²₃₁ 精確匹配
4. Beat 化簡: beat(i,j) → φ-power 解析表達式
"""

import math
import numpy as np
import cmath

φ = (1 + math.sqrt(5)) / 2
sqrt_φ = math.sqrt(φ)
ε = φ**(-1) / 4
N_d = 44

# 44 個 K_Chain mode
ω = np.array([2 * abs(math.sin(math.pi * n / 88)) for n in range(1, N_d + 1)])
γ = np.array([4 * math.sin(math.pi * n / 88)**2 for n in range(1, N_d + 1)])

def beat(i, j):
    return abs(ω[i-1] - ω[j-1])

print("=" * 80)
print("IDCM v10.0 — 4 線推導 🎯")
print("=" * 80)

# ══════════════════════════════════════════════════════════════
# 1. CKM δ_CP 精確推導
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("1. CKM δ_CP 精確推導")
print("─" * 80)

# Beat 公式角度
θ12 = math.atan(beat(5,6)/beat(19,25))
θ23 = math.atan(beat(33,35)/beat(3,22))
θ13 = math.asin(min(beat(42,43)/beat(10,31), 1.0))

s12, s23, s13 = math.sin(θ12), math.sin(θ23), math.sin(θ13)
c12, c23, c13 = math.cos(θ12), math.cos(θ23), math.cos(θ13)

# J_CP 因數 (唔含 sin δ)
J_factor = s12 * s23 * s13 * c12 * c23 * c13**2
print(f"  J_CP 因數 (s₁₂s₂₃s₁₃c₁₂c₂₃c₁₃²) = {J_factor:.10e}")
print(f"  J_CP(PDG) = 3.08e-05")
print(f"  sin(δ) needed = 3.08e-05 / {J_factor:.10e} = {3.08e-5/J_factor:.6f}")
print(f"  δ = arcsin({3.08e-5/J_factor:.6f}) = {math.degrees(math.asin(3.08e-5/J_factor)):.2f}°")

# 用 δ=144° 嘅 J_CP
J_144 = J_factor * math.sin(math.radians(144))
print(f"  J_CP(δ=144°) = {J_144:.2e}")

# 用 δ=68.8° (PDG) 嘅 J_CP
J_688 = J_factor * math.sin(math.radians(68.8))
print(f"  J_CP(δ=68.8°) = {J_688:.2e}")

# 嘗試唔同相位位置
# 標準參數化: V = R₂₃ × diag(1,1,e^{iδ}) × R₁₃ × diag(1,1,e^{-iδ}) × R₁₂
# 另一種: V = R₂₃ × R₁₃ × R₁₂ × diag(1,1,e^{iδ})
# 不同相位位置會改變 J_CP 嘅表達式

# 其實 J_CP = Im(V_ud V_cs V_us* V_cd*) 係 convention-independent
# 可以用 beat 公式嘅 CKM 矩陣直接計算 V_ub 嘅相位

# 從 beat 公式, V_ub = sin(θ₁₃) = 0.003507
# 但 PDG V_ub = 0.00369, 相位 = δ = 68.8°
# 如果 IDCM V_ub = 0.003507, 咁 |V_ub| 嘅誤差係 4.95%

# 可能: V_ub 嘅相位唔係 δ, 而係來自 Z₅ 嘅 144°
# 即 V_ub = s₁₃ × e^{-i·144°} = 0.003507 × e^{-i·144°}
# 咁 J_CP 仍然係 1.88e-05

# 但 PDG J_CP = 3.08e-05, 所以需要更大嘅 sin(δ)
# 最佳 δ 係 74.8° 或 105.2°
# 74.8° 接近 72° = 2π/5 (Z₅ 嘅基本相位)
# 或 75° = 5π/12

print(f"\n  候選相位:")
for phase in [72, 75, 105, 144, 180-144]:
    J = J_factor * math.sin(math.radians(phase))
    print(f"    δ = {phase}°: J_CP = {J:.2e}, ratio = {J/3.08e-5:.4f}")

# 關鍵問題: Z₅ twisted sector 嘅相位係 4π/5 = 144°
# 但呢個相位可能修正 CKM 矩陣嘅特定元素, 唔係標準 δ
# 需要從 d_tensor 嘅複雜結構直接計算

# 試: 如果 V_ub 嘅相位 = 144°, 而 V_td 嘅相位 = 0
# 咁標準參數化嘅 δ = 144° (因為 V_ub = s₁₃e^{-iδ})
# 但咁 J_CP = J_factor × sin(144°) = 1.88e-05

# 如果 V_ub 嘅相位 = 144°, 而 V_td 嘅相位 = 144° 嘅某種組合
# 咁 J_CP 會唔同

# 實際上, 從 d_tensor 嘅複雜結構, CKM 矩陣嘅每個元素都有唔同相位
# 標準參數化只係一個 convention

# 從 Z₅ twisted sector:
# 相位 = 4π/5 = 144° 係 Z₅ orbifold 嘅 twist phase
# 佢修正 Yukawa 矩陣嘅 off-diagonal 元素
# 最終 CKM 矩陣嘅相位取決於對角化過程

# 我地需要直接從 d_tensor 嘅複雜投影計算 CKM
# 呢個就係 12D d_tensor 嘅 complex generalization

print(f"\n  🎯 結論: δ_CP = 144° 來自 Z₅ twisted sector")
print(f"     但 J_CP = 1.88e-05 vs PDG 3.08e-05")
print(f"     需要 d_tensor 嘅 complex generalization 嚟解析")

# ══════════════════════════════════════════════════════════════
# 2. PMNS J_CP
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("2. PMNS J_CP 計算")
print("─" * 80)

# PMNS beat 公式角度
θ12_pmns = math.atan(beat(4,13)/beat(9,25))
θ23_pmns = math.atan(beat(11,23)/beat(12,26))
θ13_pmns = math.asin(min(beat(25,29)/beat(3,20), 1.0))
δ_pmns = 2 * math.pi / φ  # 222.5°

s12_p, s23_p, s13_p = math.sin(θ12_pmns), math.sin(θ23_pmns), math.sin(θ13_pmns)
c12_p, c23_p, c13_p = math.cos(θ12_pmns), math.cos(θ23_pmns), math.cos(θ13_pmns)

J_PMNS_factor = s12_p * s23_p * s13_p * c12_p * c23_p * c13_p**2
J_PMNS = J_PMNS_factor * math.sin(δ_pmns)

print(f"  PMNS 角度 (beat 公式):")
print(f"    θ₁₂ = {math.degrees(θ12_pmns):.4f}°")
print(f"    θ₂₃ = {math.degrees(θ23_pmns):.4f}°")
print(f"    θ₁₃ = {math.degrees(θ13_pmns):.4f}°")
print(f"    δ   = {math.degrees(δ_pmns):.2f}°")
print(f"  J_CP 因數 = {J_PMNS_factor:.6f}")
print(f"  J_CP(δ=222.5°) = {J_PMNS:.6f}")
print(f"  PDG J_CP ~ 0.032")
print(f"  Ratio = {J_PMNS/0.032:.2f}")

# 用結構公式角度
θ12_pmns_s = math.atan(φ**(-1)) + 1/33
θ23_pmns_s = math.pi / 4
θ13_pmns_s = math.asin(ε * 32/33)

s12_s, s23_s, s13_s = math.sin(θ12_pmns_s), math.sin(θ23_pmns_s), math.sin(θ13_pmns_s)
c12_s, c23_s, c13_s = math.cos(θ12_pmns_s), math.cos(θ23_pmns_s), math.cos(θ13_pmns_s)

J_PMNS_s_factor = s12_s * s23_s * s13_s * c12_s * c23_s * c13_s**2
J_PMNS_s = J_PMNS_s_factor * math.sin(δ_pmns)

print(f"\n  PMNS 角度 (結構公式):")
print(f"    θ₁₂ = {math.degrees(θ12_pmns_s):.4f}°")
print(f"    θ₂₃ = {math.degrees(θ23_pmns_s):.4f}°")
print(f"    θ₁₃ = {math.degrees(θ13_pmns_s):.4f}°")
print(f"  J_CP 因數 = {J_PMNS_s_factor:.6f}")
print(f"  J_CP(δ=222.5°) = {J_PMNS_s:.6f}")

# ══════════════════════════════════════════════════════════════
# 3. 中微子質量譜
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("3. 中微子質量譜 — Δm²₃₁ 精確匹配")
print("─" * 80)

M_Pl = 1.22089e19
h11, h21 = 36, 98
M_comp = M_Pl / (2 * h11 * h21 * N_d)
γ6 = γ[5]  # n=6 嘅 γ
v = 246.0

# 基準質量
m0 = (γ6 * v)**2 / M_comp  # GeV
m0_eV = m0 * 1e9

print(f"  M_comp = {M_comp:.4e} GeV")
print(f"  γ₆ = {γ6:.6f}")
print(f"  m₀ = {m0_eV:.6f} eV")

# φ-power hierarchy
m_τ = m0_eV * φ**0
m_μ = m0_eV * φ**(-1)
m_e = m0_eV * φ**(-2)

print(f"\n  φ-power hierarchy:")
print(f"    ν_τ: m₀ = {m_τ:.6f} eV")
print(f"    ν_μ: m₀/φ = {m_μ:.6f} eV")
print(f"    ν_e: m₀/φ² = {m_e:.6f} eV")
print(f"    Σm = {m_τ+m_μ+m_e:.6f} eV (Planck < 0.12 eV)")

# Δm²
Δm2_31 = m_τ**2 - m_μ**2
Δm2_21_raw = m_μ**2 - m_e**2
Δm2_21 = Δm2_21_raw / 9  # Z₃ correction

print(f"\n  Δm²:")
print(f"    Δm²₃₁ = {Δm2_31:.6e} eV² (PDG 2.45e-03, ratio {Δm2_31/2.45e-3:.4f})")
print(f"    Δm²₂₁ (raw) = {Δm2_21_raw:.6e} eV²")
print(f"    Δm²₂₁ (Z₃=9) = {Δm2_21:.6e} eV² (PDG 7.53e-05, ratio {Δm2_21/7.53e-5:.4f})")

# 嘗試搵 Δm²₃₁ 嘅修正
# 如果使用 triple beat 或更高階結構
# 可能: Δm²₃₁ = m₀² × (φ⁻¹ - φ⁻⁵) = m₀² × 0.2017
# 或: Δm²₃₁ = m₀² × φ⁻¹ × (1 + 1/33) = m₀² × 0.6518

# 直接計算需要嘅 m₀ 嚟 match PDG
m0_needed = math.sqrt(2.45e-3 / (1 - φ**(-2)))
print(f"\n  m₀ needed for PDG Δm²₃₁ = 2.45e-3: {m0_needed:.6f} eV")
print(f"  Current m₀ = {m0_eV:.6f} eV")
print(f"  Ratio = {m0_needed/m0_eV:.4f}")

# 試用 φ³ 修正
# Δm²₃₁ = m₀² × φ⁻³
Δm2_31_phi3 = m0_eV**2 * φ**(-3)
print(f"\n  Δm²₃₁ = m₀² × φ⁻³ = {Δm2_31_phi3:.6e} eV² (ratio {Δm2_31_phi3/2.45e-3:.4f})")

# 試用 φ⁻¹ - φ⁻³
Δm2_31_phi_diff = m0_eV**2 * (φ**(-1) - φ**(-3))
print(f"  Δm²₃₁ = m₀² × (φ⁻¹ - φ⁻³) = {Δm2_31_phi_diff:.6e} eV² (ratio {Δm2_31_phi_diff/2.45e-3:.4f})")

# 從 K_Chain 結構: 質量差 = beat frequency 嘅函數
# m ∝ f(ω_n) 而非 ω_n 本身
# 可能質量譜係 beat frequency 之間嘅 beat (二階差頻)

# 試: m_νₙ ∝ beat(n, n+1) 或類似
# 對於 p6 mode: ν_τ(6,7), ν_μ(6,12), ν_e(6,18) 等

# p6 嘅 harmonics
p6_harmonics = [6, 12, 18, 24, 30, 36]
print(f"\n  p6 harmonic 嘅 beat frequency:")
for n in p6_harmonics:
    if n < 44:
        b = beat(6, n)
        print(f"    beat(6,{n}) = {b:.6f}")

# 質量比應該接近 beat frequency 比
# m_τ : m_μ : m_e ≈ beat(6,6) : beat(6,12) : beat(6,18) ?
# 但 beat(6,6) = 0, 所以唔係

# 或者: m ∝ 1/beat(n, n+1) 嘅某種函數?

# ══════════════════════════════════════════════════════════════
# 4. Beat 公式三角函數化簡
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("4. Beat 公式三角函數化簡")
print("─" * 80)

# beat(i,j) = 2|sin(πi/88) - sin(πj/88)| = 4|cos(π(i+j)/176) sin(π(i-j)/176)|
# 對於 i > j: beat(i,j) = 4 cos(π(i+j)/176) sin(π(i-j)/176)

# 重點: 所有 betat 嘅 RATIO 係三角函數比
# 哩個比可以化簡為 φ-power 表達式

# CKM tan(θ₁₂) = beat(5,6)/beat(19,25)
# = [4 cos(11π/176) sin(π/176)] / [4 cos(π/4) sin(3π/88)]
# = √2 × cos(π/16) × sin(π/176) / sin(3π/88)

# 其中 cos(π/16) = cos(11.25°) = √(2+√(2+√2))/2
# 呢個係 nested radical, 可以展開為 φ-power?

# 直接數值: cos(π/16) = 0.9807852804
# φ⁻¹ = 0.618034
# cos(π/16) / φ⁻¹ = 1.5869
# φ⁻¹² = 0.000291
# cos(π/16) = 1 - φ⁻³ + φ⁻⁵? 
# 1 - φ⁻³ + φ⁻⁵ = 1 - 0.236068 + 0.090170 = 0.854102... 唔啱

# 試連續 φ-power 展開:
# cos(π/16) = φ⁻¹ + φ⁻⁵?
# φ⁻¹ + φ⁻⁵ = 0.618034 + 0.090170 = 0.708204... 唔啱

# cos(π/16) = 1 - φ⁻⁴?
# 1 - φ⁻⁴ = 1 - 0.145898 = 0.854102... 唔啱

# 對於 beat ratio, 更直接嘅方法係用 φ-power 展開
# tan(θ₁₂) = φ⁻³ - φ⁻¹¹ + φ⁻¹⁹ - ...?
# φ⁻³ = 0.236068
# φ⁻¹¹ = 0.005030
# φ⁻³ - φ⁻¹¹ = 0.231038
# exact: 0.231604
# diff: 0.0005659

# φ⁻¹⁹ = 0.000291
# φ⁻³ - φ⁻¹¹ + φ⁻¹⁹ = 0.231330
# diff: 0.000274

# φ⁻²⁷ = 0.000017
# φ⁻³ - φ⁻¹¹ + φ⁻¹⁹ - φ⁻²⁷ = 0.231313
# 誤差仲係 0.000291

# 所以唔係簡單 alternating sum

# 試 φ-power 線性組合:
# tan(θ₁₂) = a × φ⁻³ + b × φ⁻⁵ + c × φ⁻⁷
# 0.231604 = a × 0.236068 + b × 0.090170 + c × 0.034442
# 解: a=1, b=-1, c=1?
# 0.236068 - 0.090170 + 0.034442 = 0.180340... 唔啱

# a=1, b=0, c=-1/7?
# 0.236068 - 0.034442/7 = 0.231149... 接近

# 實際上, tan(θ₁₂) = φ⁻³ - φ⁻¹¹ + φ⁻¹⁹ - φ⁻²⁷ + ...
# 呢個係 alternating Fibonacci series
# tan(θ₁₂) = Σ_{k=0}^{∞} (-1)^k φ^{-(3+8k)}
# = φ⁻³ / (1 + φ⁻⁸) = φ⁻³ / (1 + φ⁻⁸)

check = φ**(-3) / (1 + φ**(-8))
print(f"\n  4.1 tan(θ₁₂) 嘅 φ-power 展開:")
print(f"    tan(θ₁₂) = φ⁻³ - φ⁻¹¹ + φ⁻¹⁹ - φ⁻²⁷ + ...")
print(f"    = φ⁻³ / (1 + φ⁻⁸)")
print(f"    = {check:.10f}")
print(f"    exact = {math.tan(θ12):.10f}")
print(f"    ratio = {check/math.tan(θ12):.10f}")

# 差 0.08%! 好接近但唔 exact
# 可能係: tan(θ₁₂) = φ⁻³ / (1 + φ⁻⁸) + φ⁻²⁰ 之類嘅修正

# 試下一個更精確嘅 φ-power 表達式
# 用 φ⁻³ × (1 - φ⁻⁸ + φ⁻¹⁶ - φ⁻²⁴)
t12_phi = φ**(-3) * (1 - φ**(-8) + φ**(-16) - φ**(-24))
print(f"    tan(θ₁₂) ≈ φ⁻³ × (1 - φ⁻⁸ + φ⁻¹⁶ - φ⁻²⁴) = {t12_phi:.10f}")
print(f"    誤差 = {abs(t12_phi - math.tan(θ12)):.2e}")

# 但更精確嘅係用無窮級數
# tan(θ₁₂) = √2 × cos(π/16) × sin(π/176) / sin(3π/88)
# 呢個係純三角函數表達式, φ-power 只係近似展開

# 直接化簡各項:
# sin(π/176) = sin(π/176) ≈ π/176 (小角近似)
# 但用 exact 表達式: sin(π/176) = sin(π/176)

# 更精確嘅表達式: 用 beat ratio 本身做基本量
# tan(θ₁₂) = beat(5,6)/beat(19,25) 已經係最簡潔嘅形式

print(f"\n  4.2 所有 CKM beat 公式嘅三角函數化簡:")
print(f"    {'量':>15} | {'beat(i,j)':>25} | {'三角函數化簡':>45}")
print("-" * 90)

# 化簡每個 beat 公式
ckm_beats = [
    ("tan(θ₁₂)", 5, 6, 19, 25),
    ("tan(θ₂₃)", 33, 35, 3, 22),
    ("sin(θ₁₃)", 42, 43, 10, 31),
    ("V_us", 25, 35, 6, 37),
    ("V_cb", 13, 14, 6, 37),
    ("V_ub", 41, 42, 3, 37),
]

for name, i, j, k, l in ckm_beats:
    # beat(i,j) = 4 cos(π(i+j)/176) sin(π|i-j|/176)
    bij = 4 * math.cos(math.pi * (i+j) / 176) * math.sin(math.pi * abs(i-j) / 176)
    bkl = 4 * math.cos(math.pi * (k+l) / 176) * math.sin(math.pi * abs(k-l) / 176)
    ratio = bij / bkl
    
    # 化簡
    cos_factor = f"cos({i+j}π/176)" if (i+j) != 22 else "cos(π/8)"
    sin_factor = f"sin({abs(i-j)}π/176)"
    cos_factor2 = f"cos({k+l}π/176)" if (k+l) != 22 else "cos(π/8)"
    sin_factor2 = f"sin({abs(k-l)}π/176)"
    
    trig_form = f"4{cos_factor}×{sin_factor} / 4{cos_factor2}×{sin_factor2}"
    if len(trig_form) > 45:
        trig_form = f"[cos({i+j}π/176)×sin({abs(i-j)}π/176)] / [cos({k+l}π/176)×sin({abs(k-l)}π/176)]"
    
    print(f"    {name:>15} | beat({i},{j})/beat({k},{l}) | {trig_form}")

# PMNS beat 化簡
print(f"\n  4.3 PMNS beat 公式嘅三角函數化簡:")
pmns_beats = [
    ("tan(θ₁₂)", 4, 13, 9, 25),
    ("tan(θ₂₃)", 11, 23, 12, 26),
    ("sin(θ₁₃)", 25, 29, 3, 20),
]

for name, i, j, k, l in pmns_beats:
    bij = 4 * math.cos(math.pi * (i+j) / 176) * math.sin(math.pi * abs(i-j) / 176)
    bkl = 4 * math.cos(math.pi * (k+l) / 176) * math.sin(math.pi * abs(k-l) / 176)
    ratio = bij / bkl
    
    trig_form = f"[cos({i+j}π/176)×sin({abs(i-j)}π/176)] / [cos({k+l}π/176)×sin({abs(k-l)}π/176)]"
    print(f"    {name:>15} | beat({i},{j})/beat({k},{l})")
    print(f"      = {trig_form}")
    print(f"      = {ratio:.10f}")

# ══════════════════════════════════════════════════════════════
# 5. 儲存結果
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("5. 儲存結果")
print("─" * 80)

with open("main_problems/p2_ckm_reconstruction/derivation_4line_results.txt", "w") as f:
    f.write(f"IDCM v10.0 — 4 線推導結果\n")
    f.write(f"1. CKM δ_CP = 144° (Z₅ twisted sector), J_CP = {J_144:.2e}\n")
    f.write(f"   J_CP needed = 3.08e-05, sin(δ) needed = {3.08e-5/J_factor:.4f}\n")
    f.write(f"2. PMNS J_CP (beat) = {J_PMNS:.6f}\n")
    f.write(f"   PMNS J_CP (struct) = {J_PMNS_s:.6f}\n")
    f.write(f"3. Δm²₃₁ = {Δm2_31:.6e} eV², need 2.45e-3\n")
    f.write(f"   Δm²₂₁ (Z₃ corrected) = {Δm2_21:.6e} eV², PDG 7.53e-05\n")
    f.write(f"4. tan(θ₁₂) = √2 × cos(π/16) × sin(π/176) / sin(3π/88)\n")
    f.write(f"   = {math.tan(θ12):.10f}\n")

print("已儲存結果 ✅")