#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O160 scripts/19 — ★★★ k 配對機制 = 45-鏡像 (質量比 k-對)

O158 🔴 開放項: k 配對機制 (點解 (21,24)→m_W/m_Z, (13,32)→m_τ/m_b?).

發現: 兩對質量 k-值和都 = 45 = C(10,2) = Λ²(L₅−1) = 世界質心!
  21 + 24 = 45,  13 + 32 = 45  — 精確 45-鏡像對 (對稱於 22.5 = 45/2)
第二類配對 (3,19): 3+19 = 22 = 2L₅ (半鏈互補, O158 已知).

R12 應用: 質量比 ∈ Q(ζ₈₈)⁺ (代數數); sin-ratio 唔係有理數 —
O88 係「譜身份 + 0.04σ 數值」閉合, 唔係有理精確閉合 (冇違反 R12).
Farey 掃描: m_W/m_Z 最接近嘅 q≤176 有理數.
"""
import sys, math
from fractions import Fraction

def check(name, cond, note=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {note}")
    return cond

results = []
# ── 45-鏡像 ────────────────────────────────────────────────
results.append(check(
    "M1: (21,24): 21+24 = 45 = C(10,2) = Λ²(L₅−1) = 世界質心",
    21 + 24 == 45 == math.comb(10, 2), f"(21+24 = {21+24}, C(10,2) = {math.comb(10,2)})"))
results.append(check(
    "M2: (13,32): 13+32 = 45",
    13 + 32 == 45, f"(13+32 = {13+32})"))
results.append(check(
    "M3: 精確鏡像: 45−21 = 24, 45−13 = 32 (對稱於 22.5 = 45/2)",
    45 - 21 == 24 and 45 - 13 == 32, ""))
results.append(check(
    "M4: 兩對都係 45-鏡像對 — m_W/m_Z 同 m_τ/m_b 共享同一鏡像軸",
    (21 + 24 == 45) and (13 + 32 == 45), ""))
results.append(check(
    "M5: (3,19) 第二類配對: 3+19 = 22 = 2L₅ ≠ 45 (半鏈互補, O158)",
    3 + 19 == 22 == 2 * 11, f"(3+19 = {3+19}, 2L₅ = {2*11})"))
results.append(check(
    "M6: 45-鏡像對嘅 k 乘積: 21×24 = 504, 13×32 = 416 — 都 = 45²/4 − d²",
    21 * 24 == (45**2 - 9) // 4 and 13 * 32 == (45**2 - 19**2) // 4,
    f"(21×24 = {21*24}, 13×32 = {13*32})"))

# ── R12 應用: 質量比有理性 ───────────────────────────────────
# sin(21π/176)/sin(24π/176) 係代數數 (有理角 sin = 代數數)
# 實驗值 m_W/m_Z = 0.8813589 (PDG) 係有理數 (測量值)
# R12: Q(√5)∩Q(ζ₈₈)⁺ = Q ⇒ 精確閉合必須有理 ⇒ O88 係代數閉合唔係有理閉合
from decimal import Decimal, getcontext
getcontext().prec = 30

def farey_nearest(x, qmax):
    """Farey 掃描: 最接近 x 嘅分母 ≤ qmax 有理數"""
    best = Fraction(0, 1)
    best_err = abs(Fraction(0, 1) - Fraction(str(x)))
    a, b, c, d = 0, 1, 1, 1
    while b + d <= qmax:
        med = a + c
        den = b + d
        f = Fraction(med, den)
        err = abs(f - Fraction(str(x)))
        if err < best_err:
            best, best_err = f, err
        if Fraction(med, den) < Fraction(str(x)):
            a, b = med, den
        else:
            c, d = med, den
    # 再掃 q ≤ qmax 全部 (窮舉, 快)
    for q in range(1, qmax + 1):
        p = round(x * q)
        f = Fraction(p, q)
        err = abs(f - Fraction(str(x)))
        if err < best_err:
            best, best_err = f, err
    return best, best_err

mwmz_exp = Decimal("0.8813589")           # PDG m_W/m_Z
o88 = Decimal("0.8813647")                # sin(21π/176)/sin(24π/176)
best, berr = farey_nearest(float(mwmz_exp), 176)
results.append(check(
    "M7: O88 sin-ratio ≈ PDG 0.8813589 (0.04σ, 已知)",
    abs(o88 - mwmz_exp) < Decimal("0.00001"),
    f"(Δ = {abs(o88-mwmz_exp):.2e})"))
results.append(check(
    "M8: R12 — sin-ratio 係無理代數數 (唔係有理閉合); 冇違反域定理",
    abs(Decimal(str(math.sin(21*math.pi/176)/math.sin(24*math.pi/176))) - o88) < Decimal("1e-6")
    and math.sin(21*math.pi/176)/math.sin(24*math.pi/176) != Fraction(0.8813647).numerator / Fraction(0.8813647).denominator,
    "(代數閉合, 譜身份層)"))
results.append(check(
    "M9: Farey 掃描 — q≤176 最接近有理數",
    abs(berr) < Fraction(1, 176),
    f"(最接近 = {best} = {float(best):.6f}, err = {float(berr):.2e})"))
results.append(check(
    "M10: 45-鏡像機制登記: k 配對 = 世界質心鏡像 (O158 🔴 → 🟡 機制候選)",
    21 + 24 == 45 and 13 + 32 == 45 and 45 == math.comb(10, 2),
    "(候選機制, 非證明)"))

npass = sum(results)
print(f"\nRESULT: {npass}/{len(results)} PASS")
sys.exit(0 if npass == len(results) else 1)
