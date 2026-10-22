#!/usr/bin/env python3
"""
C01_map_sampling.py — O4_renew C 部分: 觀測數據獨立重驗證
=================================================================
C1: SMICA map 載入 (nside, 大小)
C2: ICRS→Galactic 轉換 (frame 坑)
C3: node 0 溫度 (4.17° 平滑)
C4: 層均 d1/d0
C5: 跨地圖 (SMICA/NILC/Commander)
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
print("O4_renew C01: 觀測數據獨立驗證")
print("=" * 72)

# ---------- 圖 + 距離 ----------
nodes = np.loadtxt(f'{BASE}/cmb_cold_spot/data/a5_nodes.txt')
def radec_to_vec(ra, dec):
    r = math.radians(ra); d = math.radians(dec)
    return np.array([math.cos(d)*math.cos(r), math.cos(d)*math.sin(r), math.sin(d)])
vecs = np.array([radec_to_vec(r, d) for r, d in nodes])
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

# ---------- C1: SMICA 載入 ----------
print(f"\nC1: SMICA map 載入")
m = hp.read_map('/tmp/smica2.fits', field=0)
nside = hp.get_nside(m)
npix = len(m)
print(f"    nside = {nside}, npix = {npix}")
print(f"    → {'✅ nside 2048' if nside == 2048 else '❌'}")
print(f"    → {'✅ npix 50,331,648' if npix == 12*2048**2 else '❌'}")
print(f"    map 範圍: {np.nanmin(m):.4f} - {np.nanmax(m):.4f} (K)")
print(f"    有 NaN? {np.isnan(m).any()}")

# ---------- C2: 座標轉換 ----------
print(f"\nC2: 座標轉換 (ICRS → Galactic)")
sc = SkyCoord(ra=nodes[:, 0]*astro_u.deg, dec=nodes[:, 1]*astro_u.deg, frame='icrs')
gal = sc.galactic
print(f"    頭 3 節點 Galactic: l={gal.l.deg[:3]}, b={gal.b.deg[:3]}")
# 檢查: node 0 (冷斑) 應該喺 (209°,-57°) ICRS → Galactic 大約 (263.9°, -48.8°)?
print(f"    node 0: ICRS ({nodes[0][0]:.1f}°, {nodes[0][1]:.1f}°) → Gal ({gal.l.deg[0]:.1f}°, {gal.b.deg[0]:.1f}°)")
# 已知冷斑 Galactic 位置: (209°,-57°) (Cruz 2005)
print(f"    已知冷斑 Galactic ≈ (209.0°, -57.0°)")
print(f"    → {'✅ 轉換正確' if abs(gal.l.deg[0]-209)<1 and abs(gal.b.deg[0]+57)<1 else '❌ 轉換錯誤'}")

# 對照: 直接將 ICRS 當 Galactic 用 (frame 坑) 會得到咩?
pix_wrong = hp.ang2pix(nside, nodes[0, 0], nodes[0, 1], lonlat=True)
T_wrong = m[pix_wrong] * 1e6
pix_right = hp.ang2pix(nside, gal.l.deg[0], gal.b.deg[0], lonlat=True)
T_right = m[pix_right] * 1e6
print(f"\n    Frame 坑對照: ICRS 當 Galactic = {T_wrong:.1f} μK vs 正確轉換 = {T_right:.1f} μK")
print(f"    → {'⚠️ 反轉! 確認 frame 坑' if T_wrong > 0 and T_right < 0 else '正常'}")

# ---------- C3: node 溫度 (多尺度) ----------
print(f"\nC3: node 溫度 (4.17° 平滑)")
pix = hp.ang2pix(nside, gal.l.deg, gal.b.deg, lonlat=True)
FWHMS = [0.5, 1.0, 3.0, 4.17, 5.0]
temps = {}
for fwhm in FWHMS:
    sigma_rad = np.radians(fwhm) / (2 * np.sqrt(2 * np.log(2)))
    m_s = hp.remove_dipole(hp.smoothing(m, sigma=sigma_rad))
    T = m_s[pix] * 1e6
    temps[fwhm] = T
    print(f"    FWHM={fwhm:>5}: node0 = {T[0]:+7.1f} μK, 全體 mean|T| = {np.mean(np.abs(T)):.1f}")

# 4.17° 詳細
T = temps[4.17]
Tabs = np.abs(T)
print(f"\n    4.17°: node0 = {T[0]:+.1f} μK ({'✅ -134.2 宣稱' if abs(T[0]+134.2)<2 else '❌ 唔啱'})")
print(f"    4.17°: node0 rank (by |T|) = {int(st.rankdata(-Tabs)[0])}/60")

# ---------- C4: 層均 ----------
print(f"\nC4: 層均 (4.17°)")
layer = {}
for d in range(9):
    idx = [i for i in range(60) if dist[i] == d]
    if idx:
        layer[d] = np.mean(Tabs[idx])
        print(f"    d={d}: n={len(idx):>2}, mean|T|={layer[d]:.1f} μK")
if 0 in layer and 1 in layer:
    d1d0 = layer[1]/layer[0]
    print(f"    d1/d0 = {d1d0:.3f} ({'✅ 0.344 宣稱' if abs(d1d0-0.344)<0.03 else '❌ 唔啱'})")

# ---------- C5: 跨地圖 ----------
print(f"\nC5: 跨地圖 (SMICA/NILC/Commander)")
maps = {
    'SMICA':    ('/tmp/smica2.fits',    False),
    'NILC':     ('/tmp/nilc.fits',      True),
    'Commander':('/tmp/commander.fits', True),
}
for name, (path, is_nest) in maps.items():
    mm = hp.read_map(path, field=0)
    if is_nest:
        mm = hp.reorder(mm, n2r=True)
    ns2 = hp.get_nside(mm)
    pix2 = hp.ang2pix(ns2, gal.l.deg, gal.b.deg, lonlat=True)
    for fwhm in [0.5, 4.17]:
        sigma_rad = np.radians(fwhm) / (2 * np.sqrt(2 * np.log(2)))
        m_s2 = hp.remove_dipole(hp.smoothing(mm, sigma=sigma_rad))
        T2 = m_s2[pix2] * 1e6
        Tabs2 = np.abs(T2)
        l0 = Tabs2[0]
        d1 = [i for i in range(60) if dist[i] == 1]
        d1m = np.mean(Tabs2[d1])
        r = d1m/l0 if l0 > 0 else float('nan')
        print(f"    {name:<10} FWHM={fwhm:>5}: node0={T2[0]:+7.1f} μK, d1/d0={r:.3f}, node0 rank={int(st.rankdata(-Tabs2)[0])}")

with open(f'{BASE}/o4_renew/data/C01_map_sampling.txt', 'w') as f:
    f.write("# O4_renew C01: 觀測數據驗證\n")
    f.write(f"nside={nside} npix={npix}\n")
    f.write(f"node0_gal_l={gal.l.deg[0]:.2f} node0_gal_b={gal.b.deg[0]:.2f}\n")
    for fwhm in FWHMS:
        f.write(f"FWHM{fwhm}: node0={temps[fwhm][0]:+.1f}\n")
print(f"\n✅ 已存: data/C01_map_sampling.txt")
