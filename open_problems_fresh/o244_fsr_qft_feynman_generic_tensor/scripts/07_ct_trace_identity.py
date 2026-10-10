#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O244 — scripts/07: C_t ≡ 0 封閉證明攻堅 — T_δ 單項結構
=====================================================================================
背景 (docs/06 誠實缺口 #1): (0,1,2,3) 同 3+1 類 (a,a,a,b) 嘅差向量組和 C_t ≡ 0 —
機制已定位 (C_t 分組定理)，但「點解嗰啲 T_δ 組和會抵消」嘅 trace-identity 未寫。

關鍵結構洞察 (本 script 起點):
  T_δ := Tget(8δ₁+a₁, 8δ₂+a₂, 8δ₃+a₃, 8δ₄+a₄)  — 記號: δ=0 → u-slot, δ=1 → v-slot
  差向量 t = (δ₁−δ₄, δ₂−δ₄, δ₃−δ₄)。
  * t ≠ 0 嘅組: 恰好 1 個 δ pattern（δ₄=0 ⟹ δ=t∈{0,1}³; δ₄=1 ⟹ δ=t+1∈{0,1}³）⟹
    C_t = T_δ（單項）——「C_t ≡ 0 ∀t≠0」⟺ **所有混合 slot δ pattern 嘅 T_δ = 0**
  * t = 0: δ ∈ {(0,0,0,0), (1,1,1,1)} ⟹ C₀ = T(0,0,0,0) + T(1,1,1,1)

⟹ 要證明嘅封閉 claim:
  (T1) ∀ 混合 δ（非全 0 非全 1）: T_δ = 0
  (T2) T(0,0,0,0) = −T(1,1,1,1)
  (T3) 呢兩個恆等對邊啲色 pattern 成立 — (0,1,2,3) + 全 3+1 類 (224 個)；
       對照: 2+2 / 4同 耦合(應該有 T_δ ≠ 0), 2+1+1/全異 部分。

判據:
  [A] (0,1,2,3) + 6 個 3+1 代表: 16 個 T_δ 三分類 (全零/混合/純) EXACT 匹配預測
  [B] 3+1 類全 224 個: mixed T_δ 全零 (0/224) + T₀+T₁₁₁₁=0 (224/224)
  [C] 對照類: 4同 8/8 有 non-mixed T₀≠0; 2+2 168/168 mixed 至少一個非零
      ⟹ 禁戒層級 = T_δ 單項消滅 (u/v 槽混合項), 唔係相位巧合
  [D] T1/T2 喺 N 無關 (T_δ 係純色張量, 直接驗證唔經 V₄)
  [E] 若 (0,1,2,3) 係全異類唯一禁戒 — 統計: 全異 1680 個只得 1 個 C_t≡0?
      抽查 20 個 random 全異 pattern 嘅 T_δ 結構 (留記錄)
唯一輸入: su(3) 色代數 + Q4 張量 (同 scripts/01/05)。零自由參數。
"""
import itertools
import numpy as np
from scipy.linalg import expm
from collections import Counter

PASS = 0; FAIL = 0; TOTAL = 0
def check(name, cond, detail=""):
    global PASS, FAIL, TOTAL; TOTAL += 1
    if cond: PASS += 1; mark = "OK "
    else:    FAIL += 1; mark = "XX "
    print(f"  [{mark}] {name} {detail}")

# ── su(3) 色 (同 scripts/01/05) ──
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
    """T_δ := Tget(8δ_k+a_k)"""
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

def mixed_all_zero(aas):
    return all(abs(T_delta(aas, d)) < 1e-9 for d in MIXED)
def pure_pair(aas):
    t0 = T_delta(aas, (0,0,0,0)); t1 = T_delta(aas, (1,1,1,1))
    return t0, t1

print("="*78)
print("  O244 scripts/07: C_t ≡ 0 封閉證明 — T_δ 單項結構 (u/v 槽混合消滅)")
print("  唯一輸入: su(3) 色代數 + Q4 張量。零自由參數。")
print("="*78)

# ═══ A. (0,1,2,3) + 6 個 3+1 代表: 16 T_δ 結構 ═══
print("\n─── [A] T_δ 單項三分類 (16 δ pattern) ───")
pats = [(0,1,2,3), (0,0,0,1), (1,1,1,2), (2,2,2,5), (0,0,0,7), (4,4,4,0), (3,3,3,1)]
okA = True
for aa in pats:
    mixed_nz = [d for d in MIXED if abs(T_delta(aa, d)) > 1e-9]
    t0, t1 = pure_pair(aa)
    pair_ok = abs(t0 + t1) < 1e-9
    cl = mclass(aa)
    if mixed_nz or not pair_ok:
        okA = False
        print(f"       {aa} ({cl}): mixed 非零 {[str(d) for d in mixed_nz]} | T0+T11  = {abs(t0+t1):.2e}  ← FAIL")
    else:
        print(f"       {aa} ({cl}): mixed 全零 ✓ | T0+T11 = {abs(t0+t1):.2e} ✓")
check("A1 (0,1,2,3)+6×3+1: mixed T_δ≡0 且 T₀+T₁₁₁₁=0 (T1+T2)", okA,
      "(14 mixed δ 單項零 + 純項反號配對)")

# ═══ B. 3+1 類全 224 個 ═══
print("\n─── [B] 3+1 類全掃 224 patterns ───")
b1 = b2 = 0
for a in range(8):
    for b_ in range(8):
        if b_ == a: continue
        for pos in range(4):
            aa = [a]*4; aa[pos] = b_
            if mixed_all_zero(aa): b1 += 1
            t0, t1 = pure_pair(aa)
            if abs(t0+t1) < 1e-9: b2 += 1
check("B1 3+1 全 224: mixed T_δ 全零", b1 == 224, f"({b1}/224)")
check("B2 3+1 全 224: T₀+T₁₁₁₁ = 0", b2 == 224, f"({b2}/224)")

# ═══ C. 對照類: 4同 / 2+2 / 2+1+1 / 全異 嘅 mixed 結構 ═══
print("\n─── [C] 對照類 T_δ 單項結構 ───")
def scan_class(cls, limit=None):
    n = 0; mx = 0; pz = 0; pnz = 0; details = []
    for aa in itertools.product(range(8), repeat=4):
        if mclass(aa) != cls: continue
        n += 1
        md = sum(1 for d in MIXED if abs(T_delta(aa, d)) > 1e-9)
        if md == 0: pz += 1
        else: pnz += 1; mx = max(mx, md)
        if limit and n >= limit: break
    return n, pz, pnz, mx
for cl in ["4同", "2+2", "2+1+1", "全異"]:
    n, pz, pnz, mx = scan_class(cl)
    print(f"       {cl}: 總數 {n} | 全 mixed 零 {pz} | 有 mixed 非零 {pnz} | max mixed 非零 {mx}")
c41 = scan_class("4同")[1]
c22 = scan_class("2+2")[1]
c211 = scan_class("2+1+1")[1]
call = scan_class("全異")[1]
check("C1 4同: 8/8 有 mixed 非零 (耦合源頭)", c41 == 0, f"(全混合零 = {c41}/8)")
check("C2 2+2: 168/168 有 mixed 非零", c22 == 0, f"(全混合零 = {c22}/168)")

# ═══ D. N 無關: T_δ 係純色張量 (直接由 V4 驗證一例) ═══
print("\n─── [D] V₄ 層驗證: mixed 消滅係色張量恆等 (N 無關) ───")
okD = True
for NN in [22, 44, 88]:
    for ns in ([1,1,NN-1,NN-1], [NN//2]*4):
        for aa in [(0,1,2,3), (0,0,0,1)]:
            if abs(V4(NN, list(ns), list(aa))) > 1e-9: okD = False
check("D1 (0,1,2,3)/(0,0,0,1) 喺 N∈{22,44,88} 守恆點全零 (C_t 定理 N 無關)",
      okD, "(T_δ 無 N ⟹ 結構恆等)")

# ═══ E. 全異類: (0,1,2,3) 係咪唯一禁戒? ═══
print("\n─── [E] 全異類 C_t≡0 pattern 掃描 (全異 1680 個) ───")
n_forbid = 0; examples = []
for aa in itertools.product(range(8), repeat=4):
    if mclass(aa) != "全異": continue
    if mixed_all_zero(aa):
        t0, t1 = pure_pair(aa)
        if abs(t0+t1) < 1e-9:
            n_forbid += 1
            if len(examples) < 5: examples.append(aa)
print(f"       全異類全 C_t≡0 (T1∧T2) 嘅 pattern: {n_forbid}/1680")
check("E1 全異類禁戒 count 記錄 (預期 = 1: (0,1,2,3) 族?)", n_forbid >= 1,
      f"({n_forbid} 個; 例子 {examples})")

print(f"\n{'='*78}")
print(f"  RESULT: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print(f"{'='*78}")
import sys
sys.exit(0 if FAIL == 0 else 1)