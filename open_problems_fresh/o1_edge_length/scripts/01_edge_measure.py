#!/usr/bin/env python3
"""
01_edge_measure.py — 精確邊長測量 (全部 60 節點)
==================================================
測量成個網絡嘅最近鄰距離分佈, 確認邊長一致性。
"""
import numpy as np, math
from collections import Counter

print("=" * 66)
print("新O1: 邊長精確測量 (60 節點全網絡)")
print("=" * 66)

# 載入節點
nodes = []
with open("../cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
vecs = np.array([np.array([math.cos(math.radians(d))*math.cos(math.radians(r)),
                           math.cos(math.radians(d))*math.sin(math.radians(r)),
                           math.sin(math.radians(d))]) for r, d in nodes])
print(f"節點數: {len(vecs)}")

# 全部節點對距離
print("\n計算全部 60×59/2 = 1770 對距離...")
dists = []
for i in range(60):
    for j in range(i+1, 60):
        d = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        dists.append(d)
dists = np.array(dists)

# 最近鄰距離 (每個節點嘅最小距離)
print("\n每個節點最近鄰距離:")
nn = []
for i in range(60):
    dmin = 180
    for j in range(60):
        if i == j: continue
        d = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if d < dmin: dmin = d
    nn.append(dmin)
nn = np.array(nn)
print(f"  min = {nn.min():.6f}°")
print(f"  max = {nn.max():.6f}°")
print(f"  mean = {nn.mean():.6f}° ± {nn.std():.6f}°")
print(f"  唯一值: {sorted(set(round(v, 4) for v in nn))}")

# 全部距離直方圖 (搵主要峰)
print("\n距離直方圖 (0.5° bins, 顯示主要峰):")
bins = np.arange(0, 181, 0.5)
hist, edges = np.histogram(dists, bins=bins)
# 搵峰 (局部最大)
peaks = []
for i in range(1, len(hist)-1):
    if hist[i] > 0 and hist[i] >= hist[i-1] and hist[i] >= hist[i+1]:
        peaks.append((edges[i], hist[i]))
# 排序 by count
peaks.sort(key=lambda x: -x[1])
print(f"主要峰 (count > 3):")
for edge, cnt in peaks[:12]:
    if cnt > 3:
        print(f"  {edge:.1f}°: {cnt} 對")

# 精確峰位置: 26.09° 附近嘅值
print("\n26.09° 附近精確值:")
near = sorted([d for d in dists if 25 < d < 28])
for d in near[:10]:
    print(f"  {d:.6f}°")
print(f"  總數: {len(near)}")

# 儲存
with open("data/edge_distribution.txt", "w") as f:
    f.write(f"nn_min={nn.min():.6f} nn_max={nn.max():.6f} nn_mean={nn.mean():.6f}\n")
    f.write(f"nn_unique={sorted(set(round(v,4) for v in nn))}\n")
    f.write(f"near_26={len(near)}\n")
    for d in sorted(set(round(v, 6) for v in nn)):
        f.write(f"nn={d:.6f}\n")
print("\n✅ 已存: data/edge_distribution.txt")
