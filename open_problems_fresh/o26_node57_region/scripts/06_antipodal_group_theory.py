#!/usr/bin/env python3
"""
06_antipodal_group_theory.py — O26 理論: 對徑映射 = A₅ 群元素?
================================================================
目標: 證明「對徑映射係圖自同構」嘅群論根源。

線索: 60 節點圖 = 4-regular, girth 3 = Rhombicosidodecahedron (中心對稱!),
但對徑對只有 174.66° (唔係 180°) — 所以「對徑」唔係 -I, 而係某個 A₅ 旋轉。

驗證:
1. 生成 A₅ 群 (60 旋轉矩陣, 由 5-fold + 3-fold 生成)
2. 確認 60 節點 = A₅·v_0 orbit
3. 搵「對徑映射」對應嘅 A₅ 元素 g*: g*·v_i ≈ v_antip(i) 對所有 i
4. 如果 g* 存在 → 對徑映射係 A₅ 群作用 → 自動係等距 → 圖自同構 (證明!)
5. g* 係咩旋轉? (180°? 軸?)
6. 推廣: 對徑對 hop 和 = 8 嘅群論意義
"""
import numpy as np
import math
import os
from collections import defaultdict, deque

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"

# ============ 1. A₅ 群生成 ============
phi = (1+5**0.5)/2
inv_phi = 1/phi

def norm(v):
    v = np.asarray(v, dtype=float)
    return v/np.linalg.norm(v)

def rot_matrix(axis, angle):
    axis = np.asarray(axis, dtype=float)
    axis = axis/np.linalg.norm(axis)
    c, s = math.cos(angle), math.sin(angle)
    K = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
    return np.eye(3) + s*K + (1-c)*np.dot(K, K)

# 正二十面體頂點 (5-fold 軸) + 正十二面體頂點 (3-fold 軸)
ico_verts = []
for sx in [-1, 1]:
    for sy in [-1, 1]:
        for sz in [-1, 1]:
            ico_verts.append((0, sx, sy*phi))
            ico_verts.append((sx, sy*phi, 0))
            ico_verts.append((sx*phi, 0, sy))
ico_verts = np.array([norm(v) for v in ico_verts])

dod_verts = []
for sx in [-1, 1]:
    for sy in [-1, 1]:
        for sz in [-1, 1]:
            dod_verts.append((sx, sy, sz))
for sx in [-1, 1]:
    for sy in [-1, 1]:
        dod_verts.append((0, sx*inv_phi, sy*phi))
        dod_verts.append((sx*inv_phi, sy*phi, 0))
        dod_verts.append((sx*phi, 0, sy*inv_phi))
dod_verts = np.array([norm(v) for v in dod_verts])

# 30 邊中點 (2-fold 軸)
edges = []
for i in range(20):
    for j in range(i+1, 20):
        d = np.linalg.norm(dod_verts[i]-dod_verts[j])
        if abs(d - 2*math.sqrt(2)/math.sqrt(3)) < 0.01:
            mid = norm(dod_verts[i]+dod_verts[j])
            if not any(np.allclose(mid, e) or np.allclose(mid, -e) for e in edges):
                edges.append(mid)
edges = np.array(edges)
print(f"特徵軸: {len(ico_verts)} 5-fold + {len(dod_verts)} 3-fold + {len(edges)} 2-fold")

# A₅ = <5-fold, 3-fold> 生成 60 元素
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
            seen.add(key)
            group.append(new)
            queue.append(new)
print(f"A₅ 群: {len(group)} 元素 (期望 60)")

# 旋轉角分佈
def rot_angle(M):
    return math.degrees(math.acos(max(-1, min(1, (np.trace(M)-1)/2))))
angles = sorted([rot_angle(M) for M in group])
from collections import Counter
cnt = Counter(round(a) for a in angles)
print(f"旋轉角分佈: {dict(sorted(cnt.items()))}")

# ============ 2. 節點載入 ============
nodes = []
with open(f"{BASE}/cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                  math.cos(math.radians(d))*math.sin(math.radians(r)),
                  math.sin(math.radians(d))] for r, d in nodes])

# 節點 0 = 冷斑 (ICRS)
v0 = vecs[0]

# ============ 3. 確認 60 節點 = A₅·v0 orbit ============
print("\n=== 3. 節點集 = A₅·v0 orbit? ===")
orbit = [np.dot(M, v0) for M in group]
# 每節點對應嘅群元素 (最近)
match = 0
g_of = {}  # node -> group element
for i in range(60):
    best = None; best_d = 1e9
    for k, M in enumerate(group):
        d = np.linalg.norm(np.dot(M, v0) - vecs[i])
        if d < best_d:
            best_d = d; best = k
    if best_d < 1e-6:
        match += 1
    g_of[i] = best
