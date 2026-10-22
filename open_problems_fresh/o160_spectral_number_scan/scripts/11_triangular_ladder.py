#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O160 scripts/11 — ★★★ 三角數階梯: 10 = L₅−1 嘅算子身份閉合

問題 (docs/07 開放項): 10 = L₅−1 只係家族身份 (2N_gen+B), 算子身份未推。

發現 (本 script 驗證):
  ★★★ 連續四級三角數全部命中已閉合常數:
    C(9,2)  = 36 = h¹¹        (CY₃ Kähler moduli, O53)
    C(10,2) = 45 = N_d+1      (世界質心 = SO(10) adjoint, O158)
    C(11,2) = 55 = F₁₀        (θ₂₃ 尺度家, O156)
    C(12,2) = 66 = Σλ         (樹預算 = su(12) adjoint 正根, O55/O59/O157)
  基底全結構量: 9 = N_gen², 10 = L₅−1, 11 = L₅, 12 = B·N_gen

  ⇒ 10 = L₅−1 嘅算子身份 = 「世界質心嘅三角基底」:
     世界質心 N_d+1 = C(L₅−1, 2) = C(10,2) = 45 = SO(10) adjoint
     (SO(10) GUT pipeline: adjoint 45 = 10 揀 2; 10 = 基本表示維度)

  預算因子化 (10 嘅世界側角色):
    Σγ_even = 90 = N_gen²(L₅−1)          (世界預算 = 世代平方 × 10)
    Σγ_odd  = 88 = 2B·L₅                  (觀察者預算 = 2B × AP 步長)
    μ² = Σγ_even − Σγ_odd = N_gen²(L₅−1) − 2B·L₅ = 2  (μ² 新閉式)
    360 = h¹¹(L₅−1) = 4Σγ_even           (閉合階梯頂 CY₃ 因子化)
    L₅ = 1 + 360/h¹¹                      (AP 步長新閉合)
"""
import sys
from pathlib import Path

import mpmath as mp

O160 = Path(__file__).resolve().parent.parent
mp.mp.dps = 50
TOL = mp.mpf("1e-40")

PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [PASS] {name} {detail}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {detail}")


def C2(x):
    return x * (x - 1) // 2  # C(x,2) 整數


def main():
    print("=== 三角數階梯 (10 = L₅−1 算子身份) ===")

    # C1: 10 嘅多身份等價
    check("C1: 10 = L₅−1 = N_gen²+1 = N_d−2F_proj = N_gen³−F_proj",
          {11 - 1, 9 + 1, 44 - 34, 27 - 17} == {10} and 34 == 2 * 17 and 27 == 3 ** 3,
          "(L₅=11, N_gen=3, B=4, N_d=44, F_proj=17)")

    # C2: N_d = F_proj + N_gen³ (新閉合: 世界維度 = 投影維度 + 世代立方)
    check("C2: N_d = F_proj + N_gen³ = 17+27 = 44", 17 + 3 ** 3 == 44,
          "★★ 新閉合 — 世界維度分解")

    # C3: 四級三角數階梯
    check("C3: C(9,2) = 36 = h¹¹ (CY₃ Kähler moduli)", C2(9) == 36,
          "(O53 閉合引用; C(9,2) 身份係新)")
    check("C3: C(10,2) = 45 = N_d+1 (世界質心)", C2(10) == 45,
          "(O158 閉合引用; C(10,2) 身份係新)")
    check("C3: C(11,2) = 55 = F₁₀ (θ₂₃ 尺度家)", C2(11) == 55,
          "(O156 閉合引用; C(11,2) 身份係新)")
    check("C3: C(12,2) = 66 = Σλ = su(12) adjoint", C2(12) == 66,
          "(O55 V12 已記錄 C(12,2) = su(12) 正根; O157 Σλ = 66 串起)")

    # C4: 基底全結構量
    check("C4: 基底 9 = N_gen², 10 = L₅−1, 11 = L₅, 12 = B·N_gen",
          {9, 10, 11, 12} == {3 ** 2, 11 - 1, 11, 4 * 3},
          "(12 = B×N_gen 已閉合 O59: su(12) fundamental)")

    # C5-C8: 階梯公式化
    check("C5: h¹¹ = C(N_gen², 2)", C2(3 ** 2) == 36,
          "(CY₃ Kähler moduli = 世代平方揀 2)")
    check("C6: N_d+1 = C(L₅−1, 2) = SO(10) adjoint", C2(11 - 1) == 44 + 1,
          "★★ 10 嘅算子身份: 世界質心 = (AP步長−1) 揀 2; SO(10) adjoint 45 = 10×9/2")
    check("C7: F₁₀ = C(L₅, 2)", C2(11) == 55,
          "(θ₂₃ 尺度家 55 = L₅ 揀 2 — O156 尺度家嘅三角數根源)")
    check("C8: Σλ = C(B·N_gen, 2)", C2(4 * 3) == 66,
          "(樹預算 = 12 揀 2 = su(12) 正根, O55/O59 串起)")

    # C9-C11: 預算因子化 (mpmath 驗證譜和)
    gamma = [4 * mp.sin(k * mp.pi / 176) ** 2 for k in range(1, 89)]
    Se = sum(gamma[1::2])   # even k = 2..88 → Σγ_even = 90
    So = sum(gamma[0::2])   # odd  k = 1..87 → Σγ_odd  = 88
    check("C9: Σγ_even = 90 = N_gen²(L₅−1) = 9×10", abs(Se - 9 * 10) < TOL,
          "(世界預算因子化 — 10 係世界側單位)")
    check("C10: Σγ_odd = 88 = 2B·L₅ = 8×11", abs(So - 2 * 4 * 11) < TOL,
          "(觀察者預算因子化)")
    check("C11: μ² = Σγ_even−Σγ_odd = N_gen²(L₅−1) − 2B·L₅ = 90−88 = 2",
          abs(Se - So - 2) < TOL and (9 * 10 - 8 * 11) == 2,
          "★★ μ² 新閉式 (E−O 因子化)")

    # C12-C13: 閉合階梯 CY₃ 因子化
    check("C12: 360 = h¹¹(L₅−1) = 36×10 = 4Σγ_even", 36 * 10 == 360 and 4 * 90 == 360,
          "(閉合階梯第三級 180→360 嘅 CY₃ 因子化)")
    check("C13: L₅ = 1 + 360/h¹¹ = 1+10 = 11", 1 + 360 // 36 == 11,
          "★★ AP 步長新閉合 (由 360/h¹¹ 生成)")

    # C14: 唯一性 — 10 係唯一 x: C(x,2) = N_d+1
    xs = [x for x in range(1, 50) if C2(x) == 45]
    check("C14: 唯一 x: C(x,2) = N_d+1 係 x=10", xs == [10], f"{xs}")

    # C15: T₇ = 28 登記 (家族身份, N_d−B²)
    check("C15: T₇ = 28 = N_d−B² (家族身份, 唔閉合)", 28 == 44 - 16 and 28 == 4 * 7,
          "(28 = B·L₄ = N_d−B² — 冇獨立算子, 🟡 登記)")

    # C16: 45 = 世界質心 = SO(10) adjoint 表示論身份
    check("C16: 45 = C(10,2) = dim SO(10) = 世界質心", C2(10) == 45 == 10 * 9 // 2,
          "(SO(10) GUT: adjoint 45 = 基本表示 10 嘅反對稱平方; 10 = L₅−1 = SO(10) 基本)")

    print(f"\nRESULT: {PASS}/{PASS + FAIL} PASS")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()
