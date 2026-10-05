#!/usr/bin/env python3
"""
O53 方向①: J* vs curve volumes 分析
=======================================
J* 36D → curve volumes (tip) 185 個值
檢查: J* 嘅 36 個分量 同 curve volumes 有冇 φ 結構?
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 70)
print("O53: J* vs curve volumes")
print("=" * 70)

with open(os.path.join(BASE, 'Jstar_36D.json')) as f:
    jstar = json.load(f)
J0 = np.array(jstar['Jstar_36D'])
print(f"[1] J* (36D):")
print(f"  min = {J0.min():.6f}, max = {J0.max():.6f}")
print(f"  values: {J0}")

# J* 嘅 φ 結構
print(f"\n[2] J* 分量 vs φ^n:")
for i, v in enumerate(J0):
    if v > 0:
        n = round(math.log(v) / math.log(phi))
        dist = abs(math.log(v) / math.log(phi) - n)
        marker = "★" if dist < 0.05 else ""
        print(f"  J*[{i}] = {v:.6f} → ln(v)/lnφ = {math.log(v)/math.log(phi):7.3f}, n = {n}, Δ = {dist:.3f} {marker}")

# J* 嘅 1/12 格點結構
print(f"\n[3] J* 分量 vs 1/12 格點 (q = -ln(J*)/2π):")
qs = []
for v in J0:
    if v > 0:
        q = -math.log(v) / (2 * math.pi)
        qs.append(q)
qs = np.array(qs)
print(f"  q ∈ [{qs.min():.3f}, {qs.max():.3f}]")
m12 = np.round(qs * 12)
dist12 = np.abs(qs - m12 / 12)
print(f"  q·12 近整數: mean|Δ| = {dist12.mean():.4f}")
print(f"  m 分佈: {np.bincount(m12.astype(int).clip(0, 20))}")

# 隨機對照
rng = np.random.default_rng(11)
dist_rand = []
for _ in range(1000):
    qr = rng.uniform(qs.min(), qs.max(), len(qs))
    mr = np.round(qr * 12)
    dist_rand.append(np.abs(qr - mr / 12).mean())
dist_rand = np.array(dist_rand)
print(f"  隨機 mean|Δ| = {dist_rand.mean():.4f} ± {dist_rand.std():.4f}")
z = (dist12.mean() - dist_rand.mean()) / dist_rand.std()
print(f"  z = {z:.2f}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)