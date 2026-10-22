#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O182 scripts/10 — NILC 第四圖交叉 (強化「地圖一致」聲明)"""
import numpy as np
import healpy as hp
from pathlib import Path
from astropy.coordinates import SkyCoord
import astropy.units as u

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
OUT = ROOT / "o182_88grid_geometry/data"
A = 134.2

NILC = ROOT / "o175_entropy_theorem/data/planck/COM_CMB_IQU-nilc_2048_R3.00_full.fits"

def to_gal(pts):
    sc = SkyCoord(ra=pts[:, 0]*u.deg, dec=pts[:, 1]*u.deg, frame='icrs')
    g = sc.galactic
    return np.column_stack([g.l.deg, g.b.deg])

sets = {
    "A5_60": to_gal(np.loadtxt(ROOT / "cmb_cold_spot/data/a5_nodes.txt")),
    "G88": to_gal(np.loadtxt(OUT / "g88_nodes.txt")),
}

m = hp.read_map(str(NILC), field=0).astype(np.float64)
print(f"NILC: nside={hp.get_nside(m)}, len={len(m)}, finite={np.isfinite(m).mean():.4f}")

for fwhm in [4.17, 5.0]:
    ms = hp.smoothing(m, fwhm=np.radians(fwhm), verbose=False)
    ms = hp.remove_dipole(ms, verbose=False)
    nside = hp.get_nside(ms)
    npix = len(ms)
    th_all, ph_all = hp.pix2ang(nside, np.arange(npix))
    b_all = 90 - np.degrees(th_all)
    sm = np.std(ms[np.abs(b_all) > 20]) * 1e6
    for sname, pts in sets.items():
        pix = hp.ang2pix(nside, pts[:, 0], pts[:, 1], lonlat=True)
        T = ms[pix] * 1e6
        dT = T - T.mean()
        print(f"NILC {fwhm}° {sname}: M1 = {np.mean(np.abs(dT))/A:.5f}  (σ|b|>20={sm:.1f})")
