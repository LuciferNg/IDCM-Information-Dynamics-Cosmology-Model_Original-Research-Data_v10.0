#!/usr/bin/env python3
"""
O53: 用 CYTools 真 κ 重新分析 — λ₁ / tr(Y²) / block 結構
=============================================================
之前閉合基於 kappa_36d_raw.json (可能有問題)
而家用 CYTools 完整 intersection numbers 重做
"""
import os, json, math, sys
import numpy as np
from scipy.linalg import schur

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 70)
print("O53: CYTools 真 κ 完整分析")
print("=" * 70)

# CYTools κ (36³)
with open(os.path.join(BASE, 'cy36_98_intersection_full.json')) as f:
    ct = json.load(f)
K_ct = np.array(ct['kappa'])
print(f"CYTools κ: {K_ct.shape}, nnz = {np.count_nonzero(K_ct)}")

# J* (36D)
with open(os.path.join(BASE, 'Jstar_36D.json')) as f:
    jstar = json.load(f)
J0 = np.array(jstar['Jstar_36D'])

# --- [1] Y = κ_ijk·J*^k ---
Y = np.einsum('ijk,k->ij', K_ct, J0)
Y = (Y + Y.T) / 2
ev = np.linalg.eigvalsh(Y)
ev_sorted = np.sort(ev)[::-1]
print(f"\n[1] Y = κ·J* 譜 (36):")
print(f"  λ₁ = {ev_sorted[0]:.6f}")
print(f"  λ₂ = {ev_sorted[1]:.6f}")
print(f"  λ₃ = {ev_sorted[2]:.6f}")
print(f"  φ^(1/3) = {phi**(1/3):.6f}")
print(f"  誤差 = {abs(ev_sorted[0]-phi**(1/3))/phi**(1/3)*100:.2f}%")

# 有冇任何 λ 接近 φ^(1/3)?
closest = min(ev_sorted, key=lambda x: abs(x - phi**(1/3)))
print(f"  最接近 φ^(1/3) 嘅 λ: {closest:.6f} (誤差 {abs(closest-phi**(1/3))/phi**(1/3)*100:.2f}%)")

# --- [2] tr(Y²) ---
trY2 = np.trace(Y @ Y)
print(f"\n[2] tr(Y²) = {trY2:.4f}")
print(f"  5 = B+1: 誤差 {abs(trY2-5)/5*100:.2f}%")

# --- [3] 用 tip 做對照 (stretched cone tip) ---
with open(os.path.join(BASE, 'cy36_98_cytools_kappa.json')) as f:
    ck = json.load(f)
tip = np.array(ck['tip'])
# tip 係 32D, κ matrix 係 32×32 — 唔同 basis (divisor basis)
# 呢度用 36D 版本: 需要重新計算 tip 喺 36D? 跳過, 用 J* 為主

# --- [4] block 結構 (3×12) ---
print(f"\n[4] 3×12 block 結構 (CYTools κ):")
blocks = [(0,12), (12,24), (24,36)]
Yb = Y
for bi, (a, b) in enumerate(blocks):
    for bj, (c, d) in enumerate(blocks):
        if bi < bj:
            B = Yb[a:b, c:d]
            print(f"  block ({bi},{bj}): ||B|| = {np.linalg.norm(B):.4f}")
# 對角 block 譜
for bi, (a, b) in enumerate(blocks):
    evb = np.linalg.eigvalsh(Yb[a:b, a:b])
    print(f"  block {bi} λ_max = {evb[-1]:.4f}, λ_min = {evb[0]:.4f}")

# --- [5] Schur 分解 ---
print(f"\n[5] Schur 分解 (3×12 可約化?):")
T, Q = schur(Y, output='real')
# 檢查 3×12 block 下三角
tri_blocks = []
for bi in range(3):
    for bj in range(bi):
        a, b = blocks[bi]
        c, d = blocks[bj]
        tri_blocks.append(np.linalg.norm(T[a:b, c:d]))
print(f"  下三角 block norms: {[f'{x:.2e}' for x in tri_blocks]}")

# --- [6] 對比舊 κ 分析 ---
with open(os.path.join(BASE, 'kappa_36d_raw.json')) as f:
    old = json.load(f)
K_old = np.zeros(tuple(old['shape']))
for key, val in old['kappa'].items():
    i, j, k = map(int, key.split(','))
    K_old[i, j, k] = val
    K_old[i, k, j] = val
    K_old[j, i, k] = val
    K_old[j, k, i] = val
    K_old[k, i, j] = val
    K_old[k, j, i] = val
Y_old = np.einsum('ijk,k->ij', K_old, J0)
Y_old = (Y_old + Y_old.T) / 2
ev_old = np.linalg.eigvalsh(Y_old)
ev_old_sorted = np.sort(ev_old)[::-1]
print(f"\n[6] 舊 κ 對比:")
print(f"  舊 λ₁ = {ev_old_sorted[0]:.6f} (φ^(1/3) = {phi**(1/3):.6f}, 誤差 {abs(ev_old_sorted[0]-phi**(1/3))/phi**(1/3)*100:.2f}%)")
print(f"  舊 tr(Y²) = {np.trace(Y_old @ Y_old):.4f}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)