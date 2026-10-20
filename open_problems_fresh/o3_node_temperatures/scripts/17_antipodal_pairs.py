#!/usr/bin/env python3
"""
17_antipodal_pairs.py — 高緯度 4 節點對徑對結構驗證
====================================================
發現: #10↔#25 同 #22↔#32 都係 174.66° (近對徑), 同色
問題: 呢個係 A₅ 幾何強制, 定係巧合?

檢查:
1. 60 節點中所有近對徑對 (角距離 >170°)
2. 佢哋嘅色 (應該全部同色? 因為 hop 對徑 parity)
3. 高緯度 4 節點嘅對徑對 vs 全部對徑對
4. 旋轉不變性: 呢啲對徑對係咪 orbit 固有
"""
import numpy as np
import math
from collections import defaultdict, deque

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"

nodes = []
with open(f"{BASE}/cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                  math.cos(math.radians(d))*math.sin(math.radians(r)),
                  math.sin(math.radians(d))] for r, d in nodes])

# 著色 + hop
adj = defaultdict(set)
for i in range(60):
    for j in range(i+1, 60):
        if math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) < 28.0:
            adj[i].add(j); adj[j].add(i)
color = {0: 1}; q = deque([0])
while q:
    u = q.popleft()
    for w in adj[u]:
        if w not in color:
            color[w] = 1 - color[u]; q.append(w)
hop = {0: 0}; q = deque([0])
while q:
    u = q.popleft()
    for w in adj[u]:
        if w not in hop:
            hop[w] = hop[u] + 1; q.append(w)

print("=== 全部近對徑對 (角距離 > 170°) ===")
pairs = []
for i in range(60):
    for j in range(i+1, 60):
        ang = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if ang > 170:
            pairs.append((ang, i, j))
pairs.sort(reverse=True)
print(f"共 {len(pairs)} 對 >170°:")
for ang, i, j in pairs:
    same = "同色" if color[i] == color[j] else "異色"
    hi = "🟢高緯" if abs(np.degrees(np.arcsin(vecs[i,2]))) >= 20 or abs(np.degrees(np.arcsin(vecs[j,2]))) >= 20 else ""
    print(f"  #{i}↔#{j}: {ang:.2f}°  hop={hop[i]}/{hop[j]}  {same} {hi}")

print()
print("=== 所有 hop 對徑 (BFS 距離 8) ===")
for i in range(60):
    if hop[i] == 8:
        print(f"  #{i} 對徑節點, hop=8")

print()
print("=== 冷斑 (0) 嘅對徑 = #57 ===")
ang57 = math.degrees(math.acos(np.clip(np.dot(vecs[0], vecs[57]), -1, 1)))
print(f"  角距離: {ang57:.2f}°")

print()
print("=== 高緯度 4 節點: 對徑關係 ===")
HIGH4 = [10, 22, 25, 32]
for i in HIGH4:
    # 搵最近對徑
    best = None; best_ang = 1e9
    for j in range(60):
        if j == i: continue
        ang = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if 170 < ang < best_ang:
            best_ang = ang; best = j
    print(f"  #{i} (b={np.degrees(np.arcsin(vecs[i,2])):+.1f}) 對徑→ #{best} (b={np.degrees(np.arcsin(vecs[best,2])):+.1f}), {best_ang:.2f}°, 色={'同' if color[i]==color[best] else '異'}")
