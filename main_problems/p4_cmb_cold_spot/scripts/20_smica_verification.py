#!/usr/bin/env python3
"""
20_smica_verification.py — Planck SMICA 真數據驗證雙峰預測
============================================================
IDCM 預測: 120 條邊 (88 正常 + 32 阻挫)
- 正常邊 (冷-熱): |ΔT| 大 (~300 μK)
- 阻挫邊 (同色): |ΔT| 小 (~0)
→ 雙峰分佈, 分離度 17.3σ (SNR=5)

驗證: 讀取 SMICA 地圖喺 60 節點嘅溫度, 計算邊 |ΔT|
"""
import healpy as hp
import numpy as np
import math
from collections import defaultdict, deque

# ============ 1. 載入 SMICA ============
print("=" * 66)
print("Planck SMICA 雙峰驗證")
print("=" * 66)
m = hp.read_map('/tmp/smica2.fits', field=0)
nside = hp.get_nside(m)
print(f"SMICA: NSIDE={nside}, npix={len(m)}, std={m.std()*1e6:.1f} μK")

# ============ 2. 載入 60 節點 (RA, Dec) ============
nodes = []
with open("/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
print(f"節點: {len(nodes)} 個 (RA, Dec)")

# ============ 3. RA/Dec → 銀道 → HEALPix pixel ============
# SMICA 係銀道座標, 需要轉換
# RA/Dec (ICRS) → Galactic 用 astropy
from astropy.coordinates import SkyCoord
import astropy.units as u

ra_deg = nodes[:, 0]
dec_deg = nodes[:, 1]
sc = SkyCoord(ra=ra_deg*u.deg, dec=dec_deg*u.deg, frame='icrs')
gal = sc.galactic
l_deg = gal.l.deg
b_deg = gal.b.deg
print(f"\n銀道座標範圍: l=[{l_deg.min():.1f},{l_deg.max():.1f}], b=[{b_deg.min():.1f},{b_deg.max():.1f}]")

# HEALPix pixel (nested 定 ring? SMICA 用 ring)
pix = hp.ang2pix(nside, l_deg, b_deg, lonlat=True)
T_nodes = m[pix]
print(f"節點溫度 (μK): mean={T_nodes.mean()*1e6:.1f}, std={T_nodes.std()*1e6:.1f}")
print(f"範圍: [{T_nodes.min()*1e6:.1f}, {T_nodes.max()*1e6:.1f}] μK")

# 大冷斑檢查 (應該喺節點 0)
print(f"\n節點 0 (冷斑本體): RA={ra_deg[0]:.1f}, Dec={dec_deg[0]:.1f}")
print(f"  → l={l_deg[0]:.1f}°, b={b_deg[0]:.1f}°")
print(f"  → T = {T_nodes[0]*1e6:.1f} μK")
print(f"  → 預期 ~-150 μK (冷)")

# ============ 4. 銀河遮罩檢查 ============
# |b| < 20° 係銀河盤, 前景污染嚴重
masked = np.abs(b_deg) < 20
print(f"\n銀河遮罩: {masked.sum()}/{len(nodes)} 節點喺 |b|<20° (需剔除)")
unmasked = ~masked
print(f"可用節點: {unmasked.sum()}")

# ============ 5. 建圖 (120 邊) ============
THRESHOLD = 28.0
vecs = np.array([np.array([math.cos(math.radians(d))*math.cos(math.radians(r)),
                           math.cos(math.radians(d))*math.sin(math.radians(r)),
                           math.sin(math.radians(d))]) for r, d in nodes])
adj = defaultdict(set)
edges_list = []
for i in range(60):
    for j in range(i+1, 60):
        if math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) < THRESHOLD:
            adj[i].add(j)
            adj[j].add(i)
            edges_list.append((i, j))
print(f"邊: {len(edges_list)} (期望 120)")

# ============ 6. 錨定著色 ============
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
normal = [(u, v) for u, v in edges_list if (u, v) not in frustration]
print(f"阻挫邊: {len(frustration)}, 正常邊: {len(normal)}")

# ============ 7. 雙峰檢驗 (全部 60 節點) ============
dT_all = np.array([abs(T_nodes[u] - T_nodes[v]) for u, v in edges_list])
dT_fr = np.array([abs(T_nodes[u] - T_nodes[v]) for u, v in frustration])
dT_norm = np.array([abs(T_nodes[u] - T_nodes[v]) for u, v in normal])

