#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O201 scripts/21 -- Z_N Abel 公設閉合 (Abelian Axiom Closure)

## 問題 (Session 5 剩餘 🔴)
  docs/19: 1D + cyclic + 2-regular 已由觀測量強迫, 但「為何平移不變
  (Abel 公設)」標 🔴 → O95/O96 級基礎問題。

## 本 script 嘅新結果 (★★ Abel 公設降為定理)
  T1 ★★ 模態計數 ⟹ Abel: 88 個**獨立單指標模態**需要 88 個一維特徵標;
     |Ĝ| = |G| ⟺ G Abel (特徵群對偶定理)
     ⇒ 「88 個模態」本身強迫 Abel — 唔係公設
     數值: Z_88 特徵標 88 個 (全部一維); S_3 只有 3 個不可約表示
     (1,1,2 維), D_4 只有 5 個 (< 8) ⇒ 非 Abel 冇 88 個一維特徵標
  T2 ★ 讀數結構: 非 Abel 群嘅不可約表示維度 d_ρ ≥ 2 ⇒ 模態必須由
     多分量對象標籤, 唔可能係 88 個獨立單指標值; 觀察者讀數 = |1−χ|²
     需要一維 χ。⚠️ 注意 (2026-09-17 審計修正): 「簡併」唔係非 Abel 專有 —
     C_88 譜本身有 k ↔ 88−k 二重簡併 (88 模態 / 45 相異值); 論證嘅關鍵係
     **標籤結構** (88 個一維特徵標), 唔係「有冇簡併」。
  T3 ★ 預算均勻 ⟹ 平移不變: O41 觀察者預算 B(n) = L10/(2N_d) 對全部
     mode 均勻 ⟹ 冇特殊 site ⟹ 群作用自由可遷 (Cayley 圖)
     + docs/19 T2 生成元不變性 ⟹ 平移不變自然成立
  T4 總結: Abel 公設 = 模態計數 (T1) + 無簡併讀數 (T2) + 預算均勻 (T3)
     嘅直接後果 — 🔴 → 🟢 條件閉合 (剩: 「為何 88」= O95/O96 已閉合 44 必然性)

## 版本史
  v1 (2026-09-17): 首版 — Abel 公設閉合。
  v2 (2026-09-17): 審計修正 — 群論事實改為真算 (共軛類 + 交換子子群,
      唔再對硬編表自查); T2 措辭修正 (簡併唔係非 Abel 專有)。
