#!/usr/bin/env python3
"""
21_smica_bandpass.py — SMICA 帶通濾波雙峰驗證 (修正版)
========================================================
問題: 原始 SMICA 包含所有 ℓ 尺度, 大尺度模式 (偶極/四極) 壓過節點信號

修正: 帶通濾波保留 SYNC 模式尺度 (ℓ ≈ 44 = 2N_d)
- 低通: ℓ_max = 60 (5° 尺度 = 冷斑大小)
- 高通: ℓ_min = 20 (剔除大尺度)

IDCM 預測: 喺 ℓ≈44 尺度, 節點溫度 = ±5ε⁵/8 × T, 阻挫邊 |ΔT|≈0, 正常邊≈300μK
"""
import healpy as hp
import numpy as np
import math
from collections import defaultdict, deque
from astropy.coordinates import SkyCoord
import astropy.units as u

# ============ 1. 載入 + 帶通濾波 ============
print("=" * 66)
print("SMICA 帶通濾波雙峰驗證")
print("=" * 66)
m = hp.read_map('/tmp/smica2.fits', field=0)
nside = hp.get_nside(m)
print(f"SMICA: NSIDE={nside}, std={m.std()*1e6:.1f} μK (全部尺度)")

# 減偶極 (剔除最大污染)
m_dip = hp.remove_dipole(m)
print(f"減偶極後: std={m_dip.std()*1e6:.1f} μK")

# 帶通濾波: ℓ ∈ [20, 60] (SYNC ℓ=44 附近)
lmax = 120
alm = hp.map2alm(m_dip, lmax=lmax)
alm_band = np.zeros_like(alm)
l_arr = hp.Alm.getlm(lmax)[0]
mask_band = (l_arr >= 20) & (l_arr <= 60)
alm_band[mask_band] = alm[mask_band]
m_band = hp.alm2map(alm_band, nside=nside)
print(f"帶通 ℓ∈[20,60]: std={m_band.std()*1e6:.1f} μK")

# ============ 2. 節點溫度 ============
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

# 三種地圖節點溫度
T_raw = m[pix]
T_dip = m_dip[pix]
T_band = m_band[pix]

print(f"\n節點 0 (冷斑): l={l_deg[0]:.1f}°, b={b_deg[0]:.1f}°")
print(f"  T_raw  = {T_raw[0]*1e6:.1f} μK")
print(f"  T_dip  = {T_dip[0]*1e6:.1f} μK")
print(f"  T_band = {T_band[0]*1e6:.1f} μK")

# ============ 3. 建圖 + 著色 ============
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

# ============ 4. 三種地圖雙峰檢驗 ============
for label, T in [("原始", T_raw), ("減偶極", T_dip), ("帶通 ℓ∈[20,60]", T_band)]:
    dT_fr = np.array([abs(T[u] - T[v]) for u, v in frustration])
    dT_norm = np.array([abs(T[u] - T[v]) for u, v in normal])
    sep = (dT_norm.mean() - dT_fr.mean()) / (dT_fr.std() + 1e-12)
    print(f"\n=== {label} ===")
    print(f"阻挫邊: mean={dT_fr.mean()*1e6:.1f} μK, std={dT_fr.std()*1e6:.1f}")
    print(f"正常邊: mean={dT_norm.mean()*1e6:.1f} μK, std={dT_norm.std()*1e6:.1f}")
    print(f"分離度: {sep:.2f}σ")

# ============ 5. 冷/熱分離檢驗 (關鍵!) ============
# IDCM 預測: 冷節點 (color=1) 應該平均更冷, 熱節點 (color=0) 平均更熱
print(f"\n=== 冷/熱節點分離 (帶通地圖) ===")
T_cold = T_band[np.array([i for i in range(60) if color[i] == 1])]
T_hot = T_band[np.array([i for i in range(60) if color[i] == 0])]
print(f"冷節點 (30): mean={T_cold.mean()*1e6:.1f} μK")
print(f"熱節點 (30): mean={T_hot.mean()*1e6:.1f} μK")
print(f"冷-熱差: {(T_cold.mean()-T_hot.mean())*1e6:.1f} μK")
print(f"IDCM 預期差: -2×5ε⁵/8×T = {-2*5*(1/1.618**0.5/4)**5*2.72548*1e6:.1f} μK 附近")

# 相關性檢驗: 著色 vs 實際溫度
corr = np.corrcoef([color[i] for i in range(60)], T_band)[0, 1]
print(f"著色-溫度相關: r = {corr:.3f}")

# ============ 6. 單側檢驗: 最冷節點應該係「冷」色 ============
print(f"\n=== 最冷/最熱節點 vs 著色 ===")
order_cold = np.argsort(T_band)
print(f"最冷 5 節點:")
for i in order_cold[:5]:
    print(f"  #{i}: T={T_band[i]*1e6:.1f} μK, 色={'冷' if color[i]==1 else '熱'}")
print(f"最熱 5 節點:")
for i in order_cold[-5:]:
    print(f"  #{i}: T={T_band[i]*1e6:.1f} μK, 色={'冷' if color[i]==1 else '熱'}")

# 儲存
with open("data/smica_bandpass.txt", "w") as f:
    f.write(f"# SMICA 帶通濾波結果\n")
    f.write(f"# 帶通 ℓ∈[20,60]: 冷熱差={(T_cold.mean()-T_hot.mean())*1e6:.1f}μK, 相關 r={corr:.3f}\n")
    f.write(f"# idx color T_band_uK\n")
    for i in range(60):
        f.write(f"{i} {color[i]} {T_band[i]*1e6:.2f}\n")
print(f"\n✅ 已存: data/smica_bandpass.txt")
