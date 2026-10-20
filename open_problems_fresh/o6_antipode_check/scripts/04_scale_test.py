#!/usr/bin/env python3
"""
04_scale_test.py — O6: 平滑尺度效應 (節點 57 溫度 vs 尺度)
===========================================================
1. 節點 57 喺 0.5°→10° 嘅溫度變化 (cache 已有全部尺度)
2. 符號會唔會隨尺度翻轉?
3. 對比節點 0 (冷斑): 所有尺度都負?
4. 節點 57 嘅尺度譜 vs 冷斑: 結構尺度差異
5. 對徑點「+8.21 μK」係咪尺度依賴假象?
"""
import healpy as hp
import numpy as np
import math
import os
from collections import defaultdict, deque
from astropy.coordinates import SkyCoord
import astropy.units as u

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
NODE_FILE = os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")
CACHE = "/tmp/cache_o3"
OUT = os.path.join(BASE, "o6_antipode_check/data")

nodes = []
with open(NODE_FILE) as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)

sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic
l_deg = gal.l.deg
b_deg = gal.b.deg

print("=" * 66)
print("O6: 節點 57 平滑尺度效應")
print("=" * 66)

scales = [0.5, 1.0, 2.0, 3.0, 4.17, 5.0, 7.0, 10.0]
T57 = []
T0 = []
T_all = {}

for s in scales:
    name = f"SMICA_{s}.fits"
    m = hp.read_map(os.path.join(CACHE, name), field=0)
    nside = hp.get_nside(m)
    pix = hp.ang2pix(nside, l_deg, b_deg, lonlat=True)
    Ts = m[pix] * 1e6
    T_all[s] = Ts
    T57.append(Ts[57])
    T0.append(Ts[0])

print(f"\n{'尺度':>6} {'節點57':>9} {'節點0':>9} {'差(57-0)':>10}")
for i, s in enumerate(scales):
    print(f"{s:>6}° {T57[i]:>+9.2f} {T0[i]:>+9.2f} {T57[i]-T0[i]:>+10.2f}")

# 符號翻轉檢查
print("\n=== 符號穩定性 ===")
sign57 = [np.sign(t) for t in T57]
sign0 = [np.sign(t) for t in T0]
print(f"節點 57 符號: {sign57} (正={sign57.count(1)}, 負={sign57.count(-1)}, 零={sign57.count(0)})")
print(f"節點 0 符號: {sign0} (正={sign0.count(1)}, 負={sign0.count(-1)}, 零={sign0.count(0)})")

# 節點 57 每個尺度嘅百分位
print("\n=== 節點 57 百分位 vs 尺度 ===")
for i, s in enumerate(scales):
    sample = T_all[s][::7]
    pct = (sample < T57[i]).mean() * 100
    print(f"  {s:>5}°: T={T57[i]:+.2f} μK → 百分位 {pct:.1f}%")

# ============ 節點 57 區域 5° 平均 vs 尺度 ============
print("\n=== 節點 57 5° 區域 mean vs 尺度 ===")
for s in scales:
    m = hp.read_map(os.path.join(CACHE, f"SMICA_{s}.fits"), field=0)
    nside = hp.get_nside(m)
    disc = hp.query_disc(nside, hp.ang2vec(l_deg[57], b_deg[57], lonlat=True), np.radians(5.0))
    rmean = m[disc].mean() * 1e6
    print(f"  {s:>5}°: 5° 區域 mean={rmean:+.2f} μK")

# ============ 冷斑 vs 對徑: 尺度譜 ============
print("\n=== 尺度譜: 節點 0 vs 57 (大尺度結構) ===")
# 用 10° 平滑 (最大尺度) 睇大尺度背景
T10 = T_all[10.0]
print(f"10° 平滑: 節點 0 = {T10[0]:+.2f} μK, 節點 57 = {T10[57]:+.2f} μK")
print(f"全天空 10° std = {T10.std():.1f} μK")

# 對徑點喺最大尺度係咪「熱背景」?
print(f"\n對徑點 (57) 10° 百分位: {(T10[::7] < T10[57]).mean()*100:.1f}%")
print(f"冷斑 (0) 10° 百分位: {(T10[::7] < T10[0]).mean()*100:.1f}%")

# ============ 冷色正溫 12 節點嘅尺度穩定性 ============
print("\n=== 冷色正溫 12 節點: 各尺度符號 ===")
# 用 4.17 定義群 (同 O3)
T417 = T_all[4.17]
cold_pos = [i for i in range(60) if (i % 2 == 0 and i != 0) or i == 0]  # placeholder, 下面用真 BFS
# 正確: 重新 BFS
vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                  math.cos(math.radians(d))*math.sin(math.radians(r)),
                  math.sin(math.radians(d))] for r, d in nodes])
adj = defaultdict(set)
for i in range(60):
    for j in range(i+1, 60):
        ang = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if ang < 28.0:
            adj[i].add(j)
            adj[j].add(i)
color = {}
color[0] = 1
q = deque([0])
while q:
    u = q.popleft()
    for w in adj[u]:
        if w not in color:
            color[w] = 1 - color[u]
            q.append(w)
cold_pos = [i for i in range(60) if color[i] == 1 and T417[i] > 0]
print(f"冷色正溫群 (4.17° 定義): {sorted(cold_pos)}")
print(f"{'節點':>4} " + " ".join(f"{s:>6}" for s in scales))
for i in sorted(cold_pos):
    row = f"{i:>4} "
    for s in scales:
        row += f"{T_all[s][i]:>+6.1f} "
    print(row)

# 邊際: 12 節點平均
row = "mean "
for s in scales:
    row += f"{np.mean([T_all[s][i] for i in cold_pos]):>+6.1f} "
print(row)

# 儲存
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "scale_test.txt"), "w") as f:
    f.write(f"# O6 節點 57 平滑尺度效應\n")
    f.write(f"# scales: {scales}\n")
    f.write(f"# T57: " + " ".join(f"{t:+.2f}" for t in T57) + "\n")
    f.write(f"# T0: " + " ".join(f"{t:+.2f}" for t in T0) + "\n")
    f.write(f"# T57_signs: {sign57}\n")
    f.write(f"# T0_signs: {sign0}\n")
    f.write(f"# T57_pct: " + " ".join(f"{(T_all[scales[i]][::7] < T57[i]).mean()*100:.1f}" for i in range(len(scales))) + "\n")
print(f"\n✅ 已存: {OUT}/scale_test.txt")
