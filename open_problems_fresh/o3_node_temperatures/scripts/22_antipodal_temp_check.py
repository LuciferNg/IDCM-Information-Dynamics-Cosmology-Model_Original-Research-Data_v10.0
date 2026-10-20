#!/usr/bin/env python3
"""
22_antipodal_temp_check.py — 高緯 4 節點對徑對: 三地圖溫度差 + 方向性檢驗
==========================================================================
O3 審計輪後續 (04_high4_node45_study.md 待辦):
1. 高緯度 4 節點嘅對徑對 (10<->25, 22<->32) 喺 NILC/Commander 嘅溫度差檢驗
2. 呢 2 對同色對徑對嘅「零點」係咪有方向性 (對徑對方向 vs 冷斑)

方法 (同源, 同 01_node_temps.py):
- 地圖: o5_catalog_compare/data/smooth_cache/*_smooth4.17.fits (三地圖 4.17° 同源 cache)
- 抽值: ICRS -> Galactic -> ang2pix (NSIDE 2048)
- 對徑對: 60 節點中角距離 > 170° 嘅對 (A5 強制 30 對, 174.66°)
- 溫度差檢驗: 對徑對 |dT| vs 隨機匹配對 |dT| (permutation, 三地圖)
- 方向性: 對徑對軸方向 vs 冷斑 (節點 0) 方向角距離; 30 對 vs 隨機旋轉對照
"""
import healpy as hp
import numpy as np
import math
from collections import defaultdict, deque
from astropy.coordinates import SkyCoord
import astropy.units as u
import os

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
CACHE = os.path.join(BASE, "o5_catalog_compare/data/smooth_cache")
O3 = os.path.join(BASE, "o3_node_temperatures")

MAPS = {
    "SMICA": os.path.join(CACHE, "smica2_smooth4.17.fits"),
    "NILC": os.path.join(CACHE, "nilc2_smooth4.17.fits"),
    "Commander": os.path.join(CACHE, "commander_smooth4.17.fits"),
}

# ---------- 1. 節點 ----------
nodes = []
with open(os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")) as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                  math.cos(math.radians(d))*math.sin(math.radians(r)),
                  math.sin(math.radians(d))] for r, d in nodes])

# 著色 (anchored_coloring: cold=1)
color = {}
with open(os.path.join(BASE, "cmb_cold_spot/data/anchored_coloring.txt")) as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        parts = line.split()
        color[int(parts[0])] = int(parts[3])
color_arr = np.array([color[i] for i in range(60)])

# BFS hop (重建圖)
adj = defaultdict(set)
for i in range(60):
    for j in range(i+1, 60):
        if math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) < 28.0:
            adj[i].add(j); adj[j].add(i)
hop = {0: 0}; q = deque([0])
while q:
    uu = q.popleft()
    for w in adj[uu]:
        if w not in hop:
            hop[w] = hop[uu] + 1; q.append(w)
hop_arr = np.array([hop[i] for i in range(60)])

# 銀河 b
sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
b_deg = sc.galactic.b.deg
l_deg = sc.galactic.l.deg

# ---------- 2. 三地圖抽值 ----------
T = {}
for name, path in MAPS.items():
    m = hp.read_map(path, field=0)
    nside = hp.get_nside(m)
    pix = hp.ang2pix(nside, l_deg, b_deg, lonlat=True)
    T[name] = m[pix] * 1e6

# SMICA 同 node_temps.txt 一致性
rows = []
for line in open(os.path.join(O3, "data/node_temps.txt")):
    if line.startswith("#") or not line.strip():
        continue
    p = line.split()
    rows.append(float(p[2]))
max_d = np.abs(T["SMICA"] - np.array(rows)).max()
print(f"SMICA 抽值 vs node_temps.txt: max|d|={max_d:.6f} uK  ({'OK' if max_d < 1e-3 else 'MISMATCH'})")

# ---------- 3. 對徑對 ----------
pairs = []
for i in range(60):
    for j in range(i+1, 60):
        ang = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if ang > 170:
            pairs.append((i, j))
print(f"\n近對徑對 (>170°): {len(pairs)} 對 (期望 30)")

HIGH4_PAIRS = [(10, 25), (22, 32)]
print("\n=== 1. 高緯 4 節點對徑對三地圖溫度差 ===")
for pi, pj in HIGH4_PAIRS:
    print(f"\n#{pi}(hop{hop_arr[pi]}) <-> #{pj}(hop{hop_arr[pj]})  色: {'冷' if color_arr[pi]==1 else '熱'}/{'冷' if color_arr[pj]==1 else '熱'}")
    for name in ["SMICA", "NILC", "Commander"]:
        d = T[name][pi] - T[name][pj]
        print(f"  {name:10s}: T{pi}={T[name][pi]:+8.2f}  T{pj}={T[name][pj]:+8.2f}  |dT|={abs(d):6.2f} uK")

