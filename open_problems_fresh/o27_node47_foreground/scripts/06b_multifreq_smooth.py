#!/usr/bin/env python3
"""
06b_multifreq_smooth.py — O27: 多頻譜精確比較 (FWHM 平滑)
========================================================
用 3.0° FWHM Gaussian 平滑頻率 map (同 SMICA 3.0° 完全可比),
抽 node47 / node0 / node9 單像素, 直接對比。

CMB 冷結構: 所有頻率都冷 (K_CMB 單位, CMB 頻率無關)
Dust 污染: 217/353 上升
"""
import healpy as hp
import numpy as np
import os, json, time

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
OUT = os.path.join(BASE, "o27_node47_foreground")
DATA = os.path.join(OUT, "data")
CACHE = os.path.join(BASE, "o5_catalog_compare/data/smooth_cache")

FREQ_MAPS = {
    100: os.path.join(DATA, "HFI_SkyMap_100_2048_R3.01_full.fits"),
    143: os.path.join(DATA, "HFI_SkyMap_143_2048_R3.01_full.fits"),
    217: os.path.join(DATA, "HFI_SkyMap_217_2048_R3.01_full.fits"),
    353: os.path.join(DATA, "HFI_SkyMap_353_2048_R3.01_full.fits"),
}
FWHM = 3.0
SIGMA = np.radians(FWHM) / (2 * np.sqrt(2 * np.log(2)))

TARGETS = [
    (313.47, -8.58,  "node47"),
    (209.00, -57.00, "node0"),
    (214.92, -31.16, "node9"),
]
EXTRA = [
    (180.0, +30.0, "高緯A"), (300.0, +40.0, "高緯B"), (60.0, -35.0, "高緯C"),
    (313.47, -0.5, "銀河面A"), (0.0, +0.5, "銀河面B"),
]

print("=" * 70)
print(f"O27: 多頻譜精確比較 ({FWHM}° FWHM 平滑)")
print("=" * 70)

maps = {}
for freq, path in FREQ_MAPS.items():
    if not os.path.exists(path):
        continue
    t0 = time.time()
    m = hp.read_map(path, field=0, nest=True)
    m = hp.reorder(m, n2r=True)
    bad = (~np.isfinite(m)) | (np.abs(m) > 1e-3)
    m = np.where(bad, np.nan, m)
    mask_ok = np.isfinite(m)
    m0 = np.where(mask_ok, m, 0.0)
    sm = hp.smoothing(m0, sigma=SIGMA, verbose=False)
    sm_ok = hp.smoothing(mask_ok.astype(float), sigma=SIGMA, verbose=False)
    sm = np.where(sm_ok > 0.1, sm / sm_ok, np.nan)
    maps[freq] = sm
    print(f"  {freq} GHz: 平滑完成 ({time.time()-t0:.0f}s)")

ms3 = hp.read_map(os.path.join(CACHE, "smica2_smooth3.0.fits"), field=0)
nside = hp.get_nside(ms3)

def sample(l, b):
    pix = hp.ang2pix(nside, l, b, lonlat=True)
    out = {"SMICA": float(ms3[pix] * 1e6)}
    for freq, m in maps.items():
        v = m[pix] * 1e6
        out[freq] = float(v) if np.isfinite(v) else float('nan')
    out["r217_143"] = out[217]/out[143] if abs(out[143]) > 1 else float('nan')
    return out

print(f"\n{'目標':<10}{'SMICA':>10}{'100GHz':>10}{'143GHz':>10}{'217GHz':>10}{'353GHz':>10}"
      f"{'217/143':>9}{'143-100':>9}")
rows = []
for l, b, name in TARGETS:
    v = sample(l, b)
    d = v[143] - v[100]
    v["d143_100"] = float(d)
    rows.append({"name": name, **v})
    print(f"{name:<10}{v['SMICA']:>+10.1f}{v[100]:>+10.1f}{v[143]:>+10.1f}"
          f"{v[217]:>+10.1f}{v[353]:>+10.1f}{v['r217_143']:>9.2f}{d:>+9.1f}")

print(f"\n{'目標':<10}{'SMICA':>10}{'100GHz':>10}{'143GHz':>10}{'217GHz':>10}{'353GHz':>10}"
      f"{'217/143':>9}")
for l, b, name in EXTRA:
    v = sample(l, b)
    rows.append({"name": name, **v})
    print(f"{name:<10}{v['SMICA']:>+10.1f}{v[100]:>+10.1f}{v[143]:>+10.1f}"
          f"{v[217]:>+10.1f}{v[353]:>+10.1f}{v['r217_143']:>9.2f}")

with open(os.path.join(DATA, "multifreq_smooth_node47.json"), "w") as f:
    json.dump({"fwhm": FWHM, "rows": rows}, f, indent=2)
print(f"\n✅ 已存 data/multifreq_smooth_node47.json")
