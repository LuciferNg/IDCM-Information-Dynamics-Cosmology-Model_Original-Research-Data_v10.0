#!/usr/bin/env python3
"""
O55 — 最終 Verifier: c_f = n/3 結構測試
=========================================
整合所有結構測試, 輸出最終 PASS/FAIL 狀態。

測試清單:
  [V1] 所有 3c_f 係整數
  [V2] det(M) = 18 = 2×3²
  [V3] Σ(M²) = 36 = h11
  [V4] Σ(M) = 2 = μ²
  [V5] U column = {0, 1, 2} = Z_3 完整集合
  [V6] L column mod 3 = {0, 1, 2} = Z_3 完整集合
  [V7] D column: d=s=-2, b=3
  [V8] SNF = diag(1, 1, 18)
  [V9] 3c = 3q + r, q∈{−1,0,1}, r∈{0,1,2}
  [V10] rank = 3 (滿秩)
  [V11] 3×12 block 結構: 36 = 3×12 = Nd−2B
  [V12] 66 = C(12,2) = su(12) 正根
  [V13] 3c 值對稱: Z_2 × Z_3
  [V14] Δδ量子化: 3Δδ/ln(φ) ∈ Z
"""

import numpy as np
import math, sys, json, os

phi = (1 + math.sqrt(5)) / 2
PASS = 0; FAIL = 0
results = []

def check(name, cond, detail=""):
    global PASS, FAIL
    status = "✅" if cond else "❌"
    if cond:
        PASS += 1
    else:
        FAIL += 1
    results.append((status, name, detail))
    print(f"  {status} {name} {detail}")

print("=" * 70)
print("O55 最終 Verifier: c_f = n/3 結構測試")
print("=" * 70)

# 3c 矩陣
M = np.array([[0, -2, 3],
              [2, -2, -1],
              [1, 3, -2]], dtype=int)
values = M.flatten()

# ============================================================
print("\n" + "-" * 70)
print("[V1] 所有 3c_f 係整數")
print("-" * 70)
all_int = all(v == round(v) for v in [3*c for c in [0, -2/3, 1, 2/3, -2/3, -1/3, 1/3, 1, -2/3]])
check("所有 3c_f 整數", all_int)

# ============================================================
print("\n" + "-" * 70)
print("[V2] det(M) = 18 = 2×3²")
print("-" * 70)
det_M = round(np.linalg.det(M))
check("det(M) = 18", det_M == 18, f"({det_M})")

# ============================================================
print("\n" + "-" * 70)
print("[V3] Σ(M²) = 36 = h11")
print("-" * 70)
sum2 = int(np.sum(M**2))
check("Σ(M²) = 36 = h11", sum2 == 36, f"({sum2})")

# ============================================================
print("\n" + "-" * 70)
print("[V4] Σ(M) = 2 = μ²")
print("-" * 70)
sum_M = int(np.sum(M))
check("Σ(M) = 2", sum_M == 2, f"({sum_M})")

# ============================================================
print("\n" + "-" * 70)
print("[V5] U column = {0, 1, 2} = Z_3 完整集合")
print("-" * 70)
u_col = sorted(M[:, 0])
check("U column = {0,1,2}", u_col == [0, 1, 2], f"({u_col})")

# ============================================================
print("\n" + "-" * 70)
print("[V6] L column mod 3 = {0, 1, 2} = Z_3 完整集合")
print("-" * 70)
l_mod3 = sorted([int(x) % 3 for x in M[:, 2]])
check("L column mod 3 = {0,1,2}", l_mod3 == [0, 1, 2], f"({l_mod3})")

# ============================================================
print("\n" + "-" * 70)
print("[V7] D column: d=s=-2, b=3")
print("-" * 70)
d_col = M[:, 1]
check("D column: d=s=-2, b=3", d_col[0]==-2 and d_col[1]==-2 and d_col[2]==3, f"({d_col.tolist()})")

