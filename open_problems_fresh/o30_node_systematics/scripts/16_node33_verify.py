#!/usr/bin/env python3
"""
16_node33_verify.py — O30: node33 驗證器
===========================================
獨立重算 node33 全部宣稱數字:
  1. 4.17° SMICA 節點溫度 (−83.0)
  2. 三地圖 3°盤 (SMICA −74.1, NILC −74.6, Commander −71.8)
  3. 多頻譜 raw (143 GHz +104, 217 GHz +532, 217/143=5.09)
  4. 環背景 ΔT (100 −9.0, 143 +1.3, 217 +47.4)
  5. 353 GHz dust (+4844 μK, 8.9x node0)
  6. R3 mask unmasked
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
L, B = 191.4, -16.1

passes, fails = [], []
def check(name, cond, detail=""):
    (passes if cond else fails).append(name)
    print(f"  {'✅' if cond else '❌'} {name} {detail}")

print("=" * 66)
print("O30-16: node33 驗證器")
print("=" * 66)

# 1. 節點溫度
T_o3 = np.loadtxt(os.path.join(BASE, "o3_node_temperatures/data/node_temps.txt"), skiprows=1)
row33 = T_o3[T_o3[:,0]==33][0]
check("node33 4.17° T=-83", abs(row33[2] + 83.0) < 1.0, f"({row33[2]:+.2f})")
check("node33 b=-16.1", abs(row33[4] + 16.1) < 0.3, f"({row33[4]:+.2f})")

# 2. 三地圖 3°盤
vals3 = {}
for name, fname, exp in [("SMICA","smica2_smooth4.17.fits",-74.12),
                          ("NILC","nilc2_smooth4.17.fits",-74.60),
                          ("Commander","commander_smooth4.17.fits",-71.78)]:
    mm = hp.read_map(os.path.join(CACHE, fname), field=0)
    ns = hp.get_nside(mm)
    vec = hp.ang2vec(L, B, lonlat=True)
    p3 = hp.query_disc(ns, vec, np.radians(3.0))
    v = np.mean(mm[p3]) * 1e6
    vals3[name] = v
    check(f"{name} 3°盤 ≈{exp}", abs(v - exp) < 2.0, f"({v:+.2f})")
spread3 = (max(vals3.values()) - min(vals3.values())) / abs(np.mean(list(vals3.values()))) * 100
check("spread=3.8%", abs(spread3 - 3.8) < 0.5, f"({spread3:.1f}%)")

# 3. 多頻譜 raw (3.0° FWHM)
FWHM = 3.0
SIGMA = np.radians(FWHM) / (2 * np.sqrt(2 * np.log(2)))
FREQ_MAPS = {100: "HFI_SkyMap_100_2048_R3.01_full.fits",
             143: "HFI_SkyMap_143_2048_R3.01_full.fits",
             217: "HFI_SkyMap_217_2048_R3.01_full.fits",
             353: "HFI_SkyMap_353_2048_R3.01_full.fits"}
maps = {}
for freq, fn in FREQ_MAPS.items():
    m = hp.read_map(os.path.join(DATA27, fn), field=0, nest=True)
    m = hp.reorder(m, n2r=True)
    bad = (~np.isfinite(m)) | (np.abs(m) > 1e-3)
    m = np.where(bad, np.nan, m)
    mk = np.isfinite(m)
    sm = hp.smoothing(np.where(mk, m, 0.0), sigma=SIGMA, verbose=False)
    sm_ok = hp.smoothing(mk.astype(float), sigma=SIGMA, verbose=False)
    maps[freq] = np.where(sm_ok > 0.1, sm / sm_ok, np.nan)
nside = hp.get_nside(maps[100])
pix = hp.ang2pix(nside, L, B, lonlat=True)
T143 = maps[143][pix] * 1e6
T217 = maps[217][pix] * 1e6
T100 = maps[100][pix] * 1e6
check("143GHz +104", abs(T143 - 104.4) < 5.0, f"({T143:+.1f})")
check("217GHz +532", abs(T217 - 531.8) < 10.0, f"({T217:+.1f})")
check("100GHz +23", abs(T100 - 22.9) < 5.0, f"({T100:+.1f})")
r = T217 / T143 if abs(T143) > 1 else 99
check("217/143=5.09", abs(r - 5.09) < 0.3, f"({r:.2f})")

# 4. 環背景 ΔT
m417 = hp.read_map(os.path.join(CACHE, "smica2_smooth4.17.fits"), field=0)
ns4 = hp.get_nside(m417)
vec = hp.ang2vec(L, B, lonlat=True)
dT = {}
for freq, m in maps.items():
    ns = hp.get_nside(m)
    pc = hp.query_disc(ns, vec, np.radians(2.0))
    pr = hp.query_disc(ns, vec, np.radians(8.0))
    pi = hp.query_disc(ns, vec, np.radians(4.0))
    pr = np.setdiff1d(pr, pi)
    dT[freq] = (np.nanmean(m[pc]) - np.nanmean(m[pr])) * 1e6
check("環ΔT 100GHz -9.0", abs(dT[100] + 9.0) < 3.0, f"({dT[100]:+.1f})")
check("環ΔT 143GHz +1.3", abs(dT[143] - 1.3) < 3.0, f"({dT[143]:+.1f})")
check("環ΔT 217GHz +47", abs(dT[217] - 47.4) < 5.0, f"({dT[217]:+.1f})")

# 5. 353 GHz dust — 用 RAW map 只 finite 值 (唔理 |T|>1e-3 閾值!
#    node33 353 值 +4.8e-3 K 超過 CMB 合理範圍但正正係 dust 集中證據;
#    用 |T|<1e-3 篩會將 dust 區誤判 bad → nan)
m353_raw = hp.read_map(os.path.join(DATA27, "HFI_SkyMap_353_2048_R3.01_full.fits"),
                       field=0, nest=True)
m353_raw = hp.reorder(m353_raw, n2r=True)
m353_raw = np.where(np.isfinite(m353_raw), m353_raw, np.nan)
ns353 = hp.get_nside(m353_raw)
vec = hp.ang2vec(L, B, lonlat=True)
pc = hp.query_disc(ns353, vec, np.radians(2.0))
dust33 = np.nanmean(m353_raw[pc]) * 1e6
vec0 = hp.ang2vec(209.0, -57.0, lonlat=True)
p0 = hp.query_disc(ns353, vec0, np.radians(2.0))
dust0 = np.nanmean(m353_raw[p0]) * 1e6
check("353 dust node33 +4844", abs(dust33 - 4844) < 300, f"({dust33:+.0f})")
check("353 8.9x node0", abs(dust33/dust0 - 8.9) < 1.2, f"({dust33/dust0:.1f}x, node0={dust0:+.0f})")

# 6. R3 mask
mk = hp.read_map(os.path.join(DATA27, "COM_Mask_CMB-common-Mask-Int_2048_R3.00.fits"), field=0)
ns = hp.get_nside(mk)
check("R3 unmasked", mk[hp.ang2pix(ns, L, B, lonlat=True)] > 0.5)

# 7. JSON 存在
check("exists 15_node33_multifreq.json",
      os.path.exists(os.path.join(O30, "data/15_node33_multifreq.json")))

print(f"\n{'='*66}")
print(f"結果: {len(passes)}/{len(passes)+len(fails)} PASS")
if fails:
    print(f"❌ FAILED: {fails}")
    exit(1)
print("✅ 全部通過 — node33 數字可信")
