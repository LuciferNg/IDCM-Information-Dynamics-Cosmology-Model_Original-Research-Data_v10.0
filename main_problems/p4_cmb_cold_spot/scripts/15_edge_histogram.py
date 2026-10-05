#!/usr/bin/env python3
"""
圖身份 — 邊長直方圖分析 (搵真正邊長)
======================================
之前用 d_min×1.05 當閾值可能太鬆 (捕捉咗非邊嘅對角線)
正確方法: 睇角距離直方圖, 第一個峰 = 邊長
"""
import numpy as np
import math
from collections import defaultdict, deque

nodes = []
with open("data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))

vecs = []
for ra, dec in nodes:
    r, d = math.radians(ra), math.radians(dec)
    vecs.append(np.array([math.cos(d)*math.cos(r),
                          math.cos(d)*math.sin(r),
                          math.sin(d)]))
vecs = np.array(vecs)

# 全部兩兩距離
dists = []
for i in range(60):
    for j in range(i+1, 60):
        dot = np.clip(np.dot(vecs[i], vecs[j]), -1, 1)
        dists.append(math.degrees(math.acos(dot)))
dists = np.array(dists)

print("=" * 66)
print("角距離直方圖 (搵真正邊長)")
print("=" * 66)
print(f"最小: {dists.min():.4f}°")
print(f"排序前 20:")
sorted_d = np.sort(dists)
for i in range(20):
    print(f"  {sorted_d[i]:.4f}°")

# 搵距離 gap (第一個大 gap = 邊/非邊邊界)
print(f"\n距離間隙 (前 15):")
gaps = np.diff(sorted_d)
for i in range(15):
    print(f"  {sorted_d[i]:.3f} → {sorted_d[i+1]:.3f}  (gap {gaps[i]:.4f})")

# 自動搵閾值: 第一個 gap > 中位數 gap × 3
median_gap = np.median(gaps)
print(f"\n中位數 gap: {median_gap:.4f}")
threshold = None
for i in range(len(gaps)):
    if gaps[i] > median_gap * 5:
        threshold = (sorted_d[i] + sorted_d[i+1]) / 2
        print(f"閾值 @ {sorted_d[i]:.3f}° (gap {gaps[i]:.4f} = {gaps[i]/median_gap:.1f}× median)")
        break

if threshold is None:
    # fallback: 用第一個峰
    hist, edges = np.histogram(dists, bins=100)
    peak_bin = np.argmax(hist)
    threshold = edges[peak_bin+1]
    print(f"直方圖峰 @ {edges[peak_bin]:.2f}-{edges[peak_bin+1]:.2f}°")

# 用 threshold 重建圖
print(f"\n用閾值 {threshold:.3f}° 重建圖:")
adj = defaultdict(set)
edges_list = []
for i in range(60):
    for j in range(i+1, 60):
        if math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) < threshold:
            adj[i].add(j)
            adj[j].add(i)
            edges_list.append((i, j))

V = 60
E = len(edges_list)
degrees = defaultdict(int)
for i in range(60):
    degrees[len(adj[i])] += 1
print(f"邊 E = {E}")
print(f"度數分佈: {dict(degrees)}")
print(f"Euler F = {2 - V + E}")
