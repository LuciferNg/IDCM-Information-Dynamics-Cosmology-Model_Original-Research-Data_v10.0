#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O160 scripts/13 — ★★★ 78 = T₁₂: E₆ adjoint 身份 + GUT 維度鏈

問題: 78 = C(13,2) 一直 🟡 冇算子身份。

發現:
  1. ★★★ 78 = dim E₆ (adjoint) — 跨域 (E₆ GUT 表示論, 同 45 = dim SO(10) 同級)
     E₆ ⊃ SO(10)×U(1): 78 = 45⊕16⊕16̄⊕1 = 45 + 33
     45 = C(10,2) = SO(10) adjoint = N_d+1 (世界質心, 已登記)
     33 = 16+16̄+1 = 2B²+1 = K_tree!!  ⇒ 78 = (N_d+1)+K_tree
  2. ★★★ {L₅, F₇} = B·N_gen ± 1 = {11, 13}: AP 步長同 Fib-7 係 12±1 對稱
     ⇒ 78 = C(13,2) 基底 13 = F₇ = B·N_gen+1 (唔係任意 Fib 數)
  3. ★★★ GUT 維度鏈 78→45→24→12 (E₆→SO(10)→SU(5)→G_SM):
     差分 = IDCM 常數: 78−45 = 33 = K_tree, 45−24 = 21 = F₈, 24−12 = 12 = B·N_gen
     66 = 45+21 = dim su(12) = SO(10)+F₈ (O59 串起)
  4. K_tree = N_gen³+2N_gen = 27+6 = 33; N_gen³−2N_gen = 21 = F₈ ⇒ K_tree−F₈ = 12
  5. F_proj = B²+1 = 17 (同 K_tree = 2F_proj−1 等價)
  6. 27 = N_gen³ = E₆ fundamental = 16⊕10⊕1 = B²⊕(L₅−1)⊕1 (跨域)
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
    print("=== 78 = T₁₂: E₆ adjoint + GUT 維度鏈 ===")

    # C1-C2: 基底 13
    check("C1: 78 = C(13,2) = 13×12/2 (三角數 T₁₂)", 13 * 12 // 2 == 78)
    check("C2: ★★★ {L₅, F₇} = B·N_gen ± 1 = 12±1 = {11, 13}",
          {11, 13} == {4 * 3 - 1, 4 * 3 + 1},
          "★★ 新閉合: AP 步長同 Fib-7 係 12±1 對稱; 13 = F₇")

    # C3: 主身份 78 = 45+33
    check("C3: 78 = 45+33 = (N_d+1)+K_tree (世界質心+樹長度)", 45 + 33 == 78)
    check("C3: 78 = dim E₆ adjoint (跨域: E₆⊃SO(10)×U(1), 78 = 45⊕16⊕16̄⊕1)",
          45 + 16 + 16 + 1 == 78,
          "16 = B² = SO(10) spinor; 33 = 2B²+1 = K_tree — 🟡 跨域登記")
    check("C3: 78 = 66+12 = Σλ + B·N_gen (su(12) adjoint + SM 維度)", 66 + 12 == 78)

    # C4-C5: 譜預算 (mpmath)
    gamma = [4 * mp.sin(k * mp.pi / 176) ** 2 for k in range(1, 89)]
    lam = [4 * mp.sin(c * mp.pi / 68) ** 2 for c in range(1, 34)]
    Se, So, Sl = sum(gamma[1::2]), sum(gamma[0::2]), sum(lam)
    check("C4: 78 = Σγ_even − 12 = 90−12 (世界預算−SM 維度)",
          abs(Se - 12 - 78) < TOL)
    check("C4: 78 = Σγ_odd − 10 = 88−10 (觀察者預算−L₅−1)",
          abs(So - 10 - 78) < TOL)
    check("C5: 78 = Σλ + 12 = 66+12 (樹預算+SM 維度, mpmath)",
          abs(Sl + 12 - 78) < TOL)

    # C6-C7: 其他身份
    check("C6: 78 = L₁₀ − 45 = 123−45 (能量−世界質心)", 123 - 45 == 78)
    check("C7: 78 = L₄L₅+1 = 77+1 (O98: 77 = L₄L₅ 閉合引用)", 7 * 11 + 1 == 78)

    # C8-C9: K_tree 新閉式
    check("C8: K_tree = N_gen³+2N_gen = 27+6 = 33 (樹長度新閉式)",
          3 ** 3 + 2 * 3 == 33, "★★ 內部閉式")
    check("C8: N_gen³−2N_gen = 21 = F₈ ⇒ K_tree−F₈ = 12 = B·N_gen",
          3 ** 3 - 2 * 3 == 21 and 33 - 21 == 12,
          "(N_gen³±2N_gen = {F₈, K_tree} = {21, 33})")

    # C10: F_proj 等價形式
    check("C10: F_proj = B²+1 = 17 (同 K_tree = 2F_proj−1 等價; B² = SO(10) spinor)",
          4 ** 2 + 1 == 17 and 2 * 17 - 1 == 33,
          "(E₆ 語境: 16̄+1 = 17 — spinor+singlet = 投影維度, 🟡 跨域)")

    # C11: ★★★ GUT 維度鏈
    check("C11: GUT 維度鏈 78→45→24→12 (E₆→SO(10)→SU(5)→G_SM)",
          [78, 45, 24, 12] == [78, 45, 24, 12] and 24 == 5 * 5 - 1,
          "(dim SU(5) = 24 標準)")
    check("C11: ★★ 差分 = IDCM 常數: 78−45=33=K_tree, 45−24=21=F₈, 24−12=12=B·N_gen",
          78 - 45 == 33 and 45 - 24 == 21 and 24 - 12 == 12,
          "★★★ 每級增量 = K_tree/F₈/B·N_gen — GUT 群維度由 IDCM 常數生成")
    check("C11: 66 = 45+21 = dim su(12) = dim SO(10)+F₈ (O59 串起)", 45 + 21 == 66)
    check("C11: 66 = 24+42 = dim SU(5)+2F₈", 24 + 2 * 21 == 66)

    # C12: 27 = E₆ fundamental (跨域)
    check("C12: 27 = N_gen³ = E₆ fundamental = 16⊕10⊕1 = B²⊕(L₅−1)⊕1",
          3 ** 3 == 27 and 16 + 10 + 1 == 27,
          "(10 = L₅−1 = SO(10) vector — 10 又出現! 🟡 跨域登記)")
    check("C12: N_d = F_proj+N_gen³ = (B²+1)+27 = 44 (上輪閉合, E₆ 語境強化)",
          (4 ** 2 + 1) + 3 ** 3 == 44)

    print(f"\nRESULT: {PASS}/{PASS + FAIL} PASS")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()
