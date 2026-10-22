#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O182 scripts/09 — G88 極端節點: 點源/前景檢查 (1.5° disc min/max)"""
import numpy as np
import healpy as hp
from pathlib import Path

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
OUT = ROOT / "o182_88grid_geometry/data"

extreme = {31: "b=-6.26", 29: "b=+1.53", 69: "b=-3.83", 77: "b=-15.09",
           27: "b=-24.09", 2: "b=-67.43", 68: "b=+21.35", 57: "b=-28.29"}

lb = np.loadtxt(OUT / "g88_nodes.txt")
from astropy.coordinates import SkyCoord
import astropy.units as u
sc = SkyCoord(ra=lb[:, 0]*u.deg, dec=lb[:, 1]*u.deg, frame='icrs')
g = sc.galactic
gl, gb = g.l.deg, g.b.deg

# 讀 4.17° 平滑 SMICA (n512 快速版)
m = hp.read_map(str(ROOT / "o175_entropy_theorem/data/planck/COM_CMB_IQU-smica_2048_R3.00_full.fits"), field=0).astype(np.float64)
m512 = hp.ud_grade(m, 512, order_in='RING')
ms = hp.smoothing(m512, fwhm=np.radians(4.17), verbose=False)
ms = hp.remove_dipole(ms, verbose=False)
nside = 512

# 每個極端節點: 1.5° disc min/max 像素 (raw map — 點源喺 raw 先見到)
mraw = hp.ud_grade(m, 2048, order_in='RING')  # 用全解像 raw
npix = hp.nside2npix(2048)
th, ph = hp.pix2ang(2048, np.arange(npix))
raw_b = 90 - np.degrees(th)

print("節點  l      b      | 4.17°δT   | 1.5°disc min(μK) | 1.5°disc max(μK) | 判斷")
for i in sorted(extreme):
    l0, b0 = gl[i], gb[i]
    dT = None
    # disc 像素: 角距離 < 1.5°
    v0 = np.array([np.cos(np.radians(b0))*np.cos(np.radians(l0)),
                   np.cos(np.radians(b0))*np.sin(np.radians(l0)), np.sin(np.radians(b0))])
    vv = np.column_stack([np.cos(np.radians(raw_b))*np.cos(ph),
                          np.cos(np.radians(raw_b))*np.sin(ph), np.sin(np.radians(raw_b))])
    cosang = vv @ v0
    disc = cosang > np.cos(np.radians(1.5))
    vals = mraw[disc] * 1e6
    finite = vals[np.isfinite(vals)]
    print(f"  {i:2d}  {l0:7.2f} {b0:+7.2f} |           | min={finite.min():+8.1f}   | max={finite.max():+8.1f}   | "
          f"{'⚠️ 點源/前景' if abs(finite.min())>500 or abs(finite.max())>500 else '正常 CMB'}")

# 對比: 隨機 60 個背景 disc 嘅 min/max 範圍
print("\n背景對比 (隨機 20 disc):")
rng = np.random.default_rng(3)
bgs = []
for _ in range(20):
    l0 = rng.uniform(0, 360); b0 = np.degrees(np.arcsin(rng.uniform(-1, 1)))
    v0 = np.array([np.cos(np.radians(b0))*np.cos(np.radians(l0)),
                   np.cos(np.radians(b0))*np.sin(np.radians(l0)), np.sin(np.radians(b0))])
    disc = (vv @ v0) > np.cos(np.radians(1.5))
    vals = mraw[disc] * 1e6
    finite = vals[np.isfinite(vals)]
    bgs.append((finite.min(), finite.max()))
bgs = np.array(bgs)
print(f"  背景 disc min: {bgs[:,0].mean():+6.1f}±{bgs[:,0].std():.1f} μK, max: {bgs[:,1].mean():+6.1f}±{bgs[:,1].std():.1f} μK")
print("\nRESULT: 點源檢查完成")
