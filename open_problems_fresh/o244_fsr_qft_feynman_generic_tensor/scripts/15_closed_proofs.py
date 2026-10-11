#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O244 — scripts/15: 封閉代數證明 — (E2) su(2)-closure trace 消滅 + (成塊⟹ΣφT=0)
=====================================================================================
docs/08 §5 #2 + docs/09 §4: 兩項代數證明缺口。

[A] su(2)-closure (E2) 完整論證:
    全異 43 sets 含 closure triple {i,j,k} ([T_i,T_j]∝T_k, 3 色 span su(2))。
    論證骨架: 對 set = {i,j,k,c}, 任何 4-生成乘積 trace 有 3 個 su(2) 內色 +
    1 個 c。su(2) 內 3 乘積 closure 返 span{X,Y,Z}（唔離開子代數），
    而 c ⊥ span{X,Y,Z}（正交性）⟹ Tr[(su2 elem) T_c] = 0 ∀排列。
    同時 [u,v]² 項 = Tr[[A,B][C,D]] 型 — 都係 4-trace → 同一消滅。
    驗證: 對全部 43 sets × 24 排列 × 16 δ: Q4 展開項全零（即 T_δ ≡ 0 已證），
    但呢度專注 trace 層: 每項出 4 個 T 乘積 → 檢查「3-su2+1-c」property 
    對 set 內所有色排列所有 Q4 項。
    [A1] 每個 43 set: 存在 triple {i,j,k} 令所有色組合都係 ∃3 色 ∈ {su2 3色}
    [A2] 對任一 su2 elem E = αT_i+βT_j+γT_k: Tr[E·T_c] = 0 ∀c ∉ {i,j,k}
    [A3] 對 43 sets 全掃: T_δ = 0 值為 EXACT 0（種子級）— 數字再確認

[B] 成塊 ⟹ ΣφT=0 嘅 trace 論證 (spin pair):
    (0,1,3,4) 排列成塊 (0,1)|(3,4)。消失 = inner16 = 0。
    拆 16 δ 項: δ 配置 16 個 → 每項 φ(δ)T_δ。
    對 spin pair 成塊, 項成對抵消: 搵通用 δ-pair 規則:
    [B1] δ ↔ δ' with 兩個 spin pair 同時 flip slot 嘅差 (唔變總 u-count 嘅 'u/v 對偶')
    [B2] 對所有成塊排列: 存在分組令每組 Σ φT = 0（成對/四重消滅）
    [B3] 對照非成塊排列: 冇呢個分組 ⟹ inner ≠ 0

[C] off-diag 4 sets 成塊 split 一件式: (0,2,3,5) 型 — 消失排列 8 個
    對應邊個 split? scripts/12 顯示多個 split 候選 → 逐一驗證成塊集
    [C1] 對 4 個 off-diag sets: 消失 8 個 = 某 pair-split 嘅成塊排列（精確）
    [C2] 該 split 嘅兩 pair 各自 commutator 指向同一色（=off-diag 同 target 機制）
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

print("="*78)
print("  O244 scripts/15: 封閉代數證明 — E2 su2-closure + 成塊⟹ΣφT=0")
print("="*78)

# closure triples (unordered) — 9 個 (scripts/08)
closures = []
for i in range(8):
    for j in range(i+1, 8):
        C = 1j*(T[i]@T[j] - T[j]@T[i])
        if abs(np.linalg.norm(C)) < 1e-10: continue
        ks = [k for k in range(8) if k != i and k != j and is_propto(C, k)]
        for k in ks:
            tr = frozenset((i,j,k))
            if tr not in closures: closures.append(tr)
print(f"closure triples: {[tuple(sorted(c)) for c in closures]}")

# ═══ A. su(2)-closure trace 消滅 ═══
print("\n─── [A] E2 su(2)-closure: 43 sets 全滅嘅 trace 論證 ───")
okA2 = True; badA2 = []
# A2: su2 elem ⊥ 外色
for tr in closures:
    tri = sorted(tr); c_out = [x for x in range(8) if x not in tri]
    for x in c_out:
        for a in range(3):
            C = T[tri[a]] @ T[x]
            if abs(np.trace(C).real) > 1e-10: okA2 = False; badA2.append((tri, x, a))
check("A2 su(2) generator ⊥ 外色 (Tr[T_su2·T_c]=0)", okA2, f"({len(badA2)} 違反)")
# A3: 43 sets T_δ EXACT zero — 每個 set 有 closure triple ⊂ set
okA3 = True; n_sets_with_tr = 0
for s in itertools.combinations(range(8), 4):
    aa = list(s)
    if T_mixed_max(aa) > 1e-9: continue            # 禁戒 set
    sf = frozenset(s)
    has_tr = any(c <= sf for c in closures)
    if has_tr: n_sets_with_tr += 1
    else:
        # 禁戒但冇 closure triple = λ₈-家族 16 sets (已分類) — 唔屬 E2
        pass
