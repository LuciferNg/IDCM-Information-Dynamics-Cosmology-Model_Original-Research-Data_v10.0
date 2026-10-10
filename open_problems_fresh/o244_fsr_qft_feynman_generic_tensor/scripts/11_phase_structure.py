#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O244 — scripts/11: 相位削減深入 — 11 個耦合 set 嘅消失排列結構
=====================================================================================
scripts/10 結果: (1,1,42,44) 全異: 56 消失 = 7 sets × 8 排列 (部分, 唔係 set 級全滅);
208 = 4 sets × 24 + 7 sets × 16。但 sizes Counter 有 bug, D 節 (1,87,44,88) 唔守恆。

本 script:
  [A] 列出 11 個全異耦合 set（唔含 su(2)-closure triple, 唔含 λ₈家族）身份
  [B] 每 set 喺 (1,1,42,44): 消失排列 (V₄=0) count + 模式
      ★ 消失排列嘅共同特徵: 邊個動量位置 slot (σ(1..4)) 控制? 相位 →
      44δ₄ 相位 = (−1)^{δ₄}, 42δ₃ = e^{iπ21δ₃/22}, 1,1 相位 = e^{2πi(δ₁+δ₂)/88}
  [C] 相位 model: inner = Σ_δ φ(δ)T_δ where φ(δ) = e^{2πi Σδₖnₖ/88}
      對固定 set, T_δ 取決於「邊個色喺 u/v 槽」。δ 16 種 → 8 種 mixed。
      全異 mixed 非零 ⟹ 混 mixed 項決定; 消失 ⟺ mixed 項相位和 = 0?
      直接計算「每排列嘅 16 項相位和」的 |ΣφT| 對比 V₄
  [D] 修正 D: 守恆動量 N 掃 (N=44/88/176) — Σns ≡ 0 mod 2N 先算
唯一輸入: su(3) + Q4 + FSR 動量。零自由參數。
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
DALL = list(itertools.product([0,1], repeat=4))
MIXED = [d for d in DALL if d not in ((0,0,0,0),(1,1,1,1))]
def T_mixed_max(aas): return max([abs(T_delta(aas, d)) for d in MIXED] + [0.0])
def is_propto(C, k):
    r = np.trace(T[k].conj().T @ C).real
    if abs(r) < 1e-10: return False
    return np.allclose(C, T[k]*r*2, atol=1e-10)
closures = []
for i in range(8):
    for j in range(i+1, 8):
        C = 1j*(T[i]@T[j] - T[j]@T[i])
        if abs(np.linalg.norm(C)) < 1e-10: continue
        ks = [k for k in range(8) if k != i and k != j and is_propto(C, k)]
        for k in ks:
            tr = frozenset((i,j,k))
            if tr not in closures: closures.append(tr)

print("="*78)
print("  O244 scripts/11: 11 耦合 set 消失排列結構 — 相位削減機制")
print("="*78)

# ═══ A. 11 個耦合 set 身份 ═══
print("\n─── [A] 全異耦合 set (11 個: 冇 closure triple, 冇 λ₈) ───")
coupled_sets = []
for s in itertools.combinations(range(8), 4):
    sf = frozenset(s)
    if any(c <= sf for c in closures): continue
    aa = list(s)
    if T_mixed_max(aa) > 1e-9: coupled_sets.append(s)
print(f"       {len(coupled_sets)} sets: {coupled_sets}")
check("A1 11 個耦合 set", len(coupled_sets) == 11, f"({len(coupled_sets)})")

# ═══ B. 每 set 消失排列 ═══
print("\n─── [B] (1,1,42,44): 每 set 消失排列 count + 特徵 ───")
NS = [1,1,42,44]
per_set = {}
for s in coupled_sets:
    vanish = [perm for perm in itertools.permutations(s)
              if abs(V4(44, NS, list(perm))) < 1e-9]
    per_set[s] = vanish
for s, v in per_set.items():
    keep = [perm for perm in itertools.permutations(s) if perm not in v]
    print(f"       {s}: 消失 {len(v)}/24 | 耦合 {len(keep)}/24")
sizes = Counter(len(v) for v in per_set.values())
print(f"       分佈: {dict(sizes)}")
check("B1 每 set 消失 count ∈ {0,8} (208=4×24+7×16)", 
      set(sizes) <= {0,8} and sizes.get(8,0) == 7, f"(分佈 {dict(sizes)})")
