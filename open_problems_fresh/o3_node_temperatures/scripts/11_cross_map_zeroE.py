#!/usr/bin/env python3
"""
11_cross_map_zeroE.py — O3: 三地圖交叉驗證高緯度 ΔE=0 節點
============================================================
SMICA / NILC / Commander 對比高緯度 4 個 ΔE=0 節點
(Skill §12: NILC/Commander 要 nest=True + reorder n2r)
"""
import healpy as hp
import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u
import os

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
ZERO_E_HIGH = [10, 22, 25, 32]

nodes = []
with open(os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")) as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic

fwhm = 4.17
sigma = np.radians(fwhm) / (2 * np.sqrt(2 * np.log(2)))

# SMICA (RING)
ms = hp.read_map('/tmp/smica2.fits')
ms = hp.remove_dipole(hp.smoothing(ms, sigma=sigma))
ps = hp.ang2pix(hp.get_nside(ms), gal.l.deg, gal.b.deg, lonlat=True)

# NILC (NESTED → RING)
mn = hp.read_map('/tmp/nilc.fits', field=0, nest=True)
mn = hp.reorder(mn, n2r=True)
mn = hp.remove_dipole(hp.smoothing(mn, sigma=sigma))
pn = hp.ang2pix(hp.get_nside(mn), gal.l.deg, gal.b.deg, lonlat=True)

# Commander (NESTED → RING)
mc = hp.read_map('/tmp/commander.fits', field=0, nest=True)
mc = hp.reorder(mc, n2r=True)
mc = hp.remove_dipole(hp.smoothing(mc, sigma=sigma))
pc = hp.ang2pix(hp.get_nside(mc), gal.l.deg, gal.b.deg, lonlat=True)

print("=== 高緯度 ΔE=0 節點 (4個) 三地圖對比 ===")
print(f"{'node':<6}{'SMICA':<12}{'NILC':<12}{'Commander':<12}")
Ts, Tn, Tc = [], [], []
for i in ZERO_E_HIGH:
    ts, tn, tc = ms[ps[i]]*1e6, mn[pn[i]]*1e6, mc[pc[i]]*1e6
    Ts.append(ts); Tn.append(tn); Tc.append(tc)
    print(f"#{i:<4}{ts:+9.2f}   {tn:+9.2f}   {tc:+9.2f}")
print(f"mean|T|: SMICA={np.abs(Ts).mean():.2f}  NILC={np.abs(Tn).mean():.2f}  Commander={np.abs(Tc).mean():.2f}")

# 高緯度其他 34 節點對照
rows2 = []
with open(os.path.join(BASE, "o3_node_temperatures/data/node_temps.txt")) as f:
    for line in f:
        if line.startswith('#') or not line.strip():
            continue
        p = line.split()
        rows2.append((int(p[0]), float(p[4])))
others_high = [i for i, bb in rows2 if abs(bb) >= 20 and i not in ZERO_E_HIGH]
os_, on_, oc_ = [], [], []
for i in others_high:
    os_.append(ms[ps[i]]*1e6)
    on_.append(mn[pn[i]]*1e6)
    oc_.append(mc[pc[i]]*1e6)
print(f"\n其他高緯度節點 (n={len(others_high)}):")
print(f"mean|T|: SMICA={np.abs(os_).mean():.2f}  NILC={np.abs(on_).mean():.2f}  Commander={np.abs(oc_).mean():.2f}")
print(f"比例 (ΔE=0/其他): SMICA={np.abs(Ts).mean()/np.abs(os_).mean():.3f}  "
      f"NILC={np.abs(Tn).mean()/np.abs(on_).mean():.3f}  "
      f"Commander={np.abs(Tc).mean()/np.abs(oc_).mean():.3f}")
print("DONE")
