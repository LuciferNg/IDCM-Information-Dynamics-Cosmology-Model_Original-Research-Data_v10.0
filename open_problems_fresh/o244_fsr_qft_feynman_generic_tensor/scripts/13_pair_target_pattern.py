#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O244 — scripts/13: 相位削減 — 消失排列嘅 pair-target 模式分類
=====================================================================================
scripts/12 假設「closure-pair split ⟺ 消失」錯（23 pairs 太密; (0,3,5,7) 有 split 都 0 消失）。
本 script 用 commutator target 深挖:
  [A] 每 closure pair (i,j) 嘅 target k: [T_i,T_j] ∝ T_k (k 係 diag(=2,7) 定 off-diag)
  [B] 對每個 coupled set: 全部 24 perm 分消失/耦合; 對消失 perm, 記錄
      「相鄰位置 pair」嘅 target 組合 — (pos0,pos1)|(pos2,pos3) 同 (pos0,pos3)|(pos1,pos2)?
  [C] 歸納消失 pattern 嘅共同 target 結構 (dict: pattern → count)
  [D] 對照 (1,21,22,44): 所有 24 perm 耦合 (零削減) ⟹ target 結構對照
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
MIXED = [d for d in itertools.product([0,1], repeat=4)
         if d not in ((0,0,0,0),(1,1,1,1))]
def T_mixed_max(aas): return max([abs(T_delta(aas, d)) for d in MIXED] + [0.0])
def is_propto(C, k):
    r = np.trace(T[k].conj().T @ C).real
    if abs(r) < 1e-10: return False
    return np.allclose(C, T[k]*r*2, atol=1e-10)

print("="*78)
print("  O244 scripts/13: 消失排列 pair-target 模式 — 相位削減機制")
print("="*78)

# ═══ A. closure pair + target ═══
print("\n─── [A] closure pair [T_i,T_j]∝T_k: target 分類 (diag={2,7}) ───")
pair_target = {}
for i in range(8):
    for j in range(i+1, 8):
        C = 1j*(T[i]@T[j] - T[j]@T[i])
        if abs(np.linalg.norm(C)) < 1e-10: continue
        ks = [k for k in range(8) if k != i and k != j and is_propto(C, k)]
        if ks:
            pair_target[(i,j)] = ks[0]
for (i,j), k in sorted(pair_target.items()):
    tag = "DIAG" if k in (2,7) else "off"
    print(f"       ({i},{j}) → {k} [{tag}]")
diag_pairs = {p for p,k in pair_target.items() if k in (2,7)}
print(f"       diag-target pairs: {sorted(diag_pairs)}")
check("A1 diag-target pairs = 3 個 root pair {(0,1),(3,4),(5,6)}",
      diag_pairs == {(0,1),(3,4),(5,6)}, f"({sorted(diag_pairs)})")

# ═══ B. 消失 perm 嘅「pair 拆分模式」 ═══
print("\n─── [B] (1,1,42,44): 消失 perm 嘅 pair 結構 ───")
coupled_sets = []
for s in itertools.combinations(range(8), 4):
    aa = list(s)
    if T_mixed_max(aa) > 1e-9: coupled_sets.append(s)
NS = [1,1,42,44]
patterns = Counter()
for s in coupled_sets:
    vanish = [perm for perm in itertools.permutations(s)
              if abs(V4(44, NS, list(perm))) < 1e-9]
    for perm in vanish:
        # 三種 pair 拆分: 12|34, 13|24, 14|23
        ps = []
        for (i1,i2,i3,i4) in [(0,1,2,3),(0,2,1,3),(0,3,1,2)]:
            p1 = (perm[i1], perm[i2]); p2 = (perm[i3], perm[i4])
            p1s = tuple(sorted(p1)); p2s = tuple(sorted(p2))
            tag1 = 'D' if p1s in diag_pairs else 'o'
            tag2 = 'D' if p2s in diag_pairs else 'o'
            tgt1 = pair_target.get(p1s, None)
            tgt2 = pair_target.get(p2s, None)
            ps.append(f"{tag1}({tgt1}){tag2}({tgt2})")
        patterns[" ".join(ps)] += 1
