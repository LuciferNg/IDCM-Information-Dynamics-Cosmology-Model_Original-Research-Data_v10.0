#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O244 — scripts/09: 全異額外禁戒 16 sets 結構挖掘（T_δ 全滅機制補完）
=====================================================================================
scripts/08 結果: 全異禁戒 1416 = 1032 (su(2)-closure triple, 43 sets) + 384 (16 sets 冇
triple 但 T_δ 全滅)。本 script 將 16 個 set 嘅公共結構完整列出, 識別機制:
  * [A] 16 sets 列表 + 公共元素統計 (7=λ₈ 出現次數、pair 結構)
  * [B] 試機制候選: (a) 含「u-spin dual」triple? (b) 7-參與嘅 pseudo-closure:
        [T_i,T_7] ∝ T_k 且 {i,k} 加 7 形成 3-cycle? (c) 對每個 set, 檢查能否由
        某種「廣義 closure」解釋 (commutator 成比例 或 anticommutator 成比例)
  * [C] Tr 恆等驗證: 對 16 sets 嘅代表, Q4 expansion 嘅每項 trace 直接計
        → 睇係邊個 trace 消滅 (Tr[T_p T_q T_r] 或 Tr[T_p²T_q] = δ 型)
  * [D] 如果 [C] 揭示線索 → 全異類封閉機制 = closure triple ∪ pseudo-closure(7)
