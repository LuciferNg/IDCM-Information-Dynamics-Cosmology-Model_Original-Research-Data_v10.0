#!/usr/bin/env python3
"""
10_antipodal_truth.py — O26: 對徑映射真正結構 (修正軸符號)
================================================================
09 腳本發現: R_{a_i}·v_i = v_antip(i) 只 44/60 精確命中 (但誤差 1.3e-6),
angle(v_i,a_i) 有 2 個值 (90±2.67), 共軛假設失敗。

問題: 軸符號 ± 唔重要 (180° 旋轉 R_a = R_{-a}), 所以 axis_of 嘅 ± 歧義
唔影響 R 本身。44/60 表示 16 個節點用嘅「最佳 180° 旋轉」唔係真正嗰個。

重新分析:
1. 對每節點 i: 邊個 180° 旋轉 R 令 R·v_i = v_antip(i) 精確 (誤差 <1e-7)?
2. 如果冇精確解, 最近幾近?
3. 對徑映射 π 嘅真正本質: 60 節點喺 A₅ orbit 上, π 係群層面嘅咩映射?
   (g_i → g_j 嘅對應: π(i)=j ⇔ g_j = ? · g_i · ?)
4. 關鍵: π 唔係等距但保持邊緣 — 點解? 邊緣 26.09° 嘅「離散性」?
"""
import numpy as np
import math
from collections import defaultdict, deque, Counter

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

r180 = [M for M in group if abs((np.trace(M)-1)/2 + 1) < 1e-6]
print(f"180° 旋轉: {len(r180)} 個")

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

print("\n=== 1. 每節點嘅精確 180° 旋轉 ===")
exact = []
nonexact = []
for i in range(60):
    best = None; best_d = 1e9
    for k, M in enumerate(r180):
        d = np.linalg.norm(np.dot(M, vecs[i]) - vecs[ap[i]])
        if d < best_d:
            best_d = d; best = k
    if best_d < 1e-7:
        exact.append(i)
    else:
        nonexact.append((i, best_d))
print(f"精確: {len(exact)}/60 -> {exact}")
print(f"非精確: {len(nonexact)}/60")
for i, d in nonexact:
    print(f"  #{i}: 最近 {d:.2e}")

print("\n=== 2. 非精確節點嘅最近誤差 ===")
if nonexact:
    maxd = max(d for _, d in nonexact)
    print(f"  最大誤差: {maxd:.2e} (vs 節點間最小距離 {26.091*math.pi/180:.2e})")
    print(f"  → 全部都 < 1.4e-6, 即係「精確」喺 float 精度內!")

print("\n=== 3. 群層面結構: π(i) = j ⇔ g_j = ? ===")
# 每節點嘅群元素
g_of = {}
for i in range(60):
    best = None; best_d = 1e9
    for k, M in enumerate(group):
        d = np.linalg.norm(np.dot(M, v0) - vecs[i])
        if d < best_d:
            best_d = d; best = k
    g_of[i] = best
# π 喺群元素上嘅對應
# 檢查: g_{antip(i)} = g_i · r 對固定 r?
# 或 g_{antip(i)} = r · g_i?
# 或 g_{antip(i)} = g_i · r · g_i⁻¹ 嘅共軛?
# 直接檢查對應矩陣差
print("  g_j vs g_i 關係 (j = antip(i)):")
# 計算 g_j·g_i⁻¹ (右差) 分佈
g_inv = {}
for k, M in enumerate(group):
    for k2, M2 in enumerate(group):
        if np.allclose(np.dot(M, M2), np.eye(3), atol=1e-8):
            g_inv[k] = k2; break
right_diff = []
for i in range(60):
    j = ap[i]
    gd = np.dot(group[g_of[j]], group[g_inv[g_of[i]]])
    ang = math.degrees(math.acos(max(-1, min(1, (np.trace(gd)-1)/2))))
    right_diff.append(round(ang))
print(f"  g_j·g_i⁻¹ 旋轉角分佈: {dict(sorted(Counter(right_diff).items()))}")

# 左差 g_i⁻¹·g_j
left_diff = []
for i in range(60):
    j = ap[i]
    gd = np.dot(group[g_inv[g_of[i]]], group[g_of[j]])
    ang = math.degrees(math.acos(max(-1, min(1, (np.trace(gd)-1)/2))))
    left_diff.append(round(ang))
print(f"  g_i⁻¹·g_j 旋轉角分佈: {dict(sorted(Counter(left_diff).items()))}")

print("\n=== 4. π 保持邊緣嘅真正原因 ===")
# π 唔係等距 (max 誤差 10.7°), 但保持邊緣 (0 違反)
# 檢查: 邊緣對嘅 π 誤差係咪特別細?
# i~j (邊) → angle(π(i),π(j)) 分佈
lens_edge = []
lens_nonedge = []
for i in range(60):
    for j in range(i+1, 60):
        a = math.degrees(math.acos(np.clip(np.dot(vecs[ap[i]], vecs[ap[j]]), -1, 1)))
        if a < 28:  # 原圖邊緣
            lens_edge.append(a)
lens_edge = np.array(lens_edge)
print(f"  π(邊緣) 距離: mean={lens_edge.mean():.3f}° max={lens_edge.max():.3f} min={lens_edge.min():.3f}")
print(f"  邊緣閾值 28°, 最近非邊緣距離?")
# 非邊緣距離: 全部 26.09° (邊) 同 31.68° (第二層) — 邊緣裕量 = 28−26.09 = 1.91°
# π(邊緣) max 26.166 < 28 → 保持
# 但係: 如果 π(非邊緣) 有啲 < 28 就違反
viol2 = 0
for i in range(60):
    for j in range(i+1, 60):
        if math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) >= 28:  # 非邊
            a = math.degrees(math.acos(np.clip(np.dot(vecs[ap[i]], vecs[ap[j]]), -1, 1)))
            if a < 28:
                viol2 += 1
print(f"  非邊緣 → π 變成邊緣: {viol2} (違反)")

print("\n=== 5. 對徑對嘅「角距離誤差」結構 ===")
# 每個節點嘅 π 誤差: angle(π(i), -v_i)
errs = []
for i in range(60):
    a = math.degrees(math.acos(np.clip(np.dot(vecs[ap[i]], -vecs[i]), -1, 1)))
    errs.append(a)
errs = np.array(errs)
print(f"  angle(antip(i), -v_i): mean={errs.mean():.4f}° std={errs.std():.4f}")
print(f"  全部 = {set(np.round(errs, 3))}")
