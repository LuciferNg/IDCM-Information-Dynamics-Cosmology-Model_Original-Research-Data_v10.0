#!/usr/bin/env python3
"""
26_anchor_control.py — 錨點對照測試 (60 個錨點全循環)
========================================================
核心問題: z=-3.25σ 係咪只有錨定喺冷斑 (節點 0) 先有?

測試 1: 用節點 1-59 逐個做錨點, BFS 著色, 計阻挫邊 mean
測試 2: 用 SMICA 最冷/最熱嘅節點做錨點 (唔用節點 0)
測試 3: 隨機旋轉網絡 (脫離冷斑位置)

預期: 只有節點 0 (真冷斑) 有極端低阻挫邊 mean
"""
import healpy as hp
import numpy as np
import math
from collections import defaultdict, deque
from astropy.coordinates import SkyCoord
import astropy.units as u

rng = np.random.default_rng(42)

print("=" * 66)
print("錨點對照測試 (60 錨點全循環)")
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

# ============ 建圖 ============
adj = defaultdict(set)
edges_list = []
for i in range(60):
    for j in range(i+1, 60):
        if math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) < 28.0:
            adj[i].add(j)
            adj[j].add(i)
            edges_list.append((i, j))

dT = np.array([abs(T_obs[u] - T_obs[v]) * 1e6 for u, v in edges_list])
edge_to_idx = {(u, v): i for i, (u, v) in enumerate(edges_list)}

# ============ BFS 著色函數 ============
def bfs_color(anchor):
    color = {}
    color[anchor] = 1
    q = deque([anchor])
    while q:
        u = q.popleft()
        for w in adj[u]:
            if w not in color:
                color[w] = 1 - color[u]
                q.append(w)
    return color

def frustration_mean(color):
    """阻挫邊 mean |ΔT|"""
    fr_vals = []
    for u, v in edges_list:
        if color[u] == color[v]:
            fr_vals.append(dT[edge_to_idx[(u, v)]])
    return np.mean(fr_vals), len(fr_vals)

# ============ 隨機著色基準 (5000 次) ============
rand_fr_means = []
for _ in range(5000):
    rand_color = rng.permutation([1]*30 + [0]*30)
    fr = [dT[edge_to_idx[(u, v)]] for u, v in edges_list if rand_color[u] == rand_color[v]]
    rand_fr_means.append(np.mean(fr))
rand_fr_means = np.array(rand_fr_means)
rand_mean = rand_fr_means.mean()
rand_std = rand_fr_means.std()
print(f"隨機著色基準: {rand_mean:.1f} ± {rand_std:.1f} μK")

# ============ 測試 1: 60 個錨點全循環 ============
print(f"\n=== 測試 1: 60 個錨點 BFS 著色 ===")
print(f"{'錨點':>4} {'RA':>8} {'Dec':>7} {'T(μK)':>8} {'阻挫邊':>6} {'mean(μK)':>9} {'z':>7}")
print("-" * 62)

results = []
for anchor in range(60):
    color = bfs_color(anchor)
    fr_mean, n_fr = frustration_mean(color)
    z = (fr_mean - rand_mean) / rand_std
    results.append((anchor, fr_mean, z))
    marker = " ← 冷斑!" if anchor == 0 else ""
    print(f"{anchor:>4} {nodes[anchor,0]:>8.1f} {nodes[anchor,1]:>7.1f} {T_obs[anchor]*1e6:>8.1f} {n_fr:>6} {fr_mean:>9.1f} {z:>7.2f}{marker}")

# ============ 統計分析 ============
print(f"\n=== 錨點 z 分佈 ===")
zs = np.array([r[2] for r in results])
print(f"60 錨點 z 值: min={zs.min():.2f}, max={zs.max():.2f}, mean={zs.mean():.2f}, std={zs.std():.2f}")
print(f"節點 0 (冷斑): z = {zs[0]:.2f}")
print(f"其他 59 錨點: mean z = {np.delete(zs, 0).mean():.2f} ± {np.delete(zs, 0).std():.2f}")
print(f"節點 0 排名: {np.sum(zs <= zs[0])}/{len(zs)} (第 {np.sum(zs <= zs[0])} 低)")

# 節點 0 係咪極端?
n_below = np.sum(zs <= zs[0])
p_rank = n_below / len(zs)
print(f"節點 0 z 值排名 p = {p_rank:.3f} ({n_below}/60)")
if p_rank <= 0.05:
    print(f"✅ 節點 0 顯著低於其他錨點 (排名前 5%)!")
