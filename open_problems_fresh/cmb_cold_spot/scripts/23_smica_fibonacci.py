#!/usr/bin/env python3
"""
23_smica_fibonacci.py — Fibonacci 等級模型 vs SMICA 真數據
============================================================
IDCM 修正: 節點振幅由拓撲地位 (到冷斑 BFS 距離) 決定
- 距離 0 (冷斑): F₅ = 5×RMS = 150 μK
- 距離 1: F₄ = 3×RMS = 90 μK
- 距離 ≥2: F₃ = 2×RMS = 60 μK

預期:
- 正常邊 (冷-熱): |ΔT| ≈ A(u)+A(v) 範圍 150-240 μK
- 阻挫邊 (同色): |ΔT| ≈ |A(u)-A(v)| 範圍 30-90 μK
→ 雙峰分離應該縮細 (真實觀測 34.5 vs 53.1)

同時對比 3 級分配 vs 連續分配
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
print("Fibonacci 等級模型 vs SMICA")
print("=" * 66)

# ============ 1. 載入 + 平滑 ============
m = hp.read_map('/tmp/smica2.fits', field=0)
nside = hp.get_nside(m)
fwhm_rad = np.radians(4.17)
sigma_rad = fwhm_rad / (2 * np.sqrt(2 * np.log(2)))
m_smooth = hp.remove_dipole(hp.smoothing(m, sigma=sigma_rad))
print(f"SMICA 5° 平滑: std={m_smooth.std()*1e6:.1f} μK")

# ============ 2. 節點 + 圖 ============
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

# BFS 距離
dist = {0: 0}
q = deque([0])
while q:
    u = q.popleft()
    for v in adj[u]:
        if v not in dist:
            dist[v] = dist[u] + 1
            q.append(v)

# 著色
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

# ============ 3. 三種等級模型 ============
F5 = 5 * RMS * T_cmb * 1e6  # 150.0 μK
F4 = 3 * RMS * T_cmb * 1e6  # 90.0 μK
F3 = 2 * RMS * T_cmb * 1e6  # 60.0 μK
F2 = 1 * RMS * T_cmb * 1e6  # 30.0 μK

def assign_levels(dist, mode):
    """分配振幅 (μK)"""
    A = np.zeros(60)
    if mode == 'uniform':  # 舊模型
        A[:] = F5
    elif mode == '3level':  # 3 級: 距離 0→F5, 1→F4, ≥2→F3
        for i in range(60):
            d = dist[i]
            A[i] = F5 if d == 0 else (F4 if d == 1 else F3)
    elif mode == '5level':  # 5 級: 距離 0→F5, 1→F4, 2→F3, 3→F2, ≥4→F2
        for i in range(60):
            d = dist[i]
            A[i] = F5 if d == 0 else (F4 if d == 1 else (F3 if d == 2 else F2))
    elif mode == 'dist':  # 連續: A ∝ F5 × φ^(-d/2) 衰減
        for i in range(60):
            A[i] = F5 * (phi ** (-dist[i]/2))
    return A

# ============ 4. 模型預期 |ΔT| ============
def model_dT(A, edges, frustration_set):
    """模型邊 |ΔT|: 同色邊 = |A(u)-A(v)|, 異色邊 = A(u)+A(v)"""
    dT = []
    for u, v in edges:
        if (u, v) in frustration_set:
            dT.append(abs(A[u] - A[v]))
        else:
            dT.append(A[u] + A[v])
    return np.array(dT)

# ============ 5. 觀測 |ΔT| ============
dT_obs = np.array([abs(T_obs[u] - T_obs[v]) * 1e6 for u, v in edges_list])
dT_obs_fr = np.array([abs(T_obs[u] - T_obs[v]) * 1e6 for u, v in frustration_list])
dT_obs_norm = np.array([abs(T_obs[u] - T_obs[v]) * 1e6 for u, v in edges_list if (u, v) not in frustration_list])

print(f"\n=== 觀測 SMICA ===")
print(f"阻挫邊: mean={dT_obs_fr.mean():.1f} μK")
print(f"正常邊: mean={dT_obs_norm.mean():.1f} μK")

# ============ 6. 各模型對比 ============
print(f"\n=== 模型預期 vs 觀測 ===")
print(f"{'模型':<12} {'阻挫邊':>10} {'正常邊':>10} {'分離σ':>8} {'χ²/邊':>8}")
print("-" * 56)

for mode in ['uniform', '3level', '5level', 'dist']:
    A = assign_levels(dist, mode)
    dT_model = model_dT(A, edges_list, frustration_list)
    dT_m_fr = model_dT(A, frustration_list, frustration_list)
    dT_m_norm = model_dT(A, [(u,v) for u,v in edges_list if (u,v) not in frustration_list], frustration_list)
    
    # 分離度 (模型自身)
    sep_model = (dT_m_norm.mean() - dT_m_fr.mean()) / (dT_m_fr.std() + 1e-12)
    
    # 對比觀測: 擬合優度 (chi2 用觀測 mean 同模型 mean 差)
    chi2_fr = ((dT_obs_fr.mean() - dT_m_fr.mean())**2) / (dT_obs_fr.std()**2 + 1e-12)
    chi2_norm = ((dT_obs_norm.mean() - dT_m_norm.mean())**2) / (dT_obs_norm.std()**2 + 1e-12)
    chi2_total = chi2_fr + chi2_norm
    
    print(f"{mode:<12} {dT_m_fr.mean():>10.1f} {dT_m_norm.mean():>10.1f} {sep_model:>8.2f} {chi2_total:>8.2f}")

# ============ 7. 擬合度: 3level 模型 vs 觀測直方圖 ============
print(f"\n=== 3-level 模型擬合詳情 ===")
A3 = assign_levels(dist, '3level')
dT3_fr = model_dT(A3, frustration_list, frustration_list)
dT3_norm = model_dT(A3, [(u,v) for u,v in edges_list if (u,v) not in frustration_list], frustration_list)
print(f"模型阻挫邊: mean={dT3_fr.mean():.1f} μK (觀測 {dT_obs_fr.mean():.1f})")
print(f"模型正常邊: mean={dT3_norm.mean():.1f} μK (觀測 {dT_obs_norm.mean():.1f})")

# 分離度
sep3 = (dT3_norm.mean() - dT3_fr.mean()) / (dT3_fr.std() + 1e-12)
print(f"模型分離度: {sep3:.2f}σ (觀測 1.06σ, 舊模型 17.3σ)")

# 等級分佈
print(f"\n等級分佈:")
from collections import Counter
levels = Counter(dist[i] for i in range(60))
for d in sorted(levels):
    print(f"  距離 {d}: {levels[d]} 節點 → {'F5' if d==0 else 'F4' if d==1 else 'F3'}")

# ============ 8. 冷熱分離預測 vs 觀測 ============
T_cold_model = np.array([A3[i] * (1 if color[i]==1 else 0) for i in range(60)])
T_hot_model = np.array([A3[i] * (1 if color[i]==0 else 0) for i in range(60)])
# 注意: 模型振幅係 |ΔT| 幅度, 符號由顏色決定
T_model_sign = np.array([A3[i] * (1 if color[i]==1 else -1) for i in range(60)])
T_obs_cold = T_obs[np.array([i for i in range(60) if color[i]==1])]
T_obs_hot = T_obs[np.array([i for i in range(60) if color[i]==0])]
print(f"\n=== 冷熱分離: 模型 vs 觀測 ===")
print(f"模型: 冷節點 = -150~-60 μK, 熱節點 = +60~+150 μK")
print(f"觀測: 冷節點 mean = {T_obs_cold.mean()*1e6:.1f} μK, 熱節點 mean = {T_obs_hot.mean()*1e6:.1f} μK")
print(f"觀測冷-熱差: {(T_obs_cold.mean()-T_obs_hot.mean())*1e6:.1f} μK")

# 儲存
with open("data/smica_fibonacci.txt", "w") as f:
    f.write(f"# Fibonacci 等級模型對比\n")
    f.write(f"# 觀測: fr={dT_obs_fr.mean():.1f}, norm={dT_obs_norm.mean():.1f}, sep=1.06σ\n")
    f.write(f"# 3level: fr={dT3_fr.mean():.1f}, norm={dT3_norm.mean():.1f}, sep={sep3:.2f}σ\n")
    f.write(f"# idx dist color A_3level_uK T_obs_uK\n")
    for i in range(60):
        f.write(f"{i} {dist[i]} {color[i]} {A3[i]:.1f} {T_obs[i]*1e6:.2f}\n")
print(f"\n✅ 已存: data/smica_fibonacci.txt")
