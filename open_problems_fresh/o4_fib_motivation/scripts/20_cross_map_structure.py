#!/usr/bin/env python3
"""
20_cross_map_structure.py — 任務 3: 獨立觀測數據驗證
=================================================================
用 NILC + Commander (獨立 component-separation 方法) 驗證:
1. 層均階梯 (d1/d0, d2/d1) 係咪跨地圖一致?
2. Pearson 徑向相關 (θ,|T|) 係咪跨地圖一致?
3. ΔE=0 節點壓制係咪跨地圖一致?
4. 冷斑 (node 0) rank 係咪跨地圖一致?

如果三種獨立方法一致 → 結構係真實 (唔係 SMICA 特定假象)
如果唔一致 → 結構係分離方法假象
"""
import numpy as np
import math
from collections import defaultdict, deque
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as astro_u
from scipy import stats as st

phi = (1 + 5**0.5) / 2
BASE = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh'

print("=" * 72)
print("O4 20: 獨立觀測數據 (NILC/Commander) 跨地圖驗證")
print("=" * 72)

# ---------- 圖 ----------
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
dist = {0: 0}
q = deque([0])
while q:
    u = q.popleft()
    for v in adj[u]:
        if v not in dist:
            dist[v] = dist[u] + 1
            q.append(v)
ang = np.array([math.degrees(math.acos(np.clip(np.dot(vecs[0], vecs[i]), -1, 1))) for i in range(60)])

# ΔE=0 節點
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
deltaE0 = np.where(k_count == 2)[0]

# ---------- 地圖 ----------
maps = {
    'SMICA':    ('/tmp/smica2.fits',    False),
    'NILC':     ('/tmp/nilc.fits',      True),
    'Commander':('/tmp/commander.fits', True),
}

FWHMS = [0.5, 4.17]
print(f"\n{'地圖':<10} {'FWHM':>5} {'d1/d0':>7} {'d2/d1':>7} {'Pearson p':>9} {'Spear p':>8} {'ΔE=0 ratio':>11} {'Welch p':>8} {'node0 rank':>10}")

summary = []
for name, (path, is_nest) in maps.items():
    m = hp.read_map(path, field=0)
    if is_nest:
        m = hp.reorder(m, n2r=True)
    nside = hp.get_nside(m)
    sc = SkyCoord(ra=nodes[:, 0]*astro_u.deg, dec=nodes[:, 1]*astro_u.deg, frame='icrs')
    gal = sc.galactic
    pix = hp.ang2pix(nside, gal.l.deg, gal.b.deg, lonlat=True)

    for fwhm in FWHMS:
        sigma_rad = np.radians(fwhm) / (2 * np.sqrt(2 * np.log(2)))
        m_s = hp.remove_dipole(hp.smoothing(m, sigma=sigma_rad))
        T = m_s[pix] * 1e6
        Tabs = np.abs(T)

        # 層均
        l0 = Tabs[0]
        d1_idx = [i for i in range(60) if dist[i] == 1]
        d2_idx = [i for i in range(60) if dist[i] == 2]
        d1d0 = np.mean(Tabs[d1_idx]) / l0
        d2d1 = np.mean(Tabs[d2_idx]) / np.mean(Tabs[d1_idx])

        # 徑向
        mask = np.arange(60) != 0
        r_p, p_p = st.pearsonr(ang[mask], Tabs[mask])
        r_s, p_s = st.spearmanr(ang[mask], Tabs[mask])

        # ΔE=0
        d0_mean = np.mean(Tabs[deltaE0])
        other_mean = np.mean(np.delete(Tabs, deltaE0))
        ratio = d0_mean / other_mean
        t_stat, p_welch = st.ttest_ind(Tabs[deltaE0], np.delete(Tabs, deltaE0), equal_var=False)

        # node0 rank (1 = 最冷)
        rank0 = int(st.rankdata(-Tabs)[0])

        print(f"{name:<10} {fwhm:>5.2f} {d1d0:>7.3f} {d2d1:>7.3f} {p_p:>9.4f} {p_s:>8.4f} {ratio:>11.3f} {p_welch:>8.4f} {rank0:>10d}")
        summary.append((name, fwhm, d1d0, d2d1, p_p, p_s, ratio, p_welch, rank0))

print("\n=== 跨地圖一致性 ===")
# 對每個 FWHM, 比較 3 地圖嘅 d1/d0
for fwhm in FWHMS:
    vals = [s for s in summary if s[1] == fwhm]
    d1d0s = [s[2] for s in vals]
    pps = [s[4] for s in vals]
    print(f"FWHM={fwhm}: d1/d0 = {d1d0s} → spread {(max(d1d0s)-min(d1d0s))/np.mean(d1d0s)*100:.1f}%")
    print(f"          Pearson p = {pps} → 全部<0.05? {all(p < 0.05 for p in pps)}")

with open(f'{BASE}/o4_fib_motivation/data/cross_map_structure.txt', 'w') as f:
    f.write("# O4 20: 跨地圖結構驗證 (SMICA/NILC/Commander)\n")
    for s in summary:
        f.write(f"{s[0]} {s[1]} {s[2]:.3f} {s[3]:.3f} {s[4]:.4f} {s[5]:.4f} {s[6]:.3f} {s[7]:.4f} {s[8]}\n")
print(f"\n✅ 已存: data/cross_map_structure.txt")
