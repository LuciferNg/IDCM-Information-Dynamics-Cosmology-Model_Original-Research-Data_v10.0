#!/usr/bin/env python3
"""
O42 — Step 4: 冷斑徑向溫度剖面 (0°–15°, A₅ 節點結構驗證)
=========================================================
目標:
  1. 節點 0 (冷斑中心) 0°–15° 徑向剖面 — 驗證冷斑嘅角度尺度
  2. 比較: IDCM A=134.2 μK 結構尺度 R8=4.17° vs 文獻 5° (Vielva 2004)
  3. A₅ 節點網絡: 節點 0 嘅最近節點 (hop-1) 距離 26.17° — 剖面內唔應該有第二個冷結構
  4. 剖面形狀: 高斯 vs 拓撲缺陷 (零交叉位置)
方法:
  - SMICA 4.17° smooth cache (或 raw)
  - 以節點 0 為中心, 0°–15° ring bins, remove_dipole 後抽平均
  - 報告: T(θ), 半高寬, 最小點, A 比較
"""
import os, json
import numpy as np
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as u

T_cmb = 2.7255
A_IDCM = 134.2
OUTDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
NODES = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt'
CACHE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o5_catalog_compare/data/smooth_cache/smica2_smooth4.17.fits'

nodes = np.loadtxt(NODES)
sc = SkyCoord(ra=nodes[:,0]*u.deg, dec=nodes[:,1]*u.deg, frame='icrs')
gal = sc.galactic
l_arr = np.array([float(g.l.deg) for g in gal])
b_arr = np.array([float(g.b.deg) for g in gal])
# 節點 0 單位向量
v0 = hp.ang2vec(l_arr[0], b_arr[0], lonlat=True)

m = hp.read_map(CACHE, field=0)
nside = hp.get_nside(m)
npix = hp.nside2npix(nside)
print(f"SMICA 4.17° cache: nside={nside}")

# 全部像素嘅角度距離 (vectorised)
pix = np.arange(npix)
v = hp.pix2vec(nside, pix)
dots = np.clip(v[0]*v0[0] + v[1]*v0[1] + v[2]*v0[2], -1, 1)
ang = np.degrees(np.arccos(dots))

T = m * 1e6   # μK (cache 已係 K_CMB, 唔好乘 T_cmb!)

# 0.5° bins, 0–15°
edges = np.arange(0, 15.5, 0.5)
print(f"\n{'θ(°)':>6} {'T_mean(μK)':>12} {'T_med(μK)':>12} {'npix':>8}")
print("-" * 44)
prof = []
for i in range(len(edges)-1):
    sel = (ang >= edges[i]) & (ang < edges[i+1])
    n = sel.sum()
    tm = T[sel].mean(); tmed = np.median(T[sel])
    prof.append(dict(theta=float((edges[i]+edges[i+1])/2), T_mean=float(tm), T_med=float(tmed), npix=int(n)))
    print(f"{prof[-1]['theta']:>6.2f} {tm:>12.3f} {tmed:>12.3f} {n:>8d}")

# 關鍵量度
center_T = float(T[np.argmin(ang)])   # 中心 pixel
print(f"\n中心 (θ≈0): T = {center_T:.2f} μK")
# 冷斑尺度: 第一個 T > -20 μK 嘅 bin (回升點)
T_means = np.array([p['T_mean'] for p in prof])
th = np.array([p['theta'] for p in prof])
cold_extent = th[np.argmax(T_means > -20)] if np.any(T_means > -20) else 15.0
print(f"冷斑回升點 (T > -20 μK): θ ≈ {cold_extent:.1f}°")
# 半幅: T(θ) = -A/2 嘅位置
A_half = -A_IDCM/2
cross = np.interp(A_half, T_means[::-1], th[::-1]) if T_means.min() < A_half else np.nan
print(f"A/2 交叉點: θ ≈ {cross:.2f}° (A={A_IDCM} μK 半幅)")

# 節點距離檢查 (節點 0 嘅 hop-1 最近距離)
angs_to_nodes = np.degrees(np.arccos(np.clip(hp.ang2vec(l_arr, b_arr, lonlat=True) @ v0, -1, 1)))
order = np.argsort(angs_to_nodes)
print(f"\n最近節點距離: {[(int(i), round(float(angs_to_nodes[i]),2)) for i in order[:4]]}")

# 儲存
out = dict(center_T=center_T, cold_extent=cold_extent, A_half_cross=cross,
           nearest_nodes=[dict(node=int(i), dist_deg=float(angs_to_nodes[i])) for i in order[:4]],
           profile=prof)
with open(os.path.join(OUTDIR, '04_radial_profile.json'), 'w') as f:
    json.dump(out, f, indent=2)
print(f"\nsaved: {OUTDIR}/04_radial_profile.json")
