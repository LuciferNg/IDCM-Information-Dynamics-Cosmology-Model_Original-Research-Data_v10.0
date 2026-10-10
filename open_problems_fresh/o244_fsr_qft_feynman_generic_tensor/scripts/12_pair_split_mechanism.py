#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O244 — scripts/12: 相位削減機制確認 — 消失 ⟺ 色成對 (root-pair/closure-pair)
=====================================================================================
scripts/11 發現: (1,1,42,44) 全異 56 消失 = 7 sets × 8 排列; 8 = pair 內部 swap ×2
× pair 內部 swap ×2 × pair 位置 swap ×2。消失集例 (0,1,3,4): 消失 iff 色分成兩對
(0,1)|(3,4)。本 script 確立:
  [A] 每 7 個消失 set 嘅「消失排列集合」= 全部「雙 pair 排列」?
      定義: set 分成兩對 P1|P2（按咩規則?）→ 排列 ∈ P1×P1×P2×P2 任意序
  [B] pair 規則: 邊啲 2-色子集係「pair」? 用 commutator: {i,j} 若 ∃k: [T_i,T_j]∝T_k
      （唔需要 k ∈ set）→ closure pair list
  [C] 7 個消失 set 每個 split 成兩 pair 嘅方式 (唯一?): 驗證
  [D] 全異 264 = 4 個全耦合 set (24) + 7 個 pair-set (16); pair-set 消失數 = 8 確立,
      且 4 個全耦合 set 冇 pair split (冇一對 closure pair 完全唔重疊?)
  [E] 完整代數: 消失 ⟺ 存在 pair split ⟹ Σ_δ φ(δ)T_δ = 0 (實證, 全枚舉)
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
def T_mixed_max(aas): return max([abs(T_delta(aas, d)) for d in MIXED] + [0.0])
def is_propto(C, k):
    r = np.trace(T[k].conj().T @ C).real
    if abs(r) < 1e-10: return False
    return np.allclose(C, T[k]*r*2, atol=1e-10)
closure_pairs = []
for i in range(8):
    for j in range(i+1, 8):
        C = 1j*(T[i]@T[j] - T[j]@T[i])
        if abs(np.linalg.norm(C)) < 1e-10: continue
        ks = [k for k in range(8) if k != i and k != j and is_propto(C, k)]
        if ks: closure_pairs.append(frozenset((i,j)))
closure_pairs = list(set(closure_pairs))
print(f"closure pairs ({len(closure_pairs)}): {[tuple(sorted(p)) for p in closure_pairs]}")

print("="*78)
print("  O244 scripts/12: 消失 ⟺ 色對 split — pair 機制確認")
print("="*78)

# 11 耦合 sets
coupled_sets = []
for s in itertools.combinations(range(8), 4):
    sf = frozenset(s)
    aa = list(s)
    if T_mixed_max(aa) > 1e-9: coupled_sets.append(s)

NS = [1,1,42,44]
set_split = {}
okA = True; detailsA = []
all_split = {}
for s in coupled_sets:
    vanish = [perm for perm in itertools.permutations(s)
              if abs(V4(44, NS, list(perm))) < 1e-9]
    # pair split: 將 s 分成兩對, 每對都要係 closure pair
    splits = []
    elems = list(s)
    for (i1,i2),(j1,j2) in itertools.combinations(itertools.combinations(range(4),2),2):
        if set((i1,i2)) & set((j1,j2)): continue
        p1 = frozenset((elems[i1], elems[i2])); p2 = frozenset((elems[j1], elems[j2]))
        if p1 in closure_pairs and p2 in closure_pairs:
            splits.append((tuple(sorted(p1)), tuple(sorted(p2))))
    set_split[s] = (vanish, splits)
    # 預測: 有 split ⟹ 消失 = 8 (全部雙 pair 排列); 冇 split ⟹ 0
    if splits:
        pred = []
        for p1, p2 in splits:
            for o1 in itertools.permutations(p1):
                for o2 in itertools.permutations(p2):
                    pred.append(tuple(o1 + o2))
                    pred.append(tuple(o2 + o1))
        pred = set(pred)
        vs = set(vanish)
        match = (pred == vs) if len(pred) == 8 else False
        if match: okA = okA and True
        else:
            okA = False
            detailsA.append((s, len(pred), len(vs), pred ^ vs))
    else:
        if len(vanish) != 0:
            okA = False; detailsA.append((s, 0, len(vanish), "unexpected vanish"))
    print(f"       {s}: 消失 {len(vanish)} | split {[f'{p1}|{p2}' for p1,p2 in splits]}")

