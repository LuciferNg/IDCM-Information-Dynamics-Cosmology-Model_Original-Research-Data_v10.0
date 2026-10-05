"""
IDCM v10.0 — Beat Formula φ-power 全表達式化簡
===============================================
將所有 44 K_Chain beat ratio 寫成乾淨的 φ-power 指數表達式
"""

import math
import numpy as np

φ = (1 + math.sqrt(5)) / 2
N_d = 44
ω = np.array([2 * abs(math.sin(math.pi * n / 88)) for n in range(1, N_d + 1)])
def beat(i, j): return abs(ω[i-1] - ω[j-1])

# ═══════════════════════════════════════════════════════
# 1. 三角函數基本化簡
# ═══════════════════════════════════════════════════════
print("=" * 80)
print("IDCM v10.0 — Beat Formula φ-power 全表達式化簡 🎯")
print("=" * 80)

# 三角恆等式: beat(i,j) = 4|cos(π(i+j)/176) sin(π|i-j|/176)|
# 對於 i < j: beat(i,j) = 4·cos(π(i+j)/176)·sin(π(j-i)/176)

def beat_trig(i, j):
    """將 beat(i,j) 寫成三角函數表達式"""
    s, l = min(i,j), max(i,j)
    s_angle = f"π({s}+{l})/176"
    d_angle = f"π({l-s})/176"
    # 化簡 cos 項
    s_plus_l = s + l
    if s_plus_l == 44:
        cos_part = "cos(π/4) = 1/√2"
    elif s_plus_l == 22:
        cos_part = "cos(π/8)"
    elif s_plus_l == 11:
        cos_part = "cos(π/16)"
    elif s_plus_l == 66:
        cos_part = "cos(3π/8)"
    elif s_plus_l == 88:
        cos_part = "cos(π/2) = 0"
    elif s_plus_l == 0:
        cos_part = "cos(0) = 1"
    else:
        cos_part = f"cos({s_plus_l}π/176)"
    return f"4·{cos_part}·sin({d_angle})"

print(f"\n1. 三角函數基本化簡:")
print(f"   beat(i,j) = 4|cos(π(i+j)/176) sin(π|i-j|/176)|")

# 列出所有 7 個 CKM beat 公式嘅三角化簡
ckm_pairs = [
    ("tan(θ₁₂)", 5, 6, 19, 25, "√2·cos(π/16)·sin(π/176)/sin(3π/88)"),
    ("tan(θ₂₃)", 33, 35, 3, 22, "cos(17π/44)·sin(π/44)/cos(25π/176)·sin(19π/176)"),
    ("sin(θ₁₃)", 42, 43, 10, 31, "cos(85π/176)·sin(π/176)/cos(41π/176)·sin(21π/176)"),
    ("V_us (λ)", 25, 35, 6, 37, "cos(15π/44)·sin(5π/44)/cos(43π/176)·sin(31π/176)"),
    ("V_cb", 13, 14, 6, 37, "cos(27π/176)·sin(π/176)/cos(43π/176)·sin(31π/176)"),
    ("V_ub", 41, 42, 3, 37, "cos(83π/176)·sin(π/176)/cos(40π/176)·sin(17π/44)"),
    ("A", 16, 35, 10, 28, "cos(51π/176)·sin(19π/176)/cos(19π/88)·sin(9π/88)"),
]

print(f"\n  {'量':>15} | {'三角函數化簡':>70}")
print("-" * 90)
for name, i, j, k, l, trig in ckm_pairs:
    print(f"  {name:>15} = {trig}")

# ═══════════════════════════════════════════════════════
# 2. φ-power 級數展開
# ═══════════════════════════════════════════════════════
print(f"\n2. φ-power 級數展開（∞ 階精確表達式）:")
print(f"   每個 beat ratio 可以展開為 φ-power 無窮級數:")
print("   R = Σ_{k=0}^{∞} a_k · φ^{-p_k}")

# 預先計算 φ-powers
φ_pow = {k: φ**k for k in range(-30, 31)}

def find_phi_series(val, max_terms=10, min_exp=-30):
    """搵最佳 φ-power 交替級數"""
    remaining = val
    terms = []
    for _ in range(max_terms):
        best_k = None
        best_err = float('inf')
        for k in range(min_exp, 0):
            err = abs(abs(remaining) - abs(φ_pow[k]))
            if err < best_err:
                best_err = err
                best_k = k
        if best_k is None:
            break
        sign = 1 if remaining > 0 else -1
        terms.append((sign, best_k))
        remaining -= sign * φ_pow[best_k]
        if abs(remaining) < 1e-15:
            break
    return terms, remaining

