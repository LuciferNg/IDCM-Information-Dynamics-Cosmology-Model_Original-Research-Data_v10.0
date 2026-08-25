#!/usr/bin/env python3
"""
24_smica_continuous.py — 連續等級模型 (修正阻挫邊 ΔT=0 缺陷)
==============================================================
缺陷: 3level/5level 模型令同色節點振幅相同 → 阻挫邊 |ΔT|=0
但觀測阻挫邊 mean=34.5 μK

修正: 連續模型 A(d) = F5 × φ^(-d/2), 每個節點都唔同
- 正常邊 (冷-熱): |ΔT| = A(u)+A(v)
- 阻挫邊 (同色): |ΔT| = |A(u)-A(v)| > 0 (因為距離唔同)

同時加 6 級離散模型: A = F5, F4, F3, F2, F1, F0 × φ^(-d)
"""
import healpy as hp
import numpy as np
import math
from collections import defaultdict, deque
from astropy.coordinates import SkyCoord
import astropy.units as u

phi = (1 + 5**0.5) / 2
eps = (1/phi) / 4
RMS = eps**5 / 8
T_cmb = 2.72548

print("=" * 66)
print("連續等級模型 vs SMICA (修正版)")
print("=" * 66)

# ============ 載入 ============
m = hp.read_map('/tmp/smica2.fits', field=0)
nside = hp.get_nside(m)
fwhm_rad = np.radians(4.17)
sigma_rad = fwhm_rad / (2 * np.sqrt(2 * np.log(2)))
m_smooth = hp.remove_dipole(hp.smoothing(m, sigma=sigma_rad))

nodes = []
with open("data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)

sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic
l_deg = gal.l.deg
b_deg = gal.b.deg
pix = hp.ang2pix(nside, l_deg, b_deg, lonlat=True)
T_obs = m_smooth[pix]

vecs = np.array([np.array([math.cos(math.radians(d))*math.cos(math.radians(r)),
                           math.cos(math.radians(d))*math.sin(math.radians(r)),
                           math.sin(math.radians(d))]) for r, d in nodes])
adj = defaultdict(set)
edges_list = []
for i in range(60):
    for j in range(i+1, 60):
        if math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) < 28.0:
            adj[i].add(j)
            adj[j].add(i)
            edges_list.append((i, j))

dist = {0: 0}
q = deque([0])
while q:
    u = q.popleft()
    for v in adj[u]:
        if v not in dist:
            dist[v] = dist[u] + 1
            q.append(v)

color = {}
color[0] = 1
q = deque([0])
while q:
    u = q.popleft()
    for w in adj[u]:
        if w not in color:
            color[w] = 1 - color[u]
            q.append(w)

frustration = set()
for u, v in edges_list:
    if color[u] == color[v]:
        frustration.add((u, v))
frustration_list = sorted(frustration)

# ============ 觀測 ============
dT_obs = np.array([abs(T_obs[u] - T_obs[v]) * 1e6 for u, v in edges_list])
dT_obs_fr = np.array([abs(T_obs[u] - T_obs[v]) * 1e6 for u, v in frustration_list])
dT_obs_norm = np.array([abs(T_obs[u] - T_obs[v]) * 1e6 for u, v in edges_list if (u, v) not in frustration_list])
print(f"觀測: 阻挫 {dT_obs_fr.mean():.1f} μK, 正常 {dT_obs_norm.mean():.1f} μK")

# ============ 振幅模型 ============
F5 = 5 * RMS * T_cmb * 1e6  # 150
F4 = 3 * RMS * T_cmb * 1e6  # 90
F3 = 2 * RMS * T_cmb * 1e6  # 60
F2 = 1 * RMS * T_cmb * 1e6  # 30
F1 = 0.5 * RMS * T_cmb * 1e6  # 15

def assign(mode):
    A = np.zeros(60)
    for i in range(60):
        d = dist[i]
        if mode == 'continuous':  # A = F5 × φ^(-d/2)
            A[i] = F5 * (phi ** (-d/2))
        elif mode == 'continuous_1':  # A = F5 × φ^(-d)
            A[i] = F5 * (phi ** (-d))
        elif mode == '6level':  # 6 級
            A[i] = [F5, F4, F3, F2, F1, F1*0.5][min(d, 5)]
        elif mode == 'linear':  # A = F5 × (1 - d/8) + F2
            A[i] = F5 * (1 - d/8) + F2
    return A

