#!/usr/bin/env python3
"""
03_foreground_mask.py — O27: 前景 mask 檢查 @ node47
====================================================
檢查 node47 (l=313.47°, b=-8.58°) 喺唔同 Planck mask 嘅狀態:
1. COM_Mask_CMB-common-Mask-Int_2048_R3.00.fits — R3 CMB common mask (Int)
2. COM_Mask_CMB-IQU-common-field-MaskInt_2048_R2.01.fits — IQU common mask (R2)
3. HFI_Mask_GalPlane-apo0_2048_R2.00.fits — Galactic plane masks (GAL020-GAL099)

mask 值: 1 = 保留 (clean), 0 = 遮住 (污染)
額外: 60 節點全統計 + node47 週邊 0.5°-5° 覆蓋率
"""
import healpy as hp
import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u
import os, json

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
OUT = os.path.join(BASE, "o27_node47_foreground")
DATA = os.path.join(OUT, "data")
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
print("O27: 前景 mask 檢查 @ node47")
print("=" * 70)
print(f"node47: l={l47:.2f}° b={b47:.2f}°  (|b|={abs(b47):.2f}°)")

masks = {
    "CMB-common-Int-R3": os.path.join(DATA, "COM_Mask_CMB-common-Mask-Int_2048_R3.00.fits"),
    "CMB-IQU-common-R2": os.path.join(DATA, "COM_Mask_CMB-IQU-common-field-MaskInt_2048_R2.01.fits"),
    "GalPlane-apo0-R2":  os.path.join(DATA, "HFI_Mask_GalPlane-apo0_2048_R2.00.fits"),
}

results = {}
for mname, path in masks.items():
    if not os.path.exists(path):
        print(f"  [missing] {mname}: {path}")
        continue
    m = hp.read_map(path, field=0)
    nside = hp.get_nside(m)
    print(f"\n  {mname}: nside={nside}")
    # mask 值分佈
    vals, counts = np.unique(m, return_counts=True)
    print(f"    值分佈: {dict(zip(vals.tolist(), counts.tolist()))}")
    # node47
    pix47 = hp.ang2pix(nside, l47, b47, lonlat=True)
    v47 = m[pix47]
    print(f"    node47 mask 值 = {v47}  ({'保留/clean' if v47 > 0.5 else '遮住/污染'})")
    # 60 節點統計
    pix_all = hp.ang2pix(nside, gal.l.deg, gal.b.deg, lonlat=True)
    vals_all = m[pix_all]
    n_keep = int(np.sum(vals_all > 0.5))
    print(f"    60 節點: {n_keep}/60 保留, {60-n_keep}/60 遮住")
    # node47 週邊 0.5°-5° 覆蓋率
    disc_info = {}
    for rad in [0.5, 1.0, 2.0, 3.0, 5.0]:
        pix_disc = hp.query_disc(nside, hp.ang2vec(l47, b47, lonlat=True),
                                 np.radians(rad))
        frac_keep = float(np.mean(m[pix_disc] > 0.5))
        disc_info[rad] = frac_keep
        print(f"    {rad:>4.1f}° 盤: {frac_keep*100:5.1f}% 保留")
    results[mname] = {"node47_val": float(v47),
                      "node47_status": "clean" if v47 > 0.5 else "masked",
                      "n_nodes_keep": n_keep,
                      "disc_frac": disc_info}

with open(os.path.join(DATA, "mask_node47.json"), "w") as f:
    json.dump(results, f, indent=2)
print(f"\n✅ 已存 data/mask_node47.json")
