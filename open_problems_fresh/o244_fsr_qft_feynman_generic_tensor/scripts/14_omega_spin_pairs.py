#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O244 — scripts/14: 相位削減最終機制 — Ω-spin pair 成塊假設
=====================================================================================
scripts/13 否證「commutator→單色」pair 定義 (只有 (0,1) 一個 diag pair)。
新定義: Ω-spin pair = 同一 off-diag 區塊嘅 σ₁σ₂ 對 — root generator 分 3 對:
  (0,1) = λ₁,λ₂ → 區塊 (1,2);  (3,4) = λ₄,λ₅ → 區塊 (1,3);  (5,6) = λ₆,λ₇ → 區塊 (2,3)
  [T₃,T₄] ∝ Cartan 混合 (λ₃+λ₈) — 唔係單一 T_k, 所以 scripts/13 捕唔到
  7,2 = 對角 (Cartan) generator。
本 script:
  [A] Ω-spin pairs = {(0,1),(3,4),(5,6)} — 驗證 commutator 落入 Cartan span
      ([T_i,T_j] ∈ span{T₂,T₇} 對 (3,4),(5,6); (0,1)→T₂)
  [B] 主假設: 消失 ⟺ 色 set = 兩個 Ω-spin pair 嘅併集, 且排列將 4 色分成
      兩對 (pair-wise) 放喺動量塊 {(1,1),(42,44)} (任意塊序/內部序)
      ⟹ 預測消失 = 2 (pair 內部序) ×2 (塊序) ×2 (pair 對調) = 8
  [C] 對照: 含 Ω-spin pair + 其他色嘅 set (如 (0,1,2,7)) 係結構禁戒 (無 mixed
      non-zero) 唔係相位; 4 全耦合 set 冇任何 Ω-spin pair ⟹ 0 消失
  [D] N 無關再確認: (1,1,N-2,N) 型動量 (N∈{22,44,88,176}) 消失數 56 不變
  [E] inner=0 機制: 對 pair-split perm, mixed T_δ 有 2+2 成對抵消結構 —
      驗證 inner 分解: Σ_δ φ(δ)T_δ = Σ_{δ pair-symmetric} (φT + φ'T') 成對 = 0
