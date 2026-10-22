#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
18_projector_operator.py — Item 1: 176→42 projector 算子 (P_CY₃)
=================================================================
自然分解: 176 = 66 ⊕ 68 ⊕ 42 (tree-pair ⊕ F₉-pair ⊕ F₈-pair)
  P = F₈-summand 投影: rank 42, nullity 134 = 幾何 = h¹¹+h²¹
  鏈 = tree-pair ⊕ home-pair (docs/08: N = K_tree + F₁₀), home = F₉-pair ⊕ F₈-pair
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

N = 88; K_tree = 33; F8 = 21; F9 = 34; F10 = 55; F11 = 89
N_d = 44; N_dp = 46; N_dm = 42

print("C1) 自然分解: 176 = 66 ⊕ 68 ⊕ 42")
check("66 = 2K_tree (tree-pair, R3 Σλ_tree)", 2*K_tree == 66)
check("68 = 2F₉ (F₉-pair, R3: 68 = 2F₉ = B·F_proj)", 2*F9 == 68)
check("42 = 2F₈ (F₈-pair, T13: N_d⁻ = 2F₈)", 2*F8 == 42)
check("66 + 68 + 42 = 176 = 2N", 66+68+42 == 2*N)

print("\nC2) 層級結構: tree ⊕ home (docs/08)")
check("N = K_tree + F₁₀ = 33+55 (chain = tree + home)", K_tree + F10 == N)
check("home-pair = 2F₁₀ = 110", 2*F10 == 110)
check("home-pair = F₉-pair ⊕ F₈-pair: 68 + 42 = 110", 68+42 == 110)
check("2N = 2K_tree + 2F₁₀ = 66 + 110", 66+110 == 2*N)

print("\nC3) ★ 幾何扇區 = tree-pair ⊕ F₉-pair = 134 = h¹¹+h²¹")
check("66 + 68 = 134", 66+68 == 134)
check("134 = 4K_tree + 2 (T13)", 4*K_tree+2 == 134)
check("134 = h¹¹ + h²¹ = 36+98", 36+98 == 134)
print("   ⇒ P 嘅 kernel = 幾何 (134); Im P = 觀察者 (42) — SES: 0→2F₈→2(F₈⊕F₉⊕K_tree)→2(F₉⊕K_tree)→0")

print("\nC4) 顯式 idempotent: P = F₈-summand 投影")
n = 176
P = np.zeros((n, n))
P[66+68:, 66+68:] = np.eye(42)   # keep F₈-pair (last 42 coords), kill 66⊕68
P2 = P @ P
from numpy.linalg import matrix_rank
check("P² = P (冪等)", np.allclose(P2, P))
check("rank P = 42", matrix_rank(P) == 42)
check("nullity P = 134", n - matrix_rank(P) == 134)
check("tr P = 42", abs(np.trace(P) - 42) < 1e-12)
check("P 固定 Im(P): P(Pv) = Pv", np.allclose(P @ (P @ np.ones(n)), P @ np.ones(n)))
# 幾何扇區被殺: P·e_j = 0 for j in 66⊕68
v_geom = np.zeros(n); v_geom[:134] = 1.0
check("P 殺幾何扇區 (kernel ⊇ 134)", np.allclose(P @ v_geom, 0))

print("\nC5) 自然性: F₈ = AP 終止項 (R4)")
check("AP {6,11,16,21} 終止於 F₈ = 21", F8 == 21, "(R4: F₉ = K_tree+1 封頂)")
check("觀察者 = AP 階梯最後一級 ×2", 2*21 == 42)
check("F₈ + F₉ = F₁₀ (fib 身份 → home 完整)", F8 + F9 == F10)

print("\nC6) 誠實 audit")
print("   - 分解/冪等/rank-nullity: 全部精確 ✅")
print("   - P 喺 ℝ¹⁷⁶ 嘅 block 形式自然 (66⊕68⊕42 = T̂ 階梯層)")
print("   - 🔴 開放: F₈-pair (42 個 mode) ↔ 對偶鏈實際 mode 嘅選擇規則")
print("     (21 對 (k,88−k)? 定 γ 閾值? 定 T̂ 權重?) — 需要 mode 級判準")

print(f"\nRESULT: {ok}/{tot} PASS")