print("       消失 perm 嘅 pair 拆分模式 (佔幾多個):")
for pat, cnt in patterns.most_common():
    print(f"         {pat}: {cnt}")
check("B1 消失模式集中 (≤2 種)", len(patterns) <= 2, f"({len(patterns)} 種: {dict(patterns)})")

# ═══ C. 對照: 耦合 perm 嘅同一模式 ═══
print("\n─── [C] 耦合 perm 嘅 pair 拆分模式 (對照) ───")
cpat = Counter()
for s in coupled_sets:
    vanish = [perm for perm in itertools.permutations(s)
              if abs(V4(44, NS, list(perm))) < 1e-9]
    for perm in itertools.permutations(s):
        if perm in vanish: continue
        ps = []
        for (i1,i2,i3,i4) in [(0,1,2,3),(0,2,1,3),(0,3,1,2)]:
            p1 = (perm[i1], perm[i2]); p2 = (perm[i3], perm[i4])
            p1s = tuple(sorted(p1)); p2s = tuple(sorted(p2))
            tag1 = 'D' if p1s in diag_pairs else 'o'
            tag2 = 'D' if p2s in diag_pairs else 'o'
            tgt1 = pair_target.get(p1s, None)
            tgt2 = pair_target.get(p2s, None)
            ps.append(f"{tag1}({tgt1}){tag2}({tgt2})")
        cpat[" ".join(ps)] += 1
for pat, cnt in cpat.most_common(6):
    print(f"         {pat}: {cnt}")
print(f"       耦合模式種數: {len(cpat)} vs 消失模式種數: {len(patterns)}")
check("C1 消失模式 ⊄ 耦合模式 (有鑑別結構)",
      any(p not in cpat for p in patterns), f"(消失 {set(patterns)} vs 耦合 {set(cpat)})")

# ═══ D. (0,3,5,7) (全耦合 set) 詳細: 有冇任何 diag-pair 結構? ═══
print("\n─── [D] 全耦合 set 嘅 pair 結構 — 點解冇消失 ───")
for s in [(0,3,5,7), (0,4,6,7), (1,3,6,7), (1,4,5,7)]:
    s2 = list(s)
    pairs = [tuple(sorted(p)) for p in itertools.combinations(s, 2)]
    diags = [p for p in pairs if p in diag_pairs]
    offs = [f"{p}→{pair_target.get(p)}" for p in pairs if p in pair_target]
    print(f"       {s}: diag-pairs {diags} | closure pairs {offs}")
check("D1 全耦合 set 冇 diag-pair (得 7 有 role)", 
      all(not any(p in diag_pairs for p in itertools.combinations(s,2))
          for s in [(0,3,5,7),(0,4,6,7),(1,3,6,7),(1,4,5,7)]),
      "(冇 (0,1)/(3,4)/(5,6) 對 → 唔可能 pair-split 消失)")

# ═══ E. 機制總結: 消失 ⟺ perm 嘅 (12|34) 拆分兩對都係 diag-pair? ═══
print("\n─── [E] 主假設: 消失 ⟺ 有 pair 拆分令兩對都係 diag-pair ───")
okE = True; badE = []
for s in coupled_sets:
    vanish = [perm for perm in itertools.permutations(s)
              if abs(V4(44, NS, list(perm))) < 1e-9]
    vs = set(vanish)
    pred = set()
    for perm in itertools.permutations(s):
        for (i1,i2,i3,i4) in [(0,1,2,3),(0,2,1,3),(0,3,1,2)]:
            p1 = tuple(sorted((perm[i1],perm[i2]))); p2 = tuple(sorted((perm[i3],perm[i4])))
            if p1 in diag_pairs and p2 in diag_pairs:
                pred.add(perm)
    if pred != vs:
        okE = False
        badE.append((s, len(pred), len(vs)))
for s in coupled_sets:
    pass
check("E1 消失 ⟺ 存在 diag-pair 拆分 (!! pair ordering 需 24/3 測試)", okE,
      f"(bad {badE[:4]})")

print(f"\n{'='*78}")
print(f"  RESULT: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print(f"{'='*78}")
import sys
sys.exit(0 if FAIL == 0 else 1)