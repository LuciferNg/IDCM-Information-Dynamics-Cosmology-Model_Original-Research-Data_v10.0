#!/usr/bin/env python3
"""
02_crossmap_node47.py — O27: 三地圖一致性 @ node47
===================================================
SMICA / NILC / Commander @ node47 (l=313.47°, b=-8.58°)
尺度: 3.0° (問題尺度) + 4.17° (O3 標準) + 5.0°

判定: <5% spread 🟢🟢; 1-5% 🟢; 5-20% 🟡; >20% 🔴
"""
import healpy as hp
import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u
import os, json

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
OUT = os.path.join(BASE, "o27_node47_foreground")
O3CACHE = "/tmp/cache_o3"   # O3 平滑 cache (三地圖 × 10 尺度)
O5CACHE = os.path.join(BASE, "o5_catalog_compare/data/smooth_cache")

NODE47 = 47

nodes = []
with open(os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")) as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic
l47, b47 = gal.l.deg[NODE47], gal.b.deg[NODE47]

print("=" * 70)
print("O27: 三地圖一致性 @ node47")
print("=" * 70)
print(f"node47: l={l47:.2f}° b={b47:.2f}°")

# map 檔案策略: O3 cache 有 3.0/5.0 (SMICA 係 symlink 去 O5)
# O5 cache 有全部 10 尺度 SMICA; NILC/Commander 只有 4.17°
maps = {
    "SMICA":    {"3.0": os.path.join(O3CACHE, "SMICA_smooth3.0.fits"),
                 "4.17": os.path.join(O5CACHE, "smica2_smooth4.17.fits"),
                 "5.0": os.path.join(O3CACHE, "SMICA_smooth5.0.fits")},
    "NILC":     {"3.0": os.path.join(O3CACHE, "NILC_3.0.fits"),
                 "4.17": os.path.join(O3CACHE, "NILC_4.17.fits"),
                 "5.0": os.path.join(O3CACHE, "NILC_5.0.fits")},
    "Commander":{"3.0": os.path.join(O3CACHE, "Commander_3.0.fits"),
                 "4.17": os.path.join(O3CACHE, "Commander_4.17.fits"),
                 "5.0": os.path.join(O3CACHE, "Commander_5.0.fits")},
}

# NILC/Commander cache 係 NESTED → 需要 reorder (Skill §7 pitfall)
results = []
print(f"\n{'scale':<7}{'map':<11}{'T47(μK)':<12}{'T0(μK)':<12}")
for scale in ["3.0", "4.17", "5.0"]:
    vals = {}
    for mname, paths in maps.items():
        p = paths.get(scale)
        if not p or not os.path.exists(p):
            print(f"  {scale:>5}  {mname:<11} [missing {p}]")
            continue
        m = hp.read_map(p, field=0)
        # cache 檔 (O3 生成) 已 reorder? 檢查: O3 scripts 用 RING 讀 NILC/Commander
        # 但 /tmp/cache_o3 嘅 NILC_*.fits 係平滑後 — 平滑前已 reorder 先平滑
        # (O3 11_cross_map_zeroE.py 流程: read nest → reorder n2r → smooth → cache)
        nside = hp.get_nside(m)
        pix = hp.ang2pix(nside, l47, b47, lonlat=True)
        pix0 = hp.ang2pix(nside, gal.l.deg[0], gal.b.deg[0], lonlat=True)
        vals[mname] = (m[pix]*1e6, m[pix0]*1e6)
    if len(vals) == 3:
        Ts = [v[0] for v in vals.values()]
        spread = (max(Ts) - min(Ts)) / abs(np.mean(Ts)) * 100
        T0s = [v[1] for v in vals.values()]
        spread0 = (max(T0s) - min(T0s)) / abs(np.mean(T0s)) * 100
        results.append({"scale": scale,
                        "SMICA": float(Ts[0]), "NILC": float(Ts[1]), "Commander": float(Ts[2]),
                        "spread_pct": float(spread),
                        "node0_SMICA": float(T0s[0]), "node0_NILC": float(T0s[1]), "node0_Commander": float(T0s[2]),
                        "node0_spread_pct": float(spread0)})
        print(f"  {scale:>5}  SMICA      {Ts[0]:+9.1f}      {T0s[0]:+9.1f}")
        print(f"  {'':5}  NILC       {Ts[1]:+9.1f}      {T0s[1]:+9.1f}")
        print(f"  {'':5}  Commander  {Ts[2]:+9.1f}      {T0s[2]:+9.1f}")
        print(f"  {'':5}  spread     {spread:5.2f}%      node0: {spread0:5.2f}%")
    else:
        print(f"  {scale:>5}  [只有 {len(vals)}/3 maps]")

with open(os.path.join(OUT, "data/crossmap_node47.json"), "w") as f:
    json.dump(results, f, indent=2)
print(f"\n✅ 已存 data/crossmap_node47.json")