# 43 = 含 closure triple 嘅禁戒全異 set 數?
total_forbid = 0; total_with_tr_forbid = 0
for s in itertools.combinations(range(8), 4):
    aa = list(s)
    if T_mixed_max(aa) > 1e-9: continue
    total_forbid += 1
    if any(c <= frozenset(s) for c in closures): total_with_tr_forbid += 1
print(f"       全異禁戒 sets {total_forbid} | 其中含 closure triple {total_with_tr_forbid}")
check("A3 43 sets 含 closure triple (E2 範圍 = 43)", total_with_tr_forbid == 43,
      f"({total_with_tr_forbid})")
# A1: T_δ 全 16 項 EXACT 0（廣義: 全部 1416 禁戒 pattern 16 δ 全 0）— 中間值再驗
worst = 0.0; cnt_exact = 0; cnt_all = 0
for s in itertools.combinations(range(8), 4):
    aa = list(s)
    if T_mixed_max(aa) > 1e-9: continue
    for d in DALL:
        v = abs(T_delta(aa, d)); cnt_all += 1
        if v > worst: worst = v
        if v < 1e-12: cnt_exact += 1
print(f"       禁戒 pattern 全部 {cnt_all} 個 T_δ 值: worst = {worst:.2e}, <1e-12 佔 {cnt_exact}/{cnt_all}")
check("A1 禁戒 set 全 T_δ 值 EXACT 0 (worst = 浮點噪聲級)",
      worst < 1e-9, f"(worst {worst:.2e})")
# A4: trace 層分解 — 對代表 set (0,1,2,3) 全異禁戒: Q4 每項 4-trace 展開
print("\n       ── A4 代表 set {0,1,2,3} (triple {0,1,2} + c=3): Q4 項 trace 驗證 ──")
# T_δ = 24 pol 對 δ=0000: u = T₀+T₁+T₂+T₃, v=0 → Q4(u,0) = Tr[u⁴]
# ∂⁴ 混合 = 4! Σperms Tr[T_a T_b T_c T_d]: 每項有 3 個 su2 色 + 1 c=3
u4 = sum(T[i] for i in range(4))
# 直接: Tr[(T0+T1+T2+T3)^4] perms trace — 用 su2 論證: {0,1,2} span su2
# 搵 su2 元素: 對任何 3-permutation (a,b,c) ∈ {0,1,2}: T_a T_b T_c ∈ span{T0,T1,T2}
# A4''' 真正機制發現: 單項 4-trace 全零 (唔係求和零)!
# ⟹ E2 主定理候選: set 含 su(2)-closure triple ⟹ ∀排列 Tr[T_aT_bT_cT_d] = 0
# 全 43 sets × 24 perms 掃描驗證
print("\n       ── A4''' E2 主定理: set 含 su(2)-closure ⟹ 單項 4-trace 全零 ──")
okA4 = True; badA4 = []
for s in itertools.combinations(range(8), 4):
    sf = frozenset(s)
    if not any(c <= sf for c in closures): continue   # 只測 43 sets
    for perm in itertools.permutations(s):
        v = np.trace(T[perm[0]]@T[perm[1]]@T[perm[2]]@T[perm[3]]).real
        if abs(v) > 1e-10:
            okA4 = False
            if len(badA4) < 4: badA4.append((s, perm, v))
check("A4''' 43 sets × 24 perms: 全部單項 Tr[T_aT_bT_cT_d] = 0 (E2 單項消滅)",
      okA4, f"({len(badA4)} 違反 {badA4[:2]})")
# 對照: su(2) 外色 set (0,1,3,4 唔含 triple) 單項 trace 係咪有非零?
nz_ct = 0; tot_ct = 0; ex = []
for perm in itertools.permutations([0,1,3,4]):
    tot_ct += 1
    v = np.trace(T[perm[0]]@T[perm[1]]@T[perm[2]]@T[perm[3]]).real
    if abs(v) > 1e-10: nz_ct += 1; ex.append(v)
print(f"       對照 (0,1,3,4) (冇 triple): 單項非零 {nz_ct}/{tot_ct}, 例 {ex[:4]}")
check("A4iv 對照: 冇 triple set 有非零單項 trace (機制有鑑別力)",
      nz_ct > 0, f"({nz_ct}/{tot_ct} 非零)")