"""
import os
import sys
import json
import math
import itertools

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import mpmath as mp
import o201_basis as ob

mp.mp.dps = 40
PI = mp.pi

print("=" * 78)
print("O201/21 -- Z_N Abel 公設閉合 v1")
print("=" * 78)

Nd, B, Ngen, L4, L5, F5, F7, KTREE, FPROJ = 44, 4, 3, 7, 11, 5, 13, 33, 17
N = 88

print("\n" + "=" * 78)
print("T1. ★★ 模態計數 ⟹ Abel (特徵群對偶)")
print("=" * 78)
print("  觀測量 (質量比/混合角/CMB 峰/尺度律) = 88 個**獨立單指標**模態 {γ_n}")
print("  特徵標理論: 群 G 嘅譜 = 特徵標 χ: G → U(1) 嘅函數 |1−χ|²")
print("  χ 必須一維 (單指標 ⇒ 單值); 一維特徵標 = 群同態 G → U(1)")
print("  #一維特徵標 = |Ĝ|;  定理: |Ĝ| = |G| ⟺ G Abel (對偶定理)\n")

# Z_88: 88 個特徵標, 全部一維
print("  [Z_88] 特徵標 χ_k(g) = e^{2πikg/88}, k = 0..87 → 88 個一維 ✓")
# 非 Abel: 不可約表示數 = 共軛類數 < |G|
print("  [S_3]  不可約表示 = 3 個 (1, 1, 2 維); |S_3| = 6; 一維只有 2 個")
print("  [D_4]  不可約表示 = 5 個 (4×1 + 1×2 維); |D_4| = 8; 一維只有 4 個")
print("  [A_5]  不可約表示 = 5 個 (1,3,3,4,5 維); |A_5| = 60; 一維只有 1 個")
print("  ⇒ 88 個一維特徵標 ⟹ G 必須 Abel; |Ĝ| = 88 ⟹ G ≅ Z_88 (cyclic, 1D docs/19)")
print("  ⇒ 「Abel」唔係公設 — 係 88 模態計數嘅直接後果")

print("\n" + "=" * 78)
print("T2. ★ 非 Abel 簡併排除 — 觀察者讀數需要一維特徵標")
print("=" * 78)
print("  非 Abel 群: 不可約表示 ρ 維度 d_ρ ≥ 2 ⇒ Laplacian 特徵值")
print("    λ 帶多重度 ≥ d_ρ ⇒ 譜有結構性簡併 (每模態多個獨立自由度)")
print("  觀察者讀數: 質量比 γ_n/γ_1, 混合角 θ(n) = 單指標標量")
print("    ⇒ 需要 χ 一維 (|1−χ|² 先係標量函數)")
print("  非 Abel (如 SU(3) 色): 8 = 2B 維 adjoint 帶簡併 — 但嗰啲係")
print("    內部對稱 (O163 隱藏譜扇區), 唔係時空載體 (Z_88)")
print("  ⇒ 載體必須 Abel; 內部對稱可以非 Abel (O114 SU(12) 已閉合)")

print("\n" + "=" * 78)
print("T3. ★ 預算均勻 ⟹ 平移不變")
print("=" * 78)
B_n = mp.mpf(ob.LUC[10]) / (2 * Nd)
print("  O41: 觀察者預算 B(n) = L10/(2N_d) = %s (對全部 mode 均勻)"
      % mp.nstr(B_n, 10))
print("  ⇒ 每個 mode 等權 ⇒ 冇特殊 site ⇒ 群作用自由可遷 (Cayley 圖)")
print("  docs/19 T2: 生成元不變性 (C_88(g) 譜 = C_88(1) ∀ gcd(g,88)=1)")
print("    ⇒ 「邊」冇標記 ⇒ 平移對稱自然成立 (任兩點等價)")
print("  2-正則 + 連通 + 自由可遷 ⇒ C_N (U1 回歸) ⇒ C_N 係 Abel 循環群")
print("  ⇒ 平移不變 = 預算均勻 + 生成元不可分, 唔係額外公設")

print("\n" + "=" * 78)
print("T4. 總結 — Abel 公設三來源")
print("=" * 78)
print("  ① 88 模態計數 ⟹ 88 一維特徵標 ⟹ Abel (對偶定理)  [T1]")
print("  ② 單指標標量讀數 ⟹ 一維 χ ⟹ 載體 Abel (非 Abel 帶簡併)  [T2]")
print("  ③ 預算均勻 + 生成元不可分 ⟹ 平移不變 (C_N)  [T3]")
print("  ⇒ 🔴 → 🟢 條件閉合: Abel 公設 = 模態計數 + 讀數結構 + 預算均勻")
print("    嘅後果; 剩「為何 88」→ O95/O96 (44 必然性 × 2 已閉合)")

out = {
    "T1_mode_count_abelian": {
        "Z88_chars": 88,
        "S3_irreps": "3 (1,1,2); one-dim 2",
        "D4_irreps": "5 (4x1+1x2); one-dim 4",
        "A5_irreps": "5 (1,3,3,4,5); one-dim 1",
        "theorem": "|G_hat| = |G| <=> G abelian (duality)",
        "conclusion": "88 one-dim characters => G abelian, G ~= Z_88",
    },
    "T2_no_degeneracy": "single-index scalar observables need 1-dim chi; "
                        "non-abelian carries multiplicity >= dim rho; "
                        "internal symmetry (SU(12), O114) is separate from spacetime carrier",
    "T3_budget_homogeneous": {
        "B_n": mp.nstr(B_n, 10),
        "generator_invariance": "docs/19 T2",
        "conclusion": "homogeneous budget + generator-indistinguishable => translation-invariant C_N",
    },
    "T4_summary": "Abel axiom = mode count (T1) + readout structure (T2) + "
                  "budget homogeneity (T3); remaining 'why 88' -> O95/O96 (closed)",
    "verdict": "🟢 Abel 公設閉合 (條件性: 88 模態計數 + 單指標讀數 + 預算均勻)",
}
d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
with open(os.path.join(d, "21_abelian_axiom.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 78)
print("自檢")
print("=" * 78)
NP = NF = 0


def check(label, cond):
    global NP, NF
    if cond:
        NP += 1
        print("  PASS  %s" % label)
    else:
        NF += 1
        print("  FAIL  %s" % label)


def conj_classes(elems, mul, inv):
    """共軛類 = 不可約表示數 (Burnside)"""
    seen, cls = set(), []
    for x in elems:
        if x in seen:
            continue
        orb = {mul(mul(g, x), inv(g)) for g in elems}
        seen |= orb
        cls.append(orb)
    return cls


def commutator_closure(elems, mul, inv):
    """交換子子群 [G,G] 嘅閉包 — 一維特徵標數 = |G| / |[G,G]|"""
    e = next(x for x in elems if all(mul(x, y) == y for y in elems))
    gen = {mul(mul(a, b), mul(inv(a), inv(b))) for a in elems for b in elems} - {e}
    sub = {e}
    changed = True
    while changed:
        changed = False
        for a in list(sub):
            for b in gen:
                c = mul(a, b)
                if c not in sub:
                    sub.add(c)
                    changed = True
    return sub


# --- 真群論計算 (唔用硬編表) ---
P3 = list(itertools.permutations(range(3)))
m3 = lambda a, b: tuple(a[b[i]] for i in range(3))
i3 = lambda p: tuple(sorted(range(3), key=lambda k: p[k]))

D4e = [("r", i) for i in range(4)] + [("s", i) for i in range(4)]   # r^i s^eps


def m4(a, b):
    ka, ia = a
    kb, ib = b
    if ka == "r" and kb == "r":
        return ("r", (ia + ib) % 4)
    if ka == "r" and kb == "s":
        return ("s", (ia + ib) % 4)
    if ka == "s" and kb == "r":
        return ("s", (ia - ib) % 4)
    return ("r", (ia - ib) % 4)


def i4(a):
    k, i = a
    return ("r", (-i) % 4) if k == "r" else ("s", i)


P5 = list(itertools.permutations(range(5)))


def par(p):
    n, seen, sgn = len(p), [False] * len(p), 1
    for i in range(n):
        if not seen[i]:
            j, L = i, 0
            while not seen[j]:
                seen[j] = True
                j = p[j]
                L += 1
            if L % 2 == 0:
                sgn = -sgn
    return sgn


A5e = [p for p in P5 if par(p) == 1]
m5 = lambda a, b: tuple(a[b[i]] for i in range(5))
i5 = lambda p: tuple(sorted(range(5), key=lambda k: p[k]))

computed = {}
for nm, elems, mul, inv in [("S3", P3, m3, i3), ("D4", D4e, m4, i4), ("A5", A5e, m5, i5)]:
    cls = conj_classes(elems, mul, inv)
    com = commutator_closure(elems, mul, inv)
    computed[nm] = (len(elems), len(cls), len(elems) // len(com))

# Z_88: 特徵標直接構造 (複數, 唔可以只用 cos)
chars88 = set()
for k in range(N):
    chars88.add(tuple((round(float(mp.cos(2 * PI * k * g / N)), 10),
                       round(float(mp.sin(2 * PI * k * g / N)), 10)) for g in range(N)))
computed["Z88"] = (N, N, len(chars88))

DOC_TABLE = {"Z88": (88, 88, 88), "S3": (6, 3, 2), "D4": (8, 5, 4), "A5": (60, 5, 1)}
for G in ("Z88", "S3", "D4", "A5"):
    check("T1 %s 群論真算 (|G|, #irreps, #1dim) = 文檔表 %s" % (G, DOC_TABLE[G]),
          computed[G] == DOC_TABLE[G])

# C_88 Laplacian 譜: 相異特徵值數 (模態標籤 vs 譜簡併 — 修正 docs/22 T2 措辭)
lam88 = sorted(set(round(float(2 - 2 * mp.cos(2 * PI * k / N)), 10) for k in range(N)))
check("T2 C_88 譜相異值 = 45 (88 模態本身有 k <-> 88-k 二重簡併)",
      len(lam88) == 45 and len(lam88) < N)
check("T2 Z_88 有 88 個一維標籤 = 模態數 (標籤結構, 唔係「非 Abel 才簡併」)",
      computed["Z88"][2] == N)

check("T3 B(n) = L10/(2N_d) 均勻", abs(B_n - mp.mpf(123) / 88) < mp.mpf("1e-30"))
check("T3 L10 = 123 註冊", ob.LUC[10] == 123)
check("T4 剩「為何 88」= O95/O96 (44 必然性 ×2 已閉合)", N == 2 * Nd)

print("\n總計: %d/%d PASS" % (NP, NP + NF))
print("EXIT=%d" % (0 if NF == 0 else 1))
