#!/usr/bin/env python3
"""
03_node57_antipodal.py — O26: 對徑對統計 (0↔57 vs 29 對近對徑)
================================================================
O3 已發現: A₅ 有 30 對近對徑 (174.66°), 全部同色, hop 和 = 8。
節點 0↔57 係其中一對 (d0↔d8)。

本腳本:
1. 列舉全部 30 對近對徑
2. 每對嘅 4.17° 溫度 (SMICA)
3. 對徑對溫度差 |T_a - T_b| 分佈 vs random pair
4. 對徑對溫度「互補性」: 冷斑對 (-134 vs +8) 係咪特殊?
5. 冷斑 0↔57 喺 30 對中嘅排名 (差/和)
6. 對徑對嘅 30° 區域 mean 相關 (大尺度背景)
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

rng = np.random.default_rng(2602)

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

# 載入 node_temps (4.17° SMICA)
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

# 載入 5° 平滑地圖 (30° 區域 mean 用)
m5 = hp.read_map(f"{CACHE}/SMICA_smooth5.0.fits")
ns5 = hp.get_nside(m5)

results = []
def log(*args):
    line = " ".join(str(a) for a in args)
    print(line)
    results.append(line)

log("=" * 70)
log("O26: 對徑對統計 (0↔57 vs 其他 29 對)")
log("=" * 70)

# ============ 1. 全部近對徑對 ============
log("\n=== 1. 全部近對徑對 (>170°) ===")
pairs = []
for i in range(60):
    for j in range(i+1, 60):
        ang = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if ang > 170:
            pairs.append((ang, i, j))
pairs.sort(reverse=True)
log(f"共 {len(pairs)} 對")
for ang, i, j in pairs:
    same = "同色" if color[i] == color[j] else "異色"
    dT = abs(T[i] - T[j])
    log(f"  #{i:>2}↔#{j:>2}: {ang:.2f}° hop={hop[i]}/{hop[j]} {same} "
        f"T={T[i]:+7.2f}/{T[j]:+7.2f} |ΔT|={dT:6.2f}")

# ============ 2. 對徑對溫度差 vs random pair ============
log("\n=== 2. |ΔT| 對徑對 vs random pair ===")
dT_antipodal = [abs(T[i]-T[j]) for _, i, j in pairs]
# random pair (同一節點集, 唔限對徑)
dT_random = []
for _ in range(10000):
    i, j = rng.choice(60, 2, replace=False)
    dT_random.append(abs(T[i]-T[j]))
dT_random = np.array(dT_random)
dT_antipodal = np.array(dT_antipodal)
log(f"  對徑對 |ΔT|: mean={dT_antipodal.mean():.2f} median={np.median(dT_antipodal):.2f} max={dT_antipodal.max():.2f}")
log(f"  random  |ΔT|: mean={dT_random.mean():.2f} median={np.median(dT_random):.2f}")
pct = (dT_random > dT_antipodal.mean()).mean()*100
log(f"  對徑對 mean |ΔT| ({dT_antipodal.mean():.1f}) vs random 百分位: {pct:.1f}%")
# 0↔57 排名
dT_057 = abs(T[0]-T[57])
rank = (dT_antipodal >= dT_057).sum()
log(f"  0↔57 |ΔT| = {dT_057:.2f} — 30 對中第 {rank} 大 (共 {len(dT_antipodal)} 對)")

# ============ 3. 對徑對 30° 區域 mean ============
log("\n=== 3. 對徑對 30° 區域 mean (5° 平滑) ===")
region_means = {}
for i in range(60):
    v = vecs[i]
    d = hp.query_disc(ns5, v, np.radians(30))
    region_means[i] = m5[d].mean()*1e6
log(f"  冷斑 (0) 30° mean: {region_means[0]:+.2f}")
log(f"  對徑 (57) 30° mean: {region_means[57]:+.2f}")
# 對徑對嘅區域 mean 相關
rm_anti = [(region_means[i], region_means[j]) for _, i, j in pairs]
rm_anti = np.array(rm_anti)
corr = np.corrcoef(rm_anti[:, 0], rm_anti[:, 1])[0, 1]
log(f"  對徑對 30° mean 相關: r = {corr:+.3f}")
# random 對比
corrs = []
for _ in range(500):
    i, j = rng.choice(60, 2, replace=False)
    corrs.append((region_means[i], region_means[j]))
corrs = np.array(corrs)
corr_r = np.corrcoef(corrs[:, 0], corrs[:, 1])[0, 1]
log(f"  random pair 30° mean 相關: r = {corr_r:+.3f}")
# 0↔57 嘅區域 mean 差排名
d_rm = [abs(region_means[i]-region_means[j]) for _, i, j in pairs]
d_rm = np.array(d_rm)
d_057_rm = abs(region_means[0]-region_means[57])
rank_rm = (d_rm <= d_057_rm).sum()
log(f"  0↔57 區域 mean 差 = {d_057_rm:.2f} — 30 對中第 {rank_rm} 細 (共 {len(d_rm)} 對)")

# ============ 4. 溫度符號對 (互補性) ============
log("\n=== 4. 對徑對溫度符號 ===")
opposite = 0
for _, i, j in pairs:
    if (T[i] > 0) != (T[j] > 0):
        opposite += 1
log(f"  異號對: {opposite}/{len(pairs)} (random 期望 ~50%)")
# 冷斑對: -134 vs +8 → 異號
log(f"  0↔57: {T[0]:+.1f} vs {T[57]:+.1f} → {'異號 ✓' if (T[0]>0)!=(T[57]>0) else '同號'}")

# ============ 5. 對徑 hop 對稱 ============
log("\n=== 5. hop 和 = 8 驗證 ===")
hop_sums = [hop[i]+hop[j] for _, i, j in pairs]
log(f"  hop 和: {sorted(set(hop_sums))} (全部 8 = {all(h==8 for h in hop_sums)})")

with open(os.path.join(OUT, "node57_antipodal_results.txt"), "w") as f:
    f.write("\n".join(results) + "\n")
print(f"\n✅ 結果寫入 {OUT}/node57_antipodal_results.txt")
