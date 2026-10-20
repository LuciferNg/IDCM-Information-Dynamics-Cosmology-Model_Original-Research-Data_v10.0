#!/usr/bin/env python3
"""
01_axis_distances.py — O1: 15.11° 群不變性 + 2:3 比例驗證
"""
import numpy as np, math
from collections import defaultdict, deque

print("=" * 66)
print("O1: 15.11° 群不變性 + 2:3 比例驗證")
print("=" * 66)

# 載入節點
nodes = []
with open("../cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
vecs = np.array([np.array([math.cos(math.radians(d))*math.cos(math.radians(r)),
                           math.cos(math.radians(d))*math.sin(math.radians(r)),
                           math.sin(math.radians(d))]) for r, d in nodes])

# A5 群生成 (只用 2 個生成元, 08 腳本成功方法)
phi = (1 + 5**0.5) / 2
R5 = np.array([[np.cos(2*np.pi/5), -np.sin(2*np.pi/5), 0],
               [np.sin(2*np.pi/5),  np.cos(2*np.pi/5), 0], [0, 0, 1]])
u = np.array([1, 1, 1]) / np.sqrt(3)
c, s = np.cos(2*np.pi/3), np.sin(2*np.pi/3)
R3 = np.array([[c + u[0]**2*(1-c), u[0]*u[1]*(1-c)-u[2]*s, u[0]*u[2]*(1-c)+u[1]*s],
               [u[1]*u[0]*(1-c)+u[2]*s, c+u[1]**2*(1-c), u[1]*u[2]*(1-c)-u[0]*s],
               [u[2]*u[0]*(1-c)-u[1]*s, u[2]*u[1]*(1-c)+u[0]*s, c+u[2]**2*(1-c)]])

group = [np.eye(3)]
seen = {tuple(np.eye(3).flatten())}
queue = [np.eye(3)]
while queue:
    M = queue.pop(0)
    for gen in [R5, R3]:
        new = gen @ M
        key = tuple(np.round(new.flatten(), 10))
        if key not in seen:
            seen.add(key)
            group.append(new)
            queue.append(new)
print(f"A5 群大小: {len(group)} (期望 60)")

# 搵對稱軸 (trace 判別)
def get_axes(trace_target, tol=0.01):
    axes = set()
    for g in group:
        if abs(np.trace(g) - trace_target) < tol:
            evals, evecs = np.linalg.eig(g)
            for i, ev in enumerate(evals):
                if abs(ev - 1) < tol:
                    ax = np.real(evecs[:, i])
                    ax = ax / np.linalg.norm(ax)
                    if ax[2] < 0: ax = -ax
                    axes.add(tuple(np.round(ax, 10)))
                    break
    return [np.array(a) for a in axes]

three_axes = get_axes(0)      # tr=0 → 120°
five_axes = get_axes(phi)     # tr=φ → 72°
two_axes = get_axes(-1)       # tr=-1 → 180°
print(f"3-fold: {len(three_axes)}, 5-fold: {len(five_axes)}, 2-fold: {len(two_axes)}")

# 冷斑到軸距離
def min_angle(vec, axes):
    return min(math.degrees(math.acos(np.clip(np.dot(vec, a), -1, 1))) for a in axes)

d3 = min_angle(vecs[0], three_axes)
d5 = min_angle(vecs[0], five_axes)
d2 = min_angle(vecs[0], two_axes)
print(f"\n冷斑到軸距離:")
print(f"  3-fold: {d3:.3f}°")
print(f"  5-fold: {d5:.3f}°")
print(f"  2-fold: {d2:.3f}°")

# 群不變性: 60 節點每個到最近 3-fold 軸距離
d3_all = [min_angle(vecs[i], three_axes) for i in range(60)]
print(f"\n群不變性: 60 節點到最近 3-fold 軸")
print(f"  min={min(d3_all):.3f}°, max={max(d3_all):.3f}°, mean={np.mean(d3_all):.3f}°")
print(f"  std={np.std(d3_all):.5f}°")
if max(d3_all) - min(d3_all) < 0.01:
    print("  ✅ 常數! 群不變量確認!")
else:
    print("  ⚠️ 非常數")

# 2:3 比例驗證
ratio = d3 / d5
print(f"\n15.109 : 22.651 = {ratio:.6f}")
print(f"2/3 = {2/3:.6f}")
print(f"偏差: {abs(ratio - 2/3)/(2/3)*100:.4f}%")
print(f"3*d3 = {3*d3:.4f}, 2*d5 = {2*d5:.4f}")

# 球面共面性: 冷斑, 最近 3-fold, 最近 5-fold
def nearest(vec, axes):
    angs = [math.degrees(math.acos(np.clip(np.dot(vec, a), -1, 1))) for a in axes]
    return axes[np.argmin(angs)], min(angs)

a3, _ = nearest(vecs[0], three_axes)
a5, _ = nearest(vecs[0], five_axes)
axis_angle = math.degrees(math.acos(np.clip(np.dot(a3, a5), -1, 1)))
print(f"\n最近 3-fold → 5-fold 軸角: {axis_angle:.4f}°")
print(f"d3 + d5 = {d3 + d5:.4f}°")
if abs(axis_angle - (d3 + d5)) < 0.1:
    print("  ✅ 冷斑喺 3→5 大圓上!")
else:
    print(f"  ⚠️ 冷斑唔喺大圓上 (差 {abs(axis_angle-(d3+d5)):.2f}°)")

# 球面餘弦定律求方位角 δ
cos_axi = math.cos(math.radians(axis_angle))
cos_d3d5 = math.cos(math.radians(d3))*math.cos(math.radians(d5))
sin_d3d5 = math.sin(math.radians(d3))*math.sin(math.radians(d5))
delta = math.degrees(math.acos(np.clip((cos_axi - cos_d3d5) / sin_d3d5, -1, 1)))
print(f"  方位角 δ = {delta:.2f}° (0=共面)")
print(f"  冷斑-3-5 球面三角形: {'✅ 共面' if delta < 1 else '⚡ 非共面 δ='+f'{delta:.1f}°'}")

# 3-fold 軸之間最小角 (dodecahedron 頂點角)
three_arr = np.array(three_axes)
min_33 = 180
for i in range(len(three_arr)):
    for j in range(i+1, len(three_arr)):
        ang = math.degrees(math.acos(np.clip(np.dot(three_arr[i], three_arr[j]), -1, 1)))
        if ang < min_33: min_33 = ang
print(f"\n3-fold 軸間最小角: {min_33:.4f}° (dodecahedron 頂點角 63.435°)")

# 儲存
with open("data/axis_distances.txt", "w") as f:
    f.write(f"d3={d3:.6f} d5={d5:.6f} d2={d2:.6f}\n")
    f.write(f"ratio={ratio:.6f} 2/3={2/3:.6f}\n")
    f.write(f"3-5_axis_angle={axis_angle:.6f}\n")
    f.write(f"d3+d5={d3+d5:.6f}\n")
    f.write(f"delta={delta:.4f}\n")
print("\n✅ 已存: data/axis_distances.txt")