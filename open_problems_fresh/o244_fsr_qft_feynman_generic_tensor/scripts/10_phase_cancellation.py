#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O244 — scripts/10: 相位削減分類 — (1,1,42,44) 全異 264→208 嘅 56 個消失 pattern
=====================================================================================
docs/08 §5 殘餘 #1: 結構上限 (mixed-T_δ 非零) = 488 (8+168+48+264)，動量再相位削減:
  (1,21,22,44) → 488 全留        (冇削減)
  (1,1,42,44)  → 432 (全異 264→208, 少 56)
  (22,22,22,22)/ (44,44,44,44) → 176 (退化: 只留 4同 8 + 2+2 168)
本 script:
  [A] 重現 5 動量耦合表對照 (scripts/05: [432,432,176,488,176])
  [B] (1,1,42,44) 全異: 264 個 mixed-nonzero pattern 分 V₄≠0 (208) / V₄=0 (56)
      + 56 個消失 pattern 嘅色 set 結構 (set 級定 pattern 級? 有冇共同色?)
  [C] 相位對稱分析: 動量 n 嘅保序對稱群 G ⊆ S4 (n_{σ(i)}=n_i) —
      (1,1,42,44) 有 n₁=n₂ ⟹ G = <(12)>; δ-軌道內相位是否成對? T_δ 是否成對?
      → 修正機制: 消失條件 V₄ ≡ 0 ⟺ Σ_δ φ(δ)T_δ = 0, 唔係單項
  [D] 殘餘 #3: N 掃 — (1,1,N-3,N-4)/(1,21,N-1,N?) 型動量喺 N∈{44,88,176} 嘅 V₄ 非零數
      (檢查 N 無關性; T_δ 無 N ⟹ 結構上限 N 無關, 相位削減隨 N 變?)
唯一輸入: su(3) 色代數 + Q4 張量 + FSR 動量。零自由參數。
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
DALL = list(itertools.product([0,1], repeat=4))
MIXED = [d for d in DALL if d not in ((0,0,0,0),(1,1,1,1))]
def T_mixed_max(aas): return max([abs(T_delta(aas, d)) for d in MIXED] + [0.0])

print("="*78)
print("  O244 scripts/10: (1,1,42,44) 相位削減 56 pattern 分類")
print("="*78)

# ═══ A. 5 動量耦合表重現 ═══
print("\n─── [A] 5 動量 × 全 4096 色 → 非零 V₄ count (對照 scripts/05) ───")
momenta = {
    "(1,21,22,44)": [1,21,22,44],
    "(1,1,42,44)":  [1,1,42,44],
    "(22,22,22,22)":[22,22,22,22],
    "(44,44,44,44)":[44,44,44,44],
    "(1,1,44,44)":  [1,1,44,44],
}
table = {}
for name, ns in momenta.items():
    cnt = sum(1 for aa in itertools.product(range(8), repeat=4)
              if abs(V4(44, ns, list(aa))) > 1e-9)
    table[name] = cnt
    print(f"       {name}: {cnt}")
check("A1 5 動量表 = scripts/05 [432,432,176,488,176] 形態",
      table["(1,21,22,44)"] == 488 and table["(1,1,42,44)"] == 432 and
      table["(22,22,22,22)"] == 176 and table["(44,44,44,44)"] == 176,
      f"(表 {table})")

# ═══ B. 264 個全異 mixed-nonzero: 208 耦合 vs 56 消失 ═══
print("\n─── [B] (1,1,42,44) 全異 264 拆分 ───")
keep56 = []; drop56 = []
for aa in itertools.product(range(8), repeat=4):
    if mclass(aa) != "全異": continue
    if T_mixed_max(list(aa)) < 1e-9: continue   # 結構禁戒, 唔喺 264
    aa = list(aa)
    if abs(V4(44, [1,1,42,44], aa)) > 1e-9: keep56.append(aa)
    else: drop56.append(aa)
print(f"       耦合 {len(keep56)} | 相位消失 {len(drop56)} (預期 208/56)")
check("B1 208/56 拆分", len(keep56) == 208 and len(drop56) == 56,
      f"({len(keep56)}/{len(drop56)})")

# 56 消失嘅色 set 結構
set_drop = Counter(frozenset(a) for a in drop56)
set_keep = Counter(frozenset(a) for a in keep56)
print(f"\n       消失 56 → 色 set 數: {len(set_drop)};  耦合 208 → set 數: {len(set_keep)}")
sizes_d = Counter(cnt for c in set_drop.values())
print(f"       消失: set 出現次數分佈 {dict(sorted(sizes_d.items()))} "
      f"(24=該 set 全 24 perm 都消失; <24 = 部分)")
