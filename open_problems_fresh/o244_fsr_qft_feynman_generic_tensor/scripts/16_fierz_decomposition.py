#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O244 — scripts/16: E2 Fierz 層推導 — 單項 trace 虛部 + pol 排列消滅
=====================================================================================
scripts/15 A4''' 用 .real 攞 trace → 假 PASS 風險: Tr[T₀T₁T₂T₇] = i/(8√3) 純虛,
real=0 但 |·|≠0。修正 + 完整推導:
  [A] 重掃 43 sets × 24 perms: 單項 Tr[T_aT_bT_cT_d] 嘅 |·|、Re、Im 分佈
      → 確認 A4''' 假 PASS; 真正機制 = 虛部喺 pol 排列組合消滅
  [B] Fierz 分解: T_iT_j = (1/4)δ_ij I + ½(d_ijk + i f_ijk)T_k
      su(2)-closure triple 內部: f_{ijk} 只指 k; d 結構?
      → 對 triple 色乘積 T_aT_bT_c: 化簡到 span{I, Cartan} + 虛/實結構
  [C] 對代表 (0,1,2,7): 24 perms 嘅 trace 值表 (re/im) → 睇消滅組合
  [D] T_δ = 24·pol 全枚舉再確認 (EXACT 0, |·| 唔係 .real) — 定理級 claim 維持
  [E] ★ 新 E2 陳述: pol 嘅排列組合 (f 反對稱/d 對稱) ⟹ Σ_σ (sgn·) 虛部消滅