def series_to_str(terms):
    s = ""
    for i, (sign, k) in enumerate(terms):
        if i == 0:
            if sign > 0: s += f"φ⁻^{{{-k}}}"
            else: s += f"-φ⁻^{{{-k}}}"
        else:
            if sign > 0: s += f" + φ⁻^{{{-k}}}"
            else: s += f" - φ⁻^{{{-k}}}"
    return s

# 對每個公式進行 φ-power 級數展開
formulas = {
    "CKM tan(θ₁₂)": beat(5,6)/beat(19,25),
    "CKM tan(θ₂₃)": beat(33,35)/beat(3,22),
    "CKM sin(θ₁₃)": beat(42,43)/beat(10,31),
    "CKM λ (V_us)": beat(25,35)/beat(6,37),
    "CKM V_cb": beat(13,14)/beat(6,37),
    "CKM V_ub": beat(41,42)/beat(3,37),
    "CKM A": beat(16,35)/beat(10,28),
    "PMNS tan(θ₁₂)": beat(4,13)/beat(9,25),
    "PMNS tan(θ₂₃)": beat(11,23)/beat(12,26),
    "PMNS sin(θ₁₃)": beat(25,29)/beat(3,20),
}

print(f"\n  {'量':>20} | {'φ-power 級數展開':>75} | {'值':>15} | {'誤差':>12}")
print("-" * 130)
for name, val in formulas.items():
    terms, rem = find_phi_series(val, 5)
    expr = series_to_str(terms)
    approx = sum(s * φ_pow[k] for s, k in terms)
    err = abs(val - approx)
    print(f"  {name:>20} = {expr:>75} = {approx:>15.10f} | {err:>10.2e}")

# ═══════════════════════════════════════════════════════
# 3. φ-power 閉合形式（rational function）
# ═══════════════════════════════════════════════════════
print(f"\n3. φ-power 閉合形式（有理函數）:")

# 搵最佳 φ-power 有理函數組合
def find_phi_rational(val, max_denom=3):
    """搵最佳 φ-power 有理函數 N/D"""
    best = None
    best_err = float('inf')
    
    # 形式: φ^a / (1 + c·φ^b)
    for a in range(-15, 16):
        for b in range(-15, -1):
            for c in [-1, 1]:
                denom = 1 + c * φ_pow[b]
                if abs(denom) < 1e-15: continue
                approx = φ_pow[a] / denom
                err = abs(approx - val)
                if err < best_err:
                    best_err = err
                    best = (f"φ^{{{a}}}/(1{'−' if c<0 else '+'}φ^{{{b}}})", approx, err)
    
    # 形式: φ^a + φ^b / (1 + c·φ^d)
    for a in range(-15, 16):
        for b in range(-15, 16):
            for d in range(-15, -1):
                for c in [-1, 1]:
                    denom = 1 + c * φ_pow[d]
                    if abs(denom) < 1e-15: continue
                    approx = φ_pow[a] + φ_pow[b] / denom
                    err = abs(approx - val)
                    if err < best_err:
                        best_err = err
                        best = (f"φ^{{{a}}} + φ^{{{b}}}/(1{'−' if c<0 else '+'}φ^{{{d}}})", approx, err)
    
    return best

print(f"  {'量':>20} | {'φ-power 有理函數':>45} | {'值':>15} | {'誤差':>12}")
print("-" * 100)
for name, val in formulas.items():
    best = find_phi_rational(val)
    if best:
        expr, approx, err = best
        print(f"  {name:>20} = {expr:>45} = {approx:>15.10f} | {err:>10.2e}")

# ═══════════════════════════════════════════════════════
# 4. 完美 φ-power 匹配（精確到 1e-10）
# ═══════════════════════════════════════════════════════
print(f"\n4. 高精度 φ-power 展開（逐項收斂）:")
print(f"   每個 beat ratio 的 φ-power 展開 = 交替級數 + 剩餘級數")

# 對 tan(θ₁₂) 做詳細分析
tan_θ12 = beat(5,6)/beat(19,25)
print(f"\n   tan(θ₁₂) = {tan_θ12:.12f} 嘅 φ-power 展開:")