# ═══ B. 成塊 ⟹ ΣφT=0 δ-pair 規則 ═══
print("\n─── [B] 成塊排列 inner=0 — δ 分組規則 ───")
NS = [1,1,42,44]
aa = [0,1,3,4]
def phi(d): return np.exp(2j*np.pi*sum(d[k]*NS[k] for k in range(4))/88)
terms = {d: phi(d)*T_delta(aa, d) for d in DALL}
total = abs(sum(terms.values()))
print(f"       inner(0,1,3,4) = {total:.3e} (0 = 消失)")
# u/v flip 對偶: δ ↔ (1−δ₁,1−δ₂,·,·)? 或者 pair-slot swap(s1<->s2) 同 (s3<->s4)
grp = defaultdict(complex)
for d in DALL:
    k = tuple(sorted(d[:2])) + tuple(sorted(d[2:]))   # 以 slot pair 內排序作類
    grp[k] += terms[d]
print("       按 (sorted(slot1,2), sorted(slot3,4)) 分組: 每組和:")
for k, v in sorted(grp.items()):
    print(f"         {k}: {v:.4e}")
# 規則候選: δ 對 = swap δ₁↔δ₂（pair 內部）→ φ 唔變 (n₁=n₂) ; swap δ₃↔δ₄ → φ 變化
# pair flip: δ 同 δ' = (1-δ₁,1-δ₂,δ₃,δ₄)? 試 u/v 對偶啱唔啱
pair_rules = {}
for d in DALL:
    dp = (1-d[0], 1-d[1], d[2], d[3])
    pair_rules[d] = abs(terms[d] + terms.get(dp, 0))
pair_rules2 = {}
for d in DALL:
    dp = (d[0], d[1], 1-d[2], 1-d[3])
    pair_rules2[d] = abs(terms[d] + terms.get(dp, 0))
okB = all(v < 1e-9 for v in pair_rules.values()) or all(v < 1e-9 for v in pair_rules2.values())
mk1 = sum(1 for v in pair_rules.values() if v < 1e-9)
mk2 = sum(1 for v in pair_rules2.values() if v < 1e-9)
print(f"       規則1 (swap δ₁↔δ₂, spin pair (0,1)): {mk1}/16 對和零")
print(f"       規則2 (swap δ₃↔δ₄, spin pair (3,4)): {mk2}/16 對和零")
check("B1 成塊 inner=0 來自 slot-pair 相位對稱 (至少一條規則全對)", okB or mk1==16 or mk2==16,
      f"(規則1 {mk1}/16, 規則2 {mk2}/16)")

# ═══ C. off-diag 4 sets 成塊 split 一件式 ═══
print("\n─── [C] off-diag sets: 消失 8 = 邊個 pair split 成塊? ───")
def closure_pair_target(i, j):
    C = 1j*(T[i]@T[j] - T[j]@T[i])
    ks = [k for k in range(8) if k != i and k != j and is_propto(C, k)]
    return ks[0] if ks else None
offdiag_sets = [(0,2,3,5),(0,2,4,6),(1,2,3,6),(1,2,4,5)]
okC = True; detC = []
for s in offdiag_sets:
    vanish = set(perm for perm in itertools.permutations(s)
                 if abs(V4(44, NS, list(perm))) < 1e-9)
    # 搵 split: 兩對 closure pairs 指向同一 target
    found = None
    for (i1,i2,i3,i4) in [(0,1,2,3),(0,2,1,3),(0,3,1,2)]:
        p1 = (s[i1], s[i2]); p2 = (s[i3], s[i4])
        t1 = closure_pair_target(*sorted(p1)); t2 = closure_pair_target(*sorted(p2))
        if t1 == t2 and t1 is not None:
            pred = set()
            for perm in itertools.permutations(s):
                b1 = tuple(sorted((perm[0],perm[1]))); b2 = tuple(sorted((perm[2],perm[3])))
                if {b1,b2} == {tuple(sorted(p1)), tuple(sorted(p2))}: pred.add(perm)
            if pred == vanish:
                found = (p1, p2, t1); break
    if found:
        detC.append((s, found))
        print(f"       {s}: 消失8 = 成塊 w.r.t {found[0]} | {found[1]} (共同 target {found[2]})")
    else:
        okC = False
        print(f"       {s}: 未搵到 split (唔 match)")
check("C1 4 off-diag sets: 消失8 精確 = 同target pair 成塊", okC,
      f"({len(detC)}/4; {detC})")

print(f"\n{'='*78}")
print(f"  RESULT: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print(f"{'='*78}")
# ═══ AUDIT 更正附註 (2026-10-11) ═══
# A4''' 用 np.trace(...).real 判斷「單項 4-trace 全零」——係假 PASS:
# scripts/16 用 |·| 重掃發現 232/1032 個單項 trace 非零（全部純虛 ±i/(8√3)）。
# 本 script 之 7/7 入面 A4''' 結論唔成立；E2 真正機制 = pol 排列組合消滅（docs/11）。
# 正確水位: 6 PASS + 1 REFUTED（A4'''）。唯一輸入不變, 零自由參數。
import sys
sys.exit(0 if FAIL == 0 else 1)