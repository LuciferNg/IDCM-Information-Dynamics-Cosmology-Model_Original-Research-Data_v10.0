#!/usr/bin/env python3
"""
25_smica_bootstrap.py — 排列檢驗 + Bootstrap (無模型依賴)
==========================================================
最直接問題: 觀測嘅 32 條阻挫邊 mean=34.5 μK vs 88 條正常邊 mean=53.1 μK
呢個差異有幾顯著?

方法 1: 排列檢驗 (permutation test)
- 隨機將 120 條邊分成 32/88 兩組, 計 mean 差
- 重複 10000 次, 睇觀測差異排喺邊

方法 2: 隨機著色對照
- 隨機 2-著色 (唔用錨定), 計 32 條「阻挫」邊 mean
- 睇錨定著色嘅阻挫邊係咪特別低

方法 3: 距離-溫度相關 (核心!)
- 120 條邊嘅 |ΔT| vs 邊長
- IDCM 預測: 邊長 26.09° 嘅邊有結構 (雙峰)
- ΛCDM: 冇
"""
import healpy as hp
import numpy as np
import math
from collections import defaultdict, deque
from astropy.coordinates import SkyCoord
import astropy.units as u

rng = np.random.default_rng(42)

print("=" * 66)
print("排列檢驗 + Bootstrap (無模型)")
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

# 錨定著色
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

dT = np.array([abs(T_obs[u] - T_obs[v]) * 1e6 for u, v in edges_list])
dT_fr = np.array([abs(T_obs[u] - T_obs[v]) * 1e6 for u, v in frustration])
dT_norm = np.array([abs(T_obs[u] - T_obs[v]) * 1e6 for u, v in edges_list if (u, v) not in frustration])

print(f"觀測: 阻挫 {len(dT_fr)} 條 mean={dT_fr.mean():.1f}, 正常 {len(dT_norm)} 條 mean={dT_norm.mean():.1f}")
obs_diff = dT_norm.mean() - dT_fr.mean()
print(f"觀測差異: {obs_diff:.1f} μK")

# ============ 方法 1: 排列檢驗 ============
print(f"\n=== 方法 1: 排列檢驗 (10000 次) ===")
n_fr = len(dT_fr)
n_norm = len(dT_norm)
count = 0
diffs = []
for _ in range(10000):
    idx = rng.permutation(len(dT))
    fr_perm = dT[idx[:n_fr]]
    norm_perm = dT[idx[n_fr:]]
    diff = norm_perm.mean() - fr_perm.mean()
    diffs.append(diff)
    if diff >= obs_diff:
        count += 1
p_perm = (count + 1) / 10001
diffs = np.array(diffs)
print(f"排列 p 值: {p_perm:.4f}")
print(f"隨機差異分佈: mean={diffs.mean():.2f}, std={diffs.std():.2f}")
print(f"觀測差異 {obs_diff:.1f} μK = {obs_diff/diffs.std():.2f}σ")
if p_perm < 0.05:
    print(f"✅ 統計顯著 (p<0.05)")
else:
    print(f"⚠️ 未達顯著")

# ============ 方法 2: 隨機著色對照 ============
print(f"\n=== 方法 2: 隨機 2-著色對照 (5000 次) ===")
# 隨機著色: 30 冷 30 熱 (固定比例), 計「同色邊」mean
rand_fr_means = []
for _ in range(5000):
    rand_color = rng.permutation([1]*30 + [0]*30)
    fr_rand = [dT[i] for i, (u, v) in enumerate(edges_list) if rand_color[u] == rand_color[v]]
    if fr_rand:
        rand_fr_means.append(np.mean(fr_rand))
rand_fr_means = np.array(rand_fr_means)
print(f"隨機著色同色邊 mean: {rand_fr_means.mean():.1f} ± {rand_fr_means.std():.1f} μK")
print(f"錨定著色阻挫邊 mean: {dT_fr.mean():.1f} μK")
z = (dT_fr.mean() - rand_fr_means.mean()) / rand_fr_means.std()
print(f"錨定 vs 隨機: z = {z:.2f}σ")
if z < -2:
    print(f"✅ 錨定阻挫邊顯著低於隨機同色邊!")
elif z > 2:
    print(f"⚠️ 錨定阻挫邊顯著高於隨機 (反預期!)")
else:
    print(f"⚠️ 同隨機無分別")

# ============ 方法 3: 距離-|ΔT| 關係 ============
print(f"\n=== 方法 3: 邊長 vs |ΔT| (核心) ===")
# 所有 1770 對嘅距離 vs |ΔT|
all_dT = []
all_d = []
for i in range(60):
    for j in range(i+1, 60):
        d_ang = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        all_d.append(d_ang)
        all_dT.append(abs(T_obs[i] - T_obs[j]) * 1e6)
all_d = np.array(all_d)
all_dT = np.array(all_dT)

# 邊 (26.09°) vs 非邊
edge_mask = all_d < 28.0
print(f"邊 (26.09°): mean |ΔT| = {all_dT[edge_mask].mean():.1f} μK (n={edge_mask.sum()})")
print(f"非邊: mean |ΔT| = {all_dT[~edge_mask].mean():.1f} μK (n={(~edge_mask).sum()})")
z2 = (all_dT[edge_mask].mean() - all_dT[~edge_mask].mean()) / (all_dT[~edge_mask].std()/np.sqrt(edge_mask.sum()))
print(f"z = {z2:.2f}σ")

# 距離 bins 平均
print(f"\n距離 bins:")
bins = [0, 28, 35, 45, 55, 65, 75, 90, 110, 130, 180]
for i in range(len(bins)-1):
    mask = (all_d >= bins[i]) & (all_d < bins[i+1])
    if mask.sum() > 0:
        print(f"  {bins[i]:3d}-{bins[i+1]:3d}°: mean={all_dT[mask].mean():6.1f} μK, n={mask.sum()}")

# 儲存
with open("data/smica_permutation.txt", "w") as f:
    f.write(f"# 排列檢驗: p={p_perm:.4f}, obs_diff={obs_diff:.1f}uK, sigma={obs_diff/diffs.std():.2f}\n")
    f.write(f"# 隨機著色: z={z:.2f}, 錨定fr={dT_fr.mean():.1f}, 隨機={rand_fr_means.mean():.1f}±{rand_fr_means.std():.1f}\n")
    f.write(f"# 邊vs非邊: z={z2:.2f}, 邊={all_dT[edge_mask].mean():.1f}, 非邊={all_dT[~edge_mask].mean():.1f}\n")
print(f"\n✅ 已存: data/smica_permutation.txt")
