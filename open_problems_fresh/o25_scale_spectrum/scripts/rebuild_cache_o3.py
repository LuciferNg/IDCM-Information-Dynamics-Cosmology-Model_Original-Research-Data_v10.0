#!/usr/bin/env python3
"""
rebuild_cache_o3.py — 重建 /tmp/cache_o3 (O25 主分析 cache)
============================================================
O3 邏輯: 10 尺度 × 3 地圖, nside=2048, RING, float32, remove_dipole。
- SMICA: /tmp/smica2.fits (RING)
- NILC/Commander: /tmp/nilc.fits /tmp/commander.fits (NESTED → reorder n2r)
平滑: hp.smoothing(sigma=fwhm/(2*sqrt(2ln2))) + remove_dipole
Cache 命名: SMICA_smooth{scale}.fits / NILC_{scale}.fits / Commander_{scale}.fits
"""
import healpy as hp
import numpy as np
import os, sys, time

CACHE = "/tmp/cache_o3"
os.makedirs(CACHE, exist_ok=True)

SCALES = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 4.17, 5.0, 7.0, 10.0]

print("載入 raw 地圖...")
maps_raw = {}
maps_raw['SMICA'] = hp.read_map('/tmp/smica2.fits')
mn = hp.read_map('/tmp/nilc.fits', field=0, nest=True)
maps_raw['NILC'] = hp.reorder(mn, n2r=True)
mc = hp.read_map('/tmp/commander.fits', field=0, nest=True)
maps_raw['Commander'] = hp.reorder(mc, n2r=True)
print("  載入完成:", {k: hp.get_nside(v) for k, v in maps_raw.items()})

# SMICA 舊 cache 重用檢查 (可能仲有)
smica_cache = {}
for fw in [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 4.17, 5.0, 7.0, 10.0]:
    fname = f'/tmp/smica2_smooth{fw}.fits'
    if os.path.exists(fname):
        try:
            m = hp.read_map(fname)
            if hp.get_nside(m) == 2048 and np.isfinite(m).all():
                smica_cache[fw] = m
                print(f"[cache] SMICA {fw}° 重用")
        except Exception:
            pass

def get_smoothed(name, fw):
    if name == 'SMICA' and fw in smica_cache:
        return smica_cache[fw]
    # 命名: SMICA 用 SMICA_smooth{fw}.fits, 其他用 {name}_{fw}.fits
    if name == "SMICA":
        fname = f"{CACHE}/SMICA_smooth{fw}.fits"
    else:
        fname = f"{CACHE}/{name}_{fw}.fits"
    if os.path.exists(fname):
        try:
            m = hp.read_map(fname)
            if hp.get_nside(m) == 2048 and len(m) == 50331648 and np.isfinite(m).all():
                print(f"[cache] {name} {fw}° 重用")
                return m
        except Exception:
            pass
    t0 = time.time()
    sigma = np.radians(fw) / (2 * np.sqrt(2 * np.log(2)))
    m = hp.remove_dipole(hp.smoothing(maps_raw[name], sigma=sigma))
    hp.write_map(fname, m.astype(np.float32), overwrite=True)
    print(f"[平滑] {name} {fw}° 完成 ({time.time()-t0:.0f}s)")
    return m

print("=" * 60)
t_start = time.time()
for fw in SCALES:
    for name in ['SMICA', 'NILC', 'Commander']:
        get_smoothed(name, fw)
print(f"全部完成! 共用 {time.time()-t_start:.0f}s")
print(f"Cache 檔案數: {len(os.listdir(CACHE))}")
