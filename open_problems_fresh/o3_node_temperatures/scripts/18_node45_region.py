#!/usr/bin/env python3
"""
18_node45_region.py — Node 45 附近區域大尺度結構
==================================================
用已有 cache 分析 node 45 附近 30° 區域:
1. 5° 平滑下 node 45 附近嘅溫度場
2. 有冇大尺度冷/熱區包住 node 45
3. 對比其他 ΔE=0 節點附近
"""
import healpy as hp
import numpy as np
import math
from astropy.coordinates import SkyCoord
import astropy.units as u

nodes = []
with open('/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt') as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic

# 用 5° cache (已 remove_dipole)
m5 = hp.read_map('/tmp/smica2_smooth5.0.fits')
nside = hp.get_nside(m5)

# node 45 向量
def vec_of(i):
    return np.array([math.cos(math.radians(nodes[i,1]))*math.cos(math.radians(nodes[i,0])),
                     math.cos(math.radians(nodes[i,1]))*math.sin(math.radians(nodes[i,0])),
                     math.sin(math.radians(nodes[i,1]))])

print("=== Node 45 附近大尺度結構 (5° 平滑) ===")
v45 = vec_of(45)
# 半徑掃描
for rad in [5, 10, 15, 20, 30]:
    disc = hp.query_disc(nside, v45, np.radians(rad))
    vals = m5[disc]*1e6
    pix45 = hp.ang2pix(nside, gal.l.deg[45], gal.b.deg[45], lonlat=True)
    print(f"  {rad:>2}° 半徑: mean={vals.mean():+7.2f} std={vals.std():6.2f}  node45={m5[pix45]*1e6:+7.2f}")

print("\n=== 對比: 高緯度 4 節點附近 (5° 半徑) ===")
for i in [10, 22, 25, 32]:
    v = vec_of(i)
    disc = hp.query_disc(nside, v, np.radians(5))
    vals = m5[disc]*1e6
    pixi = hp.ang2pix(nside, gal.l.deg[i], gal.b.deg[i], lonlat=True)
    print(f"  #{i}: node={m5[pixi]*1e6:+7.2f}  5°區域 mean={vals.mean():+7.2f} std={vals.std():5.2f}")

print("\n=== 對比: 銀河盤其他 ΔE=0 節點附近 ===")
ZERO_GAL = [12, 19, 23, 28, 37, 40, 46]
for i in ZERO_GAL:
    v = vec_of(i)
    disc = hp.query_disc(nside, v, np.radians(5))
    vals = m5[disc]*1e6
    pixi = hp.ang2pix(nside, gal.l.deg[i], gal.b.deg[i], lonlat=True)
    print(f"  #{i}: node={m5[pixi]*1e6:+7.2f}  5°區域 mean={vals.mean():+7.2f} std={vals.std():5.2f}")

print("\n=== 大尺度梯度: node 45 喺咩大結構入面? ===")
# 用 10° cache 睇
m10 = hp.read_map('/tmp/smica2_smooth10.0.fits')
for i in [45] + [10, 22, 25, 32]:
    pixi = hp.ang2pix(nside, gal.l.deg[i], gal.b.deg[i], lonlat=True)
    print(f"  #{i}: 10°平滑 T={m10[pixi]*1e6:+7.2f} μK")

# Node 45 附近 30° 嘅最低/最高點 (5° 平滑)
print("\n=== Node 45 附近 30° 極值 (5° 平滑) ===")
disc30 = hp.query_disc(nside, v45, np.radians(30))
vals30 = m5[disc30]*1e6
imax = np.argmax(vals30)
imin = np.argmin(vals30)
theta_max, phi_max = hp.pix2ang(nside, disc30[imax], lonlat=True)
theta_min, phi_min = hp.pix2ang(nside, disc30[imin], lonlat=True)
print(f"  區域 max: {vals30.max():+.1f} μK @ (l={phi_max:.0f}, b={theta_max:.0f})")
print(f"  區域 min: {vals30.min():+.1f} μK @ (l={phi_min:.0f}, b={theta_min:.0f})")
print(f"  node 45 相對位置: {(m5[hp.ang2pix(nside, gal.l.deg[45], gal.b.deg[45], lonlat=True)]*1e6 - vals30.mean()):+.1f} μK vs 區域 mean")
