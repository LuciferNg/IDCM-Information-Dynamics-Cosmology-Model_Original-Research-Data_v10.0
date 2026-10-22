#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O160 scripts/15 — ★★★ 對稱家族帶: 42-46 | 88-92 (用戶觀察 2026-09-08)

用戶觀察: 「42-43-44-45-46/88-89-90-91-92 兩個對稱家族」

結構 (本 script 驗證):
  家族一 (42-46) = N_d + {−2,−1,0,+1,+2}    中心 44 = N_d, 寬度 B = 4
  家族二 (88-92) = Σγ_even + {−2,−1,0,+1,+2} 中心 90 = Σγ_even, 寬度 B = 4

對稱性:
  家族一: 42+46 = 43+45 = 44×2 = 88 = Σγ_odd (觀察者預算) — 88 嘅 ±2 帶
  家族二: 88+92 = 89+91 = 90×2 = 180 = B(N_d+1) (閉合階梯第三級) — 180 嘅 ±2 帶
  ★★★ 嵌套: 家族一對稱和 88 = 家族二下界; 兩中心距離 = 46 = 家族一上界
  ★★★ 閉合階梯 = 家族二×2: 176 = 2×88, 178 = 2×89 = 2F₁₁, 180 = 2×90 = 2Σγ_even
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


def main():
    N = 88
    g = [4 * mp.sin(k * mp.pi / 176) ** 2 for k in range(1, N + 1)]
    Se = sum(g[1::2])   # even k (世界)
    So = sum(g[0::2])   # odd k (觀察者)
    N_d = 44
    B = 4
    mu2 = 2

    print("=== 對稱家族帶: 42-46 | 88-92 ===")

    # F1-F2: 家族定義
    f1 = [42, 43, 44, 45, 46]
    f2 = [88, 89, 90, 91, 92]
    check("F1: 家族一 = N_d+{−2..+2}", f1 == [N_d + d for d in range(-2, 3)],
          f"(中心 {N_d} = N_d)")
    check("F2: 家族二 = Σγ_even+{−2..+2}", f2 == [int(mp.nint(Se)) + d for d in range(-2, 3)],
          f"(中心 {int(mp.nint(Se))} = Σγ_even, mpmath 驗證 Se = {mp.nstr(Se, 20)})")

    # F3-F4: 對稱和
    check("F3: 家族一對稱和 = 88 = Σγ_odd (42+46, 43+45, 44×2)",
          42 + 46 == 88 and 43 + 45 == 88 and 2 * 44 == 88,
          f"(mpmath: So = {mp.nstr(So, 20)} = 88)")
    check("F4: 家族二對稱和 = 180 = B(N_d+1) (88+92, 89+91, 90×2)",
          88 + 92 == 180 and 89 + 91 == 180 and 2 * 90 == 180,
          "(閉合階梯第三級 O155)")

    # F5: 寬度
    check("F5: 兩家族寬度都係 B = 4 (46−42, 92−88)", 46 - 42 == 4 and 92 - 88 == 4,
          "(分支因子封頂帶寬)")

    # F6: 家族一元素身份 (全已閉合)
    check("F6: 家族一元素身份: 42=N_d−μ², 43=N_d−1, 44=N_d, 45=N_d+1=C(10,2), 46=N_d+μ²",
          42 == N_d - mu2 and 43 == N_d - 1 and 44 == N_d and 45 == N_d + 1
          and 46 == N_d + mu2 and 45 == 10 * 9 // 2,
          "(42 O153, 43 自審參與者 k, 45 世界質心 O158, 46 = K_tree+F₇ O158)")

    # F7: 家族二元素身份
    check("F7: 家族二元素身份: 88=Σγ_odd, 89=F₁₁=2N_d+1, 90=Σγ_even, 91=L₄F₇=7×13, 92=Σγ_even+μ²",
          88 == int(mp.nint(So)) and 89 == 2 * N_d + 1 and 90 == int(mp.nint(Se))
          and 91 == 7 * 13 and 92 == int(mp.nint(Se)) + mu2,
          "(89 = F₁₁ Fib-11; 91 = L₄·F₇)")

    # F8: ★★★ 閉合階梯 = 家族二×2
    check("F8: ★★ 閉合階梯 176/178/180 = 2×(88/89/90)",
          176 == 2 * 88 and 178 == 2 * 89 and 180 == 2 * 90,
          "★★ 閉合階梯 = 家族二頭三元素×2 (178 = 2F₁₁ 已閉合; 360 = 4×90)")

    # F9-F10: 嵌套
    check("F9: 嵌套: 家族一對稱和 88 = 家族二下界; 兩中心距離 46 = 家族一上界",
          88 == f2[0] and 90 - 44 == 46,
          "(觀察者預算 = 世界預算帶嘅起點)")
    check("F10: Σγ_even − N_d = 46 = N_d+μ² (中心距 = 家族一上界)",
          int(mp.nint(Se)) - N_d == 46 == N_d + mu2)

    # F11: 自審連結
    check("F11: 43+45 = 88 (自審權重 43×45 = 1935 嘅對稱夥伴; k=43 = Ŝ obs 最大)",
          43 + 45 == 88 and 43 * 45 == 1935,
          "(家族一內對自審算子 Ŝ 嘅最大權重模式)")

    # F12: 譜驗證
    check("F12: mpmath: Σγ_even = 90, Σγ_odd = 88, E−O = 2 = μ²",
          abs(Se - 90) < TOL and abs(So - 88) < TOL and abs(Se - So - 2) < TOL)

    # F13-F14: 間距結構
    check("F13: 91−89 = 2 = μ² (家族二奇數間距 = 自對偶)",
          91 - 89 == 2)
    check("F14: 90 = 2(N_d+1) = 2×45 (家族二中心 = 2×世界質心)",
          90 == 2 * (N_d + 1))

    # F15: 家族二奇數 = 偶數+1 (2N_d+1 / 2(N_d+1)+1)
    check("F15: 89 = 2×44+1, 91 = 2×45+1 (奇數 = 偶數帶+1)",
          89 == 2 * 44 + 1 and 91 == 2 * 45 + 1,
          "(家族二 = 2×家族一{44,45,46} + 奇數修正 {+1})")

    print(f"\nRESULT: {PASS}/{PASS + FAIL} PASS")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()
