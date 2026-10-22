#!/usr/bin/env python3
"""
12_node53_antipode_mask.py — O30: node53 對徑檢查 + CMB mask 狀態
===================================================================
1. 對徑點 (l+180, -b) = (139.5, +34.2) 有冇對應結構? (A₅ 對徑檢查慣例)
2. node53 喺 Planck R3 官方 CMB mask 內定外? (O27: node47 被 mask 遮住)
3. node53 距離銀河面 |b|=34.2° — 前景污染風險量化
"""
import healpy as hp
import numpy as np
import os, json

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
DATA27 = os.path.join(BASE, "o27_node47_foreground/data")
CACHE = os.path.join(BASE, "o5_catalog_compare/data/smooth_cache")
OUT = os.path.join(BASE, "o30_node_systematics/data")

L, B = 319.50, -34.20
L_ANTI, B_ANTI = (L + 180) % 360, +34.20

print("=" * 70)
print("O30: node53 對徑 + mask 狀態")
print("=" * 70)

# 1. 對徑點 (SMICA 4.17°)
m = hp.read_map(os.path.join(CACHE, "smica2_smooth4.17.fits"), field=0)
nside = hp.get_nside(m)
vec_a = hp.ang2vec(L_ANTI, B_ANTI, lonlat=True)
pix_a = hp.query_disc(nside, vec_a, np.radians(3.0))
T_anti = np.mean(m[pix_a]) * 1e6
# node53 中心
vec = hp.ang2vec(L, B, lonlat=True)
pix = hp.query_disc(nside, vec, np.radians(3.0))
T_core = np.mean(m[pix]) * 1e6
print(f"node53 中心 (3°盤): {T_core:+.2f} μK")
print(f"對徑點 ({L_ANTI:.1f}°, {B_ANTI:+.1f}°): {T_anti:+.2f} μK")
print(f"→ {'對徑有對應熱結構' if T_anti > 50 else '對徑冇對應結構'} (|Δ|={abs(T_core-T_anti):.1f} μK)")

# 2. CMB mask 狀態
masks = {
    "R3 common (Int)": os.path.join(DATA27, "COM_Mask_CMB-common-Mask-Int_2048_R3.00.fits"),
    "R2.01 IQU": os.path.join(DATA27, "COM_Mask_CMB-IQU-common-field-MaskInt_2048_R2.01.fits"),
    "GalPlane apo0": os.path.join(DATA27, "HFI_Mask_GalPlane-apo0_2048_R2.00.fits"),
}
for name, path in masks.items():
    if not os.path.exists(path):
        print(f"{name}: 檔案缺失")
        continue
    mk = hp.read_map(path, field=0)
    ns = hp.get_nside(mk)
    p = hp.ang2pix(ns, L, B, lonlat=True)
    v = mk[p]
    print(f"{name:<22}: pixel={v:.3f} ({'✅ unmasked' if v > 0.5 else '🔴 masked'})")

# node47 對比
print(f"\nnode47 對比 (b=-8.6°):")
for name, path in masks.items():
    if not os.path.exists(path):
        continue
    mk = hp.read_map(path, field=0)
    ns = hp.get_nside(mk)
    p = hp.ang2pix(ns, 313.47, -8.58, lonlat=True)
    v = mk[p]
    print(f"  {name:<20}: pixel={v:.3f} ({'✅ unmasked' if v > 0.5 else '🔴 masked'})")

# 3. 前景風險量化 (b=34.2°)
# 用 353 GHz dust 做 tracer: node53 位置 dust 水平 vs 全 sky
m353_path = os.path.join(DATA27, "HFI_SkyMap_353_2048_R3.01_full.fits")
if os.path.exists(m353_path):
    m353 = hp.read_map(m353_path, field=0, nest=True)
    m353 = hp.reorder(m353, n2r=True)
    bad = (~np.isfinite(m353)) | (np.abs(m353) > 1e-3)
    m353 = np.where(bad, np.nan, m353)
    ns = hp.get_nside(m353)
    p = hp.ang2pix(ns, L, B, lonlat=True)
    # 3° 盤平均
    disc = hp.query_disc(ns, vec, np.radians(3.0))
    dust53 = np.nanmean(m353[disc]) * 1e6
    # 全 sky 高緯 median
    npix = hp.nside2npix(ns)
    pix_all = np.arange(npix)
    pix_hi = hp.pix2ang(ns, pix_all, lonlat=True)[1]
    hi = pix_all[abs(pix_hi) > 30]
    dust_hi = np.nanmedian(m353[hi]) * 1e6
    print(f"\n353 GHz dust tracer (μK): node53={dust53:.0f} vs 高緯 median={dust_hi:.0f}")
    print(f"→ node53 dust 水平 = {dust53/dust_hi:.2f}x 高緯 median")

# 儲存
with open(os.path.join(OUT, "12_node53_antipode_mask.json"), "w") as f:
    json.dump({"node53_core": float(T_core), "antipode": {"l": L_ANTI, "b": B_ANTI, "T": float(T_anti)},
               "mask_status": "unmasked (見 stdout)", "b_deg": B}, f, indent=2)
print(f"\n✅ 已存: {os.path.join(OUT, '12_node53_antipode_mask.json')}")
