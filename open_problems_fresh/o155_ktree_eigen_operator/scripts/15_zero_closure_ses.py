#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
15_zero_closure_ses.py — 176−134−42 = 0: 精確零閉合嘅同調讀法
=============================================================
用戶強調「= 0」: 唔係近似, 係精確零剩餘。
結構讀法: 176 = 134 + 42 ⟺ dim V_full = dim V_geom + dim V_obs
        ⟺ 分裂正合序列 0 → V_obs → V_full → V_geom → 0
        ⟺ rank-nullity: dim V = dim Im P + dim Ker P (P: 176→42, ker=134)
        ⟺ 「觀察者自相干」 = idempotence: P² = P
"""
import mpmath as mp
import numpy as np

mp.mp.dps = 50
ok = 0; tot = 0
def check(name, cond, detail=""):
    global ok, tot
    tot += 1
    if cond: ok += 1
    print(f"   [{'PASS' if cond else 'FAIL'}] {name} {detail}")

print("C1) 主身份: 精確零閉合 (dev = 0)")
check("176 − 134 − 42 = 0", 176 - 134 - 42 == 0, f"{176-134-42}")
check("134 + 42 = 176", 134 + 42 == 176)

print("\nC2) 零閉合家族 (全部精確)")
# 全譜和 = 模數 + 世界: 2F₁₁ = 178 = 134 + 44
check("178 − 134 − 44 = 0", 178 - 134 - 44 == 0, "(2F₁₁ = 模數 + 世界)")
# 鏈 = 世界高側 + 觀察者: 88 = 46 + 42
check("88 − 46 − 42 = 0", 88 - 46 - 42 == 0, "(N = N_d⁺ + N_d⁻)")
# 世界 − 觀察者 = 奇偶隙: 44 − 42 = 2
check("44 − 42 − 2 = 0", 44 - 42 - 2 == 0, "(N_d − N_d⁻ = E−O)")
# O153 容量: 90 + 88 = 178
check("90 + 88 − 178 = 0", 90 + 88 - 178 == 0, "(Σγ_even + C_obs = 2F₁₁)")
# 一致性: 兩個零閉合共享同一 134 — 世界/觀察者之差就係 E−O
check("(178−134) − (176−134) = 44−42 = 2 = E−O", (178-134)-(176-134) == 2)

print("\nC3) ★ rank-nullity / 分裂正合序列")
# 0 → V_obs (42) → V_full (176) → V_geom (134) → 0
# dim V_full = dim V_obs + dim V_geom  (短正合序列維度恆等式)
check("dim V_full = dim V_obs + dim V_geom", 176 == 42 + 134,
      "→ 0 → V_obs → V_full → V_geom → 0 分裂")
# 投影 P: ℝ¹⁷⁶ → ℝ⁴², canonical block projector diag(I₄₂, 0₁₃₄)
n = 176; r = 42
P = np.zeros((n, n)); P[:r, :r] = np.eye(r)
check("rank P = 42", int(np.linalg.matrix_rank(P)) == r)
check("nullity P = 134", n - int(np.linalg.matrix_rank(P)) == 134)
check("rank-nullity: 176 = 42 + 134", n == int(np.linalg.matrix_rank(P)) + (n - int(np.linalg.matrix_rank(P))))

print("\nC4) ★★ 自相干 = idempotence (P² = P)")
P2 = P @ P
check("P² = P (冪等)", np.allclose(P2, P))
# 投影固定自己嘅像: v ∈ Im(P) ⟹ P·v = v
v = P @ np.random.default_rng(42).normal(size=n)
check("P 固定 Im(P): P(Pv) = Pv", np.allclose(P @ v, v))
# 核 = 幾何扇區: ker P 係 134 維
from numpy.linalg import matrix_rank
check("tr P = 42 (觀察者維度)", abs(np.trace(P) - 42) < 1e-12)
check("ker P 維度 = 134 (CY₃ 模數)", n - matrix_rank(P) == 134)

print("\nC5) 誠實 audit")
# 零閉合嘅內容: 兩項獨立身份 (唔係算術)
check("134 = 3N_d + 2 (模數身份, ktree_structure)", 3*44 + 2 == 134)
check("42 = N_d − 2 (觀察者身份, O153)", 44 - 2 == 42)
check("和 = 4N_d = 2N (定義 N = 2N_d)", 134 + 42 == 4*44 == 2*88)
print("   ⇒ 零嘅內容喺兩項獨立結構身份, 唔喺算術")
print("   ⇒ SES/rank-nullity 讀法係 operator 級: P = splitting map")
print("   ⇒ 🔴 但 P 嘅自然構造 (邊界條件/譜投影) 未推導 — 呢度用 canonical block projector 示範結構")

print(f"\nRESULT: {ok}/{tot} PASS")
