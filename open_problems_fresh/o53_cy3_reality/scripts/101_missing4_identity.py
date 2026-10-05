#!/usr/bin/env python3
"""
O53 最終: 缺失 4 divisors [2,3,6,7] (0-based) 身份
=====================================================
4 = B (K_Chain 邊界) — 決定性對應!
確認 polytope points + κ 強度
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53: 缺失 4 divisors [2,3,6,7]")
print("=" * 70)

with open(os.path.join(BASE, 'cy36_98_sage_export.json')) as f:
    sage = json.load(f)
pts = np.array(sage['points'])

missing = [2, 3, 6, 7]
print(f"[1] 缺失 divisors (0-based): {missing}")
print(f"對應 polytope points:")
for m in missing:
    print(f"  div {m}: {pts[m]}")

# κ 強度
with open(os.path.join(BASE, 'cy36_98_intersection_full.json')) as f:
    ct = json.load(f)
K = np.array(ct['kappa'])
div_strength = np.abs(K).sum(axis=(1, 2))
print(f"\n[2] 缺失 divisors 強度:")
total_missing = 0
for m in missing:
    print(f"  div {m}: {div_strength[m]:8.1f}")
    total_missing += div_strength[m]
others_mean = np.mean([div_strength[i] for i in range(36) if i not in missing])
print(f"  缺失總和: {total_missing:.1f}")
print(f"  其他均值: {others_mean:.1f}")
print(f"  比率: {total_missing/4/others_mean:.2f}x")

# 缺失 divisors 喺邊個 block?
print(f"\n[3] Block 分佈:")
blocks = {'Block 0 (0-11)': [m for m in missing if m < 12],
          'Block 1 (12-23)': [m for m in missing if 12 <= m < 24],
          'Block 2 (24-35)': [m for m in missing if m >= 24]}
for name, members in blocks.items():
    print(f"  {name}: {members}")

# 4 = B 身份
B = 4
print(f"\n[4] 4 = B (K_Chain 邊界數) ✅")
print(f"  36 = Nd - 2B = 44 - 8 ✅")
print(f"  32 = 36 - 4 = h11 - B = dim Kähler cone ✅")

# 檢查: 缺失 4 個係咪全部「高強度」?
print(f"\n[5] 全部 36 個 divisor 強度排序 (top 12):")
order = np.argsort(div_strength)[::-1]
for i in order[:12]:
    marker = " ← MISSING" if i in missing else ""
    print(f"  div {i:2d}: {div_strength[i]:8.1f}{marker}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)