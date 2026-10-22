#!/usr/bin/env python3
"""
04_antipode_check.py — O27: 對徑反查 + 週邊環境
================================================
node47 (313.47°, -8.58°) 對徑 = (133.47°, +8.58°)
檢查:
1. 對徑點喺 3 個尺度嘅溫度 (對稱性測試: 真冷結構唔應該有對徑對稱)
2. node47 週邊 5°-30° 環境 (冷/熱/中性)
3. 對照: node0 (冷斑) 週邊 5°-30° 環境
"""
import healpy as hp
import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u
import os, json

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
OUT = os.path.join(BASE, "o27_node47_foreground")
CACHE = os.path.join(BASE, "o5_catalog_compare/data/smooth_cache")
NODE47 = 47

nodes = []
with open(os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")) as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic

# node47 對徑 (銀道坐標直接取反)
l47, b47 = gal.l.deg[NODE47], gal.b.deg[NODE47]
l_anti = (l47 + 180) % 360
b_anti = -b47
print("=" * 70)
print("O27: 對徑反查 + 週邊環境")
print("=" * 70)
print(f"node47: l={l47:.2f}° b={b47:.2f}°")
print(f"對徑:   l={l_anti:.2f}° b={b_anti:.2f}°")

# 對徑溫度 (多尺度)
print(f"\n--- 對徑點溫度 (SMICA) ---")
anti_T = []
for fwhm in [0.5, 1.0, 3.0, 4.17, 5.0, 10.0]:
    fname = os.path.join(CACHE, f"smica2_smooth{fwhm}.fits")
    if not os.path.exists(fname):
        continue
    m = hp.read_map(fname, field=0)
    nside = hp.get_nside(m)
    pix = hp.ang2pix(nside, l_anti, b_anti, lonlat=True)
    T = m[pix] * 1e6
    anti_T.append({"fwhm": fwhm, "T_anti": float(T)})
    print(f"  {fwhm:>5.1f}°  T_anti={T:+8.1f} μK   (node47: {'-135.7' if fwhm==3.0 else '...'})")

# node47 週邊環境 (3.0° SMICA): 0-5° 內 mean/std (唔計中心)
print(f"\n--- node47 週邊環境 (3.0° SMICA) ---")
m3 = hp.read_map(os.path.join(CACHE, "smica2_smooth3.0.fits"), field=0)
nside3 = hp.get_nside(m3)
env = {}
for rad in [3.0, 5.0, 8.0, 12.0, 20.0, 30.0]:
    vec = hp.ang2vec(l47, b47, lonlat=True)
    pix = hp.query_disc(nside3, vec, np.radians(rad))
    T = m3[pix] * 1e6
    # 減去中心像素
    pix_c = hp.ang2pix(nside3, l47, b47, lonlat=True)
    T_core = m3[pix_c] * 1e6
    T_ring = T[np.abs(m3[pix]*1e6 - T_core) > 1e-9]  # 排除中心
    env[rad] = {"mean": float(T_ring.mean()), "std": float(T_ring.std()),
                "min": float(T_ring.min()), "max": float(T_ring.max())}
    print(f"  ≤{rad:>4.1f}°: mean={T_ring.mean():+7.1f}  std={T_ring.std():5.1f}  "
          f"min={T_ring.min():+7.1f}  max={T_ring.max():+7.1f}  (n={len(T_ring)})")

# 對照: node0 (冷斑) 週邊
print(f"\n--- node0 (冷斑) 週邊環境 (3.0° SMICA) 對照 ---")
l0, b0 = gal.l.deg[0], gal.b.deg[0]
env0 = {}
for rad in [3.0, 5.0, 8.0, 12.0, 20.0, 30.0]:
    vec = hp.ang2vec(l0, b0, lonlat=True)
    pix = hp.query_disc(nside3, vec, np.radians(rad))
    T = m3[pix] * 1e6
    pix_c = hp.ang2pix(nside3, l0, b0, lonlat=True)
    T_core = m3[pix_c] * 1e6
    T_ring = T[np.abs(m3[pix]*1e6 - T_core) > 1e-9]
    env0[rad] = {"mean": float(T_ring.mean()), "std": float(T_ring.std()),
                 "min": float(T_ring.min()), "max": float(T_ring.max())}
    print(f"  ≤{rad:>4.1f}°: mean={T_ring.mean():+7.1f}  std={T_ring.std():5.1f}  "
          f"min={T_ring.min():+7.1f}  max={T_ring.max():+7.1f}  (n={len(T_ring)})")

with open(os.path.join(OUT, "data/antipode_node47.json"), "w") as f:
    json.dump({"anti_T": anti_T, "env47": env, "env0": env0,
               "anti_coord": {"l": l_anti, "b": b_anti}}, f, indent=2)
print(f"\n✅ 已存 data/antipode_node47.json")
