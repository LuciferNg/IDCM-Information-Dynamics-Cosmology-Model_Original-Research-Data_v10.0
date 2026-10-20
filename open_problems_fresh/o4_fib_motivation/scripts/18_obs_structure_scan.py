#!/usr/bin/env python3
"""
18_obs_structure_scan.py — 1+2 合併: 細平滑層均 + 其他結構檢查
=================================================================
任務 1: 用 0.1° / 未平滑 / 0.5° 重做層均 — 階梯係咪消失?
任務 2: 檢查 60 節點 |T| 有冇其他結構:
  (a) 冷斑 seed (node 0) 係咪特殊?
  (b) ΔE=0 (k=2) 節點壓制 — O3 已證實, 再確認
  (c) hop 層內嘅徑向結構 (同 node 0 角距離 vs |T|)
  (d) 冷/熱色 (2-colouring) 有冇溫度效應?
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
print("O4 18: 觀測結構掃描 — 細平滑層均 + 其他結構")
print("=" * 72)

# ---------- 載入圖 ----------
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

# ---------- ΔE=0 節點 (k=2, 12 個) ----------
A = np.zeros((60, 60))
for u, v in edges:
    A[u, v] = 1; A[v, u] = 1
# 阻挫: 從冷斑 2-colouring
color = {0: 1}
q2 = deque([0])
while q2:
    u = q2.popleft()
    for v in adj[u]:
        if v not in color:
            color[v] = 1 - color[u]
            q2.append(v)
frust_edges = frozenset(frozenset((u, v)) for u, v in edges if color[u] == color[v])
k_count = np.zeros(60, dtype=int)
for (u, v) in edges:
    if color[u] == color[v]:
        k_count[u] += 1; k_count[v] += 1
deltaE0 = np.where(k_count == 2)[0]

# ---------- 載入 SMICA ----------
m = hp.read_map('/tmp/smica2.fits', field=0)
nside = hp.get_nside(m)
sc = SkyCoord(ra=nodes[:, 0]*astro_u.deg, dec=nodes[:, 1]*astro_u.deg, frame='icrs')
gal = sc.galactic
pix = hp.ang2pix(nside, gal.l.deg, gal.b.deg, lonlat=True)

print("\n=== 任務 1: 層均階梯 vs 平滑尺度 ===")
print(f"{'FWHM':>6} {'d0':>8} {'d1':>8} {'d2':>8} {'d3':>8} {'d4':>8} | {'d1/d0':>7} {'d2/d1':>7} {'ANOVA p':>8}")
results = {}
for fwhm in [0.0, 0.1, 0.3, 0.5, 1.0, 2.0, 4.17]:
    if fwhm == 0.0:
        m_s = hp.remove_dipole(m)
    else:
        sigma_rad = np.radians(fwhm) / (2 * np.sqrt(2 * np.log(2)))
        m_s = hp.remove_dipole(hp.smoothing(m, sigma=sigma_rad))
    T = m_s[pix] * 1e6
    Tabs = np.abs(T)
    # 層均
    layer_means = {}
    layer_nodes = {}
    for d in range(9):
        idx = [i for i in range(60) if dist[i] == d]
        if idx:
            layer_means[d] = np.mean(Tabs[idx])
            layer_nodes[d] = [Tabs[i] for i in idx]
    # ANOVA
    groups = [layer_nodes[d] for d in sorted(layer_nodes) if len(layer_nodes[d]) > 1]
    f_stat, p_anova = st.f_oneway(*groups) if len(groups) >= 2 else (float('nan'), float('nan'))
    results[fwhm] = (Tabs.copy(), layer_means, p_anova)
    d1d0 = layer_means.get(1, float('nan')) / layer_means.get(0, float('nan')) if 0 in layer_means and 1 in layer_means else float('nan')
    d2d1 = layer_means.get(2, float('nan')) / layer_means.get(1, float('nan')) if 1 in layer_means and 2 in layer_means else float('nan')
    print(f"{fwhm:>6.2f} {layer_means.get(0,0):>8.1f} {layer_means.get(1,0):>8.1f} {layer_means.get(2,0):>8.1f} {layer_means.get(3,0):>8.1f} {layer_means.get(4,0):>8.1f} | {d1d0:>7.3f} {d2d1:>7.3f} {p_anova:>8.4f}")

print(f"\nφ⁻¹ = {phi**-1:.4f}, φ⁻² = {phi**-2:.4f}")
print("→ 如果階梯係平滑假象, 細平滑 (0.1°) 應該 d1/d0 → 1 (冇衰減)")

# ---------- 任務 2a: 冷斑 seed 特殊性 ----------
print("\n=== 任務 2a: 冷斑 (node 0) 特殊性 ===")
for fwhm in [0.1, 0.5, 4.17]:
    Tabs = results[fwhm][0]
    r0 = st.rankdata(-Tabs)[0]  # rank of node 0 (1 = coldest)
    mean_others = np.mean(Tabs[1:])
    z = (Tabs[0] - mean_others) / np.std(Tabs[1:])
    print(f"FWHM={fwhm:>5}: node0 |T|={Tabs[0]:6.1f} μK, 其他 59 mean={mean_others:5.1f}, rank={r0:.0f}/60, z={z:+.2f}")

# ---------- 任務 2b: ΔE=0 節點壓制 ----------
print("\n=== 任務 2b: ΔE=0 (k=2) 節點壓制 ===")
for fwhm in [0.1, 0.5, 4.17]:
    Tabs = results[fwhm][0]
    d0_mean = np.mean(Tabs[deltaE0])
    other_mean = np.mean(np.delete(Tabs, deltaE0))
    ratio = d0_mean / other_mean
    t_stat, p_welch = st.ttest_ind(Tabs[deltaE0], np.delete(Tabs, deltaE0), equal_var=False)
    print(f"FWHM={fwhm:>5}: ΔE=0 mean={d0_mean:5.1f} vs 其他={other_mean:5.1f}, ratio={ratio:.3f}, Welch p={p_welch:.4f}")

# ---------- 任務 2c: 徑向結構 (角距離 vs |T|) ----------
print("\n=== 任務 2c: 角距離 vs |T| (所有節點, 連續變量) ===")
for fwhm in [0.1, 0.5, 4.17]:
    Tabs = results[fwhm][0]
    ang = np.array([math.degrees(math.acos(np.clip(np.dot(vecs[0], vecs[i]), -1, 1))) for i in range(60)])
    rho, p_sp = st.spearmanr(ang, Tabs)
    rho2, p_pear = st.pearsonr(ang, Tabs)
    print(f"FWHM={fwhm:>5}: Spearman(θ,|T|) ρ={rho:.3f} p={p_sp:.3f} | Pearson(θ,|T|) r={rho2:.3f} p={p_pear:.3f}")

# ---------- 任務 2d: 冷/熱色 溫度效應 ----------
print("\n=== 任務 2d: 2-colour (冷色/熱色) 溫度效應 ===")
for fwhm in [0.1, 0.5, 4.17]:
    Tabs = results[fwhm][0]
    cold_col = np.array([Tabs[i] for i in range(60) if color[i] == 1])
    hot_col = np.array([Tabs[i] for i in range(60) if color[i] == 0])
    t_stat, p_welch = st.ttest_ind(cold_col, hot_col, equal_var=False)
    print(f"FWHM={fwhm:>5}: 冷色 mean={np.mean(cold_col):5.1f} (n={len(cold_col)}) vs 熱色={np.mean(hot_col):5.1f} (n={len(hot_col)}), p={p_welch:.4f}")

with open(f'{BASE}/o4_fib_motivation/data/obs_structure_scan.txt', 'w') as f:
    f.write("# O4 18: 觀測結構掃描\n")
    f.write("# 任務 1: 層均階梯 vs 平滑尺度\n")
    f.write("# 任務 2: 其他結構 (冷斑seed/ΔE=0/徑向/顏色)\n")
print(f"\n✅ 已存: data/obs_structure_scan.txt")
