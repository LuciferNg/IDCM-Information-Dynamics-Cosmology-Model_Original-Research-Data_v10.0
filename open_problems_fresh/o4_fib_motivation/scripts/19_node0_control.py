#!/usr/bin/env python3
"""
19_node0_control.py — 排除 node 0 後徑向結構係咪仍然存在?
=================================================================
任務 2c 發現: Pearson(θ,|T|) 喺細平滑顯著 (p=0.03-0.04)
關鍵控制: 如果係 node 0 (冷斑) 單點驅動, 移除後應該消失

另外檢查:
1. 移除 node 0 後 Pearson/Spearman
2. 移除 node 0 + node 57 (antipode) 後
3. 分層: d=1 內 4 節點 vs 角距離
4. |T| 對數 vs 角距離 (指數衰減測試)
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
print("O4 19: 排除 node 0 控制測試")
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

dist = {0: 0}
q = deque([0])
while q:
    u = q.popleft()
    for v in adj[u]:
        if v not in dist:
            dist[v] = dist[u] + 1
            q.append(v)

m = hp.read_map('/tmp/smica2.fits', field=0)
nside = hp.get_nside(m)
sc = SkyCoord(ra=nodes[:, 0]*astro_u.deg, dec=nodes[:, 1]*astro_u.deg, frame='icrs')
gal = sc.galactic
pix = hp.ang2pix(nside, gal.l.deg, gal.b.deg, lonlat=True)
ang = np.array([math.degrees(math.acos(np.clip(np.dot(vecs[0], vecs[i]), -1, 1))) for i in range(60)])

# antipode (最遠節點)
antipode = np.argmax(ang)
print(f"Antipode: node {antipode}, 角距離 {ang[antipode]:.2f}°")

print("\n=== 1. Pearson/Spearman 排除 node 0 ===")
for fwhm in [0.0, 0.1, 0.5, 4.17]:
    if fwhm == 0.0:
        m_s = hp.remove_dipole(m)
    else:
        sigma_rad = np.radians(fwhm) / (2 * np.sqrt(2 * np.log(2)))
        m_s = hp.remove_dipole(hp.smoothing(m, sigma=sigma_rad))
    T = m_s[pix] * 1e6
    Tabs = np.abs(T)

    # 全部
    rho_p, p_p = st.pearsonr(ang, Tabs)
    rho_s, p_s = st.spearmanr(ang, Tabs)
    # 排除 node 0
    mask1 = np.arange(60) != 0
    rho_p1, p_p1 = st.pearsonr(ang[mask1], Tabs[mask1])
    rho_s1, p_s1 = st.spearmanr(ang[mask1], Tabs[mask1])
    # 排除 node 0 + antipode
    mask2 = (np.arange(60) != 0) & (np.arange(60) != antipode)
    rho_p2, p_p2 = st.pearsonr(ang[mask2], Tabs[mask2])
    rho_s2, p_s2 = st.spearmanr(ang[mask2], Tabs[mask2])

    print(f"FWHM={fwhm:>5}: 全60: P r={rho_p:+.3f} p={p_p:.3f} | S ρ={rho_s:+.3f} p={p_s:.3f}")
    print(f"          excl0:  P r={rho_p1:+.3f} p={p_p1:.3f} | S ρ={rho_s1:+.3f} p={p_s1:.3f}")
    print(f"          excl0+anti: P r={rho_p2:+.3f} p={p_p2:.3f} | S ρ={rho_s2:+.3f} p={p_s2:.3f}")

print("\n=== 2. 對數衰減測試 (ln|T| vs 角距離) ===")
for fwhm in [0.0, 0.1, 0.5, 4.17]:
    if fwhm == 0.0:
        m_s = hp.remove_dipole(m)
    else:
        sigma_rad = np.radians(fwhm) / (2 * np.sqrt(2 * np.log(2)))
        m_s = hp.remove_dipole(hp.smoothing(m, sigma=sigma_rad))
    T = m_s[pix] * 1e6
    Tabs = np.abs(T)
    lnT = np.log(Tabs)
    mask = np.arange(60) != 0
    slope, intercept, r_val, p_val, se = st.linregress(ang[mask], lnT[mask])
    decay = math.exp(slope)  # per-degree decay
    print(f"FWHM={fwhm:>5}: ln|T| vs θ (excl node0): slope={slope:.4f}/deg, decay/deg={decay:.4f}, r={r_val:.3f}, p={p_val:.3f}")

print("\n=== 3. d=1 層內 4 節點 vs 角距離 (n=4 小樣本) ===")
d1_nodes = [i for i in range(60) if dist[i] == 1]
print(f"d=1 節點: {d1_nodes}")
for fwhm in [0.0, 0.1, 0.5, 4.17]:
    if fwhm == 0.0:
        m_s = hp.remove_dipole(m)
    else:
        sigma_rad = np.radians(fwhm) / (2 * np.sqrt(2 * np.log(2)))
        m_s = hp.remove_dipole(hp.smoothing(m, sigma=sigma_rad))
    T = m_s[pix] * 1e6
    Tabs = np.abs(T)
    vals = [(i, ang[i], Tabs[i]) for i in d1_nodes]
    vals.sort(key=lambda x: x[1])
    print(f"FWHM={fwhm:>5}: " + " | ".join(f"n{i}:{v:.0f}μK@{a:.1f}°" for i, a, v in vals))

print("\n=== 4. 冷斑 seed 方向性: 角距離分組 (0-40°, 40-80°, 80-120°, 120-180°) ===")
for fwhm in [0.0, 0.1, 0.5, 4.17]:
    if fwhm == 0.0:
        m_s = hp.remove_dipole(m)
    else:
        sigma_rad = np.radians(fwhm) / (2 * np.sqrt(2 * np.log(2)))
        m_s = hp.remove_dipole(hp.smoothing(m, sigma=sigma_rad))
    T = m_s[pix] * 1e6
    Tabs = np.abs(T)
    bins = [(0, 40), (40, 80), (80, 120), (120, 181)]
    vals = []
    for lo, hi in bins:
        idx = [i for i in range(60) if lo <= ang[i] < hi and i != 0]
        vals.append(f"{lo}-{hi}°: {np.mean(Tabs[idx]):.1f} (n={len(idx)})")
    print(f"FWHM={fwhm:>5}: " + " | ".join(vals))

with open(f'{BASE}/o4_fib_motivation/data/node0_control.txt', 'w') as f:
    f.write("# O4 19: 排除 node 0 控制測試\n")
print(f"\n✅ 已存: data/node0_control.txt")
