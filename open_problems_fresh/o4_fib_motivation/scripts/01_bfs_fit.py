#!/usr/bin/env python3
"""
01_bfs_fit.py — BFS 距離函數擬合: Fibonacci 級 vs φ 衰減
========================================================
O4 核心問題 1: 節點振幅 A(d) 係 F_{5-d}×30 (整數 Fibonacci 級)
定係 150×φ^(-d) (φ 衰減)? 定係 150×φ^(-d/2)?

對每個 BFS 距離層, 用 SMICA 4.17° 平滑數據計觀測 |T| mean,
同每個候選模型比較 (χ² 用層內 spread 做誤差)。
"""
import numpy as np
import healpy as hp
import math
from collections import defaultdict, deque
from astropy.coordinates import SkyCoord
import astropy.units as u

phi = (1 + 5**0.5) / 2
eps = (1/phi) / 4
RMS = eps**5 / 8
T_cmb = 2.72548
F = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]  # F_0..F_9

print("=" * 72)
print("O4 01: BFS 距離函數 — Fibonacci 級 vs φ 衰減")
print("=" * 72)

# ---------- 1. 載入 SMICA (4.17° = R8 平滑, 同 23_smica_fibonacci.py) ----------
m = hp.read_map('/tmp/smica2.fits', field=0)
nside = hp.get_nside(m)
fwhm_rad = np.radians(4.17)
sigma_rad = fwhm_rad / (2 * np.sqrt(2 * np.log(2)))
m_smooth = hp.remove_dipole(hp.smoothing(m, sigma=sigma_rad))

nodes = np.loadtxt('/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt')
sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic
pix = hp.ang2pix(nside, gal.l.deg, gal.b.deg, lonlat=True)
T_obs = m_smooth[pix] * 1e6  # μK

# ---------- 2. Graph + BFS ----------
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

# 著色 (冷斑 = 1)
color = {0: 1}
q = deque([0])
while q:
    u = q.popleft()
    for w in adj[u]:
        if w not in color:
            color[w] = 1 - color[u]
            q.append(w)

print(f"BFS 距離分佈: " + " ".join(f"d{i}:{sum(1 for x in range(60) if dist[x]==i)}" for i in range(9)))
print(f"邊數: {len(edges)} (期望 120)")
print(f"阻挫邊: {sum(1 for u,v in edges if color[u]==color[v])} (期望 32)")

# ---------- 3. 每層觀測 |T| ----------
print(f"\n{'d':>3} {'n':>4} {'obs|T| mean':>12} {'std':>7} {'F_{5-d}×30':>10} {'150φ^-d':>9} {'150φ^-d/2':>10} {'F_{6-d}?':>8}")
print("-" * 72)
layer_stats = {}
for d in range(9):
    idx = [i for i in range(60) if dist[i] == d]
    if not idx:
        continue
    absT = np.abs(T_obs[idx])
    mean_a, std_a = absT.mean(), absT.std()
    layer_stats[d] = (mean_a, std_a, len(idx))
    m1 = F[5-d] * 30 if (5-d) >= 0 else 30
    m2 = 150 * phi**(-d)
    m3 = 150 * phi**(-d/2)
    m4 = F[6-d] * 30 if (6-d) >= 0 else 30
    print(f"{d:>3} {len(idx):>4} {mean_a:>12.1f} {std_a:>7.1f} {m1:>10.1f} {m2:>9.1f} {m3:>10.1f} {m4:>8.1f}")

