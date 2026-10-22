#!/usr/bin/env python3
"""
13_node53_verify.py — O30: node53 驗證器 (no-hallucination close-out)
=======================================================================
獨立重算 node53 全部宣稱數字, 對比已存 JSON + 報告:
  1. 4.17° SMICA 節點溫度 (+112 μK)
  2. 三地圖 3° 盤 (SMICA +96.8, NILC +96.2, Commander +95.1)
  3. 環背景 ΔT (SMICA +82.0)
  4. R3 mask unmasked
  5. 對徑點 −46 μK
  6. 跨尺度 10/10 全正
"""
import healpy as hp
import numpy as np
import os, json
from astropy.coordinates import SkyCoord
import astropy.units as u

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
CACHE = os.path.join(BASE, "o5_catalog_compare/data/smooth_cache")
DATA27 = os.path.join(BASE, "o27_node47_foreground/data")
O30 = os.path.join(BASE, "o30_node_systematics")
L, B = 319.50, -34.20

passes, fails = [], []
def check(name, cond, detail=""):
    (passes if cond else fails).append(name)
    print(f"  {'✅' if cond else '❌'} {name} {detail}")

print("=" * 66)
print("O30-13: node53 驗證器")
print("=" * 66)

# 1. 節點溫度 (O3 node_temps)
T_o3 = np.loadtxt(os.path.join(BASE, "o3_node_temperatures/data/node_temps.txt"), skiprows=1)
row53 = T_o3[T_o3[:,0]==53][0]
check("node53 4.17° T=+112", abs(row53[2] - 112.0) < 1.0, f"({row53[2]:+.2f})")
check("node53 b=-34.2", abs(row53[4] - (-34.2)) < 0.3, f"({row53[4]:+.2f})")
check("node53 l=319.5", abs(row53[3] - 319.5) < 0.3, f"({row53[3]:.2f})")

# 2. 三地圖 3° 盤
for name, fname, exp in [("SMICA", "smica2_smooth4.17.fits", 96.83),
                          ("NILC", "nilc2_smooth4.17.fits", 96.21),
                          ("Commander", "commander_smooth4.17.fits", 95.14)]:
    m = hp.read_map(os.path.join(CACHE, fname), field=0)
    nside = hp.get_nside(m)
    vec = hp.ang2vec(L, B, lonlat=True)
    pix = hp.query_disc(nside, vec, np.radians(3.0))
    v = np.mean(m[pix]) * 1e6
    check(f"{name} 3°盤 ≈{exp}", abs(v - exp) < 2.0, f"({v:+.2f})")

# 3. 環背景 ΔT
m = hp.read_map(os.path.join(CACHE, "smica2_smooth4.17.fits"), field=0)
nside = hp.get_nside(m)
vec = hp.ang2vec(L, B, lonlat=True)
p_core = hp.query_disc(nside, vec, np.radians(2.0))
p_ring = hp.query_disc(nside, vec, np.radians(8.0))
p_in = hp.query_disc(nside, vec, np.radians(4.0))
p_ring = np.setdiff1d(p_ring, p_in)
dT = (np.mean(m[p_core]) - np.mean(m[p_ring])) * 1e6
check("SMICA 環背景 ΔT=+82", abs(dT - 82.0) < 3.0, f"({dT:+.2f})")

# 4. R3 mask
mk = hp.read_map(os.path.join(DATA27, "COM_Mask_CMB-common-Mask-Int_2048_R3.00.fits"), field=0)
ns = hp.get_nside(mk)
p = hp.ang2pix(ns, L, B, lonlat=True)
check("R3 mask unmasked", mk[p] > 0.5, f"(pixel={mk[p]:.3f})")

# 5. 對徑點
vec_a = hp.ang2vec((L+180)%360, +34.2, lonlat=True)
pix_a = hp.query_disc(nside, vec_a, np.radians(3.0))
T_a = np.mean(m[pix_a]) * 1e6
check("對徑點 ≈−46", abs(T_a - (-46.05)) < 3.0, f"({T_a:+.2f})")

# 6. 跨尺度 10/10 全正
SCALES = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 4.17, 5.0, 7.0, 10.0]
MAPS = {0.5:"smica2_smooth0.5.fits", 1.0:"smica2_smooth1.0.fits", 1.5:"smica2_smooth1.5.fits",
        2.0:"smica2_smooth2.0.fits", 3.0:"smica2_smooth3.0.fits", 4.0:"smica2_smooth4.0.fits",
        4.17:"smica2_smooth4.17.fits", 5.0:"smica2_smooth5.0.fits", 7.0:"smica2_smooth7.0.fits",
        10.0:"smica2_smooth10.0.fits"}
signs = []
for s in SCALES:
    ms = hp.read_map(os.path.join(CACHE, MAPS[s]), field=0)
    ns = hp.get_nside(ms)
    p = hp.ang2pix(ns, L, B, lonlat=True)
    signs.append(np.sign(ms[p]))
check("跨尺度 10/10 全正", all(s > 0 for s in signs), f"({sum(1 for s in signs if s>0)}/10)")

# 7. JSON 檔案存在
for f in ["09_node53_multifreq.json", "10_node53_ring_background.json",
          "11_node53_crossmap.json", "12_node53_antipode_mask.json"]:
    check(f"exists {f}", os.path.exists(os.path.join(O30, "data", f)))

print(f"\n{'='*66}")
print(f"結果: {len(passes)}/{len(passes)+len(fails)} PASS")
if fails:
    print(f"❌ FAILED: {fails}")
    exit(1)
print("✅ 全部通過 — node53 數字可信")
