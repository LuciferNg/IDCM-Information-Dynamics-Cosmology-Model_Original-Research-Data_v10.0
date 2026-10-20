#!/usr/bin/env python3
"""
12_midlayer_rotation_test.py — 中間層銀河盤偏向嘅隨機旋轉對照
==============================================================
問題: ΔE=0 節點 8/12 喺銀河盤 (紅燈 1)
假設: 呢個係「ΔE=0 必須喺中間層 d3-d5」+「中間層本身偏銀河盤」嘅間接後果

驗證:
1. ΔE=0 = k=2 節點 = 100% 喺 d3-d5 (圖論必然)
2. 中間層銀河盤比例 52.9% 係咪顯著偏離隨機旋轉?
3. ΔE=0 銀河盤數 vs 中間層條件期望 (binomial)
"""
import numpy as np
import math
from collections import defaultdict, deque
from astropy.coordinates import SkyCoord
import astropy.units as u

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"

nodes = []
with open(f"{BASE}/cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
vecs0 = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                   math.cos(math.radians(d))*math.sin(math.radians(r)),
                   math.sin(math.radians(d))] for r, d in nodes])

# 真實銀河 b (astropy)
sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
b_real = sc.galactic.b.deg
gal0 = (np.abs(b_real) < 20).astype(int)
print(f"真實銀河 b: |b|<20 = {gal0.sum()}/60")

# BFS hop
def build_graph(vecs):
    adj = defaultdict(set)
    for i in range(60):
        for j in range(i+1, 60):
            if math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) < 28.0:
                adj[i].add(j); adj[j].add(i)
    return adj
adj0 = build_graph(vecs0)
hop = {0: 0}; q = deque([0])
while q:
    uu = q.popleft()
    for w in adj0[uu]:
        if w not in hop:
            hop[w] = hop[uu] + 1; q.append(w)
mid0 = np.array([1 if hop[i] in (3, 4, 5) else 0 for i in range(60)])

obs_mid_gal = (mid0 & gal0).sum()
n_mid = mid0.sum()
print(f"中間層 (d3-d5, {n_mid} 節點) 銀河盤: {obs_mid_gal} = {obs_mid_gal/n_mid*100:.1f}%")

# 隨機旋轉對照
def rodrigues(v, axis, angle):
    k = axis / np.linalg.norm(axis)
    return v*math.cos(angle) + np.cross(k, v)*math.sin(angle) + k*np.dot(k, v)*(1-math.cos(angle))

rng = np.random.default_rng(42)
n_trial = 2000
mid_gal_arr = np.zeros(n_trial)
all_gal_arr = np.zeros(n_trial)
for k in range(n_trial):
    axis = rng.standard_normal(3); axis /= np.linalg.norm(axis)
    angle = rng.uniform(0, 2*math.pi)
    vecs_r = np.array([rodrigues(v, axis, angle) for v in vecs0])
    dec_r = np.degrees(np.arcsin(vecs_r[:, 2]))
    ra_r = np.degrees(np.arctan2(vecs_r[:, 1], vecs_r[:, 0])) % 360
    sc_r = SkyCoord(ra=ra_r*u.deg, dec=dec_r*u.deg, frame='icrs')
    b_r = sc_r.galactic.b.deg
    gal_r = (np.abs(b_r) < 20).astype(int)
    mid_gal_arr[k] = (mid0 & gal_r).sum()
    all_gal_arr[k] = gal_r.sum()

print(f"\n=== 隨機旋轉對照 (n={n_trial}) ===")
print(f"中間層銀河盤: 觀測 {obs_mid_gal}, 隨機 mean={mid_gal_arr.mean():.2f}±{mid_gal_arr.std():.2f}")
z_mid = (obs_mid_gal - mid_gal_arr.mean()) / mid_gal_arr.std()
p_mid = (mid_gal_arr >= obs_mid_gal).mean()
print(f"  z = {z_mid:.2f}σ, p = {p_mid:.4f}  ({'🟡 邊緣' if p_mid < 0.1 else '✅ 正常'})")
print(f"全部節點銀河盤: 觀測 {gal0.sum()}, 隨機 mean={all_gal_arr.mean():.2f}±{all_gal_arr.std():.2f}")
z_all = (gal0.sum() - all_gal_arr.mean()) / all_gal_arr.std()
p_all = (all_gal_arr >= gal0.sum()).mean()
print(f"  z = {z_all:.2f}σ, p = {p_all:.4f}")

print(f"\n=== ΔE=0 條件機率 ===")
ZERO_E = {10, 12, 19, 22, 23, 25, 28, 32, 37, 40, 45, 46}
ze = np.array([i in ZERO_E for i in range(60)])
ze_mid = ze & mid0.astype(bool)
print(f"ΔE=0 喺中間層: {ze_mid.sum()}/12 (100%)")
# 條件期望: 12 × 中間層銀河盤比例
from scipy import stats
exp = 12 * obs_mid_gal / n_mid
obs_ze_gal = (ze & gal0.astype(bool)).sum()
p_cond = stats.binomtest(obs_ze_gal, 12, obs_mid_gal/n_mid).pvalue
print(f"期望 (12 × {obs_mid_gal}/{n_mid}): {exp:.2f}, 觀測: {obs_ze_gal}")
print(f"binomial p (vs 中間層): {p_cond:.4f}  ({'✅ 巧合' if p_cond > 0.05 else '🚨 仍顯著'})")

print(f"\n=== 結論 ===")
if p_cond > 0.05 and p_mid > 0.05:
    print("紅燈 1 完全破解: 8/12 銀河盤 = 中間層效應, 全部喺隨機期望內")
elif p_cond > 0.05:
    print("紅燈 1 破解: ΔE=0 本身正常, 但中間層銀河盤有輕微偏向")
else:
    print("紅燈 1 未破解: ΔE=0 超出中間層期望")
