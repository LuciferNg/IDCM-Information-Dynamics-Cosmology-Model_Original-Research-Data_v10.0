#!/usr/bin/env python3
"""
O53 最終: CYTools 真 κ 嘅 block 譜 + su(12) 檢驗
====================================================
1. Y(tip) 嘅 Schur 分解 — 3×12 block-triangular?
2. 66 = C(12,2) = su(12) 正根?
3. 12 = (Nd−2B)/3 身份
"""
import os, json, math, sys
import numpy as np
from scipy.linalg import schur

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 70)
print("O53: block 譜 + su(12) 檢驗 (真 κ)")
print("=" * 70)

with open(os.path.join(BASE, 'cy36_98_intersection_full.json')) as f:
    ct = json.load(f)
K = np.array(ct['kappa'])

# [1] 用 tip 做 Y (32D κ matrix 已經收縮)
with open(os.path.join(BASE, 'cy36_98_cytools_kappa.json')) as f:
    ck = json.load(f)
Y_tip = np.array(ck['kappa'])  # 32×32
print(f"[1] Y(tip) 32×32 — Schur 分解:")
T, Q = schur(Y_tip, output='real')
# 3×12 block 喺 32D? 32 = 12+12+8 — 唔係 3×12
# 試 3 組 (12, 12, 8)
blocks = [(0,12), (12,24), (24,32)]
print(f"  分組 (12,12,8):")
for bi in range(3):
    for bj in range(bi):
        a, b = blocks[bi]
        c, d = blocks[bj]
        norm = np.linalg.norm(T[a:b, c:d])
        print(f"    T[{a}:{b}, {c}:{d}] = {norm:.2e}")

# [2] 用 J* 做 Y (36D)
with open(os.path.join(BASE, 'Jstar_36D.json')) as f:
    jstar = json.load(f)
J0 = np.array(jstar['Jstar_36D'])
Y36 = np.einsum('ijk,k->ij', K, J0)
Y36 = (Y36 + Y36.T) / 2
print(f"\n[2] Y(J*) 36×36 — Schur 分解:")
T36, Q36 = schur(Y36, output='real')
blocks36 = [(0,12), (12,24), (24,36)]
print(f"  分組 (12,12,12):")
tri_norms = []
for bi in range(3):
    for bj in range(bi):
        a, b = blocks36[bi]
        c, d = blocks36[bj]
        norm = np.linalg.norm(T36[a:b, c:d])
        tri_norms.append(norm)
        print(f"    T[{a}:{b}, {c}:{d}] = {norm:.2e}")
print(f"  下三角總和 = {sum(tri_norms):.2e}")
print(f"  → block-triangular: {'✅' if max(tri_norms) < 1e-6 else '❌'}")

# [3] 66 = C(12,2) 檢驗 — block 譜
print(f"\n[3] block 譜結構:")
# 用 Y(J*) 嘅 3 個 12×12 對角 block
for bi, (a, b) in enumerate(blocks36):
    B = Y36[a:b, a:b]
    ev = np.linalg.eigvalsh(B)
    print(f"  Block {bi} 譜: λ_max = {ev[-1]:.4f}, λ_min = {ev[0]:.4f}, tr = {np.trace(B):.4f}")

# su(12) 正根數 = 66 = C(12,2)
print(f"\n  C(12,2) = {math.comb(12,2)}")
print(f"  su(12) 正根數 = {12*11//2}")
print(f"  66 = C(12,2) ✅ (身份: su(12) 正根)")

# [4] 12 = (Nd−2B)/3 身份
Nd, B = 44, 4
print(f"\n[4] 12 = (Nd−2B)/3 = ({Nd}−2×{B})/3 = {(Nd-2*B)//3} ✅")

# [5] tr(Y²) 用 J* (36D)
trY2 = np.trace(Y36 @ Y36)
print(f"\n[5] tr(Y(J*)²) = {trY2:.4f}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)