# ---------- 4. 模型 χ² 比較 (用層內 spread 做誤差) ----------
models = {
    'uniform (all 150)':   lambda d: 150.0,
    'F_{5-d}×30 (3lv 截斷)': lambda d: F[5-d]*30 if d <= 2 else 60.0,
    'F_{5-d}×30 (全層)':   lambda d: F[5-d]*30 if (5-d) >= 0 else 30.0,
    'F_{6-d}×30 (全層)':   lambda d: F[6-d]*30 if (6-d) >= 0 else 30.0,
    '150×φ^(-d)':          lambda d: 150.0 * phi**(-d),
    '150×φ^(-d/2)':        lambda d: 150.0 * phi**(-d/2),
    '30×φ^(5-d)':          lambda d: 30.0 * phi**(5-d),
}
print(f"\n=== 模型 χ² (誤差 = 層內 std) ===")
print(f"{'模型':<26} {'χ²':>8} {'dof':>5} {'χ²/dof':>8}")
print("-" * 52)
results = {}
for name, fn in models.items():
    chi2 = 0; dof = 0
    for d in range(9):
        if d not in layer_stats:
            continue
        mean_a, std_a, n = layer_stats[d]
        pred = fn(d)
        chi2 += ((mean_a - pred) / max(std_a, 1e-9))**2
        dof += 1
    dof -= 1  # 1 參數 (全局振幅)
    results[name] = chi2 / max(dof, 1)
    print(f"{name:<26} {chi2:>8.1f} {dof:>5} {chi2/max(dof,1):>8.2f}")

# ---------- 5. 節點級 χ² (同 04_fib_ladder_fit 一致, 60 節點逐個) ----------
sky_noise = np.std(T_obs)  # ~42 μK
print(f"\n=== 節點級 χ² (誤差 = 天空噪聲 {sky_noise:.1f} μK, 同 O2 04 一致) ===")
print(f"{'模型':<26} {'χ²':>8} {'dof':>5} {'χ²/dof':>8}")
print("-" * 52)
for name, fn in models.items():
    chi2 = 0
    for i in range(60):
        pred = fn(dist[i])
        chi2 += ((abs(T_obs[i]) - pred) / sky_noise)**2
    dof = 60 - 1
    print(f"{name:<26} {chi2:>8.1f} {dof:>5} {chi2/dof:>8.2f}")

# ---------- 6. 判斷: Fibonacci 整數級 vs φ 衰減 ----------
print(f"\n=== 判定 ===")
best = min(results, key=results.get)
print(f"層均 χ² 最佳: {best} ({results[best]:.2f})")
# F_{5-d} vs φ^(-d) 嘅關鍵分辨: d=1 層
m_F4 = F[4]*30  # 90
m_phi1 = 150/phi  # 92.7
obs1 = layer_stats[1][0]
print(f"\nd=1 層分辨點: 觀測 {obs1:.1f} μK | F₄×30 = {m_F4:.1f} | 150φ⁻¹ = {m_phi1:.1f}")
print(f"偏差: F₄×30 = {abs(obs1-m_F4):.1f} μK, 150φ⁻¹ = {abs(obs1-m_phi1):.1f} μK")

# ---------- 7. 關鍵問題: 點解 3 級截斷? ----------
print(f"\n=== 3 級截斷分析 ===")
print(f"3level 模型: d=0→F₅(150), d=1→F₄(90), d≥2→F₃(60)")
print(f"即係: 只保留 3 個級 = 3 代結構 (N_gen=3, ε³ 截斷)")
print(f"BFS 層數: 0,1,2 = 3 級 (對應 2+1 = data+inversion)")

# 儲存
with open('/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o4_fib_motivation/data/bfs_fit.txt', 'w') as f:
    f.write("# O4 01: BFS 距離層統計\n")
    f.write(f"# 平滑: 4.17° FWHM, 節點: a5_nodes.txt, BFS 源: node 0 (冷斑)\n")
    f.write(f"# d n_nodes obs_absT_mean_uK obs_absT_std_uK F5-d_x30 150phi^-d 150phi^-d2\n")
    for d in range(9):
        if d not in layer_stats:
            continue
        mean_a, std_a, n = layer_stats[d]
        m1 = F[5-d]*30 if (5-d) >= 0 else 30
        m2 = 150*phi**(-d)
        m3 = 150*phi**(-d/2)
        f.write(f"{d} {n} {mean_a:.1f} {std_a:.1f} {m1:.1f} {m2:.1f} {m3:.1f}\n")
    f.write(f"\n# 節點級 χ²/dof (誤差=sky noise {sky_noise:.1f} μK)\n")
    for name, fn in models.items():
        chi2 = sum(((abs(T_obs[i]) - fn(dist[i])) / sky_noise)**2 for i in range(60))
        f.write(f"# {name}: {chi2:.1f}/{59} = {chi2/59:.2f}\n")
print(f"\n✅ 已存: data/bfs_fit.txt")
