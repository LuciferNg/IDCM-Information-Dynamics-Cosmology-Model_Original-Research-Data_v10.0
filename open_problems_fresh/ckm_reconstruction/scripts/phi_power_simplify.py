"""
IDCM v10.0 — Beat Formula φ-power 化簡
========================================
將所有 beat ratio 寫成乾淨嘅黃金分割率指數表達式
"""

import math
import numpy as np

φ = (1 + math.sqrt(5)) / 2
N_d = 44
ω = np.array([2 * abs(math.sin(math.pi * n / 88)) for n in range(1, N_d + 1)])

def beat(i, j): return abs(ω[i-1] - ω[j-1])

# 所有 beat ratio 公式
formulas = {
    "CKM tan(θ₁₂)": beat(5,6)/beat(19,25),
    "CKM tan(θ₂₃)": beat(33,35)/beat(3,22),
    "CKM sin(θ₁₃)": beat(42,43)/beat(10,31),
    "CKM V_us (λ)": beat(25,35)/beat(6,37),
    "CKM V_cb": beat(13,14)/beat(6,37),
    "CKM V_ub": beat(41,42)/beat(3,37),
    "CKM A": beat(16,35)/beat(10,28),
    "PMNS tan(θ₁₂)": beat(4,13)/beat(9,25),
    "PMNS tan(θ₂₃)": beat(11,23)/beat(12,26),
    "PMNS sin(θ₁₃)": beat(25,29)/beat(3,20),
}

print("=" * 80)
print("IDCM v10.0 — Beat Formula φ-power 化簡 🎯")
print("=" * 80)

# 預計算 φ-power 表
φ_powers = {k: φ**k for k in range(-30, 31)}

def find_best_phi_exp(val, max_terms=4):
    """搵最佳 φ-power 組合: Σ a_k × φ^k"""
    best = None
    best_err = float('inf')
    
    # 單項: a × φ^k
    for k in range(-30, 0):
        for a in [1, -1]:
            approx = a * φ**k
            err = abs(approx - val)
            if err < best_err:
                best_err = err
                best = (f"{a:+d}·φ^{{{k}}}", approx)
    
    # 雙項: a·φ^i + b·φ^j
    for i in range(-30, 0):
        for j in range(i+1, 0):
            for a in [1, -1]:
                for b in [1, -1]:
                    approx = a * φ**i + b * φ**j
                    err = abs(approx - val)
                    if err < best_err:
                        best_err = err
                        best = (f"{a:+d}·φ^{{{i}}} {b:+d}·φ^{{{j}}}", approx)
    
    # 三項
    if max_terms >= 3:
        for i in range(-30, 0):
            for j in range(i+1, 0):
                for k in range(j+1, 0):
                    for a in [1, -1]:
                        for b in [1, -1]:
                            for c in [1, -1]:
                                approx = a * φ**i + b * φ**j + c * φ**k
                                err = abs(approx - val)
                                if err < best_err:
                                    best_err = err
                                    best = (f"{a:+d}·φ^{{{i}}} {b:+d}·φ^{{{j}}} {c:+d}·φ^{{{k}}}", approx)
    
    return best, best_err

def find_best_phi_ratio(val):
    """搵最佳 φ-power 比例: a·φ^i / (b·φ^j + c·φ^k)"""
    best = None
    best_err = float('inf')
    
    # φ^i / φ^j = φ^{i-j}
    for i in range(-20, 20):
        for j in range(-20, 20):
            if i == j: continue
            approx = φ**(i-j)
            err = abs(approx - val)
            if err < best_err:
                best_err = err
                best = (f"φ^{{{i-j}}}", approx)
    
    # φ^i / (1 ± φ^j)
    for i in range(-20, 20):
        for j in range(-20, 0):
            for sign in [1, -1]:
                denom = 1 + sign * φ**j
                if denom == 0: continue
                approx = φ**i / denom
                err = abs(approx - val)
                if err < best_err:
                    best_err = err
                    best = (f"φ^{{{i}}}/(1{sign:+d}·φ^{{{j}}})", approx)
    
    return best, best_err

# 對每個公式進行 φ-power 化簡
print(f"\n{'='*80}")
print(f"1. φ-power 多項式展開（Σ a_k·φ^k）")
print(f"{'='*80}")
print(f"  {'量':>20} | {'φ-power 表達式':>40} | {'值':>15} | {'誤差':>12}")
print("-" * 95)

for name, val in formulas.items():
    (expr, approx), err = find_best_phi_exp(val, 3)
    # 清理表達式
    expr = expr.replace("+1·", "+").replace("-1·", "-").replace("+·", "+")
    expr = expr.replace("+1·", "+").replace("-1·", "-")
    if expr.startswith("+1·"): expr = expr[3:]
    if expr.startswith("+·"): expr = expr[2:]
    print(f"  {name:>20} | {expr:>40} | {approx:>15.10f} | {err:>12.2e}")

# φ-power 比例
print(f"\n{'='*80}")
print(f"2. φ-power 比例（φ^i / (1 ± φ^j)）")
print(f"{'='*80}")
print(f"  {'量':>20} | {'φ-power 比例':>40} | {'值':>15} | {'誤差':>12}")
print("-" * 95)

for name, val in formulas.items():
    (expr, approx), err = find_best_phi_ratio(val)
    print(f"  {name:>20} | {expr:>40} | {approx:>15.10f} | {err:>12.2e}")