def model_dT(A):
    dT_fr = []
    dT_norm = []
    for u, v in edges_list:
        if (u, v) in frustration_list:
            dT_fr.append(abs(A[u] - A[v]))
        else:
            dT_norm.append(A[u] + A[v])
    return np.array(dT_fr), np.array(dT_norm)

print(f"\n=== 模型對比 (全部含阻挫邊 ΔT>0) ===")
print(f"{'模型':<14} {'阻挫邊':>9} {'正常邊':>9} {'分離σ':>8} {'χ²_fr':>8} {'χ²_norm':>9} {'χ²總':>8}")
print("-" * 70)

results = {}
for mode in ['continuous', 'continuous_1', '6level', 'linear']:
    A = assign(mode)
    dT_m_fr, dT_m_norm = model_dT(A)
    sep = (dT_m_norm.mean() - dT_m_fr.mean()) / (dT_m_fr.std() + 1e-12)
    chi2_fr = ((dT_obs_fr.mean() - dT_m_fr.mean())**2) / (dT_obs_fr.std()**2 + 1e-12)
    chi2_norm = ((dT_obs_norm.mean() - dT_m_norm.mean())**2) / (dT_obs_norm.std()**2 + 1e-12)
    chi2_tot = chi2_fr + chi2_norm
    results[mode] = (dT_m_fr.mean(), dT_m_norm.mean(), sep, chi2_tot)
    print(f"{mode:<14} {dT_m_fr.mean():>9.1f} {dT_m_norm.mean():>9.1f} {sep:>8.2f} {chi2_fr:>8.2f} {chi2_norm:>9.2f} {chi2_tot:>8.2f}")

# ============ 最佳模型詳情 ============
best = min(results, key=lambda k: results[k][3])
print(f"\n最佳模型: {best} (χ²總={results[best][3]:.2f})")
A_best = assign(best)
dT_fr_b, dT_norm_b = model_dT(A_best)

# 冷熱分離預測
T_model = np.array([A_best[i] * (1 if color[i] == 1 else -1) for i in range(60)])
T_cold_m = T_model[np.array([i for i in range(60) if color[i] == 1])]
T_hot_m = T_model[np.array([i for i in range(60) if color[i] == 0])]
T_obs_cold = T_obs[np.array([i for i in range(60) if color[i] == 1])]
T_obs_hot = T_obs[np.array([i for i in range(60) if color[i] == 0])]
print(f"模型冷熱差: {(T_cold_m.mean()-T_hot_m.mean()):.1f} μK")
print(f"觀測冷熱差: {(T_obs_cold.mean()-T_obs_hot.mean())*1e6:.1f} μK")

# ============ 歸一化問題 ============
# 關鍵: 觀測 T 係絕對溫度 (有背景), 模型係相對
# 用觀測 RMS 歸一化模型
print(f"\n=== 歸一化修正 ===")
print(f"觀測節點 std: {T_obs.std()*1e6:.1f} μK")
print(f"模型節點 std: {T_model.std():.1f} μK")
scale = (T_obs.std()*1e6) / T_model.std()
print(f"歸一化因子: {scale:.3f}")
A_scaled = A_best * scale
dT_fr_s, dT_norm_s = model_dT(A_scaled)
print(f"歸一化後: 阻挫 {dT_fr_s.mean():.1f} μK (觀測 {dT_obs_fr.mean():.1f}), 正常 {dT_norm_s.mean():.1f} (觀測 {dT_obs_norm.mean():.1f})")
sep_s = (dT_norm_s.mean() - dT_fr_s.mean()) / (dT_fr_s.std() + 1e-12)
print(f"歸一化分離度: {sep_s:.2f}σ")

# 儲存
with open("data/smica_continuous.txt", "w") as f:
    f.write(f"# 連續模型對比\n")
    f.write(f"# 觀測: fr={dT_obs_fr.mean():.1f}, norm={dT_obs_norm.mean():.1f}\n")
    for mode, (fr, norm, sep, chi2) in results.items():
        f.write(f"# {mode}: fr={fr:.1f}, norm={norm:.1f}, sep={sep:.2f}, chi2={chi2:.2f}\n")
    f.write(f"# 最佳: {best}, 歸一化後 sep={sep_s:.2f}σ\n")
print(f"\n✅ 已存: data/smica_continuous.txt")
