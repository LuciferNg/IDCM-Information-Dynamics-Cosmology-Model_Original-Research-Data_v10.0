#!/usr/bin/env python3
"""
05_node_symmetry.py — 從 60 節點自身提取旋轉對稱軸
====================================================
正確方法: 唔用標準 dodecahedron 座標 (人為朝向), 而係
直接從 60 個節點 (A5 軌道) 提取固有旋轉對稱軸。

方法:
1. 60 節點向量 → 檢查所有 60 個 A5 旋轉, 邊個保持節點集不變
2. 每個保持不變嘅旋轉 → 佢嘅旋轉軸 = 對稱軸
3. 分類: 5-fold (72°), 3-fold (120°), 2-fold (180°)
4. 冷斑到最近各類軸距離
"""
import numpy as np, math
from astropy.coordinates import SkyCoord
import astropy.units as u

print("=" * 66)
print("O1: 從 60 節點提取固有對稱軸")
print("=" * 66)

# ============ 1. 載入 60 節點 (ICRS) ============
nodes = []
with open("../cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
vecs = np.array([np.array([math.cos(math.radians(d))*math.cos(math.radians(r)),
                           math.cos(math.radians(d))*math.sin(math.radians(r)),
                           math.sin(math.radians(d))]) for r, d in nodes])

# ============ 2. 冷斑向量 (節點 0) ============
v0 = vecs[0]
print(f"冷斑向量: ({v0[0]:.4f}, {v0[1]:.4f}, {v0[2]:.4f})")

# ============ 3. A5 群 (標準生成, 任意朝向) ============
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
def norm(v):
    n = math.sqrt(v[0]**2+v[1]**2+v[2]**2)
    return np.array(v)/n
verts_n = np.array([norm(v) for v in verts])

faces = []
for sx in [-1, 1]:
    for sy in [-1, 1]:
        faces.append((0, sx, sy*phi))
        faces.append((sx, sy*phi, 0))
        faces.append((sx*phi, 0, sy))
faces_n = np.array([norm(v) for v in faces])

def rot_matrix(axis, angle):
    axis = np.array(axis) / np.linalg.norm(axis)
    s, c = math.sin(angle), math.cos(angle)
    K = np.array([[0, -axis[2], axis[1]],
                  [axis[2], 0, -axis[0]],
                  [-axis[1], axis[0], 0]])
    return np.eye(3) + s*K + (1-c)*K@K

g1 = rot_matrix(faces_n[0], 2*math.pi/5)
g2 = rot_matrix(verts_n[0], 2*math.pi/3)

# ============ 4. 對齊: 搵將 60 節點映射到標準軌道嘅旋轉 ============
# 60 節點係 A5 軌道 (大小 60, 穩定子 1) — 任何兩個軌道都係 A5 同構
# 所以 60 節點本身就有完整 A5 對稱性 (作為抽象群)
# 但幾何上, 對稱軸 = 令 60 節點集不變嘅旋轉軸

# 關鍵: 60 節點集本身有旋轉對稱! 搵佢
# 方法: 每個節點 i, 嘗試旋轉將節點 0 → 節點 i, 然後檢查旋轉後嘅節點集
def rotation_align(v_from, v_to):
    """搵旋轉矩陣 R 令 R·v_from = v_to (最短旋轉)"""
    v1 = v_from / np.linalg.norm(v_from)
    v2 = v_to / np.linalg.norm(v_to)
    if np.allclose(v1, v2):
        return np.eye(3)
    if np.allclose(v1, -v2):
        # 180° 繞垂直軸
        perp = np.cross(v1, [1, 0, 0])
        if np.linalg.norm(perp) < 0.1:
            perp = np.cross(v1, [0, 1, 0])
        perp = perp / np.linalg.norm(perp)
        return rot_matrix(perp, math.pi)
    axis = np.cross(v1, v2)
    axis = axis / np.linalg.norm(axis)
    angle = math.acos(np.clip(np.dot(v1, v2), -1, 1))
    return rot_matrix(axis, angle)

# 將標準軌道對齊到 60 節點: 用標準頂點 0 → 節點 0
# 但節點 0 = 冷斑 = 一般位置 (唔係頂點)!
# 所以對齊係: 標準 dodecahedron 旋轉群 → 搵 R 令 R·(某標準點) = 冷斑
# 但標準點冇一個等於冷斑 (冷斑係一般位置)...

# 正確方法: 60 節點 = A5 軌道 = {g·v0 : g ∈ A5}
# 對稱軸 = 存在 h ∈ A5 (非單位) 同 w ∈ O(3) 令 w·(g·v0) = h(g)·v0 ∀g
# 但 A5 作為群作用本身已對稱!

# 直接方法: 對每個節點 i, 搵「保持節點集不變」嘅旋轉
# 旋轉 = 將節點 i 送到節點 j 嘅對齊, 然後驗證
print(f"\n搵 60 節點集嘅旋轉對稱...")
sym_axes = set()
sym_angles = []
for i in range(60):
    for j in range(60):
        if i == j: continue
        R = rotation_align(vecs[i], vecs[j])
        # 驗證: R·(節點集) = 節點集?
        rotated = R @ vecs.T  # 3x60
        rotated = rotated.T   # 60x3
        # 驗證: R·(節點集) = 節點集?
        match = 0
        for k in range(60):
            dists = np.linalg.norm(rotated[k] - vecs, axis=1)
            if dists.min() < 1e-6:
                match += 1
        if match == 60:
            # R 係對稱旋轉!
            # 提取軸: 特徵值 1
            evals, evecs = np.linalg.eig(R)
            for ei, ev in enumerate(evals):
                if abs(ev - 1) < 1e-6:
                    ax = np.real(evecs[:, ei])
                    ax = ax / np.linalg.norm(ax)
                    if ax[2] < 0: ax = -ax
                    sym_axes.add(tuple(np.round(ax, 8)))
                    break
            # 角度
            tr = np.trace(R)
            angle = math.degrees(math.acos(np.clip((tr-1)/2, -1, 1)))
            sym_angles.append(angle)

print(f"對稱旋轉軸: {len(sym_axes)} 個方向")
print(f"旋轉角: {sorted(set(round(a,1) for a in sym_angles))[:10]}")

# 分類
axes_arr = np.array(list(sym_axes))
print(f"\n軸數: {len(axes_arr)}")

# 冷斑到對稱軸距離
def min_angle(vec, axes):
    return min(math.degrees(math.acos(np.clip(np.dot(vec, a), -1, 1))) for a in axes)

print(f"\n冷斑到固有對稱軸:")
if len(axes_arr) > 0:
    d_min_all = min_angle(v0, axes_arr)
    print(f"  最近: {d_min_all:.4f}°")
    # 分距離 bins
    dists = sorted(math.degrees(math.acos(np.clip(np.dot(v0, a), -1, 1))) for a in axes_arr)
    print(f"  距離分佈: {[f'{d:.2f}' for d in dists[:8]]}...")
    print(f"  距離分佈: {[f'{d:.2f}' for d in dists[-5:]]}...")
else:
    print("  ❌ 冇搵到對稱軸")

# 儲存
with open("data/node_symmetry.txt", "w") as f:
    f.write(f"axes={len(sym_axes)}\n")
    f.write(f"angles={sorted(set(round(a,1) for a in sym_angles))[:10]}\n")
    if len(axes_arr) > 0:
        f.write(f"d_min={min_angle(v0, axes_arr):.6f}\n")
print("\n✅ 已存: data/node_symmetry.txt")
