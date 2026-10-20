#!/usr/bin/env python3
"""
01_node_temps.py — O3: 60 節點 SMICA 溫度提取 (核心)
====================================================
流程: 讀 SMICA → 4.17° FWHM 平滑 → remove_dipole → 60 節點抽值
       → BFS 距離 (重建 120 邊圖) → 著色合併 → 存 data/
"""
import healpy as hp
import numpy as np
import math
from collections import defaultdict, deque
from astropy.coordinates import SkyCoord
import astropy.units as u
import os

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
OUT = os.path.join(BASE, "o3_node_temperatures")
DATA = os.path.join(OUT, "data")
os.makedirs(DATA, exist_ok=True)

FWHM_DEG = 4.17
SMOOTH_CACHE = "/tmp/smica2_smooth417.fits"

print("=" * 66)
print("O3: 60 節點 SMICA 溫度提取")
print("=" * 66)

# ============ 1. 載入 + 平滑 ============
m = hp.read_map("/tmp/smica2.fits", field=0)
nside = hp.get_nside(m)
print(f"SMICA: NSIDE={nside}, npix={len(m)}, std={m.std()*1e6:.1f} μK")

fwhm_rad = np.radians(FWHM_DEG)
sigma_rad = fwhm_rad / (2 * np.sqrt(2 * np.log(2)))
print(f"平滑: {FWHM_DEG}° FWHM (sigma={math.degrees(sigma_rad):.4f}°)")

# 平滑係耗時操作 — 檢查 cache 避免重複
if os.path.exists(SMOOTH_CACHE):
    print(f"用 cache: {SMOOTH_CACHE}")
    m_smooth = hp.read_map(SMOOTH_CACHE, field=0)
else:
    m_smooth = hp.smoothing(m, sigma=sigma_rad, verbose=False)
    m_smooth = hp.remove_dipole(m_smooth)
    hp.write_map(SMOOTH_CACHE, m_smooth.astype(np.float32), overwrite=True)
    print(f"平滑+減偶極完成, cache 已存")
print(f"平滑後 std={m_smooth.std()*1e6:.1f} μK")

# ============ 2. 節點座標 → 銀道 → pixel ============
nodes = []
with open(os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")) as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)  # (60, 2) RA, Dec

sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic
l_deg = gal.l.deg
b_deg = gal.b.deg
pix = hp.ang2pix(nside, l_deg, b_deg, lonlat=True)
T_uK = m_smooth[pix] * 1e6

print(f"\n節點溫度 (μK): mean={T_uK.mean():.1f}, std={T_uK.std():.1f}")
print(f"範圍: [{T_uK.min():.1f}, {T_uK.max():.1f}]")
print(f"節點 0 (冷斑): {T_uK[0]:.1f} μK (預期 ~-134)")

# ============ 3. 重建圖 + BFS 距離 ============
vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                  math.cos(math.radians(d))*math.sin(math.radians(r)),
                  math.sin(math.radians(d))] for r, d in nodes])
adj = defaultdict(set)
for i in range(60):
    for j in range(i+1, 60):
        ang = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if ang < 28.0:
            adj[i].add(j)
            adj[j].add(i)

E = sum(len(adj[i]) for i in range(60)) // 2
print(f"圖: {len(adj)} 節點, {E} 邊 (期望 120)")

# BFS from node 0
hop = {0: 0}
q = deque([0])
while q:
    u = q.popleft()
    for w in adj[u]:
        if w not in hop:
            hop[w] = hop[u] + 1
            q.append(w)
hop_arr = np.array([hop[i] for i in range(60)])
from collections import Counter
dist_hist = Counter(hop_arr)
print(f"BFS 距離分佈: {dict(sorted(dist_hist.items()))} (期望 1+4+8+11+12+11+8+4+1)")
print(f"直徑: {hop_arr.max()} (對徑節點: {[i for i in range(60) if hop_arr[i]==8]})")

# ============ 4. 著色合併 ============
color = {}
with open(os.path.join(BASE, "cmb_cold_spot/data/anchored_coloring.txt")) as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        parts = line.split()
        idx = int(parts[0])
        color[idx] = int(parts[3])  # color(cold=1)
color_arr = np.array([color[i] for i in range(60)])
print(f"著色: 冷={np.sum(color_arr==1)}, 熱={np.sum(color_arr==0)}")

# 銀河遮罩
gal_mask = np.abs(b_deg) < 20
print(f"銀河盤 (|b|<20°): {gal_mask.sum()} 節點")

# ============ 5. 儲存 ============
with open(os.path.join(DATA, "node_temps.txt"), "w") as f:
    f.write("# idx color(cold=1) T_uK l_deg b_deg bfs_hop\n")
    for i in range(60):
        f.write(f"{i} {color_arr[i]} {T_uK[i]:.4f} {l_deg[i]:.2f} {b_deg[i]:.2f} {hop_arr[i]}\n")

with open(os.path.join(DATA, "bfs_distances.txt"), "w") as f:
    f.write("# bfs_hop count\n")
    for k in sorted(dist_hist):
        f.write(f"{k} {dist_hist[k]}\n")

print("\n✅ 已存: data/node_temps.txt + data/bfs_distances.txt")