唯一輸入: su(3) 色代數 + Q4 張量。零自由參數。
"""
import itertools
import numpy as np

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
def mclass(aa):
    from collections import Counter
    counts = sorted(Counter(aa).values(), reverse=True)
    if counts == [4]: return "4同"
    if counts == [3,1]: return "3+1"
    if counts == [2,2]: return "2+2"
    if counts == [2,1,1]: return "2+1+1"
    return "全異"
DALL = list(itertools.product([0,1], repeat=4))
def T_all_max(aas): return max(abs(T_delta(aas, d)) for d in DALL)

def is_propto(C, k):
    r = np.trace(T[k].conj().T @ C).real
    if abs(r) < 1e-10: return False
    return np.allclose(C, T[k]*r*2, atol=1e-10)

print("="*78)
print("  O244 scripts/09: 全異額外禁戒 16 sets — 機制挖掘")
print("="*78)

# closures 同 scripts/08
closures = []
for i in range(8):
    for j in range(i+1, 8):
        C = 1j*(T[i]@T[j] - T[j]@T[i])
        if abs(np.linalg.norm(C)) < 1e-10: continue
        ks = [k for k in range(8) if k != i and k != j and is_propto(C, k)]
        for k in ks:
            tr = frozenset((i,j,k))
            if tr not in closures: closures.append(tr)

# 16 sets 列表
extra_sets = []
for s in itertools.combinations(range(8), 4):
    sf = frozenset(s)
    if any(c <= sf for c in closures): continue
    aa = list(s)
    if T_all_max(aa) > 1e-9: continue   # 禁戒
    extra_sets.append(s)

print(f"\n─── [A] 額外禁戒 sets ({len(extra_sets)}): ───")
from collections import Counter
cnt = Counter()
for s in extra_sets:
    print(f"       {s}")
    cnt.update(s)
print(f"       元素出現次數: {dict(cnt)}")
check("A1 額外禁戒 sets 數 = 16", len(extra_sets) == 16, f"({len(extra_sets)})")

# ═══ B. 機制候選: 7(λ₈) 參與? 每 set 嘅 pair commutator 方向 ═══
print("\n─── [B] set 內 pair commutator 結構 ───")
pairs_finite = {}     # (i,j) -> k 方向
for i in range(8):
    for j in range(i+1, 8):
        C = 1j*(T[i]@T[j] - T[j]@T[i])
        ks = [k for k in range(8) if k != i and k != j and is_propto(C, k)]
        if ks: pairs_finite[(i,j)] = tuple(sorted(ks))
for s in extra_sets:
    inside = [(i,j, pairs_finite[(i,j)]) for (i,j) in itertools.combinations(s,2)
              if (i,j) in pairs_finite]
    print(f"       {s}: closure pairs {inside}")
# 7 嘅角色: 同 7 對易嘅 pair 有無構成 closure?  (0,1,7): [T₀,T₁]∝T₂ ∉ set
check("B1 所有額外 set 含 7 (λ₈)", all(7 in s for s in extra_sets),
      f"({sum(1 for s in extra_sets if 7 in s)}/16)")

# ═══ C. Tr 恆等: 對代表 set, Q4 各項 trace 消滅檢查 ═══
print("\n─── [C] 代表 set (0,1,3,7): mixed T_δ 嘅 trace 展開 ───")
# T_δ(0001): u = T₀+T₁+T₃, v = T₇ → ∂⁴ Q4(u(x),T₇x₄)
# прoст直接: Tr[(u−v)⁴] 係 x u 3次 v 1次 項 = Σ_perm Tr[T_a T_b T_c T₇]
# [u,v]² = (u v − v u)² 對 degree pattern (3,1) 無貢獻 (每邊最少 2 次) → 只睇 Tr[(u−v)⁴]
import itertools as it
perm_traces = []
for perm in it.permutations((0,1,3)):
    tr = np.trace(T[perm[0]]@T[perm[1]]@T[perm[2]]@T[7]).real
    perm_traces.append((perm, tr))
print(f"       Tr[T_aT_bT_cT₇] over 6 perms: {[(p, round(t,12)) for p,t in perm_traces]}")
all_zero = all(abs(t) < 1e-10 for _, t in perm_traces)
check("C1 (0,1,3,7): Tr[T_aT_bT_cT₇] = 0 ∀perm (3u+1v 主項消滅)", all_zero,
      f"(√ 機制: v-slot 色 7 同 u-slot 3 色嘅 4-trace 全零)")
# 反面對照: (0,1,3,4) (唔禁戒) 嘅 3u+1v trace
perm_traces2 = []
for perm in it.permutations((0,1,3)):
    tr = np.trace(T[perm[0]]@T[perm[1]]@T[perm[2]]@T[4]).real
    perm_traces2.append((perm, tr))
print(f"       對照 (0,1,3,4): {[(p, round(t,12)) for p,t in perm_traces2]}")
nz = sum(1 for _, t in perm_traces2 if abs(t) > 1e-10)
check("C2 對照 (0,1,3,4): 有非零 trace ⟹ 耦合", nz > 0,
      f"({nz}/6 非零)")

# ═══ D. 全異禁戒 3 分類總結 ═══
print("\n─── [D] 全異禁戒三類 vs 耦合 —— set 級 ───")
n_all = 0; n_closure = 0; n_extra = 0; n_couple = 0
for s in itertools.combinations(range(8), 4):
    aa = list(s); sf = frozenset(s)
    has_cl = any(c <= sf for c in closures)
    zero = T_all_max(aa) < 1e-9
    n_all += 1
    if zero and has_cl: n_closure += 1
    elif zero: n_extra += 1
    else: n_couple += 1
print(f"       70 4-set: closure禁戒 {n_closure} | 額外禁戒 {n_extra} | 耦合 {n_couple}")
check("D1 70 = 43 + 16 + 11 (closure + extra + couple)", 
      n_closure == 43 and n_extra == 16 and n_couple == 11,
      f"({n_closure}+{n_extra}+{n_couple}={n_closure+n_extra+n_couple})")
check("D2 set 級 ×24 = pattern 級 (1032+384=1416, 264)", 
      (n_closure+n_extra)*24 == 1416 and n_couple*24 == 264)

print(f"\n{'='*78}")
print(f"  RESULT: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print(f"{'='*78}")
import sys
sys.exit(0 if FAIL == 0 else 1)