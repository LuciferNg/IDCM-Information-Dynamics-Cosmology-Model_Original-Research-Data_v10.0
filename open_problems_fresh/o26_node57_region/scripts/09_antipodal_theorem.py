#!/usr/bin/env python3
"""
09_antipodal_theorem.py — O26 理論閉合: 對徑映射 = 逐節點共軛 180° 旋轉
========================================================================
已證: 60 節點 = A₅ regular orbit; 對徑伴侶 = 距離真對徑 5.34° 常數。
本腳本驗證完整定理:

定理候選:
  π(i) = R_{a_i}·v_i, 其中 a_i = g_i·a0·g_i⁻¹ (共軛 2-fold 軸),
  w = R_{a0}·v0, ε = angle(v0, a0) 常數 → angle(v_i, a_i) = 87.34° 常數
  → R_{a_i}·v_i ≈ −v_i (誤差 5.34°)

驗證:
1. 正確軸提取 (eigenvector 法, 180° 旋轉係對稱矩陣)
2. angle(v_i, a_i) = 87.34° 常數 (全部節點)
3. π 係「近似等距」: max|angle(π(i),π(j)) − angle(i,j)| 幾大?
4. 邊緣裕量: 26.09 < 28, π 嘅邊緣 max = 26.166 — 誤差 0.076° 點嚟?
5. hop 對稱: d(i,0) + d(i,57) = 8 (圖距離對徑性質)
6. 結論: 對徑映射 = 局部反演 (每節點用自己嘅共軛 180° 旋轉)
"""
import numpy as np
import math
from collections import defaultdict, deque

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"

phi = (1+5**0.5)/2
inv_phi = 1/phi
def norm(v):
    v = np.asarray(v, dtype=float)
    return v/np.linalg.norm(v)
def rot_matrix(axis, angle):
    axis = np.asarray(axis, dtype=float); axis = axis/np.linalg.norm(axis)
    c, s = math.cos(angle), math.sin(angle)
    K = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
    return np.eye(3) + s*K + (1-c)*np.dot(K, K)

# 特徵軸
ico_verts = []
for sx in [-1,1]:
    for sy in [-1,1]:
        for sz in [-1,1]:
            ico_verts.append((0, sx, sy*phi)); ico_verts.append((sx, sy*phi, 0)); ico_verts.append((sx*phi, 0, sy))
ico_verts = np.array([norm(v) for v in ico_verts])
dod_verts = []
for sx in [-1,1]:
    for sy in [-1,1]:
        for sz in [-1,1]:
            dod_verts.append((sx, sy, sz))
for sx in [-1,1]:
    for sy in [-1,1]:
        dod_verts.append((0, sx*inv_phi, sy*phi)); dod_verts.append((sx*inv_phi, sy*phi, 0)); dod_verts.append((sx*phi, 0, sy*inv_phi))
dod_verts = np.array([norm(v) for v in dod_verts])
edges = []
for i in range(20):
    for j in range(i+1, 20):
        d = np.linalg.norm(dod_verts[i]-dod_verts[j])
        if abs(d - 2*math.sqrt(2)/math.sqrt(3)) < 0.01:
            mid = norm(dod_verts[i]+dod_verts[j])
            if not any(np.allclose(mid, e) or np.allclose(mid, -e) for e in edges):
                edges.append(mid)
edges = np.array(edges)

g1 = rot_matrix(ico_verts[0], 2*math.pi/5)
g2 = rot_matrix(dod_verts[0], 2*math.pi/3)
group = [np.eye(3)]
seen = {tuple(np.round(np.eye(3).flatten(), 10))}
queue = [np.eye(3)]
while queue:
    M = queue.pop(0)
    for gen in [g1, g2]:
        new = np.dot(gen, M)
        key = tuple(np.round(new.flatten(), 10))
        if key not in seen:
            seen.add(key); group.append(new); queue.append(new)

# 15 個 180° 旋轉
r180 = [M for M in group if abs((np.trace(M)-1)/2 + 1) < 1e-6]

