#!/usr/bin/env python3
"""
01_node47_multiscale.py — O27: 節點 47 多尺度穩定性 (SMICA)
===========================================================
node47 (l=313.47°, b=-8.58°) 係 3.0° 第二冷 (-135.7 μK)。
測試 0.5°-10° 平滑下溫度是否穩定偏冷 + 排名。

使用 O5 smooth cache (SMICA × 10 尺度)。
"""
import healpy as hp
import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u
import os, json

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
OUT = os.path.join(BASE, "o27_node47_foreground")
CACHE = os.path.join(BASE, "o5_catalog_compare/data/smooth_cache")

# 節點 47 (a5_nodes.txt 第 48 行, 0-index 47)
NODE47_IDX = 47
NODE0_IDX = 0

nodes = []
with open(os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")) as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic

print("=" * 70)
print("O27: 節點 47 多尺度穩定性 (SMICA)")
print("=" * 70)
print(f"node47: l={gal.l.deg[NODE47_IDX]:.2f}° b={gal.b.deg[NODE47_IDX]:.2f}°")
print(f"node0 (冷斑): l={gal.l.deg[NODE0_IDX]:.2f}° b={gal.b.deg[NODE0_IDX]:.2f}°")

scales = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 4.17, 5.0, 7.0, 10.0]
results = []
for fwhm in scales:
    fname = os.path.join(CACHE, f"smica2_smooth{fwhm}.fits")
    if not os.path.exists(fname):
        print(f"  [skip] cache {fname} 唔存在")
        continue
    m = hp.read_map(fname, field=0)
    nside = hp.get_nside(m)
    pix = hp.ang2pix(nside, gal.l.deg, gal.b.deg, lonlat=True)
    T = m[pix] * 1e6
    # 排序
    order = np.argsort(T)  # 最冷排最前
    rank47 = int(np.where(order == NODE47_IDX)[0][0]) + 1
    rank0 = int(np.where(order == NODE0_IDX)[0][0]) + 1
    results.append({
        "fwhm": fwhm,
        "T47_uK": float(T[NODE47_IDX]),
        "T0_uK": float(T[NODE0_IDX]),
        "rank47": rank47,
        "rank0": rank0,
        "mean_uK": float(T.mean()),
        "std_uK": float(T.std()),
        "min_node": int(np.argmin(T)),
        "min_T_uK": float(T.min()),
        "max_node": int(np.argmax(T)),
        "max_T_uK": float(T.max()),
    })
    print(f"  {fwhm:>5.2f}°  T47={T[NODE47_IDX]:+8.1f}  rank47={rank47:>2}/60   "
          f"T0={T[NODE0_IDX]:+8.1f}  rank0={rank0:>2}/60  min={results[-1]['min_node']}:{T.min():+.1f}")

with open(os.path.join(OUT, "data/node47_multiscale.json"), "w") as f:
    json.dump(results, f, indent=2)
print(f"\n✅ 已存 data/node47_multiscale.json ({len(results)} scales)")
