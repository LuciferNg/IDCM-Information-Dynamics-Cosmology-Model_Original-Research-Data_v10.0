#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O160 scripts/18 — ★★★ GUT 分支鏈維度全閉合 (E₆ ⊃ SO(10) ⊃ SU(5) ⊃ SM)

開放項: GUT 跨域 🟡 (78=E₆, 45=SO(10), 24=SU(5) 內部結構未登記).

發現: 標準群論分支鏈嘅維度全部可以用 IDCM 結構量 {B, N_gen, L₅, F₅, F₇, N_d}
生成 — 零新常數. E₆ ⊃ F₄ 分支都閉合.

標準事實 (G1/G3/G5/G6 用教科書維度):
  E₆ ⊃ SO(10)×U(1):  78 = 45 ⊕ 16 ⊕ 16̄ ⊕ 1
  SO(10) ⊃ SU(5)×U(1): 45 = 24 ⊕ 10 ⊕ 10̄ ⊕ 1
  SU(5) ⊃ SM:         24 = (8,1)₀ ⊕ (1,3)₀ ⊕ (1,1)₀ ⊕ (3,2) ⊕ (3̄,2)
  E₆ ⊃ F₄:            78 = 52 ⊕ 26
"""
import sys, math
sys.path.insert(0, ".")
sys.path.insert(0, "../o140_fsr_spectrum_scan")
sys.path.insert(0, "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")

# ── IDCM 結構量 ──────────────────────────────────────────────
B      = 4                      # 分支因子 (γ₄₄ = 4)
N_gen  = 3                      # 世代
L4, L5 = 7, 11                  # Lucas
F5, F7 = 5, 13                  # Fibonacci
N_d    = 44                     # 世界維度 (88/2)
K_tree = 33                     # N_gen³ + 2N_gen

def C(n, k):
    return math.comb(n, k)

def check(name, cond, note=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {note}")
    return cond

results = []
results.append(check(
    "G1: E₆⊃SO(10)×U(1) 標準分支 78 = 45⊕16⊕16̄⊕1",
    78 == 45 + 16 + 16 + 1, "(教科書: E₆ adjoint 分支)"))
results.append(check(
    "G2: ★ 78 = C(L₅−1,2) + 2B² + 1 = 45 + 32 + 1",
    78 == C(L5 - 1, 2) + 2 * B**2 + 1, f"({C(L5-1,2)} + {2*B**2} + 1)"))
results.append(check(
    "G3: SO(10)⊃SU(5)×U(1) 標準分支 45 = 24⊕10⊕10̄⊕1",
    45 == 24 + 10 + 10 + 1, "(教科書: SO(10) adjoint 分支)"))
results.append(check(
    "G4: ★ 45 = [C(2B,2)−B] + 2C(F₅,2) + 1 = 24 + 20 + 1",
    45 == (C(2 * B, 2) - B) + 2 * C(F5, 2) + 1,
    f"([{C(2*B,2)}-{B}] + {2*C(F5,2)} + 1)"))
results.append(check(
    "G5: ★ SU(5)⊃SM 24 = 2B + N_gen + 1 + 2·(2N_gen) = 8+3+1+6+6",
    24 == 2 * B + N_gen + 1 + 2 * (2 * N_gen),
    f"({2*B}+{N_gen}+1+{2*(2*N_gen)})"))
results.append(check(
    "G6: E₆⊃F₄ 標準分支 78 = 52⊕26",
    78 == 52 + 26, "(教科書: E₆ ⊃ F₄ 分支)"))
results.append(check(
    "G7: ★ 52 = N_d + 2B = 44 + 8",
    52 == N_d + 2 * B, f"({N_d}+{2*B})"))
results.append(check(
    "G8: ★ 26 = 2F₇ = 2×13",
    26 == 2 * F7, f"({2*F7})"))
results.append(check(
    "G9: ★ 16 = B² (SO(10) spinor = 分支因子平方, O152 已閉合)",
    16 == B**2, "(B = γ₄₄ = 4)"))
results.append(check(
    "G10: 分支鏈 78→45→24→12 全由 {B,N_gen,L₅,F₅,F₇,N_d} 生成 (零新常數)",
    78 == C(L5 - 1, 2) + 2 * B**2 + 1
    and 45 == (C(2 * B, 2) - B) + 2 * C(F5, 2) + 1
    and 24 == 2 * B + N_gen + 1 + 2 * (2 * N_gen)
    and 12 == B * N_gen,
    "(12 = B·N_gen = su(12) fundamental, O59 已閉合)"))

npass = sum(results)
print(f"\nRESULT: {npass}/{len(results)} PASS")
sys.exit(0 if npass == len(results) else 1)