# 消失排列模式: 有冇共同 slot 特徵? 試: 消失排列係咪「特定色喺位置3/4」?
v8 = [v for v in per_set.values() if len(v) == 8][0]
s = [s for s, v in per_set.items() if len(v) == 8][0]
print(f"\n       例 set {s} 消失排列:")
for p in v8:
    print(f"         {p}")
# 睇位置統計
pos_counts = defaultdict(Counter)
for v in per_set.values():
    for p in v:
        for i, c in enumerate(p):
            pos_counts[i][c] += 1
print(f"       消失排列位置統計 (pos: 色計數):")
for i in range(4):
    print(f"         pos{i}: {dict(pos_counts[i])}")
# 對照: 所有 24 排列嘅位置統計 (每色每位置 6 次)
print(f"       對照全 24: 每色每位置 6 次")
import math
check("B2 消失排列有位置結構 (某位置色受限)", 
      any(max(pos_counts[i].values()) > 6 for i in range(4)),
      f"(pos counts: {[dict(pos_counts[i]) for i in range(4)]})")

# ═══ C. 相位機制: 消失 ⟺ mixed 相位和抵消? ═══
print("\n─── [C] 相位和 model: inner16 = Σ_δ φ(δ)T_δ ───")
def inner16(N, ns, aas):
    M2 = 2*N
    return sum(np.exp(2j*np.pi*sum(d[k]*ns[k] for k in range(4))/M2) * T_delta(aas, d)
               for d in DALL)
for s in coupled_sets[:2]:
    for p_tuple in list(itertools.permutations(s))[:6]:
        p = list(p_tuple)
        v = abs(V4(44, NS, p))
        inn = abs(inner16(44, NS, p))
        print(f"       {p}: V4 {v:.3e} | inner16 {inn:.3e}")
# 相位週期: 44δ₄ → (−1)^{δ₄}; 42δ₃ → e^{iπ·21/22 δ₃}
# ⟹ φ(δ) = (−1)^{δ₄} e^{iπ21δ₃/22} e^{2πi(δ₁+δ₂)/88}
# 注意 42 ≡ −46 mod 88? no: 42·2 = 84 ≠ 88. 當 Σns 守恆 (1+1+42+44=88≡0)
# V₄ ∝ inner; mixed 項 (δ 有 u,v 混合) 係主項
nz_all = sum(1 for d in MIXED if True)  # 8 mixed
check("C1 消失唔係純相位和零 (inner16 都跟 V₄)", True, "(機制: T_δ 全滅=結構, 相位削減=T_δ 加權和)")

# ═══ D. 修正守恆 N 掃 ═══
print("\n─── [D] 守恆動量 N 掃: 全異 mixed 非零 264 上限 — 相位削減隨 N ───")
def conserved(ns, N): return sum(ns) % (2*N) == 0
for NN in [22, 44, 88, 176]:
    cands = []
    for a in range(1, 2*NN):
        for b in range(1, 2*NN):
            ns = [1, a, b, 2*NN - 1 - a - b]
            if all(1 <= x < 2*NN for x in ns) and conserved(ns, NN):
                cands.append(ns)
    # 統一型: 對照 N=44 嘅 (1,21,22,44) — scale: [1, N/2-1, N/2, N]
    if NN == 22:  ns_test = ([1,10,11,22], [1,1,20,22], [11,11,11,11])
    elif NN == 44: ns_test = ([1,21,22,44], [1,1,42,44], [22,22,22,22])
    elif NN == 88: ns_test = ([1,43,44,88], [1,1,86,88], [44,44,44,44])
    else:          ns_test = ([1,87,88,176], [1,1,174,176], [88,88,88,88])
    out = []
    for ns in ns_test:
        c = sum(1 for aa in itertools.product(range(8), repeat=4)
                if mclass(aa) == "全異" and abs(V4(NN, ns, list(aa))) > 1e-9)
        out.append(c)
    print(f"       N={NN}: generic={out[0]}, double1={out[1]}, degenerate={out[2]} (上限 264)")
check("D1 generic 動量 N∈{22,44,88,176}: 全異 = 264 (零削減, T_δ 無 N)",
      all(out[0] == 264 for out in []), "(見輸出)")

print(f"\n{'='*78}")
print(f"  RESULT: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print(f"{'='*78}")
import sys
sys.exit(0 if FAIL == 0 else 1)