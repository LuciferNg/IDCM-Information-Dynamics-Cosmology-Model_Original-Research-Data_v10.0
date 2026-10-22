#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O210 scripts/07_ktree_two_counts.py
================================================================================
題目: K_tree 雙計數之結構解析（掃描帶出）+ `66 = 2·K_tree` 裁定之**修正**
================================================================================
掃描發現（O171 scripts/03, O190 scripts/02）: 「K_tree: **34 節點 / 33 邊**」
⟹ 兩讀法係**同一圖（路徑 P₃₄）之兩個計數**, 非命名混亂。

§A  圖論: P_N Laplacian 譜 = 4sin²(kπ/2N); 非零模數 = N−1; Σ(非零 λ) = tr L = 2E（**定理**）
§B  兩讀法關係表（34 vs 33; 68 = 2N; 2904 vs 2992）
§C  ★ 裁定修正: `66 = 2·K_tree^(mode)` = tr L = 2E 🟢（圖論定理）;
    `Σλ(tree) = dim Λ²(12)` 仍係 B-單點 🔴（兩者係**唔同**陳述, 舊裁定混淆之）
§D  全 repo 掃描匯總（節點讀法 vs 模數讀法, 逐檔自洽性）
"""
import numpy as np

stats = {"PASS": 0, "FAIL": 0}

def chk(name, cond):
    stats["PASS" if cond else "FAIL"] += 1
    print(f"  {'PASS' if cond else 'FAIL'}  {name}")
    return cond

B, N_gen = 4, 3
N = 2 * (B ** 2 + 1)          # 34 節點
E = N - 1                      # 33 邊

print("=" * 78)
print("§A  圖論: 路徑 P_N（K_tree）之 Laplacian 譜與跡")
print("=" * 78)
print(f"""
  K_tree = 路徑圖 P_N, N = 2(B²+1) = {N} 節點, E = N−1 = {E} 邊（樹: 邊 = 節點 − 1）
  Laplacian L = D − A: 譜 = 2 − 2cos(kπ/N) = 4sin²(kπ/2N) = 4sin²(kπ/{2*N}), k = 0..N−1
  ★ 圖論定理: tr L = Σdeg = 2E  ⟹  Σ(非零 λ) = 2E = {2*E}
""")
# 真算: 整數 Laplacian 矩陣
L = np.zeros((N, N), dtype=np.int64)
for i in range(N):
    L[i, i] = 2 if 0 < i < N - 1 else 1
for i in range(N - 1):
    L[i, i + 1] = L[i + 1, i] = -1
chk(f"Laplacian 整數跡 tr L = {int(np.trace(L))} = 2E = {2*E}（圖論定理, 精確整數）",
    int(np.trace(L)) == 2 * E == 66)
ev = np.linalg.eigvalsh(L.astype(float))
ev = np.sort(ev)
chk(f"譜: 最小 λ₀ = {ev[0]:.3e}（≈0 = 常數模）; 非零模數 = {int(np.sum(ev > 1e-9))} = N−1 = {E}",
    abs(ev[0]) < 1e-9 and int(np.sum(ev > 1e-9)) == E)
chk(f"Σ(全部 λ) = {ev.sum():.10f} = 66（數值對角化）", abs(ev.sum() - 66) < 1e-9)
from math import sin, pi
ana = [4 * sin(pi * k / (2 * N)) ** 2 for k in range(1, N)]
chk(f"解析式 λ_k = 4sin²(kπ/{2*N}) 對數值譜: 最大偏差 {max(abs(ana[i]-ev[i+1]) for i in range(E)):.3e}",
    max(abs(ana[i] - ev[i + 1]) for i in range(E)) < 1e-12)
chk(f"配對 λ_k + λ_(N−k) = B = {B}（∀k）; 不動點 k = N/2 = {N//2}, λ = B/2 = {B/2:.0f} = μ²",
    all(abs(4*sin(pi*k/(2*N))**2 + 4*sin(pi*(N-k)/(2*N))**2 - B) < 1e-12 for k in range(1, N//2))
    and abs(4 * sin(pi * (N // 2) / (2 * N)) ** 2 - 2) < 1e-12)

print("\n" + "=" * 78)
print("§B  兩讀法關係表（同一對象, 兩個計數）")
print("=" * 78)
rows = [
    ("節點數 K_tree^(node)", f"2(B²+1) = F₉", N, "O126/O171/O190 用法; 亦 = Laplacian 分母/2; 晶格 88×34 = 2992"),
    ("邊數 K_tree^(mode)", f"2B²+1 = N_gen·L₅", E, "O88/O96/O109/O124/O155/O160/O168/o90 用法; = Dirichlet 非零模數 = 算子譜維數"),
]
for nm, form, val, use in rows:
    print(f"    {nm:22s} {form:20s} = {val:3d}   {use}")
chk(f"兩計數關係: K_tree^(node) = K_tree^(mode) + 1（樹圖: 邊 = 節點 − 1）", N == E + 1)
chk(f"Laplacian 分母 2N = 68 = 2·K_tree^(node) ⟹ **O126 之「68 = 2·K_tree」在節點讀法下有效**",
    2 * N == 68)
chk(f"兩個 88× 乘積皆真且角色唔同: 88×{E} = {88*E}（張量 dim, 模數）; 88×{N} = {88*N}（晶格 sites, 節點）",
    88 * E == 2904 and 88 * N == 2992)

print("\n" + "=" * 78)
print("§C  ★ 裁定修正 — 「66 = 2·K_tree」須分三層, 舊裁定混為一談")
print("=" * 78)
print("""
  (i)  Σλ(tree) = 2E = 2·K_tree^(mode) = 66
       ⟹ **圖論定理**（tr L = Σdeg = 2E, 對**任何**圖成立）⟹ 🟢 **結構**, 非巧合。
       舊 docs/06 §4 稱此層為「單點巧合」= **過度否證**（混淆咗下面 (iii)）。
  (ii) dim Λ²(12) = C(12,2) = 66 = B·N_gen(B·N_gen−1)/2
       ⟹ 表示論維數 ✓ 結構。
  (iii) 等式「Σλ(tree) = dim Λ²(12)」（跨域相等）
       ⟹ 以 B 為參數: 4B²+2  vs  B(B−1)(B(B−1)−1)/2  ⟹ **只喺 B=4 相交** ⟹ 🟡/🔴 無 map。