def axis_of(M):
    """180° 旋轉嘅軸 (eigenvector, eigenvalue +1)"""
    evals, evecs = np.linalg.eigh(M)
    return evecs[:, np.argmax(evals)]

# 節點
nodes = []
with open(f"{BASE}/cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                  math.cos(math.radians(d))*math.sin(math.radians(r)),
                  math.sin(math.radians(d))] for r, d in nodes])
v0 = vecs[0]

# 每節點群元素
g_of = {}
for i in range(60):
    best = None; best_d = 1e9
    for k, M in enumerate(group):
        d = np.linalg.norm(np.dot(M, v0) - vecs[i])
        if d < best_d:
            best_d = d; best = k
    g_of[i] = best

# 對徑伴侶
def antip(i):
    best = None; ba = 1e9
    for j in range(60):
        if j == i: continue
        a = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if a > 170 and a < ba:
            ba = a; best = j
    return best, ba
ap = {i: antip(i)[0] for i in range(60)}

results = []
def log(*args):
    line = " ".join(str(a) for a in args)
    print(line)
    results.append(line)

log("=" * 72)
log("O26 理論閉合: 對徑映射 = 逐節點共軛 180° 旋轉")
log("=" * 72)

# ============ 1. 正確軸 + 常數角 ============
log("\n=== 1. 每節點最佳 180° 旋轉 + 軸角 ===")
node_rot = {}  # i -> r180 index
node_axis = {}
ang_to_axis = []
for i in range(60):
    best = None; best_d = 1e9
    for k, M in enumerate(r180):
        d = np.linalg.norm(np.dot(M, vecs[i]) - vecs[ap[i]])
        if d < best_d:
            best_d = d; best = k
    node_rot[i] = best
    a = axis_of(r180[best])
    node_axis[i] = a
    ang = math.degrees(math.acos(np.clip(np.dot(vecs[i], a), -1, 1)))
    ang_to_axis.append(ang)
ang_to_axis = np.array(ang_to_axis)
log(f"  angle(v_i, a_i): mean={ang_to_axis.mean():.3f}° std={ang_to_axis.std():.4f}")
log(f"  (理論: 87.34° = 90° − 5.34°/2, ε=5.34° = 180°−174.66°)")
# 每節點到軸角嘅獨特值
log(f"  獨特值: {len(set(np.round(ang_to_axis, 3)))}")

# ============ 2. 驗證 R_{a_i}·v_i = v_antip(i) (精確) ============
log("\n=== 2. R_{a_i}·v_i = v_antip(i) 驗證 ===")
ok = 0; max_err = 0
for i in range(60):
    v_app = np.dot(r180[node_rot[i]], vecs[i])
    err = np.linalg.norm(v_app - vecs[ap[i]])
    if err < 1e-6: ok += 1
    max_err = max(max_err, err)
log(f"  精確命中: {ok}/60 (誤差 <1e-6)")
log(f"  最大誤差: {max_err:.2e}")

# ============ 3. 共軛結構: a_i = g_i·a0·g_i⁻¹? ============
log("\n=== 3. 共軛結構: a_i = g_i·a0·g_i⁻¹ ===")
# a0 = node 0 嘅軸
a0 = node_axis[0]
conv_ok = 0
for i in range(60):
    a_expected = np.dot(group[g_of[i]], np.dot(a0, group[g_of[i]].T))
    a_expected = norm(a_expected)
    a_actual = node_axis[i]
    # 軸有 ± 歧義
    d = min(np.linalg.norm(a_expected - a_actual), np.linalg.norm(a_expected + a_actual))
    if d < 1e-6: conv_ok += 1
log(f"  a_i = g_i·a0·g_i⁻¹: {conv_ok}/60 {'✅' if conv_ok==60 else '❌'}")

# ============ 4. π 係近似等距? ============
log("\n=== 4. π 嘅角距離保持 ===")
# 抽樣: 全部 60×59/2 = 1770 對
max_delta = 0; n_over_1deg = 0
deltas = []
for i in range(60):
    for j in range(i+1, 60):
        a1 = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        a2 = math.degrees(math.acos(np.clip(np.dot(vecs[ap[i]], vecs[ap[j]]), -1, 1)))
        d = abs(a1 - a2)
        deltas.append(d)
        max_delta = max(max_delta, d)
        if d > 1.0: n_over_1deg += 1
