#!/usr/bin/env python3
"""
13_node45_multiscale.py — Node 45 深度分析 (完整版, 無超時)
============================================================
紅燈 2: node 45 (+1.57 μK @ b=-8.4°) 係咪銀河前景假象?

完整測試: 9 尺度 × 3 地圖 (SMICA/NILC/Commander)
- 每尺度每地圖平滑結果 cache 到 /tmp/cache_o3/ 避免重複運算
- SMICA 已有 cache 直接重用 (/tmp/smica2_smooth*.fits)
- 輸出完整表格 + 對照組 (全 60 節點 spread + 其他 ΔE=0 節點)
"""
import healpy as hp
import numpy as np
import math
import os
from astropy.coordinates import SkyCoord
import astropy.units as u

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
CACHE = "/tmp/cache_o3"
os.makedirs(CACHE, exist_ok=True)

nodes = []
with open(f"{BASE}/cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic
nside = 2048
pix_all = hp.ang2pix(nside, gal.l.deg, gal.b.deg, lonlat=True)

# 載入三地圖 (RING ordering)
maps_raw = {}
maps_raw['SMICA'] = hp.read_map('/tmp/smica2.fits')
mn = hp.read_map('/tmp/nilc.fits', field=0, nest=True)
maps_raw['NILC'] = hp.reorder(mn, n2r=True)
mc = hp.read_map('/tmp/commander.fits', field=0, nest=True)
maps_raw['Commander'] = hp.reorder(mc, n2r=True)

# 既有 SMICA cache (直接重用, 唔重新平滑)
smica_cache = {}
for fw in [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 7.0, 10.0]:
    fname = f'/tmp/smica2_smooth{fw}.fits'
    if os.path.exists(fname):
        smica_cache[fw] = hp.read_map(fname)
        print(f"[cache] SMICA {fw}° 重用")

def get_smoothed(name, fw):
    """平滑並 cache, 重用已有"""
    # SMICA 重用舊 cache
    if name == 'SMICA' and fw in smica_cache:
        return smica_cache[fw]
    fname = f"{CACHE}/{name}_{fw}.fits"
    if os.path.exists(fname):
        try:
            m = hp.read_map(fname)
            # 完整性驗證
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
    # 寫入前檢查空間
    hp.write_map(fname, m.astype(np.float32), overwrite=True)
    print(f"[平滑] {name} {fw}° 完成")
    return m

print("=" * 66)
print("Node 45 完整多尺度三地圖分析 (9 尺度 × 3 地圖)")
print("=" * 66)
print(f"Node 45: l={gal.l.deg[45]:.2f}, b={gal.b.deg[45]:.2f}")
print()

scales = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 4.17, 5.0, 7.0, 10.0]
print(f"{'尺度':<8}{'SMICA':<12}{'NILC':<12}{'Commander':<12}{'max|Δ|':<8}")
all_spreads = {}
for fw in scales:
    vals = []
    for name in ['SMICA', 'NILC', 'Commander']:
        m = get_smoothed(name, fw)
        vals.append(m[pix_all[45]]*1e6)
    spread = max(abs(vals[i]-vals[j]) for i in range(3) for j in range(i+1, 3))
    all_spreads[fw] = spread
    print(f"{fw:>5.2f}°  {vals[0]:+9.2f}  {vals[1]:+9.2f}  {vals[2]:+9.2f}  {spread:6.2f}")

# 對比: 全 60 節點三地圖 spread (4.17°)
print("\n=== 全 60 節點三地圖 spread (4.17°) ===")
vals_all = {}
for name in ['SMICA', 'NILC', 'Commander']:
    m = get_smoothed(name, 4.17)
    vals_all[name] = m[pix_all]*1e6
spreads = np.array([max(abs(vals_all['SMICA'][i]-vals_all['NILC'][i]),
                        abs(vals_all['SMICA'][i]-vals_all['Commander'][i]),
                        abs(vals_all['NILC'][i]-vals_all['Commander'][i])) for i in range(60)])
print(f"Node 45 spread: {spreads[45]:.2f} μK")
print(f"全 60 節點: mean={spreads.mean():.2f}, std={spreads.std():.2f}, max={spreads.max():.2f}")
print(f"Node 45 百分位: {(spreads < spreads[45]).mean()*100:.0f}%")

# 對比: 其他 ΔE=0 節點三地圖 spread (4.17°)
print("\n=== 其他 ΔE=0 節點 spread (4.17°) ===")
ZERO_E = {10, 12, 19, 22, 23, 25, 28, 32, 37, 40, 45, 46}
for i in sorted(ZERO_E):
    s = spreads[i]
    grp = "高緯" if abs(gal.b.deg[i]) >= 20 else "銀河盤"
    print(f"  #{i}: spread={s:.2f} μK ({grp})")

# Node 45 附近區域 (各尺度)
print("\n=== Node 45 附近 5° 區域 (三地圖, 各尺度) ===")
v45 = np.array([math.cos(math.radians(nodes[45,1]))*math.cos(math.radians(nodes[45,0])),
                math.cos(math.radians(nodes[45,1]))*math.sin(math.radians(nodes[45,0])),
                math.sin(math.radians(nodes[45,1]))])
for fw in [2.0, 3.0, 4.17, 5.0]:
    vals = []
    for name in ['SMICA', 'NILC', 'Commander']:
        m = get_smoothed(name, fw)
        n64 = 64
        m64 = hp.ud_grade(m, n64)
        disc = hp.query_disc(n64, v45, np.radians(5))
        vals.append(m64[disc].mean()*1e6)
    print(f"  {fw:>4.1f}°: SMICA={vals[0]:+7.2f}  NILC={vals[1]:+7.2f}  Commander={vals[2]:+7.2f}  (區域 mean)")

print("\nDONE")
