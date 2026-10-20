#!/usr/bin/env python3
"""
02_a5_axes.py — 用 08 腳本成功方法生成 A5 群 + 軸距離
=====================================================
複製 08_a5_group_nodes.py 嘅標準 dodecahedron 幾何 + 群生成,
確保 60 個旋轉, 然後計算冷斑到各軸距離。
"""
import numpy as np, math

print("=" * 66)
print("O1: A5 群 (標準幾何) + 軸距離")
print("=" * 66)

# ============ 1. 標準 dodecahedron 幾何 (08 腳本正確版本) ============
phi = (1 + 5**0.5) / 2
inv_phi = 1/phi

# 20 頂點 (3-fold 軸方向)
verts = []
for sx in [-1, 1]:
    for sy in [-1, 1]:
        for sz in [-1, 1]:
            verts.append((sx, sy, sz))
for sx in [-1, 1]:
    for sy in [-1, 1]:
        verts.append((0, sx*inv_phi, sy*phi))
        verts.append((sx*inv_phi, sy*phi, 0))
        verts.append((sx*phi, 0, sy*inv_phi))

# 12 面中心 (5-fold 軸方向) = 正二十面體頂點
faces = []
for sx in [-1, 1]:
    for sy in [-1, 1]:
        faces.append((0, sx, sy*phi))
        faces.append((sx, sy*phi, 0))
        faces.append((sx*phi, 0, sy))

def norm(v):
    n = math.sqrt(v[0]**2+v[1]**2+v[2]**2)
    return tuple(x/n for x in v)

verts_n = np.array([norm(v) for v in verts])
faces_n = np.array([norm(v) for v in faces])
print(f"頂點: {len(verts_n)} (期望 20), 面中心: {len(faces_n)} (期望 12)")

# 30 邊中點 (2-fold 軸方向)
edges = []
for i in range(20):
    for j in range(i+1, 20):
        d = np.linalg.norm(verts_n[i] - verts_n[j])
        if abs(d - 2*math.sqrt(2)/math.sqrt(3)) < 0.01:
            mid = np.array(norm(verts_n[i] + verts_n[j]))
            if not any(np.allclose(mid, e) or np.allclose(mid, -e) for e in edges):
                edges.append(mid)
edges_n = np.array(edges)
print(f"邊中心 (2-fold): {len(edges_n)} (期望 30)")

# ============ 2. 群生成 (08 成功方法) ============
def rot_matrix(axis, angle):
    axis = np.array(axis)
    axis = axis / np.linalg.norm(axis)
    s = math.sin(angle)
    c = math.cos(angle)
    K = np.array([[0, -axis[2], axis[1]],
                  [axis[2], 0, -axis[0]],
                  [-axis[1], axis[0], 0]])
    return np.eye(3) + s*K + (1-c)*np.dot(K, K)

g1 = rot_matrix(faces_n[0], 2*math.pi/5)   # 5-fold
g2 = rot_matrix(verts_n[0], 2*math.pi/3)   # 3-fold

group = [np.eye(3)]
seen = {tuple(np.eye(3).flatten())}
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
print(f"A5 群大小: {len(group)} (期望 60)")

# ============ 3. 冷斑向量 ============
cs_ra, cs_dec = 48.30, -20.44  # ICRS
cs_vec = np.array([math.cos(math.radians(cs_dec))*math.cos(math.radians(cs_ra)),
                   math.cos(math.radians(cs_dec))*math.sin(math.radians(cs_ra)),
                   math.sin(math.radians(cs_dec))])

# ============ 4. 距離計算 ============
def min_angle(vec, axes):
    return min(math.degrees(math.acos(np.clip(np.dot(vec, a), -1, 1))) for a in axes)

d3 = min_angle(cs_vec, verts_n)   # 3-fold = 頂點
d5 = min_angle(cs_vec, faces_n)   # 5-fold = 面中心
d2 = min_angle(cs_vec, edges_n)   # 2-fold = 邊中心
print(f"\n冷斑到軸距離:")
print(f"  3-fold: {d3:.4f}°")
print(f"  5-fold: {d5:.4f}°")
print(f"  2-fold: {d2:.4f}°")

# 2:3 比例
ratio = d3 / d5
print(f"\nd3:d5 = {ratio:.6f} (2/3 = {2/3:.6f})")
print(f"偏差: {abs(ratio-2/3)/(2/3)*100:.3f}%")

# 3-5 軸角
a3 = verts_n[np.argmin([math.degrees(math.acos(np.clip(np.dot(cs_vec, v), -1, 1))) for v in verts_n])]
a5 = faces_n[np.argmin([math.degrees(math.acos(np.clip(np.dot(cs_vec, f), -1, 1))) for f in faces_n])]
axis_angle = math.degrees(math.acos(np.clip(np.dot(a3, a5), -1, 1)))
print(f"\n3→5 軸角: {axis_angle:.4f}°, d3+d5 = {d3+d5:.4f}°")
if abs(axis_angle - (d3+d5)) < 0.1:
    print("  ✅ 冷斑喺 3→5 大圓上 (共面)")
else:
    print(f"  ⚠️ 非共面 (差 {abs(axis_angle-(d3+d5)):.3f}°)")

# 球面三角形方位角
cos_axi = math.cos(math.radians(axis_angle))
cos_d3d5 = math.cos(math.radians(d3))*math.cos(math.radians(d5))
sin_d3d5 = math.sin(math.radians(d3))*math.sin(math.radians(d5))
delta = math.degrees(math.acos(np.clip((cos_axi - cos_d3d5)/sin_d3d5, -1, 1)))
print(f"  方位角 δ = {delta:.2f}°")

# 標準 dodecahedron 軸角 (理論)
print(f"\n標準軸角:")
print(f"  3-3 (頂點間): {math.degrees(math.acos(1/math.sqrt(3)))*2:.3f}° (期望 63.435°)")
print(f"  3-5 (頂點-面): {math.degrees(math.acos(1/math.sqrt(15)) + math.acos(1/math.sqrt(3))):.3f}°")
print(f"  5-5 (面間): {math.degrees(math.acos(1/math.sqrt(5)))*2:.3f}° (期望 41.81°)")

# 儲存
with open("data/axis_distances.txt", "w") as f:
    f.write(f"d3={d3:.6f} d5={d5:.6f} d2={d2:.6f}\n")
    f.write(f"ratio={ratio:.6f} 2/3={2/3:.6f}\n")
    f.write(f"axis_angle={axis_angle:.6f} d3+d5={d3+d5:.6f}\n")
    f.write(f"delta={delta:.4f}\n")
print("\n✅ 已存: data/axis_distances.txt")
