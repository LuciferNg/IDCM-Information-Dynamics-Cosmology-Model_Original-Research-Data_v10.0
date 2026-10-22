#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O182 scripts/05 — 採樣方法對比: ang2pix 最近像素 vs get_interp_val"""
import numpy as np
import healpy as hp
from pathlib import Path
from astropy.coordinates import SkyCoord
import astropy.units as u

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
SMICA_FULL = ROOT / "o175_entropy_theorem/data/planck/COM_CMB_IQU-smica_2048_R3.00_full.fits"

nodes = np.loadtxt(ROOT / "cmb_cold_spot/data/a5_nodes.txt")
sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic

m = hp.read_map(str(SMICA_FULL), field=0).astype(np.float64)
nside = hp.get_nside(m)
for fwhm_deg in [4.17, 5.0]:
    ms = hp.smoothing(m, fwhm=np.radians(fwhm_deg), verbose=False)
    ms = hp.remove_dipole(ms, verbose=False)
    # (a) 最近像素 (script 22 管道, galactic lonlat)
    pix = hp.ang2pix(nside, gal.l.deg, gal.b.deg, lonlat=True)
    Ta = ms[pix] * 1e6
    # (b) 插值 (RA/Dec theta/phi)
    theta = np.radians(90.0 - nodes[:, 1]); phi = np.radians(nodes[:, 0])
    Tb = hp.get_interp_val(ms, theta, phi) * 1e6
    # (c) 插值 (galactic lonlat via vec2pix interp? 用 pix2ang 轉 galactic 方向)
    for name, T in [("nearest-pix", Ta), ("interp", Tb)]:
        dT = T - T.mean()
        print(f"{fwhm_deg}° {name:12s}: M1 = {np.mean(np.abs(dT))/134.2:.5f}  "
              f"⟨|δT|⟩={np.mean(np.abs(dT)):.2f} σ={dT.std():.2f}")
    print(f"  ΔM1 = {(np.mean(np.abs(Ta-Ta.mean()))-np.mean(np.abs(Tb-Tb.mean())))/134.2:+.5f}")
    print(f"  節點0: nearest={Ta[0]:+.2f} interp={Tb[0]:+.2f} (txt=-134.19)")