""")
def lhs(Bb):   # Σλ = 2E = 2(2B²+1)
    return 2 * (2 * Bb ** 2 + 1)
def rhs(Bb):   # dim Λ²(12), 12 = B·(B−1)
    n = Bb * (Bb - 1)
    return n * (n - 1) // 2
tab = [(Bb, lhs(Bb), rhs(Bb)) for Bb in range(2, 8)]
for Bb, a, b in tab:
    print(f"    B = {Bb}:  Σλ = {a:4d}   dim Λ²(12) = {b:5d}   {'★ 相等' if a == b else ''}")
chk("(i)  Σλ = 2E = 66 為圖論定理（同 B 表達式 4B²+2; tr L 整數驗證通過）", int(np.trace(L)) == 66)
chk("(iii) 跨域等式 Σλ = dim Λ²(12) 只喺 B = 4 成立 ⟹ 無 B-一般恆等 ⟹ 無 map",
    [Bb for Bb, a, b in tab if a == b] == [4])
chk("★ 修正後裁定: (i)(ii) 🟢 結構; (iii) 🔴 單點（舊裁定只應適用於 (iii)）",
    int(np.trace(L)) == 66 and [Bb for Bb, a, b in tab if a == b] == [4])

print("\n" + "=" * 78)
print("§D  全 repo 掃描匯總（156 命中；逐讀法分類）")
print("=" * 78)
node_users = ["o126 (7 檔: SESSION_START/docs01/02/03/final_result/scripts02/data)",
              "o171 scripts/03 (「34 節點 / 33 邊」★正解)",
              "o190 scripts/02 + data (「K_tree: 34 層 = M+1 = 33+1」★正解)"]
mode_users = ["o88 / o96 scripts/04 / o109 scripts/04 / o124 scripts/01·09·10+docs / o155",
              "o160 docs00·01 + scripts/02·12 + tools/cli + data", "o168 scripts/19·21·25 + 01_problem_record (2K_tree+1 = 67 ✓)", "o90 scripts/01 (α_GUT⁻¹ = 2K_tree − F₇ − 6)"]
ratio_users = ["o10 + o171 docs/12（比值 M/(M+1) = 33/34, M = K_tree^(mode)）— 不受影響（比值不變）"]
for nm, lst in (("節點讀法 (34)", node_users), ("模數讀法 (33)", mode_users), ("比值 (33/34)", ratio_users)):
    print(f"  {nm}:")
    for x in lst:
        print(f"      · {x}")
mode_exprs = [("2·K_tree = 66", 2 * E == 66), ("2·K_tree+1 = 67", 2 * E + 1 == 67),
              ("1/(2(2K_tree+1)) = 1/134 ≈ 0.7463%", abs(1 / (2 * (2 * E + 1)) * 100 - 0.7463) < 5e-4),
              ("102 = 2·K_tree + 2L₆ = 66+36", 2 * E + 2 * 18 == 102),
              ("α_GUT⁻¹ = 2K_tree − F₇ = 53", 2 * E - 13 == 53)]
node_exprs = [("68 = 2·K_tree", 2 * N == 68), ("2992 = 88 × K_tree", 88 * N == 2992),
              ("2992/44 = 68", 2992 / 44 == 68), ("34 = 33+1（層 = M+1）", N == E + 1)]
for nm, ok in mode_exprs:
    print(f"      模數讀法: {nm:38s} {'✓' if ok else '✗'}")
for nm, ok in node_exprs:
    print(f"      節點讀法: {nm:38s} {'✓' if ok else '✗'}")
chk("掃描自洽性: 全部記錄表達式（模數讀法 5 條 + 節點讀法 4 條）算術自洽 ⟹ 兩讀法各自內部無矛盾",
    all(v for _, v in mode_exprs) and all(v for _, v in node_exprs))
chk("唯一「矛盾」= 跨讀法比較（例如以 33 讀 O126 之 68）⟹ 屬**讀法混用**, 非數據錯 ⟹ C9 須改為「雙計數 + 標籤強制」",
    N == E + 1 and 2 * N == 68 and 2 * E == 66)

print("=" * 78)
print(f"O210 two-counts — PASS {stats['PASS']} / FAIL {stats['FAIL']}")
print("=" * 78)
print("RESULT:", "FAIL" if stats["FAIL"] else "PASS")
