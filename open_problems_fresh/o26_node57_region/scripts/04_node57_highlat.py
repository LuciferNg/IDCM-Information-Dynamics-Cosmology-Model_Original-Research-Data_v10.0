#!/usr/bin/env python3
"""
04_node57_highlat.py — O26: 節點 57 高緯度對比 + 冷斑 30° 詳細結構
====================================================================
節點 57 喺 b=+52.7° (高緯, 乾淨區域), 同冷斑 (b=-57°) 都係高緯。

本腳本:
1. 節點 57 vs 高緯度 4 節點 (10/22/25/32) 附近 5° 結構對比
2. 節點 57 vs 全 60 節點 5° 區域 mean 分佈 (百分位)
3. 冷斑 30° 區域詳細結構 (5° 平滑): 極值、梯度、冷斑喺區域嘅相對位置
4. 冷斑 30° 區域係咪「真冷斑主導」定「混合區域」
5. 對徑對嘅「背景互補性」: 0↔57 區域 mean 差 5.75 μK (30 對第 7 細)
"""
import healpy as hp
import numpy as np
import math
import os
from astropy.coordinates import SkyCoord
import astropy.units as u

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
CACHE = "/tmp/cache_o3"
OUT = os.path.join(BASE, "o26_node57_region", "data")

nodes = []
with open(f"{BASE}/cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic
vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                  math.cos(math.radians(d))*math.sin(math.radians(r)),
                  math.sin(math.radians(d))] for r, d in nodes])

rows = []
with open(f"{BASE}/o3_node_temperatures/data/node_temps.txt") as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        p = line.split()
        rows.append((int(p[0]), int(p[1]), float(p[2]), float(p[3]), float(p[4]), int(p[5])))
T = np.array([r[2] for r in rows])
color = np.array([r[1] for r in rows])
l_deg = np.array([r[3] for r in rows])
b_deg = np.array([r[4] for r in rows])
hop = np.array([r[5] for r in rows])

m5 = hp.read_map(f"{CACHE}/SMICA_smooth5.0.fits")
ns5 = hp.get_nside(m5)

results = []
def log(*args):
    line = " ".join(str(a) for a in args)
    print(line)
    results.append(line)

log("=" * 70)
log("O26: 節點 57 高緯度對比 + 冷斑區域結構")
log("=" * 70)

# ============ 1. 高緯度節點 5° 區域對比 ============
log("\n=== 1. 高緯度節點附近 5° 區域結構 (5° 平滑) ===")
HIGH = [0, 57, 10, 22, 25, 32]
log(f"  {'#':>3} {'b':>6} {'T(4.17)':>8} {'5°mean':>8} {'5°std':>7} {'5°min':>8} {'5°max':>8}")
for i in HIGH:
    v = vecs[i]
    d = hp.query_disc(ns5, v, np.radians(5))
    vals = m5[d]*1e6
    pix = hp.ang2pix(ns5, gal.l.deg[i], gal.b.deg[i], lonlat=True)
    log(f"  {i:>3} {b_deg[i]:+6.1f} {T[i]:+8.2f} {vals.mean():+8.2f} {vals.std():7.2f} "
        f"{vals.min():+8.2f} {vals.max():+8.2f}")

# ============ 2. node 57 5° 區域 mean 百分位 ============
log("\n=== 2. node 57 5° 區域 mean vs 全 60 節點 ===")
means5 = []
for i in range(60):
    v = vecs[i]
    d = hp.query_disc(ns5, v, np.radians(5))
    means5.append(m5[d].mean()*1e6)
means5 = np.array(means5)
v57 = vecs[57]
d57 = hp.query_disc(ns5, v57, np.radians(5))
mean57 = m5[d57].mean()*1e6
pct = (means5 < mean57).mean()*100
log(f"  全 60 節點 5° mean: mean={means5.mean():+.2f} std={means5.std():.2f} "
    f"min={means5.min():+.2f} max={means5.max():+.2f}")
log(f"  node 57 5° mean = {mean57:+.2f} → 百分位 {pct:.0f}%")
log(f"  冷斑 5° mean = {means5[0]:+.2f} → 百分位 {(means5<means5[0]).mean()*100:.0f}%")