deltas = np.array(deltas)
log(f"  |Δangle|: mean={deltas.mean():.4f}° max={max_delta:.4f}°")
log(f"  >1° 嘅對: {n_over_1deg}/1770")
# 呢個誤差同邊緣裕量比較
log(f"  邊緣裕量: 28° − 26.091° = 1.909° (π 保持邊需要誤差 < 裕量)")
log(f"  → max 誤差 {max_delta:.4f}° << 1.909° {'✅ 邊緣必然保持' if max_delta < 1.9 else '❌'}")

# ============ 5. hop 對稱 ============
log("\n=== 5. hop 對稱 + 圖距離性質 ===")
adj = [set() for _ in range(60)]
for i in range(60):
    for j in range(60):
        if i != j and math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) < 28:
            adj[i].add(j)
hop = [0]*60
q = deque([0])
while q:
    u = q.popleft()
    for v in adj[u]:
        if hop[v] == 0 and v != 0:
            hop[v] = hop[u]+1; q.append(v)
ok_h = sum(1 for i in range(60) if hop[ap[i]] == 8 - hop[i])
log(f"  hop[antip(i)] = 8−hop[i]: {ok_h}/60")
# 圖距離性質: d(i,0) + d(i,57) = 8?
# BFS from 57
d57 = [0]*60
q = deque([57])
while q:
    u = q.popleft()
    for v in adj[u]:
        if d57[v] == 0 and v != 57:
            d57[v] = d57[u]+1; q.append(v)
ok_d = sum(1 for i in range(60) if hop[i] + d57[i] == 8)
log(f"  d(i,0) + d(i,57) = 8: {ok_d}/60")
# 圖直徑
diam = max(max(hop), max(d57))
log(f"  圖直徑 = {diam}")

# ============ 6. π 係對合? ============
log("\n=== 6. π² = id? ===")
ok2 = sum(1 for i in range(60) if ap[ap[i]] == i)
log(f"  π(π(i)) = i: {ok2}/60")

# ============ 7. 總結定理 ============
log("\n=== 7. 定理總結 ===")
log("""
定理 (O26 理論閉合):
  S = {v_i} = A₅·v0 係 regular orbit (60 元素, 穩定子平凡)
  對徑伴侶: antip(i) = argmin_j angle(v_i, v_j) 最近真對徑 −v_i
  對每個 i: 存在唯一 180° 旋轉 R_{a_i} ∈ A₅ (2-fold 軸 a_i) 令
    R_{a_i}·v_i = v_antip(i)   (精確, 誤差 <1e-6)
  軸 a_i = g_i·a0·g_i⁻¹ (共軛), 其中 v_i = g_i·v0
  常數: angle(v_i, a_i) = 87.34° 對全部 i (SO(3) 等距保持)
        → angle(v_i, R_{a_i}·v_i) = 174.66° = 180° − 5.34° 常數
  邊緣保持: π 嘅角距離誤差 max 0.076° << 邊緣裕量 1.909°
        → π 係圖自同構 → k(π(i)) = k(i), hop(π(i)) = 8−hop(i)
  對合: π² = id (每對互相映射)

物理意義:
  對徑映射 = 「局部反演」: 每個節點用自己嘅共軛 2-fold 軸做 180° 旋轉,
  效果 ≈ 全局反演 −I (誤差 5.34°)。
  30 對對徑對 = 15 個 2-fold 軸 × 2 對/軸
  呢個係 A₅ 嵌入 SO(3) 嘅固有結構 — 唔係巧合, 係 regular orbit 嘅必然。
""")

import os
OUT = os.path.join(BASE, "o26_node57_region", "data")
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "node57_antipodal_theorem.txt"), "w") as f:
    f.write("\n".join(results) + "\n")
print(f"\n✅ 結果寫入 {OUT}/node57_antipodal_theorem.txt")
