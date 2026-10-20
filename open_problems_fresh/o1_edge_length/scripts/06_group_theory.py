#!/usr/bin/env python3
"""
06_group_theory.py — 群理論推導邊長
=====================================
正確框架: 軌道點 v 同 g·v 嘅角距離 θ 由:
cos(θ) = v·(g·v) = cos(α)·(1 - (v·n)²) + (v·n)²
其中 α = g 嘅 rotation angle, n = rotation axis

最近鄰 = 對應某個群元素 g 嘅最小 θ(v, g·v)

A₅ 元素 rotation angles: 72° (5-fold), 120° (3-fold), 180° (2-fold), 144°

對每個元素, θ 由 v 同 n 嘅夾角決定:
θ(g) = arccos[cos α + (1-cos α)(v·n)²]

最小 θ = 邊長
"""
import numpy as np, math

print("=" * 66)
print("新O1: 群理論邊長推導")
print("=" * 66)

phi = (1 + 5**0.5) / 2
inv_phi = 1/phi

# A₅ 群 (標準)
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
faces = []
for sx in [-1, 1]:
    for sy in [-1, 1]:
        faces.append((0, sx, sy*phi))
        faces.append((sx, sy*phi, 0))
        faces.append((sx*phi, 0, sy))
def norm(v):
    n = math.sqrt(v[0]**2+v[1]**2+v[2]**2)
    return np.array(v)/n
verts_n = np.array([norm(v) for v in verts])
faces_n = np.array([norm(v) for v in faces])
edges_n = []
for i in range(20):
    for j in range(i+1, 20):
        d = np.linalg.norm(verts_n[i]-verts_n[j])
        if abs(d - 2*math.sqrt(2)/math.sqrt(3)) < 0.01:
            mid = np.array(norm(verts_n[i]+verts_n[j]))
            if not any(np.allclose(mid, e) or np.allclose(mid, -e) for e in edges_n):
                edges_n.append(mid)
edges_n = np.array(edges_n)

def rot_matrix(axis, angle):
    axis = np.array(axis) / np.linalg.norm(axis)
    s, c = math.sin(angle), math.cos(angle)
    K = np.array([[0, -axis[2], axis[1]],
                  [axis[2], 0, -axis[0]],
                  [-axis[1], axis[0], 0]])
    return np.eye(3) + s*K + (1-c)*K@K

# 群
g1 = rot_matrix(faces_n[0], 2*math.pi/5)
g2 = rot_matrix(verts_n[0], 2*math.pi/3)
group = [np.eye(3)]
seen = {tuple(np.eye(3).flatten())}
queue = [np.eye(3)]
while queue:
    M = queue.pop(0)
    for gen in [g1, g2]:
        new = gen @ M
        key = tuple(np.round(new.flatten(), 10))
        if key not in seen:
            seen.add(key)
            group.append(new)
            queue.append(new)

# 冷斑向量 (a5_nodes 節點 0)
nodes = []
with open("../cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
ra0, dec0 = nodes[0]
v = np.array([math.cos(math.radians(dec0))*math.cos(math.radians(ra0)),
              math.cos(math.radians(dec0))*math.sin(math.radians(ra0)),
              math.sin(math.radians(dec0))])

# 對每個群元素, 計 θ(v, g·v)
print(f"\n=== 每個群元素對應嘅軌道點角距離 ===")
results = []
for g in group:
    gv = g @ v
    theta = math.degrees(math.acos(np.clip(np.dot(v, gv), -1, 1)))
    if theta > 0.01:
        # rotation angle + axis type
        tr = np.trace(g)
        alpha = math.degrees(math.acos(np.clip((tr-1)/2, -1, 1)))
        # axis type: 最近嘅特殊軸
        results.append((theta, alpha, g))

# 排序
results.sort(key=lambda x: x[0])
print(f"最近 8 個:")
for theta, alpha, g in results[:8]:
    print(f"  θ = {theta:.6f}° (rotation α = {alpha:.1f}°)")

# 驗證理論公式
print(f"\n=== 理論公式驗證: θ = arccos[cos α + (1-cos α)(v·n)²] ===")
# 對最短 θ (對應邊長), 搵群元素 g
theta1, alpha1, g1_el = results[0]
# 搵 g 嘅 rotation axis
evals, evecs = np.linalg.eig(g1_el)
for i, ev in enumerate(evals):
    if abs(ev - 1) < 1e-6:
        n = np.real(evecs[:, i])
        n = n / np.linalg.norm(n)
        break
# 理論值
dot_vn = np.dot(v, n)
theta_theory = math.degrees(math.acos(math.cos(math.radians(alpha1)) + (1-math.cos(math.radians(alpha1)))*dot_vn**2))
print(f"最短 θ 對應: rotation {alpha1}°, axis 同 v 夾角 {math.degrees(math.acos(abs(dot_vn))):.4f}°")
print(f"理論 θ = {theta_theory:.6f}° vs 實際 {theta1:.6f}°")

# 關鍵: 邊長 26.0913° 對應邊個元素?
print(f"\n=== 26.0913° 對應群元素 ===")
for theta, alpha, g in results:
    if abs(theta - 26.091346) < 0.001:
        # axis type
        evals, evecs = np.linalg.eig(g)
        for i, ev in enumerate(evals):
            if abs(ev - 1) < 1e-6:
                n = np.real(evecs[:, i])
                n = n/np.linalg.norm(n)
                # 最近特殊軸
                d_min = 180
                for axis_list, name in [(verts_n, "3-fold"), (faces_n, "5-fold"), (edges_n, "2-fold")]:
                    for a in axis_list:
                        d = math.degrees(math.acos(np.clip(abs(np.dot(n, a)), -1, 1)))
                        if d < d_min: d_min = d
                print(f"  θ = {theta:.6f}°: rotation {alpha:.1f}°, axis 最近特殊軸距離 {d_min:.2f}°")
                break
print(f"\n(如果冇輸出 = 邊長唔對應簡單群元素)")

# 儲存
with open("data/group_theory.txt", "w") as f:
    f.write(f"nearest 8:\n")
    for theta, alpha, g in results[:8]:
        f.write(f"  theta={theta:.6f} alpha={alpha:.1f}\n")
    f.write(f"理論公式驗證: {theta_theory:.6f} vs {theta1:.6f}\n")
print("\n✅ 已存: data/group_theory.txt")
