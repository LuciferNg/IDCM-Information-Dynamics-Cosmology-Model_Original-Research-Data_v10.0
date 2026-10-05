#!/usr/bin/env python3
"""
22_smica_smoothed.py — SMICA 5° 平滑雙峰驗證 (最終版)
========================================================
冷斑係 5° 結構 (R8 = 4.17°) — 應該用 5° FWHM 平滑先抽節點值
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
A_node = 5 * RMS
T_cmb = 2.72548
print("=" * 66)
print("SMICA 5° 平滑雙峰驗證")
print("=" * 66)
print(f"ε = φ⁻¹/4 = {eps:.6f}")
print(f"RMS = ε⁵/8 = {RMS:.6e}")
print(f"節點振幅 A = 5ε⁵/8 = {A_node:.6e} = {A_node*T_cmb*1e6:.1f} μK")

# ============ 1. 載入 + 平滑 ============
m = hp.read_map('/tmp/smica2.fits', field=0)
nside = hp.get_nside(m)

# 平滑到冷斑尺度: 4.17° FWHM (Vielva R8)
fwhm_deg = 4.17
fwhm_rad = np.radians(fwhm_deg)
sigma_rad = fwhm_rad / (2 * np.sqrt(2 * np.log(2)))
m_smooth = hp.smoothing(m, sigma=sigma_rad, verbose=False)
print(f"平滑 {fwhm_deg}° FWHM: std={m_smooth.std()*1e6:.1f} μK")

# 減偶極 + 四極? 保留大尺度結構
m_final = hp.remove_dipole(m_smooth)
print(f"減偶極: std={m_final.std()*1e6:.1f} μK")

# ============ 2. 節點溫度 ============
nodes = []
with open("/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)

sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic
l_deg = gal.l.deg
b_deg = gal.b.deg
pix = hp.ang2pix(nside, l_deg, b_deg, lonlat=True)

T_s = m_final[pix]
print(f"\n節點 0 (冷斑): T = {T_s[0]*1e6:.1f} μK (預期 -150 μK)")
print(f"全部節點: mean={T_s.mean()*1e6:.1f}, std={T_s.std()*1e6:.1f} μK")

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

# ============ 4. 雙峰檢驗 (全部節點) ============
dT_fr = np.array([abs(T_s[u] - T_s[v]) for u, v in frustration])
dT_norm = np.array([abs(T_s[u] - T_s[v]) for u, v in normal])
sep = (dT_norm.mean() - dT_fr.mean()) / (dT_fr.std() + 1e-12)
print(f"\n=== 雙峰檢驗 (5° 平滑, 全部 60 節點) ===")
print(f"阻挫邊 ({len(frustration)}): mean={dT_fr.mean()*1e6:.1f} μK, std={dT_fr.std()*1e6:.1f}")
print(f"正常邊 ({len(normal)}): mean={dT_norm.mean()*1e6:.1f} μK, std={dT_norm.std()*1e6:.1f}")
print(f"分離度: {sep:.2f}σ")

# ============ 5. 剔除銀河盤 (|b|<20°) ============
masked = np.abs(b_deg) < 20
keep = [i for i in range(60) if not masked[i]]
keep_edges = [(u, v) for u, v in edges_list if u in keep and v in keep]
keep_fr = [e for e in keep_edges if e in frustration]
keep_norm = [e for e in keep_edges if e not in frustration]
print(f"\n剔除銀河盤: 保留 {len(keep)} 節點, 邊: 正常 {len(keep_norm)}, 阻挫 {len(keep_fr)}")
if len(keep_fr) >= 5 and len(keep_norm) >= 5:
    dT_fr2 = np.array([abs(T_s[u] - T_s[v]) for u, v in keep_fr])
    dT_norm2 = np.array([abs(T_s[u] - T_s[v]) for u, v in keep_norm])
    sep2 = (dT_norm2.mean() - dT_fr2.mean()) / (dT_fr2.std() + 1e-12)
    print(f"阻挫邊: mean={dT_fr2.mean()*1e6:.1f} μK")
    print(f"正常邊: mean={dT_norm2.mean()*1e6:.1f} μK")
    print(f"分離度: {sep2:.2f}σ")

# ============ 6. 冷熱節點分離 (關鍵) ============
T_cold = T_s[np.array([i for i in range(60) if color[i] == 1])]
T_hot = T_s[np.array([i for i in range(60) if color[i] == 0])]
print(f"\n=== 冷/熱節點分離 (5° 平滑) ===")
print(f"冷節點 (30): mean={T_cold.mean()*1e6:.1f} μK")
print(f"熱節點 (30): mean={T_hot.mean()*1e6:.1f} μK")
print(f"冷-熱差: {(T_cold.mean()-T_hot.mean())*1e6:.1f} μK")
print(f"IDCM 預期: 冷-熱 ≈ -2×A×T = {-2*A_node*T_cmb*1e6:.1f} μK")

# ============ 7. Binomial 檢驗 (最冷/最熱 vs 著色) ============
order_cold = np.argsort(T_s)
n_match = 0
n_total = 10
print(f"\n=== 極端節點 vs 著色 (Binomial 檢驗) ===")
print(f"最冷 5:")
for i in order_cold[:5]:
    match = (color[i] == 1)
    n_match += match
    print(f"  #{i}: T={T_s[i]*1e6:.1f} μK, 色={'冷' if color[i]==1 else '熱'} {'✅' if match else '❌'}")
print(f"最熱 5:")
for i in order_cold[-5:]:
    match = (color[i] == 0)
    n_match += match
    print(f"  #{i}: T={T_s[i]*1e6:.1f} μK, 色={'冷' if color[i]==1 else '熱'} {'✅' if match else '❌'}")
print(f"\n符合: {n_match}/{n_total}")
from math import comb
p_val = sum(comb(n_total, k) * 0.5**n_total for k in range(n_match, n_total+1))
print(f"Binomial p 值 (隨機假設): {p_val:.4f} ({p_val*100:.1f}%)")
if p_val < 0.05:
    print(f"✅ 統計顯著 (p<0.05)")
else:
    print(f"⚠️ 未達顯著")

# 相關性
corr = np.corrcoef([color[i] for i in range(60)], T_s)[0, 1]
print(f"\n著色-溫度相關: r = {corr:.3f}")

# 儲存
with open("/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data/smica_smoothed.txt", "w") as f:
    f.write(f"# SMICA 5° 平滑驗證\n")
    f.write(f"# 冷熱差={(T_cold.mean()-T_hot.mean())*1e6:.1f}μK, 相關 r={corr:.3f}, binomial={n_match}/10 p={p_val:.4f}\n")
    f.write(f"# idx color T_smooth_uK l_deg b_deg\n")
    for i in range(60):
        f.write(f"{i} {color[i]} {T_s[i]*1e6:.2f} {l_deg[i]:.2f} {b_deg[i]:.2f}\n")
print(f"\n✅ 已存: data/smica_smoothed.txt")
