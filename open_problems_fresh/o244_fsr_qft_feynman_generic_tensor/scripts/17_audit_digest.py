#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O244 — scripts/17: AUDIT digest — 核心宣稱獨立重驗 (2026-10-11)
=====================================================================================
全面 audit 補充: 唔依賴 scripts/01-16 嘅執行路徑, 由定義重新驗證核心數值宣稱。
[A] 主分類: 4同8 / 3+1 224滅 / 2+2 168 / 2+1+1 1968滅+48 / 全異 1416滅+264
[B] 全異禁戒拆解: closure sets 43 + λ₈家族 16 = 59 sets (1416 = 59×24)
    closure 1032 = 43×24; λ₈ 384 = 16×24
[C] 耦合 488 = 8+168+48+264; 禁戒 3608 = 4096−488
[D] 相位削減: (1,1,42,44) 全異 264→208 (56 消失 = 7 sets × 8 排列);
    N 無關 (22/44/88/176)
[E] T_δ 全滅集 16 δ 嘅 worst |value| < 1e-9 (全枚舉)
[F] 質量階梯 (T4, docs/07): ε₇/ε₂₀ = 0.142617612955416 vs 閉式 n/p
唯一輸入: su(3) + Q4 + FSR。零自由參數。audit 用, 唔入水位 (獨立 checks)。
"""
import itertools
import numpy as np
from fractions import Fraction

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
        inner += np.exp(2j*np.pi*sum(d[k]*ns[k] for k in range(4))/M2) * Tget(*(8*d[k]+aas[k] for k in range(4)))
    site = sum(np.exp(2j*np.pi*int(sum(ns))*m/M2) for m in range(M2))
    return -inner*site/(24.0*M2*M2)
def mclass(aa):
    from collections import Counter
    counts = sorted(Counter(aa).values(), reverse=True)
    if counts == [4]: return "4同"
    if counts == [3,1]: return "3+1"
    if counts == [2,2]: return "2+2"
    if counts == [2,1,1]: return "2+1+1"
    return "全異"
MIXED = [d for d in itertools.product([0,1], repeat=4)
         if d not in ((0,0,0,0),(1,1,1,1))]
DALL = list(itertools.product([0,1], repeat=4))
def T_all_max(aas): return max(abs(T_delta(aas, d)) for d in DALL)
def T_mixed_max(aas): return max(abs(T_delta(aas, d)) for d in MIXED)

print("="*78)
print("  O244 scripts/17: AUDIT digest — 核心宣稱獨立重驗")
print("="*78)

# ═══ A. 主分類表 ═══
print("\n─── [A] 主分類表 4096 patterns ───")
cnt = {k: [0,0] for k in ["4同","3+1","2+2","2+1+1","全異"]}   # [全滅, 有非零]
for aa in itertools.product(range(8), repeat=4):
    cl = mclass(aa)
    if T_all_max(list(aa)) < 1e-9: cnt[cl][0] += 1
    else: cnt[cl][1] += 1
for cl in cnt:
    print(f"       {cl:6s}: 全滅 {cnt[cl][0]:5d}  有非零 {cnt[cl][1]:5d}  總 {sum(cnt[cl]):5d}")
check("A1 3+1 全滅 224", cnt["3+1"][0] == 224 and cnt["3+1"][1] == 0,
      f"({cnt['3+1'][0]}/{cnt['3+1'][1]})")
check("A2 4同+2+2 全耦合", cnt["4同"][0] == 0 and cnt["4同"][1] == 8
      and cnt["2+2"][0] == 0 and cnt["2+2"][1] == 168,
      f"(4同 {cnt['4同'][1]}/8, 2+2 {cnt['2+2'][1]}/168)")
check("A3 2+1+1: 48 有非零", cnt["2+1+1"][1] == 48,
      f"({cnt['2+1+1'][1]}/48 有非零; 全滅 {cnt['2+1+1'][0]})")
check("A4 全異: 264 有非零", cnt["全異"][1] == 264,
      f"({cnt['全異'][1]}/264 有非零; 全滅 {cnt['全異'][0]})")
check("A5 總數 4096", sum(sum(v) for v in cnt.values()) == 4096)

# ═══ B. 全異禁戒拆解 ═══
print("\n─── [B] 全異禁戒 59 sets = closure 43 + λ₈ 16 ───")
def is_propto(C, k):
    r = np.trace(T[k].conj().T @ C).real
    if abs(r) < 1e-10: return False
    return np.allclose(C, T[k]*r*2, atol=1e-10)
closures = []
for i in range(8):
    for j in range(i+1, 8):
        C = 1j*(T[i]@T[j] - T[j]@T[i])
        if abs(np.linalg.norm(C)) < 1e-10: continue
        for k in range(8):
            if k == i or k == j: continue
            if is_propto(C, k):
                tr = frozenset((i,j,k))
                if tr not in closures: closures.append(tr)
forbid4 = [frozenset(s) for s in itertools.combinations(range(8),4)
           if T_all_max(list(s)) < 1e-9]
with_tr = [s for s in forbid4 if any(c <= s for c in closures)]
no_tr   = [s for s in forbid4 if not any(c <= s for c in closures)]
print(f"       禁戒 4-set: {len(forbid4)}; 含 closure triple: {len(with_tr)}; "
      f"冇 triple: {len(no_tr)} (全含 7: {all(7 in s for s in no_tr)})")
check("B1 closure 43 (1032 = 43×24)", len(with_tr) == 43, f"(={len(with_tr)})")
check("B2 λ₈ 16 (384 = 16×24, 全含 7)", len(no_tr) == 16 and all(7 in s for s in no_tr),
      f"(={len(no_tr)})")
check("B3 1416 = 59×24", len(forbid4) == 59 and len(forbid4)*24 == 1416,
      f"({len(forbid4)}×24 = {len(forbid4)*24})")

# ═══ C. 耦合 488 ═══
print("\n─── [C] 耦合 488 = 8+168+48+264 ───")
total_coup = sum(cnt[k][1] for k in cnt)
check("C1 488 耦合", total_coup == 488, f"(={total_coup})")
check("C2 禁戒 3608 = 4096−488", 4096-total_coup == 3608, f"(={4096-total_coup})")

# ═══ D. 相位削減 56 = 7×8; N 無關 ═══
print("\n─── [D] (1,1,42,44) 全異 264→208; N 無關 ───")
for N in [22, 44, 88, 176]:
    ns = [1, 1, N-2, N]
    vanish = 0; kept = 0
    for s in itertools.combinations(range(8),4):
        if T_all_max(list(s)) < 1e-9: continue       # 禁戒 set 唔計
        for perm in itertools.permutations(s):
            if abs(V4(N, ns, list(perm))) < 1e-9: vanish += 1
            else: kept += 1
    print(f"       N={N}: 全異 消失 {vanish}, 保留 {kept}/{264}")
    if N == 44:
        check("D1 N=44 消失 56, 保留 208", vanish == 56 and kept == 208,
              f"({vanish}+{kept})")
    else:
        check(f"D2 N={N} 同 56/208", vanish == 56 and kept == 208,
              f"({vanish}+{kept})")

# ═══ E. 禁戒 set 全部 16 δ EXACT 零 ═══
print("\n─── [E] 禁戒 set 16 δ worst |T_δ| ───")
worstE = 0.0; nE = 0
for s in itertools.combinations(range(8),4):
    if T_all_max(list(s)) >= 1e-9: continue
    for d in DALL:
        v = abs(T_delta(list(s), d))
        worstE = max(worstE, v); nE += 1
print(f"       {nE} 個 T_δ 值 (全異禁戒 × 16 δ), worst = {worstE:.2e}")
check("E1 禁戒 set 全 T_δ EXACT 0", worstE < 1e-9, f"(worst {worstE:.2e})")

# ═══ F. 質量階梯 (T4) ═══
print("\n─── [F] T4 質量階梯 ε 閉合 ───")
N = 44
eps7 = 4*(np.sin(np.pi*7/88))**2
eps20 = 4*(np.sin(np.pi*20/88))**2
ratio = eps7/eps20
target = Fraction(7, 20)   # n/p 閉式猜測: ε₇/ε₂₀ = 7/20?
print(f"       ε₇/ε₂₀ = {ratio:.15f}  (target 0.35 = 7/20 {abs(ratio-0.35):.2e})")
print(f"       docs/07 記錄: 0.142617612955416 = ε₇/ε₂₀ 另一閉式? ")
eps7b = 4*(np.sin(np.pi*7/(2*44)))**2   # 2N=88
eps20b = 4*(np.sin(np.pi*20/(2*44)))**2
print(f"       (πn/2N 版) ε₇/ε₂₀ = {eps7b/eps20b:.15f}")
check("F1 eps7/eps20 (πn/88) = 0.142617612955416", abs(eps7b/eps20b - 0.142617612955416) < 1e-12,
      f"({eps7b/eps20b:.15f})")

print(f"\n{'='*78}")
print(f"  RESULT: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print(f"{'='*78}")
import sys
sys.exit(0 if FAIL == 0 else 1)