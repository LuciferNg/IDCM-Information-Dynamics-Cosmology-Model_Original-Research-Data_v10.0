#!/usr/bin/env python3
"""
06_node_clusters.py — 60 節點聚類方向分析
==========================================
60 節點 (冷斑 A5 軌道) 雖然冇完整旋轉對稱,
但可能喺特定方向有聚類 (對應某啲特殊軸)。

方法: 每個節點 i, 計其他 59 個節點到佢嘅距離分佈,
睇有冇「對稱聚類」— 例如 5 個節點等距圍繞。
"""
import numpy as np, math
from collections import Counter

print("=" * 66)
print("O1: 60 節點聚類方向分析")
print("=" * 66)

nodes = []
with open("../cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
vecs = np.array([np.array([math.cos(math.radians(d))*math.cos(math.radians(r)),
                           math.cos(math.radians(d))*math.sin(math.radians(r)),
                           math.sin(math.radians(d))]) for r, d in nodes])

# 冷斑 (節點 0) 到其他節點距離
dists0 = [math.degrees(math.acos(np.clip(np.dot(vecs[0], vecs[j]), -1, 1))) for j in range(1, 60)]
dists0 = sorted(dists0)
print(f"\n冷斑 (節點 0) 到其他 59 節點距離:")
print(f"  最短: {dists0[:6]}")
print(f"  最長: {dists0[-4:]}")
print(f"  中位: {dists0[29]:.2f}°")

# 距離直方圖 (2° bins)
print(f"\n距離直方圖 (bins=2°):")
bins = np.arange(0, 181, 2)
hist, _ = np.histogram(dists0, bins=bins)
for i, h in enumerate(hist):
    if h > 0:
        bar = '#' * h
        print(f"  {bins[i]:3d}-{bins[i+1]:3d}°: {h:2d} {bar}")

# 聚類檢測: 5 個節點等距?
print(f"\n等距聚類檢測 (5-fold 結構?):")
counts = Counter(round(d, 1) for d in dists0)
for dist, cnt in sorted(counts.items()):
    if cnt >= 4:
        print(f"  {dist}°: {cnt} 個節點 {'★' if cnt==5 else ''}")

# 關鍵: 冷斑 + 5 個等距鄰居 = 5-fold 對稱?
print(f"\n冷斑附近嘅 5 重結構:")
# 最近 10 個距離
recent = sorted(enumerate(dists0), key=lambda x: x[1])[:10]
for idx, d in recent:
    print(f"  節點 {idx+1}: {d:.3f}°")
