#!/usr/bin/env python3
"""
D02_ladder_verdict.py — 階梯性衰減最終判決 (O4_renew)
=================================================================
問題: 節點有冇「階梯性衰減」(d0 > d1 > d2 > ...)?
方法: 
1. 逐層節點值分佈 (唔止層均)
2. 層均單調性測試 (d0>d1>d2>...?)
3. 每步衰減率 + 誤差
4. 用未平滑/0.5°/4.17° 三種尺度
5. 冷斑 node 0 vs 其他節點嘅 |T| 分佈
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
print("O4_renew D02: 階梯性衰減最終判決")
print("=" * 72)

# ---------- 圖 ----------
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

# ---------- SMICA ----------
m = hp.read_map('/tmp/smica2.fits', field=0)
nside = hp.get_nside(m)
sc = SkyCoord(ra=nodes[:, 0]*astro_u.deg, dec=nodes[:, 1]*astro_u.deg, frame='icrs')
gal = sc.galactic
pix = hp.ang2pix(nside, gal.l.deg, gal.b.deg, lonlat=True)

print(f"\n=== 1. 層均單調性測試 (d0>d1>d2>...?) ===")
for fwhm in [0.0, 0.5, 4.17]:
    if fwhm == 0:
        m_s = hp.remove_dipole(m)
    else:
        sigma_rad = np.radians(fwhm) / (2 * np.sqrt(2 * np.log(2)))
        m_s = hp.remove_dipole(hp.smoothing(m, sigma=sigma_rad))
    T = m_s[pix] * 1e6
    Tabs = np.abs(T)
    means = {}
    for d in range(9):
        idx = [i for i in range(60) if dist[i] == d]
        if idx:
            means[d] = np.mean(Tabs[idx])
    # 單調性: 前 5 層
    seq = [means[d] for d in range(5) if d in means]
    monotone = all(seq[i] > seq[i+1] for i in range(len(seq)-1))
    print(f"FWHM={fwhm:>5}: 層均 = {[f'{means[d]:.1f}' for d in sorted(means)]}")
    print(f"    → 前 5 層單調遞減? {'✅ 係' if monotone else '❌ 唔係'}")

# ---------- 2. 每層節點值 (唔止 mean) ----------
print(f"\n=== 2. 逐層節點 |T| 分佈 (4.17°) ===")
sigma_rad = np.radians(4.17) / (2 * np.sqrt(2 * np.log(2)))
m_s = hp.remove_dipole(hp.smoothing(m, sigma=sigma_rad))
T = m_s[pix] * 1e6
Tabs = np.abs(T)
for d in range(5):
    idx = [i for i in range(60) if dist[i] == d]
    vals = sorted(Tabs[idx])
    print(f"d={d} (n={len(idx)}): {[f'{v:.1f}' for v in vals]}")
    print(f"    median={np.median(vals):.1f}, mean={np.mean(vals):.1f}")

# ---------- 3. 每步衰減率 + 誤差 ----------
print(f"\n=== 3. 每步衰減率 (4.17°) ===")
for d in range(4):
    idx0 = [i for i in range(60) if dist[i] == d]
    idx1 = [i for i in range(60) if dist[i] == d+1]
    if idx0 and idx1:
        r = np.mean(Tabs[idx1]) / np.mean(Tabs[idx0])
        print(f"d{d+1}/d{d}: {r:.3f} (φ⁻¹=0.618)")

# ---------- 4. 節點值分佈總覽 ----------
print(f"\n=== 4. 60 節點 |T| 分佈 (4.17°) ===")
print(f"node 0 (冷斑): {Tabs[0]:.1f} μK")
others = np.delete(Tabs, 0)
print(f"其他 59: mean={np.mean(others):.1f}, median={np.median(others):.1f}, std={np.std(others):.1f}")
print(f"其他 59 範圍: {others.min():.1f} - {others.max():.1f}")
print(f"node0 / others_median = {Tabs[0]/np.median(others):.2f}")
print(f"node0 / others_mean  = {Tabs[0]/np.mean(others):.2f}")

# 冇 node0 嘅層均
print(f"\n=== 5. 冇 node 0 嘅層均 (4.17°) ===")
for fwhm in [0.5, 4.17]:
    sigma_rad = np.radians(fwhm) / (2 * np.sqrt(2 * np.log(2)))
    m_s = hp.remove_dipole(hp.smoothing(m, sigma=sigma_rad))
    T = m_s[pix] * 1e6
    Tabs = np.abs(T)
    means = {}
    for d in range(9):
        idx = [i for i in range(60) if dist[i] == d and i != 0]
        if idx:
            means[d] = np.mean(Tabs[idx])
    seq = [means[d] for d in range(5) if d in means]
    print(f"FWHM={fwhm:>5}: 冇node0層均 = {[f'{means[d]:.1f}' for d in sorted(means)]}")

with open(f'{BASE}/o4_renew/data/D02_ladder_verdict.txt', 'w') as f:
    f.write("# O4_renew D02: 階梯性衰減最終判決\n")
print(f"\n✅ 已存: data/D02_ladder_verdict.txt")
