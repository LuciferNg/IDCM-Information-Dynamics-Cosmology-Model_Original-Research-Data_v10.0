#!/usr/bin/env python3
"""
O5 OPEN PROBLEMS STATUS — 誠實 inventory (2026-08-17)
======================================================
調律者問: O5 是否獨立仍有開放問題?
答案需要區分: ✅已關閉 / 🟡部分 / 🔴未開始
"""
import json
import os
import numpy as np
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as u

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'data')
CACHE = os.path.join(DATA, 'smooth_cache')

# 節點 (ICRS) — cmb_cold_spot 係 o5 嘅兄弟目錄
nodes = np.loadtxt(os.path.join(os.path.dirname(BASE), 'cmb_cold_spot/data/a5_nodes.txt'))
sc = SkyCoord(ra=nodes[:, 0] * u.deg, dec=nodes[:, 1] * u.deg, frame='icrs')
gal = sc.galactic
node_l, node_b = gal.l.deg, gal.b.deg

# 3.0° map
m3 = hp.read_map(os.path.join(CACHE, 'smica2_smooth3.0.fits'), field=0)
nside3 = hp.get_nside(m3)
T3 = m3 * 1e6
node_pix = hp.ang2pix(nside3, node_l, node_b, lonlat=True)
node_T = T3[node_pix]

print("=" * 66)
print("O5 開放問題現狀核查")
print("=" * 66)

# ============================================================
# 1. 節點 47 — 3.0° 第二冷 (-135.7 μK)
# ============================================================
print("\n[1] 節點 47 (3.0° 第二冷, -135.7 μK)")
print(f"    位置: l={node_l[47]:.2f}°, b={node_b[47]:.2f}°")
print(f"    3.0° T = {node_T[47]:+.1f} μK")
print(f"    |b| = {abs(node_b[47]):.1f}° {'⚠️ 接近銀河面 (<30°)' if abs(node_b[47]) < 30 else '✅ 高緯度'}")
print(f"    距離大冷斑 (node0): {np.degrees(np.arccos(np.clip(np.dot(hp.ang2vec(node_l[0],node_b[0],lonlat=True), hp.ang2vec(node_l[47],node_b[47],lonlat=True)),-1,1))):.1f}°")
# 文獻 gp10 (32,-8) 距離 node47?
d_gp10 = np.degrees(np.arccos(np.clip(np.dot(
    hp.ang2vec(32, -8, lonlat=True), hp.ang2vec(node_l[47], node_b[47], lonlat=True)), -1, 1)))
print(f"    距離 Planck gp10 (32°,-8°): {d_gp10:.1f}°")

# ============================================================
# 2. gp10 (32,-8) 最近節點
# ============================================================
print("\n[2] Planck gp10 冷斑 (32°,-8°) — 最近節點")
gp10_v = hp.ang2vec(32, -8, lonlat=True)
dists = np.degrees(np.arccos(np.clip(node_l * 0 + np.dot(
    np.stack([hp.ang2vec(l, b, lonlat=True) for l, b in zip(node_l, node_b)]),
    gp10_v), -1, 1)))
top5 = np.argsort(dists)[:5]
for i in top5:
    print(f"    node{i}: 距離 {dists[i]:.1f}° (T={node_T[i]:+.1f} μK)")

# ============================================================
# 3. 熱斑 F₆/F₇ — 最近節點距離 (已知 8-9°, 確認)
# ============================================================
print("\n[3] 熱斑 F₆/F₇ 幾何歸屬")
hotspots = {'F₆': (157.8, -70.3), 'F₇': (0.2, -37.9)}
for name, (l, b) in hotspots.items():
    hv = hp.ang2vec(l, b, lonlat=True)
    ds = np.degrees(np.arccos(np.clip(np.dot(
        np.stack([hp.ang2vec(x, y, lonlat=True) for x, y in zip(node_l, node_b)]), hv), -1, 1)))
    i = np.argmin(ds)
    print(f"    {name} ({l}°,{b}°): 最近 node{i} 距離 {ds[i]:.1f}° (T={node_T[i]:+.1f})")
    # 對徑有冇節點?
    anti_v = -hv
    ds_a = np.degrees(np.arccos(np.clip(np.dot(
        np.stack([hp.ang2vec(x, y, lonlat=True) for x, y in zip(node_l, node_b)]), anti_v), -1, 1)))
    ia = np.argmin(ds_a)
    print(f"      對徑: 最近 node{ia} 距離 {ds_a[ia]:.1f}° (T={node_T[ia]:+.1f})")

# ============================================================
# 4. mean-nearest p=0.042 弱信號 — 減冷斑後 p=0.072 來源
# ============================================================
print("\n[4] mean-nearest 弱信號成分")
print("    已確認: 主要由大冷斑驅動 (減冷斑後 p 0.042→0.072)")
print("    開放: 剩餘 p=0.072 係咪有第二結構 (node9/node47)? 需要更高 N 檢驗")

# ============================================================
# 5. 潛伏冷斑假說 — O3 堆疊
# ============================================================
print("\n[5] 潛伏冷斑假說 (低於目錄閾值嘅節點)")
print("    狀態: 🟡 未做 — 屬於 O3 節點溫度分析延伸")
# 統計: 60 節點低於 -2σ 嘅數量 (用 node_T, 唔係全 map)
sigma3 = np.std(node_T[np.abs(node_b) >= 30])
n_cold2 = (node_T[np.abs(node_b) >= 30] < -2 * sigma3).sum()
n_high = (np.abs(node_b) >= 30).sum()
print(f"    高緯度節點: {n_high} 個, 其中 < -2σ: {n_cold2} 個 (σ={sigma3:.1f} μK)")
print(f"    期望隨機: {n_high * 0.023:.1f} 個")

print("\n" + "=" * 66)
print("結論見下 (inventory 寫入 O5_OPEN_ISSUES.md)")
print("=" * 66)
