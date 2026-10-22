#!/usr/bin/env python3
"""
D01_stats_full.py — O4_renew D 部分: 統計獨立重驗證
=================================================================
D1: BIC 完整比較 (含 constant-mean + φ^-d 自由A)
D2: 排除 node 0 控制
D3: 每步衰減率
D4: p-value 獨立重算
"""
import numpy as np
import math
from collections import defaultdict, deque
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as astro_u
from scipy import stats as st

BASE = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh'
phi = (1 + 5**0.5) / 2
print("=" * 72)
print("O4_renew D01: 統計獨立驗證")
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
ang = np.array([math.degrees(math.acos(np.clip(np.dot(vecs[0], vecs[i]), -1, 1))) for i in range(60)])

# ---------- SMICA ----------
m = hp.read_map('/tmp/smica2.fits', field=0)
nside = hp.get_nside(m)
sc = SkyCoord(ra=nodes[:, 0]*astro_u.deg, dec=nodes[:, 1]*astro_u.deg, frame='icrs')
gal = sc.galactic
pix = hp.ang2pix(nside, gal.l.deg, gal.b.deg, lonlat=True)

print(f"\n=== D1: BIC 完整比較 (4.17° 平滑, N=60) ===")
sigma_rad = np.radians(4.17) / (2 * np.sqrt(2 * np.log(2)))
m_s = hp.remove_dipole(hp.smoothing(m, sigma=sigma_rad))
T = m_s[pix] * 1e6
Tabs = np.abs(T)
sigma_noise = np.std(T)
N = 60

# 模型
models = {}
# constant-mean
models['constant-mean (k=1)'] = (np.full(60, np.mean(Tabs)), 1)
# φ^-d 自由 A
A_best = np.sum(Tabs * phi**np.array([-dist[i] for i in range(60)])) / np.sum(phi**np.array([-2*dist[i] for i in range(60)]))
models[f'φ^-d freeA={A_best:.0f} (k=1)'] = (A_best * phi**np.array([-dist[i] for i in range(60)]), 1)
# φ^-d A=150 固定
models['φ^-d A=150 (k=1)'] = (150 * phi**np.array([-dist[i] for i in range(60)]), 1)
# 3lv
lv3 = np.array([150 if dist[i]==0 else 90 if dist[i]==1 else 60 for i in range(60)])
models['3lv (k=3)'] = (lv3, 3)
# 5lv
lv5 = np.array([150, 90, 60, 30, 30, 30])[[min(dist[i], 5) for i in range(60)]]
models['5lv (k=5)'] = (lv5, 5)
# 6lv
lv6 = np.array([150, 90, 60, 30, 30, 20])[[min(dist[i], 5) for i in range(60)]]
models['6lv (k=6)'] = (lv6, 6)

print(f"{'模型':<26} {'k':>2} {'χ²':>7} {'BIC':>7}")
print("-" * 45)
results = []
for name, (pred, k) in models.items():
    chi2 = np.sum(((Tabs - pred) / sigma_noise)**2)
    bic = chi2 + k * math.log(N)
    results.append((chi2, bic, name, k))
    print(f"{name:<26} {k:>2} {chi2:>7.1f} {bic:>7.1f}")

results.sort(key=lambda x: x[1])
best = results[0]
print(f"\n最佳模型: {best[2]} (BIC={best[1]:.1f})")
print(f"→ {'✅ constant 贏 (距離衰減冇支持)' if 'constant' in best[2] else '❌ 距離模型贏?!'}")
print(f"→ {'✅ 確認舊發現' if abs(best[1] - 33.5) < 0.5 else '⚠️ 數字有出入'}")

# ---------- D2: 排除 node 0 ----------
print(f"\n=== D2: 排除 node 0 控制 ===")
for fwhm in [0.1, 0.5, 4.17]:
    sigma_rad = np.radians(fwhm) / (2 * np.sqrt(2 * np.log(2)))
    m_s = hp.remove_dipole(hp.smoothing(m, sigma=sigma_rad))
    T2 = m_s[pix] * 1e6
    Tabs2 = np.abs(T2)
    mask = np.arange(60) != 0
    r_p_all, p_p_all = st.pearsonr(ang, Tabs2)
    r_p_ex, p_p_ex = st.pearsonr(ang[mask], Tabs2[mask])
    r_s_ex, p_s_ex = st.spearmanr(ang[mask], Tabs2[mask])
    print(f"FWHM={fwhm:>5}: 全60 Pearson p={p_p_all:.3f} | excl0 Pearson p={p_p_ex:.3f} | excl0 Spearman p={p_s_ex:.3f}")
    print(f"    → {'✅ 單點驅動確認' if p_p_all < 0.05 and p_p_ex > 0.05 else ('⚠️ 唔同結果' if p_p_all < 0.05 else '兩者都唔顯著')}")

# ---------- D3: 每步衰減 ----------
print(f"\n=== D3: 每步衰減率 (0.5° + 4.17°) ===")
for fwhm in [0.5, 4.17]:
    sigma_rad = np.radians(fwhm) / (2 * np.sqrt(2 * np.log(2)))
    m_s = hp.remove_dipole(hp.smoothing(m, sigma=sigma_rad))
    T2 = m_s[pix] * 1e6
    Tabs2 = np.abs(T2)
    layers = {}
    for d in range(9):
        idx = [i for i in range(60) if dist[i] == d]
        if idx:
            layers[d] = np.mean(Tabs2[idx])
    r1 = layers.get(1, np.nan) / layers.get(0, np.nan)
    r2 = layers.get(2, np.nan) / layers.get(1, np.nan)
    r3 = layers.get(3, np.nan) / layers.get(2, np.nan)
    print(f"FWHM={fwhm:>5}: d1/d0={r1:.3f} d2/d1={r2:.3f} d3/d2={r3:.3f} (φ⁻¹={phi**-1:.3f})")
    print(f"    → {'✅ 唔穩定確認' if abs(r1-r2) > 0.1 or abs(r2-r3) > 0.1 else '⚠️ 穩定?'}")

# ---------- D4: ΔE=0 ----------
print(f"\n=== D4: ΔE=0 (k=2) 節點 ===")
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
print(f"    ΔE=0 節點: {deltaE0} (n={len(deltaE0)})")
for fwhm in [0.5, 4.17]:
    sigma_rad = np.radians(fwhm) / (2 * np.sqrt(2 * np.log(2)))
    m_s = hp.remove_dipole(hp.smoothing(m, sigma=sigma_rad))
    T2 = m_s[pix] * 1e6
    Tabs2 = np.abs(T2)
    d0_mean = np.mean(Tabs2[deltaE0])
    other_mean = np.mean(np.delete(Tabs2, deltaE0))
    t_stat, p_welch = st.ttest_ind(Tabs2[deltaE0], np.delete(Tabs2, deltaE0), equal_var=False)
    print(f"    FWHM={fwhm:>5}: ΔE=0={d0_mean:.1f} vs other={other_mean:.1f}, ratio={d0_mean/other_mean:.3f}, p={p_welch:.4f}")

with open(f'{BASE}/o4_renew/data/D01_stats.txt', 'w') as f:
    f.write("# O4_renew D01: 統計驗證\n")
    for chi2, bic, name, k in results:
        f.write(f"BIC {name}: chi2={chi2:.1f} bic={bic:.1f}\n")
    f.write(f"best={best[2]} bic={best[1]:.1f}\n")
print(f"\n✅ 已存: data/D01_stats.txt")