check("A1 消失 set = 有 closure-pair split 嘅 set (7), 消失集 = 雙 pair 排列 (8)",
      okA and len([s for s in coupled_sets if set_split[s][1]]) == 7,
      f"(details {detailsA[:2]})")

# ═══ B. 4 個全耦合 set 冇 split ═══
print("\n─── [B] 全耦合 set: 應該冇 pair split ───")
no_split = [s for s in coupled_sets if not set_split[s][1]]
print(f"       全耦合 sets ({len(no_split)}): {no_split}")
check("B1 4 個全耦合 set 冇 closure-pair split", len(no_split) == 4,
      f"({len(no_split)})")

# ═══ C. split 唯一性 + 消失數 8 全枚舉驗證 ═══
print("\n─── [C] 7 個 split set 消失數 + pair 唯一性 ───")
okC = True
for s in coupled_sets:
    vanish, splits = set_split[s]
    if splits:
        # 消失必須恰好 8, 且 split 唯一 (唔計 pair 次序)
        if len(vanish) != 8: okC = False
        if len(splits) != 1: okC = False
print(f"       (檢查 7 個 split set: 消失=8, split 唯一)")
check("C1 每 split set: 消失恰 8 且 split 唯一", okC)

# ═══ D. 相位結構: 為何 pair 排列消失? — δ 對稱 ═══
print("\n─── [D] 機制: 動量 (1,1,42,44) 有 n₁=n₂, …; pair split ⟹ T_δ 內在對稱 ───")
# 對 (0,1,3,4): 消失排列 (0,1,3,4)/(0,1,4,3)/(1,0,3,4)/(1,0,4,3)/(3,4,0,1)/(3,4,1,0)/(4,3,0,1)/(4,3,1,0)
# 對照 V₄(ns) 定義: site 因子 Σ_m e^{2πi m Σn/88} — Σn=88⟹e^{2πi m}=1⟹site=44
# inner = Σ_δ φ(δ) T_δ; 對 pair 排列, δ 嘅 8 mixed 項相位: φ(1,0,0,0) = e^{2πi/88}, …
# 消失數 = 8 ⟹ inner 嘅兩 pair 對稱令 φ-加權 T_δ 對消
# 直接驗: 任選一個 split set, 消失排列 (∀perm) 嘅 inner 複數期望 = 0 EXACT
s_ex = (0,1,3,4)
for perm in [(0,1,3,4), (3,4,0,1), (0,3,1,4)]:
    v = abs(V4(44, NS, list(perm)))
    print(f"       V4({perm}) = {v:.3e} ({'消失' if v<1e-9 else '耦合'})")
check("D1 pair 排列 V₄ = 0 而 mixed 排列 ≠ 0 (機制: pair 內 T_δ 對稱對消)", 
      abs(V4(44, NS, [0,1,3,4])) < 1e-9 and abs(V4(44, NS, [0,3,1,4])) > 1e-9,
      "(費曼對稱性: 同色值喺同動量值 slot 對稱 → 相位和零)")

# ═══ E. 2+1+1 同期: 48 個 mixed-nonzero 喺 (1,1,42,44) 有冇削減? ═══
print("\n─── [E] 2+1+1 48 個 mixed-nonzero: (1,1,42,44) 相位削減檢查 ───")
kept = 0; dropped = 0
for aa in itertools.product(range(8), repeat=4):
    if mclass(aa) != "2+1+1": continue
    aa = list(aa)
    if T_mixed_max(aa) < 1e-9: continue
    if abs(V4(44, NS, aa)) > 1e-9: kept += 1
    else: dropped += 1
print(f"       2+1+1: 耦合 {kept}, 相位消失 {dropped} (上限 48)")
check("E1 2+1+1 喺 (1,1,42,44) 冇削減 (48 全留; 色重複打破 pair 機制)",
      kept == 48 and dropped == 0, f"({kept}/{dropped})")

print(f"\n{'='*78}")
print(f"  RESULT: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print(f"{'='*78}")
import sys
sys.exit(0 if FAIL == 0 else 1)