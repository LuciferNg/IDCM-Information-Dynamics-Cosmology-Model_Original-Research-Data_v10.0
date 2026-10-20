#!/usr/bin/env python3
"""
21_highlat_deltaE0_cross.py — 高緯 ΔE=0 子集跨地圖驗證
=================================================================
釐清: O3 聲稱高緯 4 節點 (10,22,25,32) 跨地圖 ratio 0.375-0.416
     但 20 顯示全部 12 節點喺 NILC/Commander 唔顯著

檢查: 高緯 4 節點子集 (|b|≥30°) 喺 SMICA/NILC/Commander 嘅 ratio
"""
import numpy as np
import math
from collections import defaultdict, deque
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as astro_u
from scipy import stats as st

BASE = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh'

print("=" * 72)
print("O4 21: 高緯 ΔE=0 子集跨地圖驗證")
print("=" * 72)

nodes = np.loadtxt(f'{BASE}/cmb_cold_spot/data/a5_nodes.txt')
vecs = np.array([np.array([math.cos(math.radians(d))*math.cos(math.radians(r)),
                           math.cos(math.radians(d))*math.sin(math.radians(r)),
                           math.sin(math.radians(d))]) for r, d in nodes])
adj = defaultdict(set)
edges = []
for i in range(60):
    for j in range(i+1, 60):
        if math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) < 28.0:
            adj[i].add(j); adj[j].add(i)
            edges.append((i, j))
color = {0: 1}
q2 = deque([0])
while q2:
    u = q2.popleft()
    for v in adj[u]:
        if v not in color:
            color[v] = 1 - color[u]
            q2.append(v)
k_count = np.zeros(60, dtype=int)
for (u, v) in edges:
    if color[u] == color[v]:
        k_count[u] += 1; k_count[v] += 1
deltaE0_all = np.where(k_count == 2)[0]

# 高緯 (|b|≥30°)
sc_all = SkyCoord(ra=nodes[:, 0]*astro_u.deg, dec=nodes[:, 1]*astro_u.deg, frame='icrs')
gal_all = sc_all.galactic
b_abs = np.abs(gal_all.b.deg)
highlat_dE0 = deltaE0_all[b_abs[deltaE0_all] >= 30]
highlat_others = np.array([i for i in range(60) if b_abs[i] >= 30 and k_count[i] != 2])
print(f"高緯 ΔE=0 節點: {highlat_dE0}")
print(f"高緯其他節點 (n={len(highlat_others)}): {highlat_others}")

maps = {
    'SMICA':    ('/tmp/smica2.fits',    False),
    'NILC':     ('/tmp/nilc.fits',      True),
    'Commander':('/tmp/commander.fits', True),
}

print(f"\n{'地圖':<10} {'FWHM':>5} {'高緯ΔE=0 mean':>14} {'高緯其他 mean':>14} {'ratio':>7} {'Welch p':>8}")
for name, (path, is_nest) in maps.items():
    m = hp.read_map(path, field=0)
    if is_nest:
        m = hp.reorder(m, n2r=True)
    nside = hp.get_nside(m)
    sc = SkyCoord(ra=nodes[:, 0]*astro_u.deg, dec=nodes[:, 1]*astro_u.deg, frame='icrs')
    gal = sc.galactic
    pix = hp.ang2pix(nside, gal.l.deg, gal.b.deg, lonlat=True)
    for fwhm in [0.5, 4.17]:
        sigma_rad = np.radians(fwhm) / (2 * np.sqrt(2 * np.log(2)))
        m_s = hp.remove_dipole(hp.smoothing(m, sigma=sigma_rad))
        T = m_s[pix] * 1e6
        Tabs = np.abs(T)
        d0_mean = np.mean(Tabs[highlat_dE0])
        other_mean = np.mean(Tabs[highlat_others])
        ratio = d0_mean / other_mean
        t_stat, p_welch = st.ttest_ind(Tabs[highlat_dE0], Tabs[highlat_others], equal_var=False)
        print(f"{name:<10} {fwhm:>5.2f} {d0_mean:>14.2f} {other_mean:>14.2f} {ratio:>7.3f} {p_welch:>8.4f}")

with open(f'{BASE}/o4_fib_motivation/data/highlat_deltaE0_cross.txt', 'w') as f:
    f.write("# O4 21: 高緯 ΔE=0 子集跨地圖驗證\n")
print(f"\n✅ 已存: data/highlat_deltaE0_cross.txt")
