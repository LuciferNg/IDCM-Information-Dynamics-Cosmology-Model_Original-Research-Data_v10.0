#!/usr/bin/env python3
"""
05_commander_anomaly.py — O27: Commander @ node47 異常調查
==========================================================
Commander @ node47 = -146.7 μK vs SMICA -135.7 / NILC -132.9 (spread 9.95%)
但 node0 只有 0.67% spread。

假設: Commander 喺銀河面 (|b|<20°) 有系統偏差 (比 SMICA/NILC 更冷)。
測試: 60 節點中 |b|<20° 嘅 23 節點, Commander vs SMICA 差 vs 高緯節點。
"""
import healpy as hp
import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u
import os, json

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
OUT = os.path.join(BASE, "o27_node47_foreground")
O3CACHE = "/tmp/cache_o3"

nodes = []
with open(os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")) as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic

print("=" * 70)
print("O27: Commander @ node47 異常調查")
print("=" * 70)

# 3.0° 三地圖
ms = hp.read_map(os.path.join(O3CACHE, "SMICA_smooth3.0.fits"), field=0)
mn = hp.read_map(os.path.join(O3CACHE, "NILC_3.0.fits"), field=0)
mc = hp.read_map(os.path.join(O3CACHE, "Commander_3.0.fits"), field=0)
nside = hp.get_nside(ms)
pix = hp.ang2pix(nside, gal.l.deg, gal.b.deg, lonlat=True)

Ts, Tn, Tc = ms[pix]*1e6, mn[pix]*1e6, mc[pix]*1e6
low = np.abs(gal.b.deg) < 20
high = ~low

d_cs = Tc - Ts
d_ns = Tn - Ts

print(f"節點分類: 低緯 {low.sum()}, 高緯 {high.sum()}")
print(f"\nCommander-SMICA 差 (μK):")
print(f"  低緯: mean={d_cs[low].mean():+6.1f}  std={d_cs[low].std():5.1f}")
print(f"  高緯: mean={d_cs[high].mean():+6.1f}  std={d_cs[high].std():5.1f}")
print(f"\nNILC-SMICA 差 (μK):")
print(f"  低緯: mean={d_ns[low].mean():+6.1f}  std={d_ns[low].std():5.1f}")
print(f"  高緯: mean={d_ns[high].mean():+6.1f}  std={d_ns[high].std():5.1f}")

# 每節點明細
print(f"\n{'node':<5}{'b':>7}{'SMICA':>9}{'NILC':>9}{'Comm':>9}{'C-S':>8}")
for i in np.argsort(np.abs(d_cs))[::-1][:12]:
    print(f"{i:<5}{gal.b.deg[i]:>+7.1f}{Ts[i]:>+9.1f}{Tn[i]:>+9.1f}{Tc[i]:>+9.1f}{d_cs[i]:>+8.1f}")

# 統計
from scipy import stats
t, p = stats.ttest_ind(d_cs[low], d_cs[high])
print(f"\n低緯 vs 高緯 C-S 差: t={t:.2f}, p={p:.4f}")

# node47 局部 (0.5°-5°) Commander vs SMICA
print(f"\n--- node47 週邊 Commander vs SMICA (3.0°) ---")
l47, b47 = gal.l.deg[47], gal.b.deg[47]
for rad in [0.5, 1.0, 2.0, 3.0, 5.0]:
    vec = hp.ang2vec(l47, b47, lonlat=True)
    p_disc = hp.query_disc(nside, vec, np.radians(rad))
    d = (mc[p_disc] - ms[p_disc]) * 1e6
    print(f"  ≤{rad:>4.1f}°: C-S mean={d.mean():+6.1f}  std={d.std():5.1f}  (n={len(p_disc)})")

with open(os.path.join(OUT, "data/commander_anomaly.json"), "w") as f:
    json.dump({"low_lat_CminusS_mean": float(d_cs[low].mean()),
               "high_lat_CminusS_mean": float(d_cs[high].mean()),
               "low_lat_NminusS_mean": float(d_ns[low].mean()),
               "high_lat_NminusS_mean": float(d_ns[high].mean()),
               "ttest_p": float(p)}, f, indent=2)
print(f"\n✅ 已存 data/commander_anomaly.json")