print(f"\n=== 雙峰檢驗 (全部節點, 含銀河盤) ===")
print(f"阻挫邊 |ΔT|: mean = {dT_fr.mean()*1e6:.1f} μK, std = {dT_fr.std()*1e6:.1f}")
print(f"正常邊 |ΔT|: mean = {dT_norm.mean()*1e6:.1f} μK, std = {dT_norm.std()*1e6:.1f}")
sep = (dT_norm.mean() - dT_fr.mean()) / (dT_fr.std() + 1e-12)
print(f"分離度: {sep:.2f}σ")
print(f"IDCM 預期: 17.3σ (SNR=5), ΛCDM: 0.38σ")
if sep > 3:
    print(f"✅ 雙峰存在!")
else:
    print(f"⚠️ 雙峰唔明顯")

# ============ 8. 剔除銀河盤後重驗 ============
if unmasked.sum() >= 20:
    # 只保留兩端都喺 |b|>=20° 嘅邊
    keep_edges = [(u, v) for u, v in edges_list if unmasked[u] and unmasked[v]]
    keep_fr = [e for e in keep_edges if e in frustration]
    keep_norm = [e for e in keep_edges if e not in frustration]
    if len(keep_fr) >= 5 and len(keep_norm) >= 5:
        dT_fr2 = np.array([abs(T_nodes[u] - T_nodes[v]) for u, v in keep_fr])
        dT_norm2 = np.array([abs(T_nodes[u] - T_nodes[v]) for u, v in keep_norm])
        print(f"\n=== 雙峰檢驗 (剔除銀河盤 |b|<20°) ===")
        print(f"邊: 正常 {len(keep_norm)}, 阻挫 {len(keep_fr)}")
        print(f"阻挫邊 |ΔT|: mean = {dT_fr2.mean()*1e6:.1f} μK, std = {dT_fr2.std()*1e6:.1f}")
        print(f"正常邊 |ΔT|: mean = {dT_norm2.mean()*1e6:.1f} μK, std = {dT_norm2.std()*1e6:.1f}")
        sep2 = (dT_norm2.mean() - dT_fr2.mean()) / (dT_fr2.std() + 1e-12)
        print(f"分離度: {sep2:.2f}σ")
        if sep2 > 3:
            print(f"✅ 雙峰存在!")
        else:
            print(f"⚠️ 雙峰唔明顯")
    else:
        print(f"\n剔除後樣本太少 (fr={len(keep_fr)}, norm={len(keep_norm)}) — 無法檢驗")

# ============ 9. 對照組: 隨機節點 (ΛCDM 預期) ============
rng = np.random.default_rng(42)
random_ra = rng.uniform(0, 360, 60)
random_dec = rng.uniform(-90, 90, 60)
sc_r = SkyCoord(ra=random_ra*u.deg, dec=random_dec*u.deg, frame='icrs')
gal_r = sc_r.galactic
pix_r = hp.ang2pix(nside, gal_r.l.deg, gal_r.b.deg, lonlat=True)
T_rand = m[pix_r]

# 隨機 60 節點同樣結構 (最近鄰圖)
vecs_r = np.array([np.array([math.cos(math.radians(d))*math.cos(math.radians(r)),
                             math.cos(math.radians(d))*math.sin(math.radians(r)),
                             math.sin(math.radians(d))]) for r, d in zip(random_ra, random_dec)])
adj_r = defaultdict(set)
edges_r = []
for i in range(60):
    for j in range(i+1, 60):
        if math.degrees(math.acos(np.clip(np.dot(vecs_r[i], vecs_r[j]), -1, 1))) < 28.0:
            adj_r[i].add(j)
            adj_r[j].add(i)
            edges_r.append((i, j))
dT_rand_edges = np.array([abs(T_rand[u] - T_rand[v]) for u, v in edges_r]) if edges_r else np.array([0])

print(f"\n=== 對照: 隨機 60 節點 (ΛCDM 預期) ===")
print(f"隨機邊數: {len(edges_r)}")
if len(dT_rand_edges) > 5:
    print(f"隨機邊 |ΔT|: mean = {dT_rand_edges.mean()*1e6:.1f} μK, std = {dT_rand_edges.std()*1e6:.1f}")

# 儲存
with open("/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data/smica_verification.txt", "w") as f:
    f.write(f"# SMICA 雙峰驗證\n")
    f.write(f"# 全部邊: fr_mean={dT_fr.mean()*1e6:.1f}uK, norm_mean={dT_norm.mean()*1e6:.1f}uK, sep={sep:.2f}sigma\n")
    f.write(f"# 剔除銀河: fr_mean={dT_fr2.mean()*1e6:.1f}uK, norm_mean={dT_norm2.mean()*1e6:.1f}uK, sep={sep2:.2f}sigma\n")
    f.write(f"# edge u v type dT_uK\n")
    for i, (u, v) in enumerate(edges_list):
        ft = 'F' if (u, v) in frustration else 'N'
        f.write(f"{u} {v} {ft} {abs(T_nodes[u]-T_nodes[v])*1e6:.2f}\n")
print(f"\n✅ 結果已存: data/smica_verification.txt")