唯一輸入: su(3) + Q4 + FSR。零自由參數。
"""
import itertools
import numpy as np
from collections import Counter, defaultdict

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
def is_propto(C, k):
    r = np.trace(T[k].conj().T @ C).real
    if abs(r) < 1e-10: return False
    return np.allclose(C, T[k]*r*2, atol=1e-10)

print("="*78)
print("  O244 scripts/16: E2 Fierz 層 — 單項 trace 虛部 / pol 排列消滅")
print("="*78)

closures = []
for i in range(8):
    for j in range(i+1, 8):
        C = 1j*(T[i]@T[j] - T[j]@T[i])
        if abs(np.linalg.norm(C)) < 1e-10: continue
        ks = [k for k in range(8) if k != i and k != j and is_propto(C, k)]
        for k in ks:
            tr = frozenset((i,j,k))
            if tr not in closures: closures.append(tr)

# ═══ A. 重掃: 單項 trace 嘅 |·| / Re / Im ═══
print("\n─── [A] 43 sets × 24 perms: 單項 trace 全結構 ───")
cnt_abs = 0; cnt_imag = 0; cnt_real0 = 0; total = 0; first_imag = []
for s in itertools.combinations(range(8), 4):
    sf = frozenset(s)
    if not any(c <= sf for c in closures): continue
    for perm in itertools.permutations(s):
        v = np.trace(T[perm[0]]@T[perm[1]]@T[perm[2]]@T[perm[3]])
        total += 1
        if abs(v) > 1e-10: cnt_abs += 1
        if abs(v.imag) > 1e-10: cnt_imag += 1
        if abs(v.real) < 1e-10 and abs(v) > 1e-10: cnt_real0 += 1
        if abs(v.imag) > 1e-12 and len(first_imag) < 5:
            first_imag.append((s, perm, v))
print(f"       總 perms {total}: |Tr|>0 嘅 {cnt_abs}, 有虛部 {cnt_imag}, "
      f"real=0 但非零 {cnt_real0}")
print(f"       例 (虛): {first_imag}")
check("A1 ★ A4''' 假 PASS 確認: 存在單項 trace 非零 (純虛)", cnt_abs > 0 and cnt_real0 > 0,
      f"({cnt_abs} 非零, 其中 {cnt_real0} 個 real=0)")

# ═══ B. Fierz: su(2) 內雙色乘積結構 ═══
print("\n─── [B] Fierz: su(2) triple 內 T_iT_j (i≠j) / T_i² ───")
# T_iT_j = ¼δ_ij·I + ½(d_ijk+i f_ijk)T_k — su(2) 內: f 只指第3色, d?
f3 = {}; d3 = {}
for tr in closures:
    tri = sorted(tr)
    for i in tri:
        for j in tri:
            if i == j: continue
            P = T[i]@T[j]
            # f: [T_i,T_j] = i f T_k; d: {T_i,T_j} = ...
            comm = P - P.conj().T  # = i[T_i,T_j] (Hermitian) → 2i·f_{ijk}T_k
            ks = [k for k in range(8) if k != i and k != j and is_propto(comm.T - comm, k)]
            # 直接: [T_i,T_j] = iΣ f T_k
            C = T[i]@T[j] - T[j]@T[i]
            fval = 0.0; fdir = None
            for k in range(8):
                if k in tri:
                    # Tr[[Ti,Tj] Tk] = i f_{ijk}/2?  [Ti,Tj] = i f T_k
                    v = np.trace((C) @ T[k]).imag
                    if abs(v) > 1e-10: fdir = k; fval = v
            if fdir is not None:
                f3[(i,j)] = (fdir, fval)
print("       f-structure (內): ", {f"{k}->{v[0]}:{v[1]:.3f}" for k, v in list(f3.items())[:6]})
# T_i² 結構: 任何色平方 = 對角 = span{I, T₂, T₇} (Cartan 全體, 唔只 T₇)
bad_sq = []
for i in range(8):
    sq = T[i]@T[i]
    basis = np.array([np.eye(3).flatten(), T[2].flatten(), T[7].flatten()]).T
    coef, *_ = np.linalg.lstsq(basis, sq.flatten(), rcond=None)
    res = sq.flatten() - basis@coef
    if np.linalg.norm(res) > 1e-10:
        bad_sq.append((i, np.linalg.norm(res)))
print(f"       T_i² ∉ span{{I,T₂,T₇}} 嘅色: {bad_sq}")
okB = len(bad_sq) == 0
check("B1 ∀色: T_i² ∈ span{I, T₂, T₇} (Cartan 全體)", okB, f"({len(bad_sq)} bad {bad_sq[:4]})")

# ═══ C. 代表 (0,1,2,7): 24 perms trace 表 ═══
print("\n─── [C] (0,1,2,7) 24 perms: re/im 結構 ───")
vals = []
for perm in itertools.permutations([0,1,2,7]):
    v = np.trace(T[perm[0]]@T[perm[1]]@T[perm[2]]@T[perm[3]])
    vals.append((perm, v))
nz = [(p, v) for p, v in vals if abs(v) > 1e-10]
print(f"       非零 {len(nz)}/24: {[(p, f'{v:.4f}') for p, v in nz[:8]]}")
all_imag = all(abs(v.real) < 1e-10 for _, v in nz)
check("C1 (0,1,2,7) 非零單項 trace 全部純虛 (real=0)", all_imag,
      f"({len(nz)} 非零, 全虛: {all_imag})")

# ═══ D. T_δ = 24·pol EXACT 0 (|·| 檢查, 唔係 .real) ═══
print("\n─── [D] T_δ 全枚舉 (|·|): 禁戒 set T_δ ≡ 0 維持 ───")
worstD = 0.0; totalD = 0
for s in itertools.combinations(range(8), 4):
    aa = list(s)
    # 計算 T_delta 需要 Tget — 重用 (Q4 real → T_δ real)
    has_nz_mixed = False
    import itertools as it
    for d in it.product([0,1], repeat=4):
        if d in ((0,0,0,0),(1,1,1,1)): continue
        key = tuple(sorted(8*d[k]+aa[k] for k in range(4)))
        if key not in _tensor:
            _tensor[key] = 24*pol(*[E16[x] for x in key])
        v = abs(_tensor[key])
        totalD += 1
        if v > 1e-9: has_nz_mixed = True
    if has_nz_mixed: continue   # 耦合 set
    # 禁戒: 16 δ 全零
    for d in itertools.product([0,1], repeat=4):
        key = tuple(sorted(8*d[k]+aa[k] for k in range(4)))
        if key not in _tensor:
            _tensor[key] = 24*pol(*[E16[x] for x in key])
        worstD = max(worstD, abs(_tensor[key]))
print(f"       禁戒 set 全 T_δ 值 worst |·| = {worstD:.2e} (遍歷 {totalD} mixed)")
check("D1 ★ T_δ 消滅係真 (|·| 全枚舉): worst ~浮點噪聲 (1e-15 級)",
      worstD < 1e-9, f"(worst {worstD:.2e})")

# ═══ E. ★ 新 E2 陳述: polarisation — pure 必零; 耦合靠 mixed δ ═══
print("\n─── [E] 新機制: pure T_δ 全異類必零; mixed δ 先有耦合 ───")
# Tget(0,1,3,4) = 純 u-slot (δ=0000) — 全異類 pure 必零 (scripts/08 A2: 3920/4096)
key = tuple(sorted((0,1,2,7)))
val = _tensor.get(key, 24*pol(*[E16[x] for x in key]))
print(f"       Tget(0,1,2,7)[pure] = {val:.3e} (禁戒: 零)")
key2 = tuple(sorted((0,1,3,4)))
val2 = _tensor.get(key2, 24*pol(*[E16[x] for x in key2]))
print(f"       Tget(0,1,3,4)[pure] = {val2:.3e} (耦合 set 但 pure 都零 — 全異類性質)")
# 耦合嘅真正來源 = mixed δ: Tget(8+0, 1, 3, 4) = δ=(1,0,0,0)
keym = tuple(sorted((8+0, 1, 3, 4)))
valm = _tensor.get(keym, 24*pol(*[E16[x] for x in keym]))
# 正確: mixed δ 用 max (唔係單一 δ=1000)
mm = 0.0
for d in itertools.product([0,1], repeat=4):
    if d in ((0,0,0,0),(1,1,1,1)): continue
    kk = tuple(sorted(8*d[k]+[0,1,3,4][k] for k in range(4)))
    if kk not in _tensor: _tensor[kk] = 24*pol(*[E16[x] for x in kk])
    mm = max(mm, abs(_tensor[kk]))
print(f"       Tget(8,1,3,4)[δ=1000] = {valm:.3e} (單一 mixed 都可能零)")
print(f"       Tget mixed max (0,1,3,4) = {mm:.3e} (耦合: 有非零 mixed)")
check("E1 mixed δ 先係耦合來源 (pure 全異必零; mixed max 非零)",
      abs(val) < 1e-9 and abs(val2) < 1e-9 and mm > 1e-9,
      f"(禁戒 pure {val:.2e}, 耦合pure {val2:.2e}, 耦合mixed max {mm:.3e})")

print(f"\n{'='*78}")
print(f"  RESULT: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print(f"{'='*78}")
import sys
sys.exit(0 if FAIL == 0 else 1)