# 三角函數化簡
print(f"\n{'='*80}")
print(f"3. 三角函數化簡（beat(i,j) = 4 cos(π(i+j)/176) sin(π|i-j|/176)）")
print(f"{'='*80}")

def trig_form(i, j, k, l):
    """將 beat(i,j)/beat(k,l) 化簡為三角函數表達式"""
    # beat(i,j) = 4 cos(π(i+j)/176) sin(π|i-j|/176) for i > j
    # 實際上 beat(i,j) = 2|sin(πi/88) - sin(πj/88)| = 4|cos(π(i+j)/176) sin(π(i-j)/176)|
    
    # 分母可能可以化簡
    # 如果 k+l = 44 或 88 等，cos 項化簡
    cos_simp = ""
    if (k+l) % 88 == 0:
        cos_simp = "1"
    elif (k+l) % 44 == 0:
        cos_simp = "0"
    elif (k+l) == 44:
        cos_simp = "cos(π/4) = 1/√2"
    elif (k+l) == 22:
        cos_simp = "cos(π/8)"
    elif (k+l) == 11:
        cos_simp = "cos(π/16)"
    else:
        cos_simp = f"cos({k+l}π/176)"
    
    return f"4·cos({i+j}π/176)·sin({abs(i-j)}π/176) / 4·{cos_simp}·sin({abs(k-l)}π/176)"

print(f"  {'量':>20} | {'三角函數化簡':>60}")
print("-" * 85)

trig_pairs = [
    ("CKM tan(θ₁₂)", 5, 6, 19, 25),
    ("CKM tan(θ₂₃)", 33, 35, 3, 22),
    ("CKM sin(θ₁₃)", 42, 43, 10, 31),
    ("CKM V_us", 25, 35, 6, 37),
    ("CKM V_cb", 13, 14, 6, 37),
    ("CKM V_ub", 41, 42, 3, 37),
    ("CKM A", 16, 35, 10, 28),
    ("PMNS tan(θ₁₂)", 4, 13, 9, 25),
    ("PMNS tan(θ₂₃)", 11, 23, 12, 26),
    ("PMNS sin(θ₁₃)", 25, 29, 3, 20),
]

for name, i, j, k, l in trig_pairs:
    tf = trig_form(i, j, k, l)
    print(f"  {name:>20} | {tf}")

# 分析 φ-power 嘅精確度
print(f"\n{'='*80}")
print(f"4. φ-power 精確度分析")
print(f"{'='*80}")

print(f"\n  CKM 角度嘅 φ-power 表達式:")
print(f"  θ₁₂ = arctan(tan(θ₁₂)) = arctan(beat(5,6)/beat(19,25))")
print(f"      = arctan(√2·cos(π/16)·sin(π/176)/sin(3π/88))")
print(f"      = 13.0400°")

# 用 φ-power 展開 tan(θ₁₂)
tan_θ12 = beat(5,6)/beat(19,25)
print(f"\n  tan(θ₁₂) = {tan_θ12:.10f}")
print(f"  φ⁻³ = {φ**(-3):.10f}")
print(f"  φ⁻³ - φ⁻¹¹ = {φ**(-3) - φ**(-11):.10f}")
print(f"  φ⁻³ - φ⁻¹¹ + φ⁻¹⁶ = {φ**(-3) - φ**(-11) + φ**(-16):.10f}")
print(f"  φ⁻³ - φ⁻¹¹ + φ⁻¹⁶ - φ⁻²⁴ = {φ**(-3) - φ**(-11) + φ**(-16) - φ**(-24):.10f}")
print(f"  φ⁻³/(1+φ⁻⁸) + φ⁻¹⁶ = {φ**(-3)/(1+φ**(-8)) + φ**(-16):.10f}")

# 搵最好嘅 φ-power 展開
best_series = None
best_series_err = float('inf')
for a in range(1, 10):
    for b in range(a+1, 20):
        # Alternating series: φ^{-a} - φ^{-b} + φ^{-(b+a)} - ...
        approx = φ**(-a)
        k = a
        sign = -1
        terms = [a]
        while abs(φ**(-k)) > 1e-12:
            k += b - a
            if k > 30: break
            approx += sign * φ**(-k)
            terms.append(k)
            sign *= -1
        err = abs(approx - tan_θ12)
        if err < best_series_err:
            best_series_err = err
            best_series = (a, b, terms, approx, err)

if best_series:
    a, b, terms, approx, err = best_series
    print(f"\n  最佳 φ-power 交替級數:")
    expr = f"φ⁻^{a}"
    for i, t in enumerate(terms[1:]):
        sign = "+" if i % 2 == 0 else "-"
        expr += f" {sign} φ⁻^{t}"
    print(f"  {expr}")
    print(f"  = {approx:.10f}")
    print(f"  誤差 = {err:.2e}")

# 儲存結果
print(f"\n{'='*80}")
print(f"5. 儲存結果")
print(f"{'='*80}")

lines = []
lines.append("IDCM v10.0 — Beat Formula φ-power 化簡")
lines.append("=" * 60)
lines.append("")

for name, val in formulas.items():
    (expr, approx), err = find_best_phi_exp(val, 3)
    expr = expr.replace("+1·", "+").replace("-1·", "-")
    if expr.startswith("+1·"): expr = expr[3:]
    if expr.startswith("+·"): expr = expr[2:]
    lines.append(f"{name:>20} = {expr} = {approx:.10f} (err {err:.2e})")

with open("open_problems_fresh/ckm_reconstruction/phi_power_simplification.txt", "w") as f:
    f.write("\n".join(lines))

print("已儲存結果 ✅")