#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O244 — scripts/05 (v2): T2 尾 — 4g 色 sector 選擇律機制
=====================================================================================
v1 發現 (logs/05.txt 前半): (0,1,2,3) 禁戒【已推導】= 差向量組和 C_t ≡ 0 (純張量,
N/動量無關, 全拓樸零恆等)。但 488 唔普適: 5 動量非零數 = [432,432,176,488,176] —
docs/02 寫「488/4096 = 61/512」係單一動量資料, 要更正。

v2 結構假設 (想證):
  R2 ★ 3+1 (a,a,a,b) 類全禁戒 (224 個色模式, 任何動量): C_t ≡ 0 ∀ t —— 同 (0,1,2,3)
     一類嘅張量定理。
  R3 退化動量 (n 全等, e.g. (22,22,22,22)): V₄ = Σ_δ T_δ (所有相位=1) ⟹ 耦合 ⟺
     σ(aa) := Σ_δ T_δ ≠ 0。實測 176 = 8+168 ⟹ σ = 0 凡 ≥3 個相異色。
  R4 4同/2+2 全耦合 (8+168 = 176 基礎, 任何動量)。

判據:
  A 拓樸零 (0,1,2,3) vs 對照 (0,0,0,0)                     [重驗 v1]
  B C_t 組和: (0,1,2,3) 全零 + (0,0,0,1) 全零 (R2) + 對照   [機制推導]
  C 5 動量 × 全 8⁴ 色非零數表 (+ 類別拆解)
  D R4: 4同 8/8 + 2+2 168/168 全耦合跨 5 動量
  E R2: 3+1 非零數 = 0 跨 5 動量 (C_t 定理 ⟹ 預測全零)
  F R3: 退化動量只 4同+2+2 耦合 (176 = 8+168 EXACT)
  G 2+1+1/全異 計數: 動量相關 (相位誘發), 報表唔宣稱閉式
唯一輸入: su(3) 色代數 + V₄ 張量。零自由參數。
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

# ── su(3) 色 (同 scripts/01) ──
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

def V4(N, ns, aas):
    M2 = 2*N
    inner = 0.0
    for d in itertools.product([0,1], repeat=4):
        idx = [8*d[k] + aas[k] for k in range(4)]
        inner += np.exp(2j*np.pi*sum(d[k]*ns[k] for k in range(4))/M2) * Tget(*idx)
    site = sum(np.exp(2j*np.pi*int(sum(ns))*m/M2) for m in range(M2))
    return -inner*site/(24.0*M2*M2)

def group_sums(aas):
    """C_t := Σ_{δ: (δ1−δ4,δ2−δ4,δ3−δ4)=t} T_δ"""
    groups = {}
    for d in itertools.product([0,1], repeat=4):
        t = (d[0]-d[3], d[1]-d[3], d[2]-d[3])
        idx = [8*d[k] + aas[k] for k in range(4)]
        groups.setdefault(t, 0.0 + 0.0j)
        groups[t] += Tget(*idx)
    return groups

def sigma_all(aas):
    """σ := Σ_{δ∈{0,1}⁴} T_δ (退化動量嘅 V₄ 張量核)"""
    return sum(Tget(8*d[0]+aas[0], 8*d[1]+aas[1], 8*d[2]+aas[2], 8*d[3]+aas[3])
               for d in itertools.product([0,1], repeat=4))

def mclass(aa):
    counts = sorted(Counter(aa).values(), reverse=True)
    if counts == [4]: return "4同"
    if counts == [3,1]: return "3+1"
    if counts == [2,2]: return "2+2"
    if counts == [2,1,1]: return "2+1+1"
    return "全異"

print("="*78)
print("  O244 scripts/05 (v2): 4g 色 sector 選擇律 — 機制 + 類別結構")
print("  唯一輸入: su(3) 色代數 + V₄ 張量。零自由參數。")
print("="*78)

N = 44; M2 = 2*N

# ═══ A. 拓樸零 (重驗 v1) ═══
print("\n─── [A] 拓樸擴展 (全 Z_88³) ───")
rng = np.random.default_rng(20261010)
zeros = 0
for _ in range(300):
    n1, n2, n3 = [int(x) for x in rng.integers(0, 88, size=3)]
    n4 = (-(n1+n2+n3)) % 88
    if abs(V4(44, [n1, n2, n3, n4], [0, 1, 2, 3])) < 1e-9: zeros += 1
check("A1 色 (0,1,2,3): 300 隨機全拓樸點全零", zeros == 300, f"({300 - zeros} 非零)")
check("A2 對照 (0,0,0,0) 喺物理動量耦合", abs(V4(44, [1,1,42,44], [0,0,0,0])) > 1e-9)

# ═══ B. C_t 組和 (機制推導) ═══
print("\n─── [B] C_t 張量組和 (N/動量無關) ───")
gs_0123 = group_sums([0,1,2,3])
worstB = max(abs(v) for v in gs_0123.values())
check("B1 (0,1,2,3): C_t ≡ 0 (16 差向量組, 15 非空)", worstB < 1e-9,
      f"(worst |C_t| = {worstB:.2e})")
# R2: (0,0,0,1) — 3+1 代表
gs_0001 = group_sums([0,0,0,1])
nz_groups_0001 = sum(1 for v in gs_0001.values() if abs(v) > 1e-9)
check("B2 ★ 3+1 (0,0,0,1): C_t ≡ 0 — 類全禁戒 (R2)", nz_groups_0001 == 0,
      f"({nz_groups_0001}/{len(gs_0001)} 組非零, worst {max(abs(v) for v in gs_0001.values()):.2e})")