else:
    print(f"⚠️ 節點 0 唔係唯一極端")

# ============ 測試 2: 最冷/最熱節點做錨點 ============
print(f"\n=== 測試 2: SMICA 最冷/最熱節點做錨點 ===")
order = np.argsort(T_obs)
coldest = order[:5]
hottest = order[-5:]
print("最冷 5 節點:")
for i in coldest:
    color = bfs_color(i)
    fr_mean, n_fr = frustration_mean(color)
    z = (fr_mean - rand_mean) / rand_std
    print(f"  #{i}: T={T_obs[i]*1e6:.1f} μK, 阻挫邊 mean={fr_mean:.1f}, z={z:.2f}")
print("最熱 5 節點:")
for i in hottest:
    color = bfs_color(i)
    fr_mean, n_fr = frustration_mean(color)
    z = (fr_mean - rand_mean) / rand_std
    print(f"  #{i}: T={T_obs[i]*1e6:.1f} μK, 阻挫邊 mean={fr_mean:.1f}, z={z:.2f}")

# ============ 測試 3: 隨機旋轉網絡 ============
print(f"\n=== 測試 3: 隨機旋轉網絡 (脫離冷斑位置) ===")
# 隨機旋轉 60 節點座標, 用節點 0 做錨點
rot_zs = []
for trial in range(1000):
    # 隨機旋轉矩陣
    q = rng.normal(size=3)
    q = q / np.linalg.norm(q)
    theta = rng.uniform(0, 2*np.pi)
    # Rodrigues 旋轉
    K = np.array([[0, -q[2], q[1]], [q[2], 0, -q[0]], [-q[1], q[0], 0]])
    R = np.eye(3) + np.sin(theta)*K + (1-np.cos(theta))*K@K
    
    rotated = (R @ vecs.T).T
    # 旋轉後節點 0 嘅新位置 → 溫度
    # 直接: 搵旋轉後網絡同原網絡嘅對應, 但最簡單: 用旋轉後座標查 SMICA
    rot_sc = SkyCoord(ra=np.degrees(np.arctan2(rotated[:,1], rotated[:,0]))%360*u.deg,
                      dec=np.degrees(np.arcsin(rotated[:,2]))*u.deg, frame='icrs')
    rot_gal = rot_sc.galactic
    rot_pix = hp.ang2pix(nside, rot_gal.l.deg, rot_gal.b.deg, lonlat=True)
    T_rot = m_smooth[rot_pix]
    
    # 用旋轉後溫度重算 dT, 節點 0 做錨點
    dT_rot = np.array([abs(T_rot[u] - T_rot[v]) * 1e6 for u, v in edges_list])
    color0 = bfs_color(0)
    fr_rot = [dT_rot[edge_to_idx[(u, v)]] for u, v in edges_list if color0[u] == color0[v]]
    rot_zs.append(np.mean(fr_rot))

rot_zs = np.array(rot_zs)
print(f"1000 次隨機旋轉 (錨點=節點 0): mean={rot_zs.mean():.1f} ± {rot_zs.std():.1f} μK")
print(f"原始 (未旋轉): {results[0][1]:.1f} μK")
z_rot = (results[0][1] - rot_zs.mean()) / rot_zs.std()
print(f"原始 vs 隨機旋轉: z = {z_rot:.2f}σ")
if z_rot < -2:
    print(f"✅ 只有真實冷斑位置有極端低阻挫邊!")
else:
    print(f"⚠️ 隨機旋轉都可以達到類似效果")

# 儲存
with open("data/anchor_control.txt", "w") as f:
    f.write(f"# 錨點對照測試\n")
    f.write(f"# 隨機著色基準: {rand_mean:.1f} ± {rand_std:.1f}\n")
    f.write(f"# anchor z rank: node0={zs[0]:.2f}, p={p_rank:.3f}\n")
    f.write(f"# 隨機旋轉: 原始={results[0][1]:.1f}, 旋轉={rot_zs.mean():.1f}±{rot_zs.std():.1f}, z={z_rot:.2f}\n")
    for anchor, fr_mean, z in results:
        f.write(f"{anchor} {fr_mean:.2f} {z:.2f}\n")
print(f"\n✅ 已存: data/anchor_control.txt")
