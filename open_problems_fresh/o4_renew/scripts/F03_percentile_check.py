#!/usr/bin/env python3
"""F03_percentile_check.py — 冷斑真實百分位獨立驗證"""
import numpy as np
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as u

print("=" * 60)
print("F03: 冷斑真實百分位驗證 (SMICA 4.17° 平滑)")
print("=" * 60)

m = hp.read_map('/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o5_catalog_compare/data/smooth_cache/smica2_smooth4.17.fits', field=0)
nside = hp.get_nside(m)

# 冷斑 Galactic (209°, -57°)
sc = SkyCoord(l=209*u.deg, b=-57*u.deg, frame='galactic')
pix = hp.ang2pix(nside, sc.l.deg, sc.b.deg, lonlat=True)
T_cold = m[pix] * 1e6

# 全圖像素
pix_all = m[~np.isnan(m)] * 1e6
print(f"冷斑溫度: {T_cold:.2f} μK")
print(f"全圖: mean={pix_all.mean():.2f}, std={pix_all.std():.2f}, N={len(pix_all)}")
z = (T_cold - pix_all.mean()) / pix_all.std()
print(f"z-score = {z:.3f}")

# 實際百分位
pct_colder = np.mean(pix_all < T_cold) * 100
pct_warmer = np.mean(pix_all > T_cold) * 100
print(f"比冷斑更冷嘅像素: {pct_colder:.2f}%")
print(f"比冷斑更暖嘅像素: {pct_warmer:.2f}%")
print(f"→ 冷斑百分位 (由冷至暖) = {pct_colder:.2f}%")

# 高斯對照
from scipy import stats as st
g_colder = st.norm.cdf(z) * 100
print(f"高斯近似更冷: {g_colder:.2f}%")
print(f"高斯近似更暖: {(100-g_colder):.2f}%")

print()
print("文檔宣稱: 98.2% 更冷")
print(f"實際: {pct_colder:.2f}% 像素比冷斑更冷 (即冷斑係 {100-pct_colder:.2f}% 百分位)")
print(f"如果文檔意思係「冷斑比 98.2% 像素更冷」→ 即 {100-pct_colder:.2f}% 像素更暖... 方向要釐清")

with open('/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o4_renew/data/F03_percentile.txt', 'w') as f:
    f.write(f"T_cold={T_cold:.2f} z={z:.3f}\n")
    f.write(f"pct_colder={pct_colder:.2f} pct_warmer={pct_warmer:.2f}\n")
print("\n✅ 已存")
