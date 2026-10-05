#!/usr/bin/env python3
"""
O53: block 結構細節 — 邊個 divisor 主導 + 譜結構
====================================================
block (0,0,0) = 5209 特別大 — 檢查邊個 divisor 貢獻
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53: block 結構細節")
print("=" * 70)

with open(os.path.join(BASE, 'cy36_98_intersection_full.json')) as f:
    ct = json.load(f)
K = np.array(ct['kappa'])

# 每個 divisor 嘅總強度
print("[1] 每個 divisor 嘅 |κ| 總和:")
div_strength = np.abs(K).sum(axis=(1, 2))
order = np.argsort(div_strength)[::-1]
for i in order[:12]:
    print(f"  divisor {i:2d}: {div_strength[i]:8.1f}")
print(f"  ...")
for i in order[-5:]:
    print(f"  divisor {i:2d}: {div_strength[i]:8.1f}")

# block (0,0,0) 內部: 邊啲 divisor 主導?
print(f"\n[2] block (0,0,0) 內部強度分佈 (前 10):")
entries = []
for i in range(12):
    for j in range(12):
        for k in range(12):
            if abs(K[i,j,k]) > 0:
                entries.append((abs(K[i,j,k]), i, j, k))
entries.sort(reverse=True)
for val, i, j, k in entries[:10]:
    print(f"  K[{i},{j},{k}] = {K[i,j,k]:8.0f}")

# 檢查: block (0,0,0) 強度主要來自邊個 divisor?
print(f"\n[3] block (0,0,0) 各 divisor 貢獻:")
sub = K[0:12, 0:12, 0:12]
d_contrib = np.abs(sub).sum(axis=(1, 2))
for i in np.argsort(d_contrib)[::-1]:
    print(f"  divisor {i}: {d_contrib[i]:8.1f}")

# 同 offset 9 分組對比
print(f"\n[4] offset 9 分組 (9-20, 21-32, 33-8):")
perm = [(9 + i) % 36 for i in range(36)]
Kp = K[np.ix_(perm, perm, perm)]
blocks = [(0,12), (12,24), (24,36)]
for bi, (a, b) in enumerate(blocks):
    for bj, (c, d) in enumerate(blocks):
        for bk, (e, f) in enumerate(blocks):
            if bi == bj == bk:
                s = np.abs(Kp[a:b, c:d, e:f]).sum()
                nnz = np.count_nonzero(Kp[a:b, c:d, e:f])
                print(f"  block ({bi},{bj},{bk}): |Σ| = {s:8.2f}, nnz = {nnz}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)