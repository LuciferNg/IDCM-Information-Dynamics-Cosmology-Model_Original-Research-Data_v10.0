#!/usr/bin/env python3
"""
O53 A1: block 譜本徵值 1/3 結構 vs c_f
==========================================
Block 0 譜: 3.67, 0.333, 0.166, 0.110...
0.333 ≈ 1/3, 0.166 ≈ 1/6 — 1/3 倍數!

測試: block 本徵值同 c_f 有冇對應?
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53: block 譜 1/3 結構")
print("=" * 70)

with open(os.path.join(BASE, 'cy36_98_intersection_full.json')) as f:
    ct = json.load(f)
K = np.array(ct['kappa'])

with open(os.path.join(BASE, 'Jstar_36D.json')) as f:
    jstar = json.load(f)
J0 = np.array(jstar['Jstar_36D'])

Y = np.einsum('ijk,k->ij', K, J0)
Y = (Y + Y.T) / 2

blocks = [(0,12), (12,24), (24,36)]

# 收集所有 block 本徵值
all_evals = []
for bi, (a, b) in enumerate(blocks):
    B = Y[a:b, a:b]
    ev = np.linalg.eigvalsh(B)
    all_evals.append(ev)

# 檢查每個本徵值離 1/3 格點 (n/3) 幾近
print("[1] 每個 block 本徵值 vs n/3 格點:")
for bi, ev in enumerate(all_evals):
    ev_sorted = np.sort(ev)[::-1]
    for e in ev_sorted:
        # 最近 n/3
        n = round(e * 3)
        dist = abs(e - n/3)
        marker = "★" if dist < 0.05 else ""
        print(f"  Block {bi}: λ = {e:8.4f} → n/3 = {n}/3 ({n/3:.4f}), Δ = {dist:.4f} {marker}")

# 統計: 有幾多本徵值近 n/3 (Δ < 0.05)?
print(f"\n[2] 統計:")
total = 0
near = 0
for ev in all_evals:
    for e in ev:
        total += 1
        n = round(e * 3)
        if abs(e - n/3) < 0.05:
            near += 1
print(f"  近 n/3 (Δ<0.05): {near}/{total}")

# 隨機對照
rng = np.random.default_rng(1)
near_random = 0
for _ in range(1000):
    e = rng.normal(0, 1)
    n = round(e * 3)
    if abs(e - n/3) < 0.05:
        near_random += 1
print(f"  隨機 (1000 次): {near_random}/1000 = {near_random/10:.1f}%")
print(f"  觀測: {near/total*100:.1f}%")

# 3×12 block 嘅 su(12) 對角化?
# su(12) 有 11 個 Cartan — block 12×12 本徵值應該有結構
print(f"\n[3] 每個 block 12 個本徵值:")
for bi, ev in enumerate(all_evals):
    ev_sorted = np.sort(ev)[::-1]
    # 正本徵值數
    n_pos = sum(1 for e in ev_sorted if e > 0)
    n_neg = sum(1 for e in ev_sorted if e < 0)
    print(f"  Block {bi}: +{n_pos} 正 / -{n_neg} 負, 最大 {ev_sorted[0]:.4f}, 最小 {ev_sorted[-1]:.4f}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)