# 其他 3+1 代表: (1,1,1,2), (2,2,2,5), (0,0,0,7), (4,4,4,0)
ok31 = True
for pat in ([1,1,1,2], [2,2,2,5], [0,0,0,7], [4,4,4,0]):
    if max(abs(v) for v in group_sums(pat).values()) > 1e-9: ok31 = False
check("B3 3+1 類: 5 個代表 (a,a,a,b) 全 C_t ≡ 0", ok31, "(a≠b)")

# ═══ C. 5 動量 × 全色 非零數 ═══
print("\n─── [C] 非零色組合數跨動量 ───")
momenta = [(1,1,42,44), (2,2,40,44), (22,22,22,22), (1,21,22,44), (44,44,44,44)]
per_mom = {}
for ns in momenta:
    cnt = sum(1 for aa in itertools.product(range(8), repeat=4)
              if abs(V4(44, list(ns), list(aa))) > 1e-9)
    per_mom[ns] = cnt
print(f"       非零數: {[per_mom[m] for m in momenta]}")
check("C1 非零數跨動量唔一樣（488 唔係普適 — 更正 docs/02）",
      len(set(per_mom.values())) > 1, f"(值集 = {sorted(set(per_mom.values()))})")

# ═══ D. 類別拆解 × 動量 (R4/E) ═══
print("\n─── [D] 類別拆解 × 動量 ───")
class_nz = {}
for ns in momenta:
    cn = {k: 0 for k in ["4同", "3+1", "2+2", "2+1+1", "全異"]}
    for aa in itertools.product(range(8), repeat=4):
        if abs(V4(44, list(ns), list(aa))) > 1e-9:
            cn[mclass(aa)] += 1
    class_nz[ns] = cn
for ns in momenta:
    cn = class_nz[ns]
    print(f"       {ns}: 4同 {cn['4同']} | 3+1 {cn['3+1']} | 2+2 {cn['2+2']} | "
          f"2+1+1 {cn['2+1+1']} | 全異 {cn['全異']}  = {sum(cn.values())}")
ok_r4 = all(class_nz[m]["4同"] == 8 and class_nz[m]["2+2"] == 168 for m in momenta)
check("D1 R4: 4同 8/8 + 2+2 168/168 全耦合 (5 動量)", ok_r4)
ok_r2 = all(class_nz[m]["3+1"] == 0 for m in momenta)
check("D2 R2: 3+1 全禁戒 (5 動量, 0/224)", ok_r2,
      "(機理 = B2/B3 C_t ≡ 0 ⟹ 任何動量)")

# ═══ E. 退化動量核: (22,22,22,22) 相位 i^{Σδ}, (44,44,44,44) 相位 (−1)^{Σδ} ═══
print("\n─── [E] 退化動量核: K_w(aa) := Σ_δ w^{Σδ} T_δ (w=i / w=−1) ───")
def sigma_weighted(aas, w):
    return sum((w**(sum(d)))*Tget(8*d[0]+aas[0], 8*d[1]+aas[1], 8*d[2]+aas[2], 8*d[3]+aas[3])
               for d in itertools.product([0,1], repeat=4))
ok_sigma = True
details = []
for aa in [(0,0,0,0), (0,0,0,1), (0,0,1,1), (0,0,1,2), (0,1,2,3), (0,1,2,4), (5,5,7,7)]:
    cl = mclass(aa)
    s_i = sigma_weighted(list(aa), 1j)   # (22,22,22,22) 核
    s_m = sigma_weighted(list(aa), -1)   # (44,44,44,44) 核
    pred_i = cl in ("4同", "2+2")
    pred_m = cl in ("4同", "2+2")
    ok_i = (abs(s_i) > 1e-9) == pred_i
    ok_m = (abs(s_m) > 1e-9) == pred_m
    if not (ok_i and ok_m): ok_sigma = False
    details.append(f"{cl}:|Ki|={abs(s_i):.1e}/|K-|={abs(s_m):.1e}")
check("E1 R3: K_i / K_−1 ≠ 0 ⟺ 色數 ≤ 2 (7 代表 × 2 核)",
      ok_sigma, "(4同/2+2 非零; 3+1/2+1+1/全異 零)")
# 直接對照: 退化動量 176 = 4同 8 + 2+2 168（已喺 D 表）
check("E2 (22,22,22,22) 非零 = 176 = 8 + 168 EXACT (只有 4同+2+2)",
      per_mom[(22,22,22,22)] == 176 and
      class_nz[(22,22,22,22)]["4同"] == 8 and class_nz[(22,22,22,22)]["2+2"] == 168 and
      class_nz[(22,22,22,22)]["2+1+1"] == 0 and class_nz[(22,22,22,22)]["全異"] == 0)

# ═══ F. 2+1+1 / 全異 動量相關報表 ═══
print("\n─── [F] 2+1+1 / 全異 計數（動量相關相位誘發, 非閉式） ───")
for ns in momenta:
    cn = class_nz[ns]
    print(f"       {ns}: 2+1+1 = {cn['2+1+1']}/2016, 全異 = {cn['全異']}/1680")
check("F1 2+1+1/全異 計數隨動量變（唔係結構常數）",
      len(set((class_nz[m]['2+1+1'], class_nz[m]['全異']) for m in momenta)) > 1,
      "(相位誘發零 — 記錄, 唔聲稱閉式)")

print(f"\n{'='*78}")
print(f"  RESULT: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print(f"{'='*78}")
import sys
sys.exit(0 if FAIL == 0 else 1)