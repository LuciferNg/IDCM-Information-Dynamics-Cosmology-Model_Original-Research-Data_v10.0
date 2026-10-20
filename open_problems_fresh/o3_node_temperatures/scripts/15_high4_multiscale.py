#!/usr/bin/env python3
"""
15_high4_multiscale.py — 高緯度 4 節點三地圖 × 多尺度 (完整版, 無超時)
======================================================================
驗證 4 個高緯度 ΔE=0 節點 (10,22,25,32) 嘅零溫度信號:
完整測試: 7 尺度 × 3 地圖, 全部平滑唔 skip
- cache 機制 /tmp/cache_o3/ 重用
- SMICA 重用已有 /tmp/smica2_smooth*.fits
"""
import healpy as hp
import numpy as np
import os
from astropy.coordinates import SkyCoord
import astropy.units as u

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
CACHE = "/tmp/cache_o3"
os.makedirs(CACHE, exist_ok=True)

HIGH4 = [10, 22, 25, 32]

nodes = []
with open(f"{BASE}/cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic
b_arr = gal.b.deg
nside = 2048

# 高緯度其他 34 節點
others_high = [i for i in range(60) if abs(b_arr[i]) >= 20 and i not in HIGH4]
print(f"高緯度其他: {len(others_high)} 節點")

# 載入三地圖
maps_raw = {}
maps_raw['SMICA'] = hp.read_map('/tmp/smica2.fits')
mn = hp.read_map('/tmp/nilc.fits', field=0, nest=True)
maps_raw['NILC'] = hp.reorder(mn, n2r=True)
mc = hp.read_map('/tmp/commander.fits', field=0, nest=True)
maps_raw['Commander'] = hp.reorder(mc, n2r=True)

pix_all = hp.ang2pix(nside, gal.l.deg, gal.b.deg, lonlat=True)

# SMICA cache 重用
smica_cache = {}
for fw in [1.0, 2.0, 3.0, 4.0, 4.17, 5.0, 7.0, 10.0]:
    fname = f'/tmp/smica2_smooth{fw}.fits'
    if os.path.exists(fname):
        smica_cache[fw] = hp.read_map(fname)
        print(f"[cache] SMICA {fw}° 重用")

def get_smoothed(name, fw):
    if name == 'SMICA' and fw in smica_cache:
        return smica_cache[fw]
    fname = f"{CACHE}/{name}_{fw}.fits"
    if os.path.exists(fname):
        try:
            m = hp.read_map(fname)
            if hp.get_nside(m) == 2048 and len(m) == 50331648 and np.isfinite(m).all():
                print(f"[cache] {name} {fw}° 重用")
                return m
            else:
                print(f"[cache] {name} {fw}° 損壞, 重新平滑")
                os.remove(fname)
        except Exception as e:
            print(f"[cache] {name} {fw}° 讀取失敗 ({e}), 重新平滑")
            os.remove(fname)
    sigma = np.radians(fw) / (2 * np.sqrt(2 * np.log(2)))
    m = hp.remove_dipole(hp.smoothing(maps_raw[name], sigma=sigma))
    hp.write_map(fname, m.astype(np.float32), overwrite=True)
    print(f"[平滑] {name} {fw}° 完成")
    return m

scales = [1.0, 2.0, 3.0, 4.0, 4.17, 5.0, 7.0, 10.0]
print(f"\n{'尺度':<7}" + "".join(f"{name:<24}" for name in ['SMICA', 'NILC', 'Commander']) + "比例")
for fw in scales:
    row = f"{fw:>5.2f}° "
    ratios = []
    for name in ['SMICA', 'NILC', 'Commander']:
        m = get_smoothed(name, fw)
        vals = m[pix_all] * 1e6
        Tz = np.abs(vals[HIGH4]).mean()
        To = np.abs(vals[others_high]).mean()
        ratios.append(Tz/To)
        row += f"ΔE0={Tz:5.1f} 其他={To:5.1f} (r={Tz/To:.3f})  "
    row += f"  [{ratios[0]:.3f}/{ratios[1]:.3f}/{ratios[2]:.3f}]"
    print(row)

# 個別節點 4.17° 三地圖
print("\n=== 個別節點 4.17° 三地圖 ===")
print(f"{'#':<5}" + "".join(f"{name:<14}" for name in ['SMICA', 'NILC', 'Commander']))
for fw in [4.17]:
    m_s, m_n, m_c = get_smoothed('SMICA', fw), get_smoothed('NILC', fw), get_smoothed('Commander', fw)
    for i in HIGH4:
        print(f"#{i:<4}{m_s[pix_all[i]]*1e6:+10.2f}   {m_n[pix_all[i]]*1e6:+10.2f}   {m_c[pix_all[i]]*1e6:+10.2f}")

print("\nDONE")
