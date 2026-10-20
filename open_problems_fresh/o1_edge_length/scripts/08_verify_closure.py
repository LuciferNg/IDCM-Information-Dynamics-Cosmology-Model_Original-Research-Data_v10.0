#!/usr/bin/env python3
"""
08_verify_closure.py — 閉合鏈雙重驗證 + 幻覺檢查
=================================================
獨立驗證新O1閉合鏈嘅所有關鍵數字:

[1] 邊長測量: 26.091346° ± 0.000022° (120 對)
[2] 旋轉不變性: std = 0° (相似不變量)
[3] 群理論: θ = arccos(cos²δ − sin²δ/2) = 26.091357° vs 26.091346°
[4] δ = 15.108516° (冷斑到最近 3-fold 軸)
[5] 反推: δ = arccos(√((2cosθ+1)/3))
[6] 其他距離群元素對應 (31.68°, 42.97°)
"""
import numpy as np, math

print("=" * 66)
print("新O1 閉合鏈 — 雙重驗證")
print("=" * 66)
errors = []
def check(name, calc, doc, tol=1e-4):
    diff = abs(calc - doc)
    status = "✅" if diff < tol else "❌"
    print(f"  {status} {name}: {calc:.8f} vs 文檔 {doc:.8f} (差 {diff:.2e})")
    if diff >= tol:
        errors.append(f"{name}: {calc} vs {doc}")

# ============ 載入 ============
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

# 60 節點
nodes = []
with open("../cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
vecs = np.array([np.array([math.cos(math.radians(d))*math.cos(math.radians(r)),
                           math.cos(math.radians(d))*math.sin(math.radians(r)),
                           math.sin(math.radians(d))]) for r, d in nodes])
v0 = vecs[0]

# [4] δ = 冷斑到最近 3-fold 軸 (頂點方向)
print(f"\n[4] δ 測量:")
d3 = min(math.degrees(math.acos(np.clip(np.dot(v0, a), -1, 1))) for a in verts_n)
check("δ (3-fold)", d3, 15.108516)

# [1] 邊長測量 (全網絡)
print(f"\n[1] 邊長測量:")
nn = []
for i in range(60):
    dmin = 180
    for j in range(60):
        if i == j: continue
        d = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if d < dmin: dmin = d
    nn.append(dmin)
nn = np.array(nn)
print(f"  最近鄰: mean={nn.mean():.8f}° ± {nn.std():.8f}°")
check("邊長 mean", nn.mean(), 26.091346)
print(f"  範圍: [{nn.min():.8f}, {nn.max():.8f}]")
check("邊長 max-min", nn.max()-nn.min(), 0.000063, tol=1e-4)

# [2] 旋轉不變性 (15 次)
print(f"\n[2] 旋轉不變性:")
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

def nearest_of_orbit(v, group):
    dmin = 180
    pts = [g @ v for g in group]
    for i in range(len(pts)):
        for j in range(i+1, len(pts)):
            d = math.degrees(math.acos(np.clip(np.dot(pts[i], pts[j]), -1, 1)))
            if d < dmin: dmin = d
    return dmin

def rand_rotation(rng):
    q = rng.normal(size=3)
    q = q / np.linalg.norm(q)
    theta = rng.uniform(0, 2*math.pi)
    K = np.array([[0, -q[2], q[1]], [q[2], 0, -q[0]], [-q[1], q[0], 0]])
    return np.eye(3) + math.sin(theta)*K + (1-math.cos(theta))*K@K

rng = np.random.default_rng(123)
vals = []
for _ in range(15):
    R = rand_rotation(rng)
    rot_group = [R @ g for g in group]
    vals.append(nearest_of_orbit(v0, rot_group))
vals = np.array(vals)
print(f"  15 次旋轉: std = {vals.std():.2e}°")
if vals.std() < 1e-6:
    print("  ✅ 旋轉不變性確認 (std ~ 0)")
else:
    errors.append(f"旋轉 std: {vals.std()}")

# [3] 群理論公式
print(f"\n[3] 群理論公式:")
theta_formula = math.degrees(math.acos(math.cos(math.radians(d3))**2 - math.sin(math.radians(d3))**2/2))
check("θ = arccos(cos²δ−sin²δ/2)", theta_formula, 26.091357, tol=1e-5)
print(f"  觀測: 26.091346°")
diff = abs(theta_formula - 26.091346)
print(f"  閉合偏差: {diff:.2e}°")
if diff < 2e-5:
    print("  ✅ 閉合 (偏差 < 0.00002°)")
else:
    errors.append(f"閉合偏差: {diff}")

# [5] 反推 δ
print(f"\n[5] 反推 δ:")
cos2_delta = (2*math.cos(math.radians(26.091346)) + 1)/3
delta_rev = math.degrees(math.acos(math.sqrt(cos2_delta)))
check("δ 反推", delta_rev, 15.108509, tol=1e-4)

# [6] 其他距離群元素
print(f"\n[6] 其他距離:")
from collections import Counter
ang_counter = Counter()
for g in group:
    gv = g @ v0
    theta = math.degrees(math.acos(np.clip(np.dot(v0, gv), -1, 1)))
    if theta > 0.01:
        ang_counter[round(theta, 3)] += 1
# 26.09 附近
n26 = sum(cnt for ang, cnt in ang_counter.items() if 25 < ang < 27)
print(f"  25-27° 元素數: {n26} (文檔 4)")
if n26 != 4: errors.append(f"26° 元素數: {n26}")
n31 = sum(cnt for ang, cnt in ang_counter.items() if 31 < ang < 32.5)
print(f"  31-32.5° 元素數: {n31} (文檔 1)")
n42 = sum(cnt for ang, cnt in ang_counter.items() if 41 < ang < 44)
print(f"  41-44° 元素數: {n42} (文檔 3)")

# ============ 結果 ============
print(f"\n{'='*66}")
if errors:
    print(f"❌ 發現 {len(errors)} 個不一致:")
    for e in errors: print(f"  - {e}")
else:
    print(f"✅✅ 全部驗證通過! 閉合鏈數字正確!")
print(f"{'='*66}")
