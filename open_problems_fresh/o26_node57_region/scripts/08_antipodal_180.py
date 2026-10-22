#!/usr/bin/env python3
"""
08_antipodal_180.py — O26: 對徑映射 = 180° 旋轉繞 2-fold 軸?
================================================================
發現: g*_i 全部係 180° 旋轉 (15 個 2-fold 軸之一), ε=5.34° 常數。

核心問題: 對徑映射 π(i) = 180°旋轉(繞軸 a_i)·v_i, 但 a_i 隨 i 變?
定係: 對徑映射 = 固定 180° 旋轉 + 節點集嘅「軌道結構」令效果一致?

關鍵觀察: 如果 π(i) = R_a·v_i 對固定軸 a (某個 2-fold 軸), 咁:
- R_a 係 SO(3) 等距 → 保持角距離 → 自動圖自同構!
- ε = 5.34° = angle(v_i, R_a·v_i) 對全部 i — 但呢個要求 v_i 全部喺
  以 a 為軸嘅 5.34° 環帶? 唔可能!
- 另一可能: π(i) = 某個「對合」— π² = id, 而且 π 係圖自同構

真實驗證:
1. 對每個 2-fold 軸 a, 檢查 R_a·v_i 最近邊個節點
2. 搵固定 g* ∈ {15 個 180° 旋轉} 令 g*·v_i = v_antip(i) 對最多 i?
3. 對徑映射嘅「每節點 g*」結構: 15 個軸點樣分配畀 60 節點?
4. 對徑映射 π 係咪 A₅ 群內嘅「廣義對合」(唔係單一元素, 而係陪集?):
   π(i) = g*_i·i 其中 g*_i ∈ A₅ 但唔固定 — 但 π 仍然係自同構?
5. 檢查: 對徑對嘅「群元素差」結構
"""
import numpy as np
import math
from collections import Counter, defaultdict

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"

# ============ A₅ 群 ============
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

# 15 個 180° 旋轉 (2-fold 軸)
r180 = [M for M in group if abs((np.trace(M)-1)/2 + 1) < 1e-6]
print(f"180° 旋轉數: {len(r180)} (期望 15)")

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

# ============ 1. 固定 180° 旋轉測試 ============
print("\n=== 1. 有冇固定 g* ∈ r180 令 g*·v_i = v_antip(i) 對全部 i? ===")
best_count = 0; best_g = None
for M in r180:
    cnt = 0
    for i in range(60):
        v = np.dot(M, vecs[i])
        if np.allclose(v, vecs[ap[i]], atol=1e-5):
            cnt += 1
    if cnt > best_count:
        best_count = cnt; best_g = M
print(f"  最佳固定 g*: {best_count}/60 命中")
if best_count == 60:
    print("  ✅ 對徑映射 = 固定 180° 旋轉!")
else:
    print(f"  ❌ 唔係固定 — 每節點用唔同旋轉 ({best_count}/60)")

# ============ 2. 每節點用邊個 2-fold 軸 ============
print("\n=== 2. 每節點嘅最佳 180° 旋轉 ===")
node_axis = {}  # i -> (axis index, rotation index)
for i in range(60):
    best = None; best_d = 1e9
    for k, M in enumerate(r180):
        d = np.linalg.norm(np.dot(M, vecs[i]) - vecs[ap[i]])
        if d < best_d:
            best_d = d; best = k
    node_axis[i] = best
cnt_axis = Counter(node_axis.values())
print(f"  60 節點用嘅 180° 旋轉分佈: {dict(sorted(cnt_axis.items()))}")
print(f"  獨特軸數: {len(cnt_axis)}")
# 每軸對應幾多節點
axis_counts = defaultdict(int)
for i, a in node_axis.items():
    axis_counts[a] += 1
print(f"  每軸節點數: {sorted(axis_counts.values())}")

# ============ 3. 對徑對嘅「群元素差」 ============
print("\n=== 3. 對徑對嘅群元素結構 ===")
# 每節點嘅群元素 (A₅)
g_of = {}
for i in range(60):
    best = None; best_d = 1e9
    for k, M in enumerate(group):
        d = np.linalg.norm(np.dot(M, vecs[0]) - vecs[i])
        if d < best_d:
            best_d = d; best = k
    g_of[i] = best
# 對徑對嘅「群差」= g_antip · g_i⁻¹
g_inv = {}
for k, M in enumerate(group):
    for k2, M2 in enumerate(group):
        if np.allclose(np.dot(M, M2), np.eye(3), atol=1e-8):
            g_inv[k] = k2; break
gdiff = {}
for i in range(60):
    gs = np.dot(group[g_of[ap[i]]], group[g_inv[g_of[i]]])
    # 搵 index
    for k, M in enumerate(group):
        if np.allclose(M, gs, atol=1e-6):
            gdiff[i] = k; break
# 群差分佈
cnt_gdiff = Counter(gdiff.values())
print(f"  群差獨特元素: {len(cnt_gdiff)} (15 = 全部 180° 旋轉)")
# 每對嘅群差係咪同對嘅「中點軸」相關?
# 180° 旋轉 R_a 作用: R_a·v = 2(v·a)a - v → v 同 R_a·v 嘅中點 = (v·a)a 沿 a 軸
# ε = angle(v, R_a·v): cos(ε) = v·R_a·v = 2(v·a)² - 1
# → (v·a)² = (1+cos ε)/2 = cos²(ε/2) → v 同軸 a 嘅夾角 = ε/2 = 2.67°
# 驗證!
print("\n=== 4. 幾何驗證: v_i 到其 g* 軸嘅距離 ===")
eps2 = []
for i in range(60):
    M = r180[node_axis[i]]
    ax = np.array([M[2,1]-M[1,2], M[0,2]-M[2,0], M[1,0]-M[0,1]])
    ax = norm(ax)
    ang = math.degrees(math.acos(np.clip(np.dot(vecs[i], ax), -1, 1)))
    eps2.append(ang)
eps2 = np.array(eps2)
print(f"  angle(v_i, g*軸): mean={eps2.mean():.3f}° std={eps2.std():.3f}")
print(f"  ε/2 = {5.340/2:.3f}°")
print(f"  一致? {abs(eps2.mean()-5.340/2) < 0.01}")

# ============ 5. 對徑對嘅「對稱軸」結構 ============
print("\n=== 5. 對徑對 (0↔57 等) 嘅 180° 軸 ===")
# 每對 (i, ap[i]) 嘅公共軸: R_a·v_i = v_j 嘅 a
for i in [0, 9, 4, 20, 10, 28]:
    j = ap[i]
    M = r180[node_axis[i]]
    ax = np.array([M[2,1]-M[1,2], M[0,2]-M[2,0], M[1,0]-M[0,1]])
    ax = norm(ax)
    print(f"  #{i}↔#{j}: 軸=({ax[0]:.4f},{ax[1]:.4f},{ax[2]:.4f})")
    # 軸對應咩?
    for name, pts in [("5-fold", ico_verts), ("3-fold", dod_verts), ("2-fold", edges)]:
        ds = [math.degrees(math.acos(np.clip(np.dot(ax, p), -1, 1))) for p in pts]
        md = min(ds)
        if md < 1:
            print(f"    軸 ≈ {name} 軸 ({md:.2f}°)")
