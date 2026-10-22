#!/usr/bin/env python3
"""D03_coldspot_position.py — 大冷斑定位確認 (用本地數據)"""
import numpy as np
import math
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as astro_u
from scipy import stats as st

BASE = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh'
print("=" * 72)
print("O4_renew D03: 大冷斑定位確認")
print("=" * 72)

nodes = np.loadtxt(f'{BASE}/cmb_cold_spot/data/a5_nodes.txt')
print(f"\n=== 1. a5_nodes.txt 節點 0 (冷斑候選) ===")
print(f"    ICRS (RA, Dec) = ({nodes[0][0]:.4f}°, {nodes[0][1]:.4f}°)")

sc = SkyCoord(ra=nodes[0][0]*astro_u.deg, dec=nodes[0][1]*astro_u.deg, frame='icrs')
gal = sc.galactic
print(f"    → Galactic (l, b) = ({gal.l.deg:.4f}°, {gal.b.deg:.4f}°)")

# SMICA 上冷斑像素 (最冷點)
m = hp.read_map('/tmp/smica2.fits', field=0)
nside = hp.get_nside(m)
# 平滑後搵最冷點
sigma_rad = np.radians(4.17) / (2 * np.sqrt(2 * np.log(2)))
m_s = hp.remove_dipole(hp.smoothing(m, sigma=sigma_rad))
coldest_pix = np.argmin(m_s)
coldest_l, coldest_b = hp.pix2ang(nside, coldest_pix, lonlat=True)
print(f"\n=== 2. SMICA 4.17° 平滑全圖最冷點 ===")
print(f"    Galactic (l, b) = ({coldest_l:.2f}°, {coldest_b:.2f}°)")
print(f"    溫度 = {m_s[coldest_pix]*1e6:.1f} μK")

# 同 node 0 距離
ang = hp.rotator.angdist(np.array([gal.l.deg, gal.b.deg]), np.array([coldest_l, coldest_b]), lonlat=True)
print(f"    同 node 0 角距離 = {np.degrees(ang)[0]:.2f}°")

# node 0 附近最冷?
pix0 = hp.ang2pix(nside, gal.l.deg, gal.b.deg, lonlat=True)
print(f"\n=== 3. node 0 位置 ===")
print(f"    node0 溫度 (4.17° 平滑) = {m_s[pix0]*1e6:.1f} μK")
print(f"    node0 喺全圖 rank = {int(st.rankdata(m_s)[pix0])}/{len(m_s)} (1=最冷)")

# 文獻參考: Cruz 2005 冷斑 (Galactic 209°, -57°)
print(f"\n=== 4. 文獻對照 ===")
print(f"    Cruz 2005: 冷斑 Galactic (209°, -57°)")
print(f"    node 0:    Galactic ({gal.l.deg:.1f}°, {gal.b.deg:.1f}°)")
print(f"    → 偏差 = ({abs(gal.l.deg-209):.2f}°, {abs(gal.b.deg+57):.2f}°)")

with open(f'{BASE}/o4_renew/data/D03_coldspot_position.txt', 'w') as f:
    f.write("# O4_renew D03: 冷斑定位\n")
    f.write(f"node0_ICRS={nodes[0][0]:.4f},{nodes[0][1]:.4f}\n")
    f.write(f"node0_Gal={gal.l.deg:.4f},{gal.b.deg:.4f}\n")
    f.write(f"smica_coldest_Gal={coldest_l:.2f},{coldest_b:.2f} temp={m_s[coldest_pix]*1e6:.1f}\n")
    f.write(f"node0_temp={m_s[pix0]*1e6:.1f}\n")
print(f"\n✅ 已存: data/D03_coldspot_position.txt")
