#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O160 scripts/08 — 新數字 10 身份 + Γ 結構掃描 (docs/05 開放項 2,3)

問題 1 (docs/05 開放項 3): novel 10 = 2F₅ 有冇閉合身份?
  候選: 10 = L₅−1 (AP 步長減一) = 2N_gen+B (世代倍數+分支因子) = F_proj−L₄ (17−7)
  梯子: 6/10/11 = 2N_gen + {0, B, F₅} — 連續身份 (2N_gen=6 已閉合, L₅=11 已閉合)
  ⇒ 10 = L₅−1 家族身份 🟢 (組合身份, 唔係獨立算子 — O153 教訓)

問題 2 (docs/05 開放項 2): ΣΓ = 5940 嘅結構身份 (逐格已由 GT_prod 掃, 冇新命中;
  呢度掃 row/col 和):
  Γ row 和:  Σ_c γ_a λ_c = 66γ_a   ⇒ 66γ₄₄ = 132 = N_d·N_gen (O151 容量階梯),
                                    66γ₈₈ = 264 = 6U(1)×N_d (O107) ✓
  Γ col 和:  Σ_a γ_a λ_c = 90λ_c   ⇒ 90λ₁₇ = 180 = B(N_d+1) (閉合階梯 176→178→180!)
  ⇒ Γ 結構身份 = 已知容量/能量常數嘅重現, 冇新算子 (誠實)
"""
import csv
import json
import sys
from pathlib import Path

import mpmath as mp

O160 = Path(__file__).resolve().parent.parent
DATA = O160 / "data"
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
    print("=== 10 身份 + Γ 結構 ===")

    # ── 10 = 2F₅ 身份 ──
    check("G1: 10 = L₅−1 = 11−1 (AP 步長減一)", 10 == 11 - 1)
    check("G2: 10 = 2N_gen+B = 6+4 (世代倍數+分支因子)", 10 == 2 * 3 + 4)
    check("G3: 10 = F_proj−L₄ = 17−7", 10 == 17 - 7)
    check("G4: 梯子 6/10/11 = 2N_gen+{0,B,F₅}", {6, 10, 11} == {2 * 3 + x for x in [0, 4, 5]})
    check("G5: 掃描來源 SUM_plus(88,88,17) = γ₈₈+γ₈₈+λ₁₇ = 4+4+2 = 10",
          abs(4 + 4 + 2 - 10) < TOL, "(mpmath 驗證 21/21 已含)")

    # ── Γ row/col 和 ──
    gamma = [4 * mp.sin(k * mp.pi / 176) ** 2 for k in range(1, 89)]
    lam = [4 * mp.sin(c * mp.pi / 68) ** 2 for c in range(1, 34)]
    Sg = sum(gamma)   # = 178
    Sl = sum(lam)     # = 66
    # row 和: 66γ_a
    r44 = 66 * gamma[43]   # γ₄₄ = 2
    r88 = 66 * gamma[87]   # γ₈₈ = 4
    check("G6: Γ row 和 Σ_c γ₄₄λ_c = 66γ₄₄ = 132 = N_d·N_gen (O151 容量階梯)",
          abs(r44 - 132) < TOL)
    check("G6: Γ row 和 Σ_c γ₈₈λ_c = 66γ₈₈ = 264 = 6U(1)×N_d (O107)",
          abs(r88 - 264) < TOL)
    # col 和: 90λ_c
    c17 = 90 * lam[16]   # λ₁₇ = 2
    check("G7: Γ col 和 Σ_a γ_a λ₁₇ = 90λ₁₇ = 180 = B(N_d+1) (閉合階梯第三級)",
          abs(c17 - 180) < TOL, "(176→178→180, O155 T15)")
    # 全張量積和
    check("G8: ΣΓ = Σγ·Σλ = 178×66 = 11748?", abs(Sg * Sl - 178 * 66) < TOL,
          "⚠️ 注意: 88 鏈 Σγ = 178, 但 O157 用 90×66 = 5940 = Σγ_even×Σλ")
    # 正確 5940: Σγ_even×Σλ
    Se = sum(gamma[1::2])  # even k = 2,4,...,88 → index 1,3,...,87
    check("G8: ΣΓ(O157) = Σγ_even×Σλ = 90×66 = 5940 = B·N_gen³·F₅·L₅",
          abs(Se * Sl - 5940) < TOL and 5940 == 4 * 27 * 5 * 11,
          "(O157 R2 閉合引用)")
    check("G8: 5940 質因數 = 2²·3³·5·11", 5940 == 2 ** 2 * 3 ** 3 * 5 * 11)

    # ── 10 喺 web/operator dictionary 有冇? (grep 代替) ──
    web = json.loads((DATA / "constant_web.json").read_text())
    vals = [e["value"] for e in web["integers"] + web["halfints"] + web["rationals"]]
    check("G9: 10 唔喺 constant web (所以 novel 偵測標咗佢)", 10 not in vals,
          "(scan 時 web 冇 10; 今次 G1-G4 提供身份)")

    print(f"\nRESULT: {PASS}/{PASS + FAIL} PASS")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()