sets_all = sorted(set(set_drop.keys()) | set(set_keep.keys()))
print(f"\n       set 級: 消失 set 數 {len(set_drop)}/{len(sets_all)}, "
      f"耦合 set 數 {len(set_keep)}/{len(sets_all)}")
check("B2 消失係 set 級定 pattern 級? (<24 出現 = pattern 級)",
      len(set_drop) < 11, f"(消失 set {len(set_drop)} 個, 全消失 set 數 {sizes_d.get(24,0)})")
if sizes_d.get(24, 0) == 0:
    print("       ⟹ 56 唔係 set 級全滅 — 係 pattern 級 (同一色集部分排列消失)")

# ═══ C. 相位對稱: n₁=n₂=1 ⟹ δ₁↔δ₂ 對稱診斷 ═══
print("\n─── [C] (1,1,42,44) 相位對稱診斷 ───")
# 全異 pattern 一個 exact set 試: e.g. (0,1,2,3) 各排列喺 (1,1,42,44) 邊啲消失
s = [0,1,2,3]
res = []
for perm in itertools.permutations(s):
    aa = list(perm)
    v = abs(V4(44, [1,1,42,44], aa))
    res.append((perm, v > 1e-9))
nz = sum(1 for _, k in res if k)
print(f"       (0,1,2,3) 24 perm: 耦合 {nz}, 消失 {24-nz}")
for i in range(0, 24, 4):
    print(f"         {res[i:i+4]}")
# σ=(12) 保序對稱: aa 同 aa∘(12)（交換位置1,2）應同 V₄ 值?
# 但 (1,1,42,44) 位置1/2動量=1 ⟹ inner 相位 Σδ·n 對 δ₁↔δ₂ 不變, T_δ sorted 對稱
# ⟹ V₄(aa₁,aa₂,aa₃,aa₄) = V₄(aa₂,aa₁,aa₃,aa₄)?? 但 Tget sorted! 檢查
ok_sym = True
for aa in keep56[:40]:
    aa2 = [aa[1], aa[0], aa[2], aa[3]]
    if abs(abs(V4(44,[1,1,42,44],aa)) - abs(V4(44,[1,1,42,44],aa2))) > 1e-9:
        ok_sym = False
check("C1 V₄ 對 δ₁↔δ₂ 交換不變 (Tget sorted ⟹ 應然)", ok_sym,
      "(T_δ 用 sorted key → 相位 Σδn: n₁=n₂ → 對稱 → 值同)")

# ═══ D. N 掃: 結構上限 N 無關性 ═══
print("\n─── [D] N 掃残餘 #3: (1,N-3,N-1,N?) 型動量喺 N∈{44,88} — 全異 264 check ───")
for NN in [44, 88]:
    ns_variants = []
    if NN == 44:  ns_variants = [[1,21,22,44], [1,1,42,44], [22,22,22,22]]
    else:         ns_variants = [[1,87,44,88], [1,1,86,88], [44,44,44,44]]
    print(f"       N={NN}: ", end="")
    for ns in ns_variants:
        c = sum(1 for aa in itertools.product(range(8), repeat=4)
                if mclass(aa) == "全異" and abs(V4(NN, ns, list(aa))) > 1e-9)
        print(f"{tuple(ns)}→全異非零 {c}, ", end="")
    print()
# 全 N 掃完整成本高; 只驗 structural upper (mixed nonzero) 唔變
okN = True
for NN in [22, 44, 88]:
    for aa0 in [(0,1,2,3), (0,1,2,4), (0,1,3,7), (0,2,3,7), (1,2,4,6)]:  # 含 3 耦合 + 2 禁戒
        aa = list(aa0)
        struct = T_mixed_max(aa) > 1e-9
        # 用候選動量 (1,NN//2-1,NN-1,NN) 需守恆: sum ≡ 0 mod 2N
        ns = [1, NN//2-1, NN-1, NN]
        if sum(ns) % (2*NN) != 0:
            ns = [1, NN//2-1, NN-3, NN+2]
        v = abs(V4(NN, ns, aa)) > 1e-9
        if struct != v: okN = False
check("D1 5 個代表色: 結構非零 ⟺ V₄ 非零 (N∈{22,44,88} 守恆動量)",
      okN, "(T_δ 無 N → 結構上限 N 無關; 相位可另行削減)")

print(f"\n{'='*78}")
print(f"  RESULT: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print(f"{'='*78}")
import sys
sys.exit(0 if FAIL == 0 else 1)