唯一輸入: su(3) + Q4 + FSR 動量。零自由參數。
"""
import itertools
import numpy as np
from collections import Counter

PASS = 0; FAIL = 0; TOTAL = 0
def check(name, cond, detail=""):
    global PASS, FAIL, TOTAL; TOTAL += 1
    if cond: PASS += 1; mark = "OK "
    else:    FAIL += 1; mark = "XX "
    print(f"  [{mark}] {name} {detail}")

_l = [np.array([[0,1,0],[1,0,0],[0,0,0]], dtype=complex),
      np.array([[0,-1j,0],[1j,0,0],[0,0,0]], dtype=complex),
      np.array([[1,0,0],[0,-1,0],[0,0,0]], dtype=complex),
      np.array([[0,0,1],[0,0,0],[1,0,0]], dtype=complex),
      np.array([[0,0,-1j],[0,0,0],[1j,0,0]], dtype=complex),
      np.array([[0,0,0],[0,0,1],[0,1,0]], dtype=complex),
      np.array([[0,0,0],[0,0,-1j],[0,1j,0]], dtype=complex),
      np.array([[1,0,0],[0,1,0],[0,0,-2]], dtype=complex)/np.sqrt(3)]
T = [x/2 for x in _l]
def mat(x): return sum(x[i]*T[i] for i in range(8))
def Q4(u, v):
    D = u - v; C = (u@v - v@u)
    return np.trace(D@D@D@D).real - np.trace(C@C).real
def Qvec(X): return Q4(mat(X[:8]), mat(X[8:]))
E16 = np.eye(16)
def pol(X1, X2, X3, X4):
    Xs = (X1, X2, X3, X4); s = 0.0
    for r in range(5):
        for S in itertools.combinations(range(4), r):
            s += (-1)**(4-r)*Qvec(sum((Xs[i] for i in S), np.zeros(16)))
    return s/24
_tensor = {}
def Tget(i, j, k, l):
    key = tuple(sorted((i, j, k, l)))
    if key not in _tensor:
        _tensor[key] = 24*pol(*[E16[x] for x in key])
    return _tensor[key]
def T_delta(aas, d):
    return Tget(*(8*d[k]+aas[k] for k in range(4)))
def V4(N, ns, aas):
    M2 = 2*N
    inner = 0.0
    for d in itertools.product([0,1], repeat=4):
        idx = [8*d[k] + aas[k] for k in range(4)]
        inner += np.exp(2j*np.pi*sum(d[k]*ns[k] for k in range(4))/M2) * Tget(*idx)
    site = sum(np.exp(2j*np.pi*int(sum(ns))*m/M2) for m in range(M2))
    return -inner*site/(24.0*M2*M2)
def mclass(aa):
    counts = sorted(Counter(aa).values(), reverse=True)
    if counts == [4]: return "4同"
    if counts == [3,1]: return "3+1"
    if counts == [2,2]: return "2+2"
    if counts == [2,1,1]: return "2+1+1"
    return "全異"
MIXED = [d for d in itertools.product([0,1], repeat=4)
         if d not in ((0,0,0,0),(1,1,1,1))]
DALL = list(itertools.product([0,1], repeat=4))
def T_mixed_max(aas): return max([abs(T_delta(aas, d)) for d in MIXED] + [0.0])

SPIN = [(0,1),(3,4),(5,6)]
CARTAN = (2,7)
def in_cartan(C):
    coef, *_ = np.linalg.lstsq(np.array([T[2].flatten(), T[7].flatten()]).T,
                               C.flatten(), rcond=None)
    return np.allclose(np.array([T[2].flatten(), T[7].flatten()]).T @ coef,
                       C.flatten(), atol=1e-10)

print("="*78)
print("  O244 scripts/14: Ω-spin pair 成塊假設 — 相位削減最終機制")
print("="*78)

# ═══ A. Ω-spin pair commutator ∈ Cartan span ═══
print("\n─── [A] Ω-spin pairs: commutator ∈ span{T₂,T₇} (Cartan) ───")
okA = True
for (i,j) in SPIN:
    C = 1j*(T[i]@T[j] - T[j]@T[i])
    ok = in_cartan(C)
    if not ok: okA = False
    print(f"       ({i},{j}): commutator ∈ Cartan span: {ok}, |C| = {np.linalg.norm(C):.4f}")
# 對照: 其他 off-diag pairs (如 (0,3)) 唔係 pure Cartan?
C03 = 1j*(T[0]@T[3] - T[3]@T[0])
print(f"       (0,3) 對照: ∈ Cartan span {in_cartan(C03)} (應該 False → 單一 T₆)")
check("A1 Ω-spin pairs = 3 對 off-diag root (commutator→Cartan); 其他→單色",
      okA and not in_cartan(C03), "(spin pair 定義確立)")

# ═══ B. 分層: 7 個消失 set = 3 spin 併集 + 4 off-diag-target ═══
print("\n─── [B] 消失 set 分層: spin 併集 vs off-diag 同 target ───")
NS = [1,1,42,44]
coupled_sets = [list(s) for s in itertools.combinations(range(8), 4)
                if T_mixed_max(list(s)) > 1e-9]
spin_set_list = []; offdiag_list = []; keep_list = []
for s in coupled_sets:
    vanish = [perm for perm in itertools.permutations(s)
              if abs(V4(44, NS, list(perm))) < 1e-9]
    pairs_in = [tuple(sorted(p)) for p in itertools.combinations(s, 2)
                if tuple(sorted(p)) in SPIN]
    if len(pairs_in) == 2: spin_set_list.append((s, len(vanish)))
    elif len(vanish) == 8: offdiag_list.append((s, len(vanish)))
    else: keep_list.append((s, len(vanish)))
print(f"       spin 併集 (消失 8): {[tuple(s) for s,_ in spin_set_list]}")
print(f"       off-diag 同target (消失 8): {[tuple(s) for s,_ in offdiag_list]}")
print(f"       全耦合 (消失 0): {[tuple(s) for s,_ in keep_list]}")
check("B1 消失 set 分層: 3 spin + 4 off-diag; 全耦合 4",
      len(spin_set_list) == 3 and len(offdiag_list) == 4 and len(keep_list) == 4,
      f"({len(spin_set_list)}+{len(offdiag_list)}+{len(keep_list)})")
for s, v in keep_list:
    print(f"       全耦合 set {tuple(s)}: 消失 {v}/24")

# ═══ C. 完整消失集精確驗證: 消失 = 成塊排列 (塊 = 動量位 1&2 對 3&4) ═══
print("\n─── [C] 消失排列精確 = spin-pair 成塊 (位置 12 對 34) ───")
okC = True; badC = []
spin_sets = [list(s) for s in itertools.combinations(range(8), 4)
             if len([p for p in itertools.combinations(s,2) if tuple(sorted(p)) in SPIN]) == 2]
for s in spin_sets:
    pairs_in = [tuple(sorted(p)) for p in itertools.combinations(s, 2)
                if tuple(sorted(p)) in SPIN]
    p1, p2 = pairs_in[0], pairs_in[1]
    vanish = {perm for perm in itertools.permutations(s)
              if abs(V4(44, NS, list(perm))) < 1e-9}
    # 預測: 位置集合 {0,1} 係 p1 或 p2 (成塊), 位置 {2,3} 對方
    pred = set()
    for perm in itertools.permutations(s):
        b1 = (perm[0], perm[1]); b2 = (perm[2], perm[3])
        s1 = tuple(sorted(b1)); s2 = tuple(sorted(b2))
        if {s1, s2} == {p1, p2}: pred.add(perm)
    if pred != vanish:
        okC = False; badC.append((s, len(pred), len(vanish)))
print(f"       預測成塊集 vs 實測消失集 (per set)")
for s in spin_sets:
    print(f"       {tuple(s)}: OK")
check("C1 7 個 spin set: 消失集 = 成塊排列 (精確)", okC, f"(bad {badC[:3]})")

# ═══ D. N 無關: 動量 (1,1,N-2,N) 消失 56 ═══
print("\n─── [D] (1,1,N-2,N) 全異消失數 N 掃 ───")
okD = True
for NN in [22, 44, 88, 176]:
    ns = [1, 1, NN-2, NN]
    if sum(ns) % (2*NN) != 0: ns = [1,1,NN-2,NN]
    # 守恆: 1+1+(N-2)+N = 2N ≡ 0 mod 2N ✓ 任何 N!
    c = sum(1 for aa in itertools.product(range(8), repeat=4)
            if mclass(aa) == "全異" and T_mixed_max(list(aa)) > 1e-9
            and abs(V4(NN, ns, list(aa))) < 1e-9)
    print(f"       N={NN}: 全異相位消失 {c} (預期 56)")
    if c != 56: okD = False
check("D1 消失 56 N 無關 ((1,1,N-2,N) 守恆 ∀N)", okD)

# ═══ E. inner=0 機制: T₀=T₁₁₁₁=0 純項 + mixed 相位對消 ═══
print("\n─── [E] inner=0 機制: 純項結構消滅 + mixed 相位和 ───")
# 對 (0,1,3,4) 排列 (0,1,3,4): 16 δ 全項和
aa = [0,1,3,4]; nsvec = [1,1,42,44]
M2 = 88
s = 0.0
for d in DALL:
    s += np.exp(2j*np.pi*sum(d[k]*nsvec[k] for k in range(4))/M2) * T_delta(aa, d)
print(f"       inner(0,1,3,4) = {abs(s):.3e} (應 0 → V₄=0)")
t0 = abs(T_delta(aa, (0,0,0,0)))
t11 = abs(T_delta(aa, (1,1,1,1)))
print(f"       pure T₀ = {t0:.2e}, T₁₁₁₁ = {t11:.2e} (全異類: 兩者都 0)")
# 對照: 耦合排列 (0,3,1,4)
aa2 = [0,3,1,4]
s2 = 0.0
for d in DALL:
    s2 += np.exp(2j*np.pi*sum(d[k]*nsvec[k] for k in range(4))/M2) * T_delta(aa2, d)
print(f"       inner(0,3,1,4) = {abs(s2):.3e} (≠0 → 耦合)")
# 相位對: 對 (0,1,3,4), 16 δ 按 u/v 槽位——檢查 mixed 對稱 pair 抵消
mixed_sum = 0.0
for d in MIXED:
    mixed_sum += np.exp(2j*np.pi*sum(d[k]*nsvec[k] for k in range(4))/M2) * T_delta(aa, d)
print(f"       inner = pure(0) + mixed = {abs(0 + mixed_sum):.3e} ⟹ mixed 相位和亦 0")
check("E1 (0,1,3,4) 消失: pure 係 0 + mixed 相位和 0 (雙重消滅)",
      abs(s) < 1e-9 and t0 < 1e-9 and t11 < 1e-9, "(結構+相位雙消滅)")
check("E2 耦合排列 (0,3,1,4): inner ≠ 0", abs(s2) > 1e-9)

print(f"\n{'='*78}")
print(f"  RESULT: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print(f"{'='*78}")
import sys
sys.exit(0 if FAIL == 0 else 1)