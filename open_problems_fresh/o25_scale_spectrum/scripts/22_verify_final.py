#!/usr/bin/env python3
"""
22_verify_final.py — O25: 最終驗證 (scripts/19-21)
===================================================
獨立重算:
1. l=3 冷軸 (82.09, 17.04) — 最近節點 z=-0.18σ 冇對齊
2. l=3 冷極 + 冷區中心值
3. τ 確認: 5 點線性衰減 slope
4. Eridanus 距離
"""
import healpy as hp
import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u
import os, sys, json

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
CACHE = os.path.join(BASE, "o25_scale_spectrum", "data", "smooth_cache_large")
DATA = os.path.join(BASE, "o25_scale_spectrum", "data")

m = hp.read_map(os.path.join(CACHE, "Commander_smooth15.0.fits"), field=0)
m_low = hp.ud_grade(m, 512)
nside_low = 512

passes, fails = 0, 0
def check(name, claimed, recomputed, tol):
    global passes, fails
    if isinstance(claimed, bool):
        if bool(recomputed) == claimed:
            passes += 1
            print(f"  ✅ {name}: {claimed} == {bool(recomputed)}")
        else:
            fails += 1
            print(f"  ❌ {name}: claimed={claimed} recomputed={bool(recomputed)}")
        return
    if abs(claimed - recomputed) <= tol:
        passes += 1
        print(f"  ✅ {name}: {claimed} ≈ {recomputed:.2f}")
    else:
        fails += 1
        print(f"  ❌ {name}: claimed={claimed} recomputed={recomputed:.2f}")

print("O25 最終驗證 (l=3 軸 + τ + Eridanus)")
print("=" * 60)

# 1. l=3 冷軸
alm = hp.map2alm(m_low, lmax=10)
n_alm = hp.Alm.getsize(10)
alm3 = np.zeros(n_alm, dtype=complex)
for mm in range(-3, 4):
    idx = hp.Alm.getidx(10, 3, abs(mm))
    alm3[idx] = alm[idx]
only3 = hp.alm2map(alm3, nside_low, lmax=10)
ipix_min = np.argmin(only3)
l_min, b_min = hp.pix2ang(nside_low, ipix_min, lonlat=True)
l_min = float(np.asarray(l_min).item()); b_min = float(np.asarray(b_min).item())
print(f"  l=3 冷軸: ({l_min:.2f}, {b_min:.2f})")
check("l=3 冷軸 l", 82.09, l_min, 2.0)
check("l=3 冷軸 b", 17.04, b_min, 2.0)

# 2. 冷區中心 l=3 值
pix_cc = hp.ang2pix(nside_low, 197.74, -20.26, lonlat=True)
l3_cc = only3[pix_cc] * 1e6
check("冷區中心 l=3", -29.99, l3_cc, 1.0)

# 3. l=3 冷軸最近節點
nodes = []
with open(os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")) as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic

def angdist(l1, b1, l2, b2):
    l1, b1, l2, b2 = map(np.radians, [l1, b1, l2, b2])
    return np.degrees(np.arccos(np.clip(np.sin(b1)*np.sin(b2)+np.cos(b1)*np.cos(b2)*np.cos(l1-l2), -1, 1)))

d_l3 = [angdist(l_min, b_min, gal.l.deg[i], gal.b.deg[i]) for i in range(60)]
i_min = np.argmin(d_l3)
print(f"  l=3 冷軸最近節點: node {i_min} ({d_l3[i_min]:.2f}°)")
check("l=3 最近節點 node23", 23, i_min, 0)
check("l=3 最近節點距離", 9.47, d_l3[i_min], 1.0)

# 4. τ 衰減線性 (從 tau_confirm.json)
with open(os.path.join(DATA, "tau_confirm.json")) as f:
    tc = json.load(f)
slope = tc["linear"]["slope"]
check("τ 線性 slope", 1.202, slope, 0.1)
print(f"  τ 線性 slope: {slope:.3f} μK/°")

# 5. Eridanus 距離
d_erid = angdist(197.74, -20.26, 209.6, -56.0)
print(f"  Eridanus 距離: {d_erid:.1f}°")
check("Eridanus > 20° (唔係同一結構)", True, d_erid > 20, 0)

print(f"\n{'='*60}")
print(f"結果: {passes} PASS, {fails} FAIL")
sys.exit(1 if fails else 0)
