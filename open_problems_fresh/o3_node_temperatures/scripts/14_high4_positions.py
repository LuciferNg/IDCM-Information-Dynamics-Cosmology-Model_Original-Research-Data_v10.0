#!/usr/bin/env python3
"""高緯度 4 節點位置分析"""
import numpy as np
import math
from astropy.coordinates import SkyCoord
import astropy.units as uu

nodes = []
with open('/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt') as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                  math.cos(math.radians(d))*math.sin(math.radians(r)),
                  math.sin(math.radians(d))] for r, d in nodes])
sc = SkyCoord(ra=nodes[:,0]*uu.deg, dec=nodes[:,1]*uu.deg, frame='icrs')
b_arr = sc.galactic.b.deg
l_arr = sc.galactic.l.deg

HIGH4 = [10, 22, 25, 32]
print("=== 高緯度 4 節點: 天球位置 ===")
print(f"{'#':<5}{'RA':<10}{'Dec':<10}{'l(deg)':<9}{'b(deg)':<9}{'|b|'}")
for i in HIGH4:
    print(f"#{i:<4}{nodes[i,0]:8.2f}  {nodes[i,1]:+8.2f}  {l_arr[i]:6.1f}  {b_arr[i]:+6.1f}  {abs(b_arr[i]):5.1f}")

print()
print("=== 節點間角距離 ===")
for a in range(4):
    for b2 in range(a+1, 4):
        i, j = HIGH4[a], HIGH4[b2]
        ang = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        print(f"  #{i} <-> #{j}: {ang:.2f} deg")

rows = []
with open('/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o3_node_temperatures/data/node_temps.txt') as f:
    for line in f:
        if line.startswith('#') or not line.strip():
            continue
        p = line.split()
        rows.append((int(p[0]), int(p[1]), float(p[2])))
T = np.array([r[2] for r in rows]); color = np.array([r[1] for r in rows])
print()
print("=== 溫度符號匹配 ===")
for i in HIGH4:
    c = "冷" if color[i] == 1 else "熱"
    ok = "OK" if (color[i] == 1) == (T[i] < 0) else "MISMATCH"
    print(f"  #{i}: T={T[i]:+.2f} uK, color={c} [{ok}]")
