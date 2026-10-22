#!/usr/bin/env python3
"""
14_hot_ring_geometry.py — O25: 熱環徑向結構 + 節點間距幾何檢驗
================================================================
開放問題 #2: 熱環半徑 20-30° vs 節點間距 26° — 巧合定結構?

檢驗:
1. 熱環徑向掃描: node9 四周 0-45° 每 2° 環帶溫度 — 熱環真正峰喺邊?
2. 節點間距分佈: A₅ 60 節點所有對距離 — 26° 係咪特殊?
3. node9 熱環峰 vs 最近節點距離比較
4. 冷區中心熱環: 冷區中心 (197.74, -20.26) 有冇更強熱環?
"""
import healpy as hp
import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u
import os, json

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
CACHE = os.path.join(BASE, "o25_scale_spectrum", "data", "smooth_cache_large")
DATA = os.path.join(BASE, "o25_scale_spectrum", "data")

node9 = {"l": 214.92, "b": -31.16}
cold_center = {"l": 197.74, "b": -20.26}

m = hp.read_map(os.path.join(CACHE, "Commander_smooth15.0.fits"), field=0)
m_low = hp.ud_grade(m, 512)
nside_low = 512

print("=" * 70)
print("熱環徑向結構 + 節點間距幾何檢驗")
print("=" * 70)

# ============ 1. 熱環徑向掃描 ============
print("\n[1] node9 四周徑向環帶溫度 (每 2°, Commander 15° 平滑)")
def ring_profiles(l_deg, b_deg, max_r=46, step=2):
    vec = hp.ang2vec(l_deg, b_deg, lonlat=True)
    rings = []
    for r0 in range(0, max_r, step):
        r1 = r0 + step
        d_out = hp.query_disc(nside_low, vec, np.radians(r1))
        if r0 == 0:
            ring = d_out
        else:
            d_in = hp.query_disc(nside_low, vec, np.radians(r0))
            ring = np.setdiff1d(d_out, d_in)
        rings.append((r0+step/2, m_low[ring].mean()*1e6, m_low[ring].std()*1e6))
    return np.array(rings)

for name, pos in [("node9", node9), ("冷區中心", cold_center)]:
    prof = ring_profiles(pos["l"], pos["b"])
    print(f"\n  {name} ({pos['l']:.1f}, {pos['b']:.1f}):")
    for r, t, s in prof:
        bar = "█" * max(0, int((t + 10) / 3))
        print(f"    {r:>5.1f}°: {t:>+7.2f} μK {bar}")
    # 熱環峰
    imax = np.argmax(prof[:, 1])
    print(f"    → 最熱環帶: {prof[imax, 0]:.1f}° ({prof[imax, 1]:+.2f} μK)")

# ============ 2. 節點間距分佈 ============
print("\n[2] A₅ 節點間距分佈 (60 節點, 全部對)")
nodes = []
with open(os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")) as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic

def angdist_mat(l_arr, b_arr):
    # 所有對距離
    n = len(l_arr)
    d = np.zeros((n, n))
    for i in range(n):
        for j in range(i+1, n):
            l1, b1, l2, b2 = map(np.radians, [l_arr[i], b_arr[i], l_arr[j], b_arr[j]])
            d[i, j] = d[j, i] = np.degrees(np.arccos(np.clip(
                np.sin(b1)*np.sin(b2)+np.cos(b1)*np.cos(b2)*np.cos(l1-l2), -1, 1)))
    return d

D = angdist_mat(gal.l.deg, gal.b.deg)
pairs = D[np.triu_indices(60, k=1)]
print(f"  總對數: {len(pairs)}")
print(f"  距離統計: min={pairs.min():.2f}°, median={np.median(pairs):.2f}°, max={pairs.max():.2f}°")
# 最近距離 (節點間距)
nn = np.sort(pairs)[:20]
print(f"  最近 20 對距離: {np.round(nn, 2)}")
# 26° 附近有幾多對?
n26 = ((pairs > 24) & (pairs < 28)).sum()
print(f"  24-28° 對數: {n26} ({n26/len(pairs)*100:.1f}%)")
# 直方圖 bin
hist, edges = np.histogram(pairs, bins=18, range=(0, 180))
print("\n  距離直方圖:")
for i in range(18):
    bar = "█" * int(hist[i] / max(hist.max(), 1) * 60)
    print(f"    {edges[i]:>5.1f}-{edges[i+1]:>5.1f}°: {hist[i]:4d} {bar}")

# ============ 3. node9 最近節點 ============
print("\n[3] node9 嘅節點間距")
d9 = D[9]
order = np.argsort(d9)
print(f"  node9 最近鄰居:")
for i in order[1:6]:
    print(f"    node {i:2d}: {d9[i]:.2f}°")
print(f"  node9 平均距離: {d9[d9>0].mean():.2f}°")

# ============ 4. 冷區中心熱環 vs node9 ============
print("\n[4] 熱環比較: node9 vs 冷區中心")
for name, pos in [("node9", node9), ("冷區中心", cold_center)]:
    vec = hp.ang2vec(pos["l"], pos["b"], lonlat=True)
    d20 = hp.query_disc(nside_low, vec, np.radians(20.0))
    # 熱環峰位置用最熱 5° 環帶
    prof = ring_profiles(pos["l"], pos["b"])
    imax = np.argmax(prof[:, 1])
    r_peak = prof[imax, 0]
    t_peak = prof[imax, 1]
    t_disc = m_low[d20].mean() * 1e6
    print(f"  {name}: 20°盤={t_disc:+.2f}, 熱環峰@{r_peak:.0f}°={t_peak:+.2f}, 峰-盤={t_peak-t_disc:+.2f}")

# 儲存
out = {
    "node9_rings": [[float(r), float(t)] for r, t, s in ring_profiles(node9["l"], node9["b"])],
    "coldcenter_rings": [[float(r), float(t)] for r, t, s in ring_profiles(cold_center["l"], cold_center["b"])],
    "pair_dist_stats": {"min": float(pairs.min()), "median": float(np.median(pairs)), "max": float(pairs.max()),
                         "n_24_28": int(n26), "frac_24_28": float(n26/len(pairs))},
    "nearest_20": [float(x) for x in nn],
    "node9_neighbors": [{"node": int(i), "dist": float(d9[i])} for i in order[1:6]],
}
with open(os.path.join(DATA, "hot_ring_geometry.json"), "w") as f:
    json.dump(out, f, indent=2)
print("\n✅ saved data/hot_ring_geometry.json")