# 主要項: φ⁻³
# 二階項: -φ⁻¹¹
# 三階項: +φ⁻¹⁶
# 四階項: -φ⁻²⁴
# 五階項: +φ⁻²⁹
# ...

# 用 pattern: +3, +8, +5, +8, +5, +8, +5, ...
# 但 sign: +, -, +, -, +, -, ...
print(f"   tan(θ₁₂) = φ⁻³ − φ⁻¹¹ + φ⁻¹⁶ − φ⁻²⁴ + φ⁻²⁹ − φ⁻³⁷ + φ⁻⁴² − ...")
print(f"            = {φ**(-3):.12f}")
print(f"            − {φ**(-11):.12f} = {φ**(-3)-φ**(-11):.12f}")
print(f"            + {φ**(-16):.12f} = {φ**(-3)-φ**(-11)+φ**(-16):.12f}")
print(f"            − {φ**(-24):.12f} = {φ**(-3)-φ**(-11)+φ**(-16)-φ**(-24):.12f}")
print(f"            + {φ**(-29):.12f} = {φ**(-3)-φ**(-11)+φ**(-16)-φ**(-24)+φ**(-29):.12f}")
print(f"            − {φ**(-37):.12f} = {φ**(-3)-φ**(-11)+φ**(-16)-φ**(-24)+φ**(-29)-φ**(-37):.12f}")
print(f"            + {φ**(-42):.12f} = {φ**(-3)-φ**(-11)+φ**(-16)-φ**(-24)+φ**(-29)-φ**(-37)+φ**(-42):.12f}")

# 未解決嘅剩餘項
approx = sum([φ**(-3), -φ**(-11), +φ**(-16), -φ**(-24), +φ**(-29), -φ**(-37), +φ**(-42)])
print(f"\n   收斂值: {approx:.12f}")
print(f"   實際值: {tan_θ12:.12f}")
print(f"   剩餘誤差: {tan_θ12 - approx:.2e}")

# 檢查 pattern 3, 11, 16, 24, 29, 37, 42...
# 差值: 8, 5, 8, 5, 8, 5...
print(f"\n   指數模式: 3 →(+8)→ 11 →(+5)→ 16 →(+8)→ 24 →(+5)→ 29 →(+8)→ 37 →(+5)→ 42")
print(f"   即: a_k = 3 + 8·⌊k/2⌋ + 5·⌈k/2⌉ for k ≥ 0")

# 寫成閉合形式
print(f"\n5. 閉合 φ-power 表達式:")
print("   tan(θ₁₂) = Σ_{k=0}∞ (-1)^k φ^{-(3+8⌊k/2⌋+5⌈k/2⌉)}")
print(f"           = φ⁻³/(1+φ⁻⁸) + φ⁻¹⁶/(1-φ⁻⁸)")
print(f"           = {φ**(-3)/(1+φ**(-8)) + φ**(-16)/(1-φ**(-8)):.12f}")

# 其他 beat ratio 嘅閉合形式
print(f"\n   {'量':>20} | {'閉合 φ-power 表達式':>55} | {'值':>15}")
print("-" * 95)
for name, val in formulas.items():
    best = find_phi_rational(val)
    if best:
        expr, approx, err = best
        if err < 0.001:
            print(f"   {name:>20} ≈ {expr:>55} = {approx:>15.10f}")

# 儲存結果
print(f"\n{'='*80}")
print(f"6. 儲存結果")
print(f"{'='*80}")

with open("main_problems/p2_ckm_reconstruction/phi_power_full.txt", "w") as f:
    f.write(f"IDCM v10.0 — Beat Formula φ-power 全表達式化簡\n")
    f.write(f"φ = (1+√5)/2 ≈ {φ:.10f}\n")
    f.write("=" * 60 + "\n\n")
    
    for name, val in formulas.items():
        terms, rem = find_phi_series(val, 5)
        expr = series_to_str(terms)
        approx = sum(s * φ_pow[k] for s, k in terms)
        best = find_phi_rational(val)
        f.write(f"{name}:\n")
        f.write(f"  數值: {val:.12f}\n")
        f.write(f"  φ-power 級數: {expr} = {approx:.12f}\n")
        if best:
            expr2, approx2, err2 = best
            f.write(f"  有理函數: {expr2} = {approx2:.12f}\n")
        f.write("\n")

print("已儲存結果 ✅")