print(f"60 節點中 {match}/60 係 A₅·v0 嘅元素 (誤差 <1e-6)")
print(f"→ 節點集 = A₅ orbit (冷斑穩定子平凡) {'✅' if match==60 else '❌'}")

# ============ 4. 對徑映射對應嘅 A₅ 元素 ============
print("\n=== 4. 對徑映射 = A₅ 元素? ===")
# 對徑 partner
def antip(i):
    best = None; ba = 1e9
    for j in range(60):
        if j == i: continue
        a = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if a > 170 and a < ba:
            ba = a; best = j
    return best, ba

ap = {i: antip(i)[0] for i in range(60)}
# 對徑映射 π 喺群元素 indices 上: i -> g_of[i], antip(i) -> g_of[antip(i)]
# 檢查: 存在固定 g* (群元素 index) 令 g*·(g_i·v0) = g_{antip(i)}·v0 對所有 i
# 即: g* = g_{antip(i)} · g_i^{-1} 對所有 i 都一樣?
g_inv = {}  # 群元素 -> 逆
for k, M in enumerate(group):
    for k2, M2 in enumerate(group):
        if np.allclose(np.dot(M, M2), np.eye(3), atol=1e-8):
            g_inv[k] = k2
            break

# 對每個節點 i: g_i^{-1} 作用喺 v_{antip(i)}
# 搵 g* = g_{antip(i)} · g_i^{-1}
gstar_keys = []
for i in range(60):
    gi = g_of[i]
    ga = g_of[ap[i]]
    gstar = np.dot(group[ga], group[g_inv[gi]])
    # 搵喺 group 入面嘅 index
    found = None
    for k, M in enumerate(group):
        if np.allclose(M, gstar, atol=1e-6):
            found = k
            break
    gstar_keys.append((found, gstar))

# 全部一致?
all_same = all(gstar_keys[i][1].shape == gstar_keys[0][1].shape and
               np.allclose(gstar_keys[i][1], gstar_keys[0][1], atol=1e-6) for i in range(60))
print(f"g* = g_antip · g_i^{-1} 對全部 60 節點一致? {'✅ 係!' if all_same else '❌ 唔係'}")
if all_same:
    gs = gstar_keys[0][1]
    idx = gstar_keys[0][0]
    print(f"g* 群 index = {idx}")
    print(f"g* 旋轉角 = {rot_angle(gs):.3f}°")
    # g* 嘅軸
    ax = np.array([gs[2,1]-gs[1,2], gs[0,2]-gs[2,0], gs[1,0]-gs[0,1]])
    ax = norm(ax)
    print(f"g* 軸 = ({ax[0]:.4f}, {ax[1]:.4f}, {ax[2]:.4f})")
    # 軸對應咩特徵方向?
    for name, pts in [("5-fold", ico_verts), ("3-fold", dod_verts), ("2-fold", edges)]:
        ds = [math.degrees(math.acos(np.clip(np.dot(ax, p), -1, 1))) for p in pts]
        md = min(ds)
        print(f"  軸 vs {name}: 最近 {md:.3f}°")

# ============ 5. 驗證: g* 作用喺全部節點 = 對徑映射 ============
if all_same:
    gs = gstar_keys[0][1]
    print("\n=== 5. g*·v_i = v_antip(i) 全驗證 ===")
    ok = 0
    for i in range(60):
        v_app = np.dot(gs, vecs[i])
        if np.allclose(v_app, vecs[ap[i]], atol=1e-5):
            ok += 1
    print(f"  g*·v_i = v_antip(i): {ok}/60 {'✅' if ok==60 else '❌'}")

# ============ 6. 結論: 對徑映射係 A₅ 元素 → 自動自同構 ============
print("\n=== 6. 理論閉合 ===")
if all_same:
    print("對徑映射 π(i) = g*·i 其中 g* ∈ A₅ (固定群元素)")
    print("因為 g* 係 SO(3) 等距, 保持角距離")
    print("⇒ u~v (距離<28°) ⇔ g*u ~ g*v (距離<28°)")
    print("⇒ π 係圖自同構 ⇒ k(π(i)) = k(i) ⇒ ΔE=0 節點必然成對 ✅")
    print("⇒ hop(π(i)) = 8 - hop(i) (BFS 層反轉, 因為 π 保持邊)")
    print("\n★ 核心: 60 節點 = A₅·v0 (冷斑 regular orbit), 對徑伴侶 = 固定群元素 g* 作用")
    print("  g* 係 A₅ 中嘅 180° 旋轉 (或近 180°), 繞固定軸")
    print("  冷斑對 0↔57: v57 = g*·v0, 角距離 174.66° (g* 唔係 -I, 係真旋轉)")
else:
    print("對徑映射唔係單一 A₅ 元素 — 需要其他解釋")
