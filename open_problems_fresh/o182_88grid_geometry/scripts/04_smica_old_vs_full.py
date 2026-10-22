#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O182 scripts/04 — SMICA 舊 txt vs 完整全圖逐節點對比
====================================================
驗證假說: O175 嘅 SMICA 0.2443 (11/45 命中) 係咪截斷檔案產物?
管道完全複製 22_smica_smoothed.py: 4.17° smoothing + remove_dipole
+ ang2pix 最近像素 (galactic lonlat)。
"""
import numpy as np
import healpy as hp
from pathlib import Path
from astropy.coordinates import SkyCoord
import astropy.units as u

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
SMICA_FULL = ROOT / "o175_entropy_theorem/data/planck/COM_CMB_IQU-smica_2048_R3.00_full.fits"

# 舊 txt
rows = []
for line in (ROOT / "cmb_cold_spot/data/smica_smoothed.txt").read_text().splitlines():
    if line.startswith("#") or not line.strip(): continue
    p = line.split()
    rows.append((int(p[0]), float(p[2]), float(p[3]), float(p[4])))  # idx, T_uK, l, b
T_old = np.array([r[1] for r in rows])
print(f"舊 txt: {len(T_old)} 節點, ⟨|δT|⟩/A = {np.mean(np.abs(T_old - T_old.mean()))/134.2:.5f}")

# /tmp/smica2.fits 檢查
import os
tmp = "/tmp/smica2.fits"
if os.path.exists(tmp):
    print(f"/tmp/smica2.fits: {os.path.getsize(tmp)} bytes, realpath: {os.path.realpath(tmp)}")
    try:
        m_tmp = hp.read_map(tmp, field=0)
        print(f"  readable: nside={hp.get_nside(m_tmp)}, len={len(m_tmp)}, finite={np.isfinite(m_tmp).mean():.4f}")
    except Exception as e:
        print(f"  READ ERROR: {e}")
else:
    print("/tmp/smica2.fits: 唔存在 (WSL /tmp 已清)")

# 完整 SMICA: 4.17° 平滑 + remove_dipole + 最近像素 (script 22 管道)
m = hp.read_map(str(SMICA_FULL), field=0).astype(np.float64)
fwhm_rad = np.radians(4.17)
sigma_rad = fwhm_rad / (2 * np.sqrt(2 * np.log(2)))
m_s = hp.smoothing(m, sigma=sigma_rad, verbose=False)
m_f = hp.remove_dipole(m_s, verbose=False)

nodes = np.loadtxt(ROOT / "cmb_cold_spot/data/a5_nodes.txt")
sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic
nside = hp.get_nside(m_f)
pix = hp.ang2pix(nside, gal.l.deg, gal.b.deg, lonlat=True)
T_new = m_f[pix] * 1e6

dT_new = T_new - T_new.mean()
print(f"\n完整全圖 (4.17°+dipole+最近像素): ⟨|δT|⟩/A = {np.mean(np.abs(dT_new))/134.2:.5f}")
print(f"舊 txt 同管道:                      ⟨|δT|⟩/A = {np.mean(np.abs(T_old - T_old.mean()))/134.2:.5f}")

# 逐節點
print("\n節點     舊txt      新提取     差")
for i in range(60):
    d = T_old[i] - T_new[i]
    flag = " ***" if abs(d) > 5 else ""
    print(f"  {i:2d}  {T_old[i]:+9.2f}  {T_new[i]:+9.2f}  {d:+8.2f}{flag}")

corr = np.corrcoef(T_old, T_new)[0, 1]
print(f"\n相關: r = {corr:.4f}")
print(f"mean|差| = {np.mean(np.abs(T_old - T_new)):.2f} μK")
print(f"11/45 命中判定: 舊={np.mean(np.abs(T_old-T_old.mean()))/134.2:.5f} vs 新={np.mean(np.abs(dT_new))/134.2:.5f}")
