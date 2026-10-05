#!/usr/bin/env python3
"""
O53: 對比 CYTools κ vs κ_36d_raw.json
=========================================
兩個 κ 差別 → 之前閉合係咪有效?
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53: κ 對比")
print("=" * 70)

# CYTools κ
with open(os.path.join(BASE, 'cy36_98_intersection_full.json')) as f:
    ct = json.load(f)
K_ct = np.array(ct['kappa'])
print(f"CYTools κ: {K_ct.shape}, nnz = {np.count_nonzero(K_ct)}")

# 舊 κ
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
print(f"舊 κ: {K_old.shape}, nnz = {np.count_nonzero(K_old)}")

# 數值對比
print(f"\n數值對比 (非零 entries):")
ct_entries = set()
for i in range(36):
    for j in range(36):
        for k in range(36):
            if abs(K_ct[i,j,k]) > 1e-6:
                ct_entries.add((i,j,k))
old_entries = set()
for i in range(36):
    for j in range(36):
        for k in range(36):
            if abs(K_old[i,j,k]) > 1e-6:
                old_entries.add((i,j,k))
print(f"  CYTools entries: {len(ct_entries)}")
print(f"  舊 entries: {len(old_entries)}")
print(f"  共同: {len(ct_entries & old_entries)}")
print(f"  只喺 CYTools: {len(ct_entries - old_entries)}")
print(f"  只喺舊: {len(old_entries - ct_entries)}")

# 共同 entries 嘅值比較
common = ct_entries & old_entries
vals_ct = [K_ct[e] for e in common]
vals_old = [K_old[e] for e in common]
arr_ct = np.array(vals_ct)
arr_old = np.array(vals_old)
if len(common) > 0:
    diff = np.abs(arr_ct - arr_old)
    print(f"\n共同 {len(common)} entries:")
    print(f"  CYTools: mean={arr_ct.mean():.2f}, std={arr_ct.std():.2f}")
    print(f"  舊: mean={arr_old.mean():.2f}, std={arr_old.std():.2f}")
    print(f"  diff: mean={diff.mean():.4f}, max={diff.max():.4f}")
    print(f"  完全一樣: {np.sum(diff < 1e-6)}/{len(common)}")
    # 比例
    ratio = arr_ct / np.where(arr_old != 0, arr_old, 1)
    print(f"  ratio: mean={ratio.mean():.3f}, std={ratio.std():.3f}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)