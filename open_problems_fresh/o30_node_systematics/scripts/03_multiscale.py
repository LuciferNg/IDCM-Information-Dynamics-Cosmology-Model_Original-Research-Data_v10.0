#!/usr/bin/env python3
"""
03_multiscale.py — O30: 多尺度 (0.5°-10°) 系統性
==================================================
問題: 60節點微冷系統性隨平滑尺度點變?
方法:
  1. 每尺度 cache (0.5/1.0/1.5/2.0/3.0/4.0/4.17/5.0/7.0/10.0°) → 抽 60 節點
  2. mean vs 1000 組各向同性隨機 (每尺度) → z(scale)
  3. 高緯子集重複
  4. 剔除 node0/node9 重複
  5. 檢查 z(scale) 有冇尺度趨勢 (系統性 vs 單一尺度)
框架: ICRS→Galactic
"""
import healpy as hp
import numpy as np
import os
from astropy.coordinates import SkyCoord
import astropy.units as u
from scipy import stats

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
CACHE_DIR = os.path.join(BASE, "o5_catalog_compare/data/smooth_cache")
NODES = os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")
OUT = os.path.join(BASE, "o30_node_systematics/data")

RNG = np.random.default_rng(20260817)
N_CONTROL = 1000
SCALES = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 4.17, 5.0, 7.0, 10.0]
MAPS = {0.5: "smica2_smooth0.5.fits", 1.0: "smica2_smooth1.0.fits",
        1.5: "smica2_smooth1.5.fits", 2.0: "smica2_smooth2.0.fits",
        3.0: "smica2_smooth3.0.fits", 4.0: "smica2_smooth4.0.fits",
        4.17: "smica2_smooth4.17.fits", 5.0: "smica2_smooth5.0.fits",
        7.0: "smica2_smooth7.0.fits", 10.0: "smica2_smooth10.0.fits"}

print("=" * 66)
print("O30-03: 多尺度系統性 (0.5°-10°)")
print("=" * 66)

# 節點 (一次轉換)
nodes = np.loadtxt(NODES)
sc = SkyCoord(ra=nodes[:,0]*u.deg, dec=nodes[:,1]*u.deg, frame='icrs')
gal = sc.galactic
l_deg, b_deg = gal.l.deg, gal.b.deg
hi_mask = np.abs(b_deg) >= 30
keep = np.array([i for i in range(60) if i not in (0, 9)])

rows = []
print(f"{'scale':>6} {'N mean':>8} {'HI mean':>8} {'z':>7} {'z_hi':>7} {'z_drop':>7}")
for s in SCALES:
    f = os.path.join(CACHE_DIR, MAPS[s])
    m = hp.read_map(f, field=0)
    nside = hp.get_nside(m)
    npix = hp.nside2npix(nside)
    pix = hp.ang2pix(nside, l_deg, b_deg, lonlat=True)
    T = m[pix] * 1e6

    # 控制組 (各向同性)
    ctrl = np.empty(N_CONTROL)
    ctrl_hi = np.empty(N_CONTROL)
    for k in range(N_CONTROL):
        rpix = RNG.integers(0, npix, size=60)
        Tc = m[rpix] * 1e6
        ctrl[k] = Tc.mean()
        ctrl_hi[k] = Tc[hi_mask].mean()

    z = (T.mean() - ctrl.mean()) / ctrl.std(ddof=1)
    z_hi = (T[hi_mask].mean() - ctrl_hi.mean()) / ctrl_hi.std(ddof=1)

    # 剔除 0,9
    ctrl_k = np.empty(N_CONTROL)
    for k in range(N_CONTROL):
        rpix = RNG.integers(0, npix, size=len(keep))
        ctrl_k[k] = m[rpix].mean() * 1e6
    z_drop = (T[keep].mean() - ctrl_k.mean()) / ctrl_k.std(ddof=1)

    rows.append((s, T.mean(), T[hi_mask].mean(), z, z_hi, z_drop))
    print(f"{s:>6.2f} {T.mean():>+8.2f} {T[hi_mask].mean():>+8.2f} {z:>+7.2f} {z_hi:>+7.2f} {z_drop:>+7.2f}")

# 尺度趨勢: z(scale) 有冇系統性?
z_all = np.array([r[3] for r in rows])
z_hi = np.array([r[4] for r in rows])
z_drop = np.array([r[5] for r in rows])
print(f"\nz 範圍: all [{z_all.min():+.2f}, {z_all.max():+.2f}], hi [{z_hi.min():+.2f}, {z_hi.max():+.2f}], drop [{z_drop.min():+.2f}, {z_drop.max():+.2f}]")
print(f"z mean: all {z_all.mean():+.2f}, hi {z_hi.mean():+.2f}, drop {z_drop.mean():+.2f}")

# 儲存
with open(os.path.join(OUT, "03_multiscale.txt"), "w") as f:
    f.write("# O30-03: 多尺度系統性 (μK)\n")
    f.write(f"# 日期: 2026-08-21, 控制組 {N_CONTROL}/尺度\n")
    f.write("# scale node_mean hi_mean z z_hi z_drop\n")
    for r in rows:
        f.write(f"{r[0]:.2f} {r[1]:+.3f} {r[2]:+.3f} {r[3]:+.3f} {r[4]:+.3f} {r[5]:+.3f}\n")

print(f"\n✅ 已存: {os.path.join(OUT, '03_multiscale.txt')}")
