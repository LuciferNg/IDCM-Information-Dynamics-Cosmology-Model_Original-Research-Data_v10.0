#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O182 scripts/02b — 三圖節點溫度提取 (修正版: 銀河座標採樣)
=============================================================
修正 02 嘅座標 bug: Planck 地圖係銀河座標, 必須 RA/Dec(ICRS) -> 銀河(l,b)
然後 theta = 90°−b, phi = l 採樣 (O175 script 16 正確做法)。

管道: read_map(as-is, RING 驗證) -> smoothing(FWHM) -> remove_dipole
     -> 節點採樣 (ang2pix 最近像素, 同 O175/cmb_cold_spot 原設定)
     -> ⟨|δT|⟩/A, A = 134.2 μK
"""
import numpy as np
import healpy as hp
import json
from pathlib import Path
from astropy.coordinates import SkyCoord
import astropy.units as u

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
OUT = ROOT / "o182_88grid_geometry/data"

MAPS = {
    "SMICA":     ROOT / "o175_entropy_theorem/data/planck/COM_CMB_IQU-smica_2048_R3.00_full.fits",
    "Commander": ROOT / "data_gated_unlock/COM_CMB_IQU-commander_2048_R3.00_full.fits",
    "SEVEM":     ROOT / "o42_independent_measurement_A/data/bands/sevem_final.fits",
}

def to_gal(pts):
    """RA/Dec ICRS -> (l, b) deg"""
    sc = SkyCoord(ra=pts[:, 0]*u.deg, dec=pts[:, 1]*u.deg, frame='icrs')
    g = sc.galactic
    return np.column_stack([g.l.deg, g.b.deg])

a5 = to_gal(np.loadtxt(ROOT / "cmb_cold_spot/data/a5_nodes.txt"))
g88 = to_gal(np.loadtxt(OUT / "g88_nodes.txt"))
g32 = to_gal(np.loadtxt(OUT / "g32_frustration_midpoints.txt"))
g120 = np.vstack([g88, g32])
sets = {"A5_60": a5, "G88": g88, "G32frust": g32, "G120_all": g120}
for k, v in sets.items():
    print(f"節點集 {k}: {len(v)}")

# 讀地圖 + ordering 驗證 (as-is vs reorder)
print("\n=== ordering 驗證 ===")
sm = hp.read_map(str(MAPS["SMICA"]), field=0).astype(np.float64)
sel = np.arange(0, len(sm), 3000)
prepared = {}
for name, path in MAPS.items():
    m = hp.read_map(str(path), field=0).astype(np.float64)
    c0 = np.corrcoef(m[sel], sm[sel])[0, 1]
    mr = hp.reorder(m, n2r=True)
    c1 = np.corrcoef(mr[sel], sm[sel])[0, 1]
    m_final = m if c0 >= c1 else mr
    prepared[name] = m_final
    print(f"  {name:10s}: as-is={c0:+.4f} reorder={c1:+.4f} -> {'as-is' if c0>=c1 else 'reorder'}")

SMOOTHS = [4.17, 5.0]
results = {}
for fwhm in SMOOTHS:
    print(f"\n=== 平滑 {fwhm}° (最近像素, 銀河座標) ===")
    for name, m in prepared.items():
        ms = hp.smoothing(m, fwhm=np.radians(fwhm), verbose=False)
        ms = hp.remove_dipole(ms, verbose=False)
        nside = hp.get_nside(ms)
        # 地圖 σ (masked |b|>20 乾淨 CMB + 全圖)
        npix = len(ms)
        th_all, ph_all = hp.pix2ang(nside, np.arange(npix))
        b_all = 90.0 - np.degrees(th_all)
        gmask = np.abs(b_all) > 20.0
        sigma_masked = np.std(ms[gmask]) * 1e6
        sigma_all = np.std(ms) * 1e6
        for sname, pts in sets.items():
            pix = hp.ang2pix(nside, pts[:, 0], pts[:, 1], lonlat=True)
            T = ms[pix] * 1e6
            key = (fwhm, name, sname)
            results[key] = {"T": T.tolist()}
            dT = T - T.mean()
            m1 = np.mean(np.abs(dT)) / 134.2
            print(f"  {fwhm:>4.2f}° {name:10s} {sname:8s}: M1 = {m1:.5f}  "
                  f"(σ|b|>20={sigma_masked:.1f}, σ_all={sigma_all:.1f} μK)")
        results[(fwhm, name, "META")] = {"sigma_masked": sigma_masked, "sigma_all": sigma_all}

for fwhm in SMOOTHS:
    for name in MAPS:
        d = {sname: results[(fwhm, name, sname)]["T"] for sname in ("A5_60", "G88", "G32frust", "G120_all")}
        d["META"] = results[(fwhm, name, "META")]
        (OUT / f"temps2_{name}_{fwhm}deg.json").write_text(json.dumps(d))
print("\n已存: data/temps2_{map}_{fwhm}deg.json (含 META σ)")
print("RESULT: 修正提取完成")
