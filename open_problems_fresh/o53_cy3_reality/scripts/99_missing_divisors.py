#!/usr/bin/env python3
"""
O53 重大發現: 缺失 5 divisors [0,3,4,7,8] 身份分析
=====================================================
1. 呢 5 個 divisor 對應邊啲 GLSM fields / polytope points?
2. 5 = B+1 = φ³-φ⁻³+1?
3. 12-5 = 7 有咩意義?
4. 缺 5 個全喺 Block 0 → Block 0 只有 7 個 independent divisors
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53: 缺失 divisors [0,3,4,7,8] 身份")
print("=" * 70)

with open(os.path.join(BASE, 'cy36_98_sage_export.json')) as f:
    sage = json.load(f)
pts = np.array(sage['points'])
print(f"polytope points: {pts.shape}")

# 每個 point 對應 divisor index (0-based)
missing = [0, 3, 4, 7, 8]
print(f"\n缺失 divisors: {missing}")
print(f"對應 polytope points:")
for m in missing:
    print(f"  divisor {m} (point {m}): {pts[m]}")

# 特別檢查: 邊啲係 interior points?
# (0,0,0,0) 係 origin, (1,1,0,0) 係 interior
print(f"\n特別 points:")
print(f"  point 0 = {pts[0]} (origin / interior?)")
print(f"  point 8 = {pts[8]} (interior?)")

# GLSM 數據
glsm_fields = sage.get('glsm', None)
if glsm_fields is not None:
    print(f"\nGLSM fields: {len(glsm_fields)}")

# 統計: 缺失 vs 非缺失 divisor 嘅 κ 強度
with open(os.path.join(BASE, 'cy36_98_intersection_full.json')) as f:
    ct = json.load(f)
K = np.array(ct['kappa'])
div_strength = np.abs(K).sum(axis=(1, 2))
print(f"\n缺失 divisors 強度:")
for m in missing:
    print(f"  divisor {m}: {div_strength[m]:8.1f}")
print(f"非缺失 (均值): {np.mean([div_strength[i] for i in range(36) if i not in missing]):.1f}")

# 5 = B+1?
B = 4
print(f"\n5 = B+1 = {B+1} ✅ (K_Chain 邊界數+1)")
print(f"12-5 = 7 (Block 0 淨 independent divisors)")
print(f"7 = F₆? = {13-6} ... 定 L₄ = {4+3}?")

# 36-5 = 31? 32-5 = 27?
print(f"\n32 = Kähler dim")
print(f"36-32 = 4 = B")
print(f"32+4 = 36 = Nd-2B+2B = Nd")
print(f"32 = Nd - 2B + 2B - 4 = Nd - 4?")
print(f"  Nd = 44, 44-4 = 40 ≠ 32")
print(f"  但 36 = h11, 36-4 = 32 ✅ (h11 - 4 = dim Kähler)")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)