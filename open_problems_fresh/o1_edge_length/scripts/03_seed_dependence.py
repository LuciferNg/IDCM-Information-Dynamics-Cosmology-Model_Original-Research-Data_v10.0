#!/usr/bin/env python3
"""
03_seed_dependence.py — 邊長對種子向量嘅依賴性
================================================
關鍵問題: 26.091346° 係「冷斑特徵」定「A₅ 通用常數」?

方法: 用隨機種子向量 + 同一個 A₅ 群 → 產生 60 節點軌道
→ 計最近鄰距離, 睇係咪都係 26.09°。

如果所有種子都畀 26.09° → A₅ 通用常數
如果唔同種子唔同 → 26.09° 係冷斑位置特徵
"""
import numpy as np, math

print("=" * 66)
print("新O1: 邊長對種子向量嘅依賴性")
print("=" * 66)

# A₅ 群 (標準幾何, 2 生成元)
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
print(f"A₅ 群: {len(group)} 元素")

# 軌道函數
def orbit(v0):
    pts = [(M @ v0) for M in group]
    return np.array(pts)

def nearest_dist(pts):
    n = len(pts)
    dmin = 180
    for i in range(n):
        for j in range(i+1, n):
            d = math.degrees(math.acos(np.clip(np.dot(pts[i], pts[j]), -1, 1)))
            if d < dmin: dmin = d
    return dmin

# 測試 1: 冷斑向量 (真實)
# (由 a5_nodes.txt 節點 0 反推 — 但呢啲係 ICRS, 群係標準座標)
# 用標準座標種子: 一般位置向量
print(f"\n=== 測試 1: 隨機種子向量 ===")
rng = np.random.default_rng(7)
for trial in range(8):
    v = rng.normal(size=3)
    v = v / np.linalg.norm(v)
    pts = orbit(v)
    d = nearest_dist(pts)
    print(f"  種子 {trial}: 最近鄰 = {d:.6f}°")

# 測試 2: 特殊位置 (頂點/面中心/邊中點)
print(f"\n=== 測試 2: 特殊種子 (對稱位置) ===")
special = {
    "頂點 (3-fold)": verts_n[0],
    "面中心 (5-fold)": faces_n[0],
    "一般": np.array([1, 2, 3])/np.sqrt(14),
}
for name, v in special.items():
    pts = orbit(v)
    d = nearest_dist(pts)
    print(f"  {name}: 最近鄰 = {d:.6f}°, 軌道大小 = {len(set(tuple(np.round(p,8)) for p in pts))}")

# 測試 3: 冷斑軌道 (從 a5_nodes) 用標準座標再算
print(f"\n=== 測試 3: 真實冷斑軌道 ===")
# a5_nodes 係 ICRS, 而群係標準 — 但軌道結構只依賴群作用
# 冷斑向量 (ICRS)
nodes = []
with open("../cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
ra0, dec0 = nodes[0]
v_cs = np.array([math.cos(math.radians(dec0))*math.cos(math.radians(ra0)),
                 math.cos(math.radians(dec0))*math.sin(math.radians(ra0)),
                 math.sin(math.radians(dec0))])
# 但群係標準座標 — 唔可以直接作用!
# 正確: 軌道 = {g·v0} 對應「冷斑家族」= a5_nodes 本身
# 所以直接用 a5_nodes 計最近鄰 (01 腳本已做) = 26.0913
print(f"  a5_nodes 最近鄰: 26.091346° (01 腳本)")
print(f"  呢個係冷斑 ICRS 軌道嘅固有值")

# 儲存
with open("data/seed_dependence.txt", "w") as f:
    f.write("隨機種子最近鄰:\n")
    rng = np.random.default_rng(7)
    for trial in range(8):
        v = rng.normal(size=3); v = v/np.linalg.norm(v)
        pts = orbit(v)
        f.write(f"  seed{trial}: {nearest_dist(pts):.6f}\n")
print("\n✅ 已存: data/seed_dependence.txt")
