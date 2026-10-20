#!/usr/bin/env python3
"""
07_edge_formula_verify.py — 邊長公式最終驗證
=============================================
完整推導鏈:
冷斑位置 v (觀測) → 到最近 3-fold 軸角 δ = 15.1085°
→ 邊長 θ = arccos[cos(120°) + (1-cos(120°))·cos²(δ)]

驗證: 全網絡 120 條邊都用同一公式?
其他距離 (31.68°, 42.1°, 42.97°) 係咪都對應群元素?
"""
import numpy as np, math

print("=" * 66)
print("新O1: 邊長公式最終驗證")
print("=" * 66)

phi = (1 + 5**0.5) / 2
inv_phi = 1/phi
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

# 冷斑向量
nodes = []
with open("../cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
ra0, dec0 = nodes[0]
v = np.array([math.cos(math.radians(dec0))*math.cos(math.radians(ra0)),
              math.cos(math.radians(dec0))*math.sin(math.radians(ra0)),
              math.sin(math.radians(dec0))])

# 1. 最近 3-fold 軸角 δ
d3 = min(math.degrees(math.acos(np.clip(np.dot(v, a), -1, 1))) for a in verts_n)
print(f"最近 3-fold 軸角 δ = {d3:.6f}°")

# 2. 公式: θ = arccos[cos(120°) + (1-cos(120°))cos²(δ)]
theta = math.degrees(math.acos(-0.5 + 1.5*math.cos(math.radians(d3))**2))
print(f"公式 θ = {theta:.6f}°")
print(f"觀測  = 26.091346°")
print(f"偏差  = {abs(theta-26.091346):.6f}°")

# 3. 球面幾何直接推導: δ 同 θ 嘅關係
# 兩個點 v 同 g·v (g = 繞軸 n 旋轉 120°)
# cos θ = v·gv = cos²δ + sin²δ·cos(120°) = cos²δ - sin²δ/2
theta2 = math.degrees(math.acos(math.cos(math.radians(d3))**2 - math.sin(math.radians(d3))**2/2))
print(f"\n直接球面公式 θ = arccos(cos²δ - sin²δ/2) = {theta2:.6f}°")
print(f"偏差 = {abs(theta2-26.091346):.6f}°")

# 4. 反推: 由觀測 θ 反推 δ
# cos θ = cos²δ - sin²δ/2 = (3cos²δ - 1)/2
# cos²δ = (2cosθ + 1)/3
cos2_delta = (2*math.cos(math.radians(26.091346)) + 1)/3
delta_rev = math.degrees(math.acos(math.sqrt(cos2_delta)))
print(f"\n反推 δ = arccos(√((2cosθ+1)/3)) = {delta_rev:.6f}°")
print(f"直接量度 δ = {d3:.6f}°")
print(f"偏差 = {abs(delta_rev-d3):.6f}°")

# 5. 反推 δ 嘅精確值 → 結構意義
print(f"\n=== δ = 15.1085° 結構分析 ===")
print(f"δ = {d3:.6f}°")
print(f"δ/15 = {d3/15:.8f}")
print(f"δ - 15 = {d3-15:.6f}°")
print(f"δ 同 φ 冪:")
for p in [-2, -3, -4, -5]:
    print(f"  φ^{p} rad = {math.degrees(phi**p):.6f}°")
print(f"δ rad = {math.radians(d3):.8f}")
print(f"φ⁻³ rad = {phi**-3:.8f}")
print(f"δ - φ⁻³ = {math.radians(d3)-phi**-3:.8f} rad = {math.degrees(math.radians(d3)-phi**-3):.6f}°")
print(f"δ/φ⁻³ = {math.radians(d3)/phi**-3:.6f}")

# 6. 其他距離驗證 (對應群元素)
print(f"\n=== 其他軌道距離 (群元素對應) ===")
def rot_matrix(axis, angle):
    axis = np.array(axis) / np.linalg.norm(axis)
    s, c = math.sin(angle), math.cos(angle)
    K = np.array([[0, -axis[2], axis[1]],
                  [axis[2], 0, -axis[0]],
                  [-axis[1], axis[0], 0]])
    return np.eye(3) + s*K + (1-c)*K@K
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

# 每個元素 → 角度, 歸類
from collections import Counter
ang_counter = Counter()
for g in group:
    gv = g @ v
    theta = math.degrees(math.acos(np.clip(np.dot(v, gv), -1, 1)))
    if theta > 0.01:
        ang_counter[round(theta, 4)] += 1
print("群元素角度分佈 (top 10):")
for ang, cnt in sorted(ang_counter.items())[:10]:
    print(f"  {ang:.4f}°: {cnt} 個元素")

# 邊長 26.09 = 4 個元素 (2 對)
print(f"\n26.09° 元素數: {ang_counter[round(26.091357, 4)]}")
print(f"31.68° 元素數: {ang_counter[round(31.678679, 4)]}")
print(f"42.97° 元素數: {ang_counter[round(42.971157, 4)]}")

# 儲存
with open("data/edge_formula.txt", "w") as f:
    f.write(f"delta={d3:.8f}\n")
    f.write(f"theta_formula={theta:.8f} theta_obs={26.091346:.8f}\n")
    f.write(f"delta_rev={delta_rev:.8f}\n")
    f.write(f"theta2={theta2:.8f}\n")
print("\n✅ 已存: data/edge_formula.txt")
