#!/usr/bin/env python3
"""
O53 方向①: curve volumes + divisor volumes 分析
====================================================
curve volumes: [277, 97, 5, 1, 140, 5, 66, 51, 3, 3, 197, 22, 44, 282, 67, 1, ...]
divisor volumes: 混合大細值

測試: 有冇 φ 結構?
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 70)
print("O53: curve/divisor volumes φ 分析")
print("=" * 70)

# curve volumes (從上一個 script 輸出)
cv = [277, 97, 5, 1, 140, 5, 66, 51, 3, 3, 197, 22, 44, 282, 67, 1, 1, 120, 16, 5, 1, 44, 5, 1, 82, 13, 5, 1, 10, 1, 76, 31, 41, 9, 1, 3, 3, 1, 12, 54, 1, 2, 1, 2, 3, 2, 1, 1, 2, 4, 158, 7, 4, 1, 1, 26, 907, 2, 59, 4, 89, 4, 1, 1, 71, 53, 30, 54, 1, 57, 1, 3, 55, 12, 912, 63, 1, 25, 63, 1, 1, 7, 66, 7, 48, 52, 155, 1, 2, 2, 5, 7, 113, 62, 2, 42, 45, 1, 53, 15, 1, 15, 106, 67, 160, 39, 1, 43, 61, 45, 3, 3, 1, 1, 67, 27, 3, 146, 1, 8, 24, 4, 4, 158, 2, 188, 2, 52, 2, 28, 2, 6, 63, 210, 3, 15, 1, 9, 12, 1, 10, 2, 26, 2, 2, 7, 57, 3, 1, 2, 3, 67, 99, 59, 1, 165, 27, 1, 1, 27, 1, 1, 27, 9, 66, 1, 112, 2, 2, 1, 47, 10, 2, 3, 280, 1, 2, 2, 2, 12, 2, 53, 5, 4, 7]
cv = np.array(cv)
print(f"curve volumes: {len(cv)} 個")
print(f"  範圍: [{cv.min()}, {cv.max()}]")
print(f"  mean: {cv.mean():.1f}, median: {np.median(cv):.0f}")
print(f"  1 嘅數量: {(cv == 1).sum()} ({(cv==1).mean()*100:.0f}%)")

# φ 結構: cv 值 = φ^n?
print(f"\n[1] curve volumes vs φ^n:")
for v in sorted(set(cv))[:20]:
    # ln(v)/ln(φ) 近整數?
    n = round(math.log(v) / math.log(phi))
    dist = abs(math.log(v) / math.log(phi) - n)
    marker = "★" if dist < 0.05 else ""
    print(f"  v={v:4d}: ln(v)/lnφ = {math.log(v)/math.log(phi):7.3f}, n={n}, Δ={dist:.3f} {marker}")

# 統計
ns = []
for v in cv:
    if v > 0:
        ns.append(round(math.log(v) / math.log(phi)))
ns = np.array(ns)
near_int = sum(1 for v in cv if v > 0 and abs(math.log(v)/math.log(phi) - round(math.log(v)/math.log(phi))) < 0.05)
print(f"\n近整數 (Δ<0.05): {near_int}/{len(cv)} = {near_int/len(cv)*100:.1f}%")

# 隨機對照
rng = np.random.default_rng(3)
vals = cv[cv > 0]
near_rand = 0
for _ in range(len(vals)):
    v = rng.integers(1, 1000)
    if abs(math.log(v)/math.log(phi) - round(math.log(v)/math.log(phi))) < 0.05:
        near_rand += 1
print(f"隨機 (1-1000): {near_rand}/{len(vals)} = {near_rand/len(vals)*100:.1f}%")

# 但 curve volumes 係 tip 依賴 (J 縮放) — 冇 invariant 意義
print(f"\n[2] 重要: curve volumes 依賴 tip 選擇 (唔係 invariant)")
print(f"  只有 GW/GV invariants 先係拓撲不變量")
print(f"  → curve volumes 唔可以直接同 φ 比")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)