# ============ 3. 冷斑 30° 區域詳細結構 ============
log("\n=== 3. 冷斑 30° 區域詳細結構 (5° 平滑) ===")
v0 = vecs[0]
d0 = hp.query_disc(ns5, v0, np.radians(30))
vals0 = m5[d0]*1e6
imax = np.argmax(vals0); imin = np.argmin(vals0)
t_max, p_max = hp.pix2ang(ns5, d0[imax], lonlat=True)
t_min, p_min = hp.pix2ang(ns5, d0[imin], lonlat=True)
log(f"  冷斑 30°: mean={vals0.mean():+.2f} std={vals0.std():.2f}")
log(f"  區域 max: {vals0.max():+.1f} μK @ (l={p_max:.0f}, b={t_max:.0f})")
log(f"  區域 min: {vals0.min():+.1f} μK @ (l={p_min:.0f}, b={t_min:.0f})")
pix0 = hp.ang2pix(ns5, gal.l.deg[0], gal.b.deg[0], lonlat=True)
log(f"  冷斑 (node 0) 5° 平滑值 = {m5[pix0]*1e6:+.2f} μK")
log(f"  冷斑相對 30° mean: {m5[pix0]*1e6 - vals0.mean():+.1f} μK")
# 冷斑喺 30° 區域嘅百分位
pct_cs = (vals0 < m5[pix0]*1e6).mean()*100
log(f"  冷斑喺 30° 區域嘅百分位: {pct_cs:.1f}% (0% = 全區域最冷)")
# 負像素比例
log(f"  30° 區域負像素比例: {(vals0 < 0).mean()*100:.1f}%")

# 冷斑 30° 嘅同心環結構 (5°, 10°, 15°, 20°, 30°)
log("\n  冷斑同心環 mean:")
for rad in [3, 5, 8, 10, 15, 20, 30]:
    d = hp.query_disc(ns5, v0, np.radians(rad))
    log(f"    {rad:>2}°: {m5[d].mean()*1e6:+7.2f} μK (n={len(d)})")

# ============ 4. 對徑對 30° 區域 mean 表 ============
log("\n=== 4. 30 對近對徑 30° 區域 mean 差 (細 = 背景相似) ===")
rm = {}
for i in range(60):
    v = vecs[i]
    d = hp.query_disc(ns5, v, np.radians(30))
    rm[i] = m5[d].mean()*1e6
# 列出 0↔57 附近嘅
log(f"  0↔57: {rm[0]:+.2f} vs {rm[57]:+.2f} 差={abs(rm[0]-rm[57]):.2f}")
# 全部對嘅差排名
diffs = []
for i in range(60):
    for j in range(i+1, 60):
        ang = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if ang > 170:
            diffs.append((abs(rm[i]-rm[j]), i, j))
diffs.sort()
log("  最相似背景 5 對:")
for d, i, j in diffs[:5]:
    log(f"    #{i:>2}↔#{j:>2}: {d:.2f} μK")
log("  最唔相似背景 5 對:")
for d, i, j in diffs[-5:]:
    log(f"    #{i:>2}↔#{j:>2}: {d:.2f} μK")

# ============ 5. 對徑對溫度 vs 區域 mean (去背景後) ============
log("\n=== 5. 去 30° 區域背景後嘅節點溫度 (T_local) ===")
T_local = T - np.array([rm[i] for i in range(60)])
log(f"  {'#':>3} {'T':>8} {'reg30':>7} {'T_local':>9}")
for i in [0, 57, 10, 22, 25, 32]:
    log(f"  {i:>3} {T[i]:+8.2f} {rm[i]:+7.2f} {T_local[i]:+9.2f}")
# 0↔57 去背景後
log(f"\n  0↔57: T_local 差 = {abs(T_local[0]-T_local[57]):.2f} μK "
    f"(原始 |ΔT| = {abs(T[0]-T[57]):.2f})")
# 冷斑係咪仲係極端? 全部節點 T_local
log(f"  冷斑 T_local = {T_local[0]:+.2f} — 60 節點中第 {(T_local>T_local[0]).sum()+1} 冷")
log(f"  對徑 T_local = {T_local[57]:+.2f} — 60 節點中第 {(T_local>T_local[57]).sum()+1} 冷")

with open(os.path.join(OUT, "node57_highlat_results.txt"), "w") as f:
    f.write("\n".join(results) + "\n")
print(f"\n✅ 結果寫入 {OUT}/node57_highlat_results.txt")
