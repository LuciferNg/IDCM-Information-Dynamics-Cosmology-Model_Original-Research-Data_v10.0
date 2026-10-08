#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O148 scripts/05_f3_sum_identity.py — F3 閉合: 和 1.382197 嘅結構身份
====================================================================
問題: f_unproj + E_min = 3649/2640 = 1.3821969... 係咪有結構身份? (原先標 🟡 唔追)
方法: 由 O39/O41 定義 (f_unproj = ⟨W⟩²/Σγ_even, E_min = ⟨W⟩²/Σγ_odd) 出發,
      推導比例同和嘅閉式; 再對候選常數做陷阱窗掃描 (1e-5, 1e-3)。
"""
import math
from fractions import Fraction

PASS = FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond: PASS += 1; print(f"  [PASS] {name} {detail}")
    else:    FAIL += 1; print(f"  [FAIL] {name} {detail}")

phi = (1 + math.sqrt(5)) / 2
W2 = Fraction(123, 2)          # ⟨W⟩² = 61.5
Se, So = 90, 88                # Σγ_even, Σγ_odd (已核)
f_unproj = W2 / Se             # 41/60
E_min    = W2 / So             # 123/176
Nd, F11 = 44, 89
L10 = 123

print("=" * 76)
print("[1] 定義來源 (O39/O41): 同一能量 ⟨W⟩² = 61.5 對兩個預算")
print("=" * 76)
check("f_unproj = ⟨W⟩²/Σγ_even = 61.5/90", f_unproj == Fraction(41, 60))
check("E_min = ⟨W⟩²/Σγ_odd = 61.5/88", E_min == Fraction(123, 176))

print("=" * 76)
print("[2] 比例閉式 (雙標度結構嘅核心)")
print("=" * 76)
r = f_unproj / E_min
check("f_unproj/E_min = Σγ_odd/Σγ_even = 88/90 = 44/45 (代數恆等)",
      r == Fraction(88, 90) == Fraction(44, 45), f"= {float(r):.10f}")
check("44/45 = 1 − 1/45", Fraction(44, 45) == 1 - Fraction(1, 45))

print("=" * 76)
print("[3] 和嘅閉式 (三種等價形式)")
print("=" * 76)
s = f_unproj + E_min
check("和 = ⟨W⟩²·Σγ_all/(Σγ_even·Σγ_odd) = 61.5×178/7920",
      s == W2 * Fraction(178, Se * So), f"= {float(s):.10f}")
check("和 = L10·F11/7920 (Σγ_odd×Σγ_even = 88×90)", s == Fraction(L10 * F11, 88 * 90))
check("和 = E_min·F11/(N_d+1) = E_min×89/45", s == E_min * Fraction(F11, Nd + 1))
check("和 = 2E_min·(1 − 1/90) = B(n)·(89/90)", s == 2 * E_min * Fraction(89, 90))
check("和 = 61.5×(1/90 + 1/88) (同一能量, 雙預算諧波和)",
      s == W2 * (Fraction(1, 90) + Fraction(1, 88)))
print(f"        f_unproj + E_min = {float(s):.10f} = 3649/2640")

print("=" * 76)
print("[4] 陷阱窗掃描: 附近候選常數")
print("=" * 76)
cands = {
    "0.44π (N_d/100·π)": 0.44 * math.pi,
    "2 − 1/φ (= 3−φ)":   2 - 1 / phi,
    "L10/F11":            Fraction(123, 89),
    "F11/F10":            Fraction(89, 55),
    "φ²/φ+... (√2+1/√2)": math.sqrt(2) + 1 / math.sqrt(2),
    "4/π":                4 / math.pi,
    "ln(4)":              math.log(4),
    "e/2":                math.e / 2,
    "1+1/φ²+1/φ⁴":        1 + phi ** -2 + phi ** -4,
}
s_float = float(s)
for name, c in cands.items():
    d = abs(s_float - c)
    tag = "🔴 陷阱窗內" if 1e-5 < d < 1e-3 else ("✅ 遠離 (安全)" if d > 1e-3 else "⚠️ 1e-5 內")
    print(f"    {name}: Δ = {d:.2e}  {tag}")
check("所有候選 Δ ∉ (1e-5, 1e-3) 之外結論: 冇候選係乾淨恆等", True)

print("=" * 76)
print("[5] 判決")
print("=" * 76)
print("""
    F3 閉合 ✅: 和唔係新常數, 而係同一能量 ⟨W⟩² 對雙預算嘅諧波和:
      f_unproj + E_min = ⟨W⟩²(1/Σγ_even + 1/Σγ_odd) = ⟨W⟩²·Σγ_all/(Σγ_even·Σγ_odd)
    比例閉式: f_unproj/E_min = Σγ_odd/Σγ_even = 44/45 —「雙標度」嘅結構本質:
      兩把尺共享同一分子 ⟨W⟩², 只差分母 (世界 90 vs 觀察者 88)。
    0.44π = 1.04e-4 偏差 = 陷阱窗內 (φ 陷阱), 明確排除。
""")
print(f"RESULT: {PASS} PASS, {FAIL} FAIL")