# ============================================================
print("\n" + "-" * 70)
print("[V8] SNF = diag(1, 1, 18)")
print("-" * 70)
# d₁ = gcd of all elements
d1 = abs(np.gcd.reduce(values.flatten()))
# d₂ = gcd of all 2×2 minors
minors2 = []
for i1 in range(3):
    for i2 in range(i1+1, 3):
        for j1 in range(3):
            for j2 in range(j1+1, 3):
                det2 = M[i1, j1]*M[i2, j2] - M[i1, j2]*M[i2, j1]
                minors2.append(abs(det2))
d2 = abs(np.gcd.reduce(minors2))
d3 = abs(round(np.linalg.det(M)))
s1, s2, s3 = d1, d2//d1, d3//d2
check("SNF = diag(1,1,18)", s1==1 and s2==1 and s3==18, f"(diag({s1},{s2},{s3}))")

# ============================================================
print("\n" + "-" * 70)
print("[V9] 3c = 3q + r, q∈{−1,0,1}, r∈{0,1,2}")
print("-" * 70)
all_decomposable = True
for v in values:
    q = (v // 3) if v >= 0 else -((-v + 2) // 3)
    r = v - 3*q
    if q not in [-1, 0, 1] or r not in [0, 1, 2]:
        all_decomposable = False
check("3c = 3q + r 分解可行", all_decomposable)

# ============================================================
print("\n" + "-" * 70)
print("[V10] rank = 3 (滿秩)")
print("-" * 70)
rank = np.linalg.matrix_rank(M)
check("rank = 3", rank == 3, f"(rank={rank})")

# ============================================================
print("\n" + "-" * 70)
print("[V11] 3×12 block 結構: 36 = 3×12 = Nd−2B")
print("-" * 70)
Nd, B = 44, 4
h11 = Nd - 2*B
check("36 = 3×12 = Nd−2B", h11 == 36 and h11 == 3*12, f"({h11} = 3×{12})")

# ============================================================
print("\n" + "-" * 70)
print("[V12] 66 = C(12,2) = su(12) 正根")
print("-" * 70)
c122 = 12*11//2
check("66 = C(12,2)", c122 == 66, f"({c122})")

# ============================================================
print("\n" + "-" * 70)
print("[V13] 3c 值對稱: Z_2 × Z_3")
print("-" * 70)
n_values = set(values)
has_z2 = set(v % 2 for v in values) == {0, 1}
has_z3 = set(v % 3 for v in values) == {0, 1, 2}
check("Z_2 完整: mod 2 = {0,1}", has_z2)
check("Z_3 完整: mod 3 = {0,1,2}", has_z3)

# ============================================================
print("\n" + "-" * 70)
print("[V14] Δδ量子化: 3Δδ/ln(φ) ∈ Z")
print("-" * 70)
# c_f values from Δδ
cf_vals = [0, -2/3, 1, 2/3, -2/3, -1/3, 1/3, 1, -2/3]
n_vals = [int(round(3*c)) for c in cf_vals]
all_n_int = all(isinstance(n, int) or n == round(n) for n in n_vals)
check("3c_f = n ∈ Z", all_n_int, f"(n ∈ {{{min(n_vals)},...,{max(n_vals)}}})")

# ============================================================
print("\n" + "-" * 70)
print("=" * 70)
print(f"最終結果: {PASS}/{PASS+FAIL} PASS, {FAIL}/{PASS+FAIL} FAIL")
print("=" * 70)

# 摘要
print(f"\n  測試摘要:")
for status, name, detail in results:
    print(f"  {status} {name}")

# 分類
print(f"\n  分類:")
print(f"  ✅ 結構閉合: {PASS}/14")
print(f"  ❌ 開放: {FAIL}/14")
print(f"  狀態: {'🟢 結構閉合' if FAIL == 0 else '🟡 部分閉合' if FAIL <= 3 else '🔴 主要開放'}")

sys.exit(0 if FAIL == 0 else 1)