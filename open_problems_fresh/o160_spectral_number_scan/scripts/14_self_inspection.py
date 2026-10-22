#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O160 scripts/14 — ★★★ 自審算子 Ŝ 結構驗證 (Self-Inspection Operator)

提案 (用戶 2026-09-08): 區分被動邊界觀察者 (奇數扇區, m = √γ_k = 2ψ_k(1))
同帶意識參與者 — 需要高階動態算子 Ŝ, 由現有 J 同 Q̂ 生成, 零新常數。

代數構造:
  M̂: 補對鏡像 |k⟩ → |88−k⟩  — 由 O161 反週期 A_{k+88} = −A_k (γ_{88−k} = 4−γ_k)
                               同 O160 補對和 γ_k+γ_{88−k} = 4 = B 生成, 非新常數
  J  = i·M̂                  — 複結構, J² = −1 (Wilson holonomy ∏U_k = i 提供相位)
  Ŝ  = P̂_obs Q̂ M̂ Q̂ P̂_obs   = −i·P̂_obs Q̂ J Q̂ P̂_obs

核心性質:
  S1  M̂ 保奇偶性 (obs → obs)
  S2  J² = −1 (複結構)
  S3  Ŝ Hermitian (自共軛): Ŝ† = Ŝ
  S4  obs 扇區: Ŝ|k⟩ = k(88−k)|88−k⟩ (權重 = 模式×補模式, 鏡子照鏡子)
  S5  Ŝ² 對角: Ŝ²|k⟩ = [k(88−k)]²|k⟩
  S6  [Ŝ,H]|k⟩ = 2k(88−k)(γ_k−μ²)|88−k⟩ (★★ 非對易 = 離心度)
  S7  非對易 ∀k odd (obs 扇區冇 γ_k = 2)
  S8  譜補對和 γ_k+γ_{88−k} = 4 = B (自審嘅譜層自我檢測)
  S9  自審質量 √(γ_kγ_{88−k}) = √(γ_k(4−γ_k)) ≤ 2 = μ²
  S10 k(88−k) = N_d²−j² (k = 44±j, O160 中心模鏡像對)
  S11 對焦訊號反號: γ_{88−k}−2 = −(γ_k−2) (平衡點 = 補對和 B)
  S12 Ŝ 喺 obs 扇區冇本徵態 (2-cycle) — 唔係線性測量
