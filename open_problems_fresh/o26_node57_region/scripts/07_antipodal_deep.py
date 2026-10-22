#!/usr/bin/env python3
"""
07_antipodal_deep.py — O26 理論: 對徑映射嘅真正本質
====================================================
發現: 對徑映射唔係單一 A₅ 元素, 但係圖自同構 (0 邊違反, hop 對稱 60/60)。

問題: 呢個「近似反演」點解完美保持邊?

檢查:
1. 每節點對徑誤差 ε_i = 180° − angle(v_i, v_antip(i)) — 常數定變數?
2. g*_i = g_antip(i)·g_i⁻¹ 分佈 — 係咪集中喺特定子集?
3. 對徑伴侶置換 π 喺群元素層面嘅結構
4. 節點集係咪「近似中心對稱」— -v_i 距離最近節點幾遠?
5. 圖自同構嘅根源: 邊緣保持係咪因為 ε 細?
"""
import numpy as np
import math
from collections import Counter, defaultdict

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"

# ============ A₅ 群 (同 06) ============
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
print(f"A₅ 群: {len(group)} 元素")

# ============ 節點 ============
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

# 每節點嘅群元素
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

print("\n=== 1. 對徑誤差 ε_i = 180° − angle(v_i, v_antip) ===")
eps = []
for i in range(60):
    a = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[ap[i]]), -1, 1)))
    eps.append(180 - a)
eps = np.array(eps)
print(f"  ε: mean={eps.mean():.3f}° std={eps.std():.3f} min={eps.min():.3f} max={eps.max():.3f}")
print(f"  ε 分佈: {sorted(set(np.round(eps, 2)))[:10]}...")
# 睇下 ε 係咪得幾個值
print(f"  獨特值: {len(set(np.round(eps, 2)))}")

print("\n=== 2. -v_i 嘅最近 orbit 點距離 ===")
d_neg = []
for i in range(60):
    vn = -vecs[i]
    ds = [math.degrees(math.acos(np.clip(np.dot(vn, vecs[j]), -1, 1))) for j in range(60) if j != i]
    d_neg.append(min(ds))
d_neg = np.array(d_neg)
print(f"  angle(-v_i, 最近節點): mean={d_neg.mean():.3f}° std={d_neg.std():.3f} min={d_neg.min():.3f} max={d_neg.max():.3f}")
print(f"  → 對徑伴侶距離 180°−ε = {180-eps.mean():.3f}° mean")

print("\n=== 3. g*_i = g_antip(i)·g_i⁻¹ 分佈 ===")
# 逆元素
g_inv = {}
for k, M in enumerate(group):
    for k2, M2 in enumerate(group):
        if np.allclose(np.dot(M, M2), np.eye(3), atol=1e-8):
            g_inv[k] = k2; break
gstar_angles = []
gstar_idx = []
for i in range(60):
    gs = np.dot(group[g_of[ap[i]]], group[g_inv[g_of[i]]])
    ang = math.degrees(math.acos(max(-1, min(1, (np.trace(gs)-1)/2))))
    gstar_angles.append(round(ang))
    found = None
    for k, M in enumerate(group):
        if np.allclose(M, gs, atol=1e-6):
            found = k; break
    gstar_idx.append(found)
print(f"  g* 旋轉角分佈: {dict(sorted(Counter(gstar_angles).items()))}")
print(f"  g* 獨特元素數: {len(set(gstar_idx))}")
# 每個 g* 元素用幾多次
cnt_g = Counter(gstar_idx)
print(f"  最常用 g*: {cnt_g.most_common(5)}")

print("\n=== 4. 對徑伴侶嘅 hop 結構 ===")
# hop
adj = [set() for _ in range(60)]
for i in range(60):
    for j in range(60):
        if i != j and math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) < 28:
            adj[i].add(j)
hop = [0]*60
from collections import deque
q = deque([0])
while q:
    u = q.popleft()
    for v in adj[u]:
        if hop[v] == 0 and v != 0:
            hop[v] = hop[u]+1; q.append(v)
# hop 層內嘅對徑結構
for h in range(9):
    layer = [i for i in range(60) if hop[i] == h]
    aps = [ap[i] for i in layer]
    aps_hop = Counter(hop[a] for a in aps)
    print(f"  hop={h} ({len(layer)}節點) → 對徑 hop 分佈: {dict(sorted(aps_hop.items()))}")

print("\n=== 5. 邊緣保持嘅幾何解釋 ===")
# 對徑對嘅邊緣: i~j (angle<28°) → antip(i)~antip(j)?
viol = 0
max_sep = 0
for i in range(60):
    for j in adj[i]:
        if j > i:
            a, b = ap[i], ap[j]
            sep = math.degrees(math.acos(np.clip(np.dot(vecs[a], vecs[b]), -1, 1)))
            if sep >= 28:
                viol += 1
            max_sep = max(max_sep, sep)
print(f"  邊緣違反 (antip 距離 ≥28°): {viol}")
print(f"  antip 邊緣最大距離: {max_sep:.3f}° (邊緣閾值 28°)")
# 對徑後嘅「邊緣長度」分佈
lens = []
for i in range(60):
    for j in adj[i]:
        if j > i:
            a, b = ap[i], ap[j]
            lens.append(math.degrees(math.acos(np.clip(np.dot(vecs[a], vecs[b]), -1, 1))))
lens = np.array(lens)
print(f"  antip 邊緣長度: mean={lens.mean():.3f}° std={lens.std():.3f} min={lens.min():.3f} max={lens.max():.3f}")
print(f"  (原圖邊緣 26.09°, 閾值 28°)")
# 26.09 同 28 之間有冇空隙?
print(f"  → 如果 antip 邊緣 max < 28 但原圖邊緣 = 26.09, 中間有 {28-lens.max():.3f}° 安全距離")