# ---------- 4. 對徑對 |dT| vs 隨機匹配對 (permutation) ----------
print("\n=== 2. 全部 30 對徑對 |dT| vs 隨機 30 對 (三地圖, 2000 次) ===")
rng = np.random.default_rng(42)
for name in ["SMICA", "NILC", "Commander"]:
    obs = np.mean([abs(T[name][i] - T[name][j]) for i, j in pairs])
    cnt = 0
    n_perm = 2000
    idx = np.arange(60)
    for k in range(n_perm):
        rng.shuffle(idx)
        rand = np.mean([abs(T[name][idx[2*m]] - T[name][idx[2*m+1]]) for m in range(30)])
        if rand >= obs:
            cnt += 1
    print(f"  {name:10s}: 對徑對 mean|dT|={obs:6.2f} uK | 隨機 mean={obs:.2f} 百分位 p={(cnt+1)/(n_perm+1):.4f}")

# 高緯 4 對徑對 |dT| 喺 30 對中排名
print("\n=== 3. 高緯 2 對喺 30 對徑對中嘅 |dT| 排名 ===")
for name in ["SMICA", "NILC", "Commander"]:
    dts = sorted([abs(T[name][i] - T[name][j]) for i, j in pairs])
    rk10 = dts.index(abs(T[name][10] - T[name][25])) + 1
    rk22 = dts.index(abs(T[name][22] - T[name][32])) + 1
    print(f"  {name:10s}: (10,25) |dT|={abs(T[name][10]-T[name][25]):6.2f} 排第 {rk10}/30 ; (22,32) |dT|={abs(T[name][22]-T[name][32]):6.2f} 排第 {rk22}/30")

# ---------- 5. 方向性: 對徑對軸 vs 冷斑 ----------
print("\n=== 4. 方向性: 對徑對軸方向 vs 冷斑 (節點 0) ===")
v0 = vecs[0]
def axis_angle_to_cold(i, j):
    # 軸 = v_i + v_j (歸一化) ; 用 min(angle(axis,v0), angle(-axis,v0)) 計軸線角距離
    ax = vecs[i] + vecs[j]
    ax /= np.linalg.norm(ax)
    ang = math.degrees(math.acos(np.clip(np.dot(ax, v0), -1, 1)))
    return min(ang, 180 - ang)

print("\n高緯 2 對:")
for pi, pj in HIGH4_PAIRS:
    a = axis_angle_to_cold(pi, pj)
    print(f"  #{pi}<->#{pj}: 軸-冷斑角距離 = {a:.1f}°")

all_ang = np.array([axis_angle_to_cold(i, j) for i, j in pairs])
print(f"\n全部 30 對軸-冷斑角距離: mean={all_ang.mean():.1f}°, min={all_ang.min():.1f}°, max={all_ang.max():.1f}°")
print(f"  90° 附近 (<45° 指向冷斑, >135° 遠離): <45° 有 {(all_ang<45).sum()} 對, >135° 有 {(all_ang>135).sum()} 對")
print(f"  隨機期望: 軸-固定點角距離均勻分佈喺 [0,90]°, mean≈45°")

# 隨機旋轉對照: 冷斑方向固定, 旋轉 A5 骨架
rng2 = np.random.default_rng(7)
def rodrigues(v, axis, angle):
    k = axis / np.linalg.norm(axis)
    return v*math.cos(angle) + np.cross(k, v)*math.sin(angle) + k*np.dot(k, v)*(1-math.cos(angle))
n_trial = 2000
stat_arr = np.zeros(n_trial)
obs_stat = all_ang.mean()
for k in range(n_trial):
    ax_rot = rng2.standard_normal(3); ax_rot /= np.linalg.norm(ax_rot)
    ang_rot = rng2.uniform(0, 2*math.pi)
    vr = np.array([rodrigues(v, ax_rot, ang_rot) for v in vecs])
    pr = []
    for i in range(60):
        for j in range(i+1, 60):
            if math.degrees(math.acos(np.clip(np.dot(vr[i], vr[j]), -1, 1))) > 170:
                pr.append((i, j))
    ar = np.array([min(math.degrees(math.acos(np.clip(np.dot((vr[i]+vr[j])/np.linalg.norm(vr[i]+vr[j]), v0), -1, 1))), 180 - math.degrees(math.acos(np.clip(np.dot((vr[i]+vr[j])/np.linalg.norm(vr[i]+vr[j]), v0), -1, 1)))) for i, j in pr])
    stat_arr[k] = ar.mean()
p_rot = (stat_arr <= obs_stat).mean()
print(f"\n隨機旋轉對照 (2000x): 觀測 mean 軸-冷斑角 = {obs_stat:.1f}° vs 隨機 mean={stat_arr.mean():.1f}±{stat_arr.std():.1f}°, p(<=)={p_rot:.4f}")

print("\n✅ 完成: 22_antipodal_temp_check.py")
