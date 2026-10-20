#!/usr/bin/env python3
"""
10_delta_group_word.py — δ 嘅群論根源 (最後攻關)
=================================================
δ = 冷斑 v 到最近 3-fold 軸 (頂點) 夾角

關鍵洞察: 冷斑 v 係 A₅ 軌道成員, 軌道 = {g·v}
最近頂點 n3 都係「某個」方向 — 但 v 本身係一般位置

真正問題: v 到 n3 嘅夾角 δ 有冇「群論意義」?

方法: 考慮 v 嘅「球面 Voronoi cell」— 由 20 個頂點 (3-fold 軸)
分割天球。v 喺邊個 cell? δ = cell 半徑?

Voronoi cell 半徑對所有一般位置都唔同 → δ 係 v 嘅特徵
但: 如果 v 係「結構點」— 例如 v 對應某個群元素嘅「最短字」
→ δ 可能有閉合公式

測試: v 同 n3 嘅關係 — v 喺唔喺「頂點 → 某個特殊方向」嘅大圓上?
"""
import numpy as np, math

print("=" * 66)
print("任務2b: δ 嘅群論根源")
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

nodes = []
with open("../cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
ra0, dec0 = nodes[0]
v = np.array([math.cos(math.radians(dec0))*math.cos(math.radians(ra0)),
              math.cos(math.radians(dec0))*math.sin(math.radians(ra0)),
              math.sin(math.radians(dec0))])

# 最近頂點
n3 = min(verts_n, key=lambda a: math.degrees(math.acos(np.clip(np.dot(v, a), -1, 1))))
d3 = math.degrees(math.acos(np.clip(np.dot(v, n3), -1, 1)))

# 最近面中心
n5 = min(faces_n, key=lambda a: math.degrees(math.acos(np.clip(np.dot(v, a), -1, 1))))
d5 = math.degrees(math.acos(np.clip(np.dot(v, n5), -1, 1)))

# 球面三角形: v, n3, n5
a35 = math.degrees(math.acos(np.clip(np.dot(n3, n5), -1, 1)))
print(f"δ3 = {d3:.6f}°, δ5 = {d5:.6f}°, 軸角 3-5 = {a35:.4f}°")
print(f"δ3 + δ5 = {d3+d5:.4f}°")

# v 喺 n3-n5 大圓上?
if abs(a35 - (d3+d5)) < 0.5:
    print("✅ v 喺頂點-面大圓上!")
else:
    print(f"❌ v 唔喺大圓 (差 {abs(a35-d3-d5):.2f}°)")

# 球面三角形角 (v 位置)
cosA = (math.cos(math.radians(d5)) - math.cos(math.radians(d3))*math.cos(math.radians(a35))) / \
       (math.sin(math.radians(d3))*math.sin(math.radians(a35)))
A = math.degrees(math.acos(np.clip(cosA, -1, 1)))
print(f"\n球面三角形 A (喺 n3): {A:.4f}°")

# A 嘅結構意義
print(f"A = {A:.4f}°")
print(f"72 - A = {72-A:.4f}°")
print(f"120 - A = {120-A:.4f}°")
print(f"A × φ = {A*phi:.4f}°")
print(f"A/2 = {A/2:.4f}°")
print(f"36 - A = {36-A:.4f}° (36° = π/5)")

# 三角形過剩
cosC = (math.cos(math.radians(a35)) - math.cos(math.radians(d3))*math.cos(math.radians(d5))) / \
       (math.sin(math.radians(d3))*math.sin(math.radians(d5)))
C = math.degrees(math.acos(np.clip(cosC, -1, 1)))
cosB = (math.cos(math.radians(d3)) - math.cos(math.radians(d5))*math.cos(math.radians(a35))) / \
       (math.sin(math.radians(d5))*math.sin(math.radians(a35)))
B = math.degrees(math.acos(np.clip(cosB, -1, 1)))
excess = A + B + C - 180
print(f"\n三角形角: A={A:.3f}°, B={B:.3f}°, C={C:.3f}°")
print(f"過剩 = {excess:.4f}°")

# 過剩同 ε/κ 關係?
eps = 1/(4*phi)
print(f"過剩 {excess:.4f}° vs:")
print(f"  ε rad = {math.degrees(eps):.4f}°")
print(f"  κ rad = {math.degrees(1/16):.4f}°")
print(f"  ε³ rad = {math.degrees(eps**3):.4f}°")
print(f"  ε² rad = {math.degrees(eps**2):.4f}°")

# 關鍵: δ 可能係「頂點球面三角形」嘅 inradius?
# 20 個頂點構成球面 Delaunay 三角形 (每個 3-3-3)
# 如果 v 喺三角形內部, δ = 到最近頂點距離
# 但 v 係一般位置 → δ 由 v 決定, 冇封閉公式

print(f"\n=== 結論評估 ===")
print(f"δ = 15.1085° 係「冷斑位置特徵」(觀測輸入)")
print(f"由 δ 推導邊長 θ 係閉合 (0.000011°)")
print(f"δ 本身冇獨立結構公式 — 佢由冷斑 ICRS 位置決定")
print(f"但冷斑位置 (209°, -57°) = (180+L₇, -(N_d+F₇)) 有結構碼!")

# 最後: δ 同位置碼嘅精確關係
print(f"\n=== δ 同位置碼 ===")
print(f"銀道 (l, b) = (209, -57)")
print(f"l = 180 + 29 = 180 + L₇")
print(f"b = -(44 + 13) = -(N_d + F₇)")
print(f"δ = 15.1085° — 由 l, b 決定 (球面幾何)")
print(f"δ/15 = 1.00723 → 15° + 0.72% 修正")
print(f"修正 0.72% ≈ 1/139? = {1/139*100:.3f}%")
print(f"修正 0.72% ≈ ε/12.3?")

# 儲存
with open("data/delta_group_word.txt", "w") as f:
    f.write(f"d3={d3:.8f} d5={d5:.8f} a35={a35:.8f}\n")
    f.write(f"A={A:.6f} B={B:.6f} C={C:.6f} excess={excess:.6f}\n")
print("\n✅ 已存: data/delta_group_word.txt")