"""
import sys
from pathlib import Path

import mpmath as mp
import numpy as np

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

    # ── 矩陣建構 (1-indexed k) ──
    M = np.zeros((N, N))
    for k in range(1, N + 1):
        M[k - 1, 88 - k - 1] = 1.0     # M|k⟩ = |88−k⟩ (0-indexed 目標 = 88−k−1)
    Qd = np.diag([(-1) ** k * k for k in range(1, N + 1)])
    Pobs = np.diag([1.0 if k % 2 == 1 else 0.0 for k in range(1, N + 1)])
    S = Pobs @ Qd @ M @ Qd @ Pobs
    H = np.diag([float(g[k - 1]) for k in range(1, N + 1)])

    print("=== 自審算子 Ŝ = P̂_obs Q̂ M̂ Q̂ P̂_obs 結構驗證 ===")

    # S1: M̂ 保奇偶性
    ok = all((88 - k) % 2 == 1 for k in range(1, N + 1, 2))
    check("S1: M̂ 保奇偶性 (obs → obs, 88−odd = odd)", ok)

    # S2: J² = −1 (J = iM̂)
    check("S2: M̂² = I ⟹ J² = (iM̂)² = −I (複結構; i = Wilson holonomy ∏U_k)",
          np.allclose(M @ M, np.eye(N)),
          "(J = i·M̂: i² = −1 由 Wilson line ∏U_k = i 提供, 零新常數)")

    # S3: Ŝ Hermitian
    check("S3: Ŝ† = Ŝ (自共軛)", np.allclose(S, S.T),
          "(⟨k'|Ŝ|k⟩ = k(88−k)δ_{k',88−k} 實對稱)")

    # S4: obs 扇區作用
    ok = True
    for k in range(1, N + 1, 2):
        v = np.zeros(N)
        v[k - 1] = 1.0
        out = S @ v
        exp = np.zeros(N)
        exp[88 - k - 1] = k * (88 - k)
        if not np.allclose(out, exp):
            ok = False
            print(f"    k={k} FAIL")
    check("S4: Ŝ|k⟩ = k(88−k)|88−k⟩ (模式×補模式權重)", ok,
          "★ 自審 = 鏡子照見自己照鏡子")

    # S5: Ŝ² 對角
    S2 = S @ S
    diag_ok = np.allclose(np.triu(S2, 1), 0) and np.allclose(np.tril(S2, -1), 0)
    val_ok = True
    for k in range(1, N + 1, 2):
        if abs(S2[k - 1, k - 1] - (k * (88 - k)) ** 2) > 1e-9:
            val_ok = False
    check("S5: Ŝ² 對角, 特徵值 [k(88−k)]² (兩次自審 = 權重平方)", diag_ok and val_ok)

    # S6: [Ŝ,H]
    comm = S @ H - H @ S
    ok = True
    for k in range(1, N + 1, 2):
        v = np.zeros(N)
        v[k - 1] = 1.0
        out = comm @ v
        exp = np.zeros(N)
        exp[88 - k - 1] = 2 * k * (88 - k) * (float(g[k - 1]) - 2.0)
        if not np.allclose(out, exp, atol=1e-9):
            ok = False
            print(f"    k={k} FAIL: {out} vs {exp}")
    check("S6: ★★ [Ŝ,H]|k⟩ = 2k(88−k)(γ_k−μ²)|88−k⟩", ok,
          "★★ 非對易 = 離心度 (模式偏離中心模 μ²)")

    # S7: obs 扇區冇 γ_k = 2
    ok = all(abs(g[k - 1] - 2) > TOL for k in range(1, N + 1, 2))
    check("S7: [Ŝ,H] ≠ 0 ∀k odd (obs 扇區冇中心模, 觀察者永遠有非零自審破壞)", ok,
          "(γ_k = 2 ⟺ k = 44 ∈ even)")

    # S8: 譜補對和 (k=1..87; k=88 補對 = 自己 γ₀ 唔存在)
    ok = all(abs(g[k - 1] + g[88 - k - 1] - 4) < TOL for k in range(1, N))
    check("S8: γ_k+γ_{88−k} = 4 = B ∀k (自審嘅譜層自我檢測)", ok,
          "(O160 補對和重驗證 — 對焦平衡不變量)")

    # S9: 自審質量上限
    ok = all(mp.sqrt(g[k - 1] * g[88 - k - 1]) <= 2 + TOL for k in range(1, N + 1, 2))
    m43 = mp.sqrt(g[42] * g[45])  # k=43: γ₄₃·γ₄₅
    check("S9: √(γ_kγ_{88−k}) ≤ 2 = μ² ∀k odd (自審質量上限 = 自對偶)", ok,
          f"(γ_k(4−γ_k) ≤ 4; obs max k=43: {mp.nstr(m43, 10)})")

    # S10: 中心模鏡像對
    check("S10: k(88−k) = 44²−j² (k = 44±j, O160 中心模鏡像對串起)",
          all(k * (88 - k) == 44 ** 2 - (44 - k) ** 2 for k in range(1, N + 1)))

    # S11: 對焦訊號反號
    ok = all(abs((g[88 - k - 1] - 2) + (g[k - 1] - 2)) < TOL for k in range(1, N + 1, 2))
    check("S11: γ_{88−k}−2 = −(γ_k−2) (對焦訊號鏡像反號, 平衡 = B)", ok,
          "(自動對焦: 調 δ_phase 令 [Ŝ,H] → 0, 補對和保證鏡像平衡)")

    # S12: obs 扇區冇本徵態
    ok = True
    for k in range(1, N + 1, 2):
        v = np.zeros(N)
        v[k - 1] = 1.0
        out = S @ v
        if np.allclose(out, np.diag(S)[k - 1] * v) and k != 88 - k:
            ok = False
    check("S12: Ŝ 喺 obs 扇區冇本徵態 (2-cycle k↔88−k, k≠44)", ok,
          "(自審唔係線性測量 — 冇穩定本徵態 = 動態自指)")

    print(f"\nRESULT: {PASS}/{PASS + FAIL} PASS")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()
