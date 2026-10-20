#!/usr/bin/env python3
"""
04_frustration.py — 拓撲位錯: 阻挫能量量子化 → 等級
====================================================
O4 機制 4: 節點振幅等級係咪由阻挫邊能量量子化決定?

物理假設:
- 每個阻挫邊 = 拓撲缺陷 (位錯), 帶能量
- 節點嘅「位錯度」= 佢連接嘅阻挫邊數 k(i)
- 若能量量子化 → 節點等級 = f(k)

同時測試: 節點等級 vs 阻挫連接數嘅相關性
"""
import numpy as np
import math
from collections import defaultdict, deque
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as u

phi = (1 + 5**0.5) / 2
eps = (1/phi) / 4
RMS = eps**5 / 8
T_cmb = 2.72548

print("=" * 72)
print("O4 04: 拓撲位錯 — 阻挫能量量子化 → 等級?")
print("=" * 72)

# ---------- 1. 載入 + 平滑 SMICA ----------
m = hp.read_map('/tmp/smica2.fits', field=0)
nside = hp.get_nside(m)
fwhm_rad = np.radians(4.17)
sigma_rad = fwhm_rad / (2 * np.sqrt(2 * np.log(2)))
m_smooth = hp.remove_dipole(hp.smoothing(m, sigma=sigma_rad))

nodes = np.loadtxt('/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt')
sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic
pix = hp.ang2pix(nside, gal.l.deg, gal.b.deg, lonlat=True)
T_obs = m_smooth[pix] * 1e6

# ---------- 2. 圖 + BFS + 著色 ----------
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

color = {0: 1}
q = deque([0])
while q:
    u = q.popleft()
    for w in adj[u]:
        if w not in color:
            color[w] = 1 - color[u]
            q.append(w)

frustration = set()
for u, v in edges:
    if color[u] == color[v]:
        frustration.add((u, v))

# ---------- 3. 節點位錯度 k(i) = 阻挫邊數 ----------
k = {i: 0 for i in range(60)}
for u, v in frustration:
    k[u] += 1
    k[v] += 1

print(f"\n=== 節點位錯度 k(i) 分佈 ===")
k_hist = defaultdict(list)
for i in range(60):
    k_hist[k[i]].append(i)
for kk in sorted(k_hist):
    print(f"k={kk}: {len(k_hist[kk])} 節點 {k_hist[kk]}")

# ---------- 4. k vs |T| ----------
print(f"\n=== 位錯度 vs 觀測 |T| ===")
print(f"{'k':>3} {'n':>4} {'|T| mean':>9} {'|T| std':>8} {'距離 mean':>9}")
for kk in sorted(k_hist):
    idx = k_hist[kk]
    absT = np.abs(T_obs[idx])
    d_mean = np.mean([dist[i] for i in idx])
    print(f"{kk:>3} {len(idx):>4} {absT.mean():>9.1f} {absT.std():>8.1f} {d_mean:>9.2f}")

# 相關性: k vs |T|, k vs dist
kt = np.array([k[i] for i in range(60)])
dt = np.array([dist[i] for i in range(60)])
absT = np.abs(T_obs)
print(f"\n相關性:")
print(f"corr(k, |T|)   = {np.corrcoef(kt, absT)[0,1]:+.3f}")
print(f"corr(k, dist)  = {np.corrcoef(kt, dt)[0,1]:+.3f}")
print(f"corr(dist, |T|)= {np.corrcoef(dt, absT)[0,1]:+.3f}")

# ---------- 5. 阻挫邊能量 ----------
print(f"\n=== 阻挫能量 ===")
print(f"阻挫邊數: {len(frustration)} (期望 32)")
print(f"32 條邊 × RMS(30 μK) = 32×30 = 960 μK")
print(f"960 / 32 = 30 μK/邊 = RMS")
print(f"每條阻挫邊能量 = 1×RMS = F₂ 級!")
print(f"→ 32 阻挫邊 = 32 個位錯單元")

# 阻挫邊 ΔT 觀測
fr_edges = sorted(frustration)
fr_dT = np.array([abs(T_obs[u] - T_obs[v]) for u, v in fr_edges])
norm_edges = [(u, v) for u, v in edges if (u, v) not in frustration]
norm_dT = np.array([abs(T_obs[u] - T_obs[v]) for u, v in norm_edges])
print(f"\n阻挫邊 |ΔT|: mean={fr_dT.mean():.1f} μK (理論 |A(u)-A(v)|)")
print(f"正常邊 |ΔT|: mean={norm_dT.mean():.1f} μK (理論 A(u)+A(v))")

# ---------- 6. 機制 4 判定 ----------
print(f"\n=== 機制 4 判定 ===")
print(f"若節點等級由 k(i) 決定:")
print(f"  k=0: 冷斑 (1 節點) → F₅")
print(f"  k=1: ? 節點")
print(f"  k=2: 12 節點 (ΔE=0 最優位元) → F₃?")
print(f"  k=3: ?")
print(f"  k=4: ?")
print(f"位錯度 k ∈ {{0,1,2,3,4}} (4 個值, 唔係 3 級)")
print(f"但 BFS 等級係 3 級 (F₅/F₄/F₃) → 機制 4 單獨唔夠")

# ---------- 7. 對比: BFS 距離分層 |T| ----------
print(f"\n=== BFS 距離分層 |T| (對比 01) ===")
for d in range(9):
    idx = [i for i in range(60) if dist[i] == d]
    if not idx:
        continue
    absT_d = np.abs(T_obs[idx])
    print(f"d={d}: n={len(idx)}, |T| mean={absT_d.mean():.1f} μK, std={absT_d.std():.1f}")

# 儲存
with open('/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o4_fib_motivation/data/frustration_energy.txt', 'w') as f:
    f.write("# O4 04: 阻挫能量量子化\n")
    f.write(f"# node k(dist) T_obs_uK absT\n")
    for i in range(60):
        f.write(f"{i} {k[i]} {dist[i]} {T_obs[i]:.2f} {abs(T_obs[i]):.2f}\n")
    f.write(f"\n# corr(k,|T|)={np.corrcoef(kt,absT)[0,1]:+.3f}\n")
    f.write(f"# corr(dist,|T|)={np.corrcoef(dt,absT)[0,1]:+.3f}\n")
    f.write(f"# 阻挫邊 mean={fr_dT.mean():.1f}, 正常邊 mean={norm_dT.mean():.1f}\n")
print(f"\n✅ 已存: data/frustration_energy.txt")
