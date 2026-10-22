#!/usr/bin/env python3
"""
02_node57_multiscale.py — O26: 節點 57 多尺度深度分析 (fix 座標混淆 bug)
========================================================================
背景: 01 腳本 §7 出現 node 0/node 57 溫度互換跡象 (SMICA 0.5° 兩者差 200 μK,
NILC 完全唔同) — 追查發現係 `gal.l.deg[57]` 索引錯位 (gal.l 係 60 元素 array,
但 lonlat=True 嗰度用咗 `nodes[57]` RA 對應嘅 l 值, 而 a5_nodes.txt 第 58 行
RA=311.70/Dec=+20.44 轉 galactic = l=34.55/b=+52.71, 但 O3 node_temps.txt 記嘅
node57 係 l=34.55/b=52.71 — 一致! 真正問題: 01 §7 用 nodes[57]=(311.70,20.44)
而 node_temps 表頭第 58 行係 (233.71,22.21)? 睇下 a5_nodes.txt 第 58 行:
line 58 = '311.7001 20.4373' → 呢個係 RA=311.70 Dec=+20.44 ✓
node_temps.txt line 58 = '57 1 8.2073 34.55 52.71 8' → l=34.55 b=52.71 ✓
所以 gal.l.deg[57]=34.55 ✓ 冇錯位。01 §7 數字怪異原因: 0.5° 平滑地圖喺
nside=2048 下 pixel 極細, SMICA/NILC pixel 中心值可以差 200 μK (白噪), 唔係 bug。
但 NILC 0.5°=-203 vs SMICA=-5.76 太誇張 — 用更高平滑核 1° 起對比 + 檢查 cache。
"""
import healpy as hp
import numpy as np
import math
import os
from astropy.coordinates import SkyCoord
import astropy.units as u

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
CACHE = "/tmp/cache_o3"
OUT = os.path.join(BASE, "o26_node57_region", "data")

nodes = []
with open(f"{BASE}/cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic

def load_map(name, fw):
    if name == 'SMICA':
        path = f"{CACHE}/SMICA_smooth{fw}.fits"
    else:
        path = f"{CACHE}/{name}_{fw}.fits"
    return hp.read_map(path)

# 節點 0 同 57 嘅正確 galactic 座標
print("=== 座標確認 (galactic) ===")
for i in [0, 57]:
    print(f"  node {i}: RA={nodes[i,0]:.2f} Dec={nodes[i,1]:.2f} -> l={gal.l.deg[i]:.2f} b={gal.b.deg[i]:.2f}")

# 1. 檢查 0.5°/1.0° cache 嘅 pixel 對齊問題
print("\n=== 0.5°-1.0° 細尺度檢查 (pixel 對齊) ===")
for fw in [0.5, 1.0]:
    for name in ['SMICA', 'NILC', 'Commander']:
        m = load_map(name, fw)
        ns = hp.get_nside(m)
        p57 = hp.ang2pix(ns, gal.l.deg[57], gal.b.deg[57], lonlat=True)
        p0 = hp.ang2pix(ns, gal.l.deg[0], gal.b.deg[0], lonlat=True)
        print(f"  {name} {fw}°: node57={m[p57]*1e6:+8.2f}  node0={m[p0]*1e6:+8.2f}  "
              f"(nside={ns}, pixel57={p57}, pixel0={p0})")

# 2. 節點 57 附近 5° 區域嘅像素分佈 (0.5° 平滑) — 睇下係咪白噪
print("\n=== 0.5° 平滑: node 57 附近 5° 區域統計 ===")
m05 = load_map('SMICA', 0.5)
ns = hp.get_nside(m05)
v57 = np.array([math.cos(math.radians(gal.b.deg[57]))*math.cos(math.radians(gal.l.deg[57])),
                math.cos(math.radians(gal.b.deg[57]))*math.sin(math.radians(gal.l.deg[57])),
                math.sin(math.radians(gal.b.deg[57]))])
d5 = hp.query_disc(ns, v57, np.radians(5))
vals = m05[d5]*1e6
print(f"  5° 區域: n_pix={len(d5)}, mean={vals.mean():+.2f}, std={vals.std():.2f}, "
      f"min={vals.min():+.2f}, max={vals.max():+.2f}")
# 節點像素 vs 區域 median
p57 = hp.ang2pix(ns, gal.l.deg[57], gal.b.deg[57], lonlat=True)
print(f"  node57 pixel = {m05[p57]*1e6:+.2f}, 區域 median = {np.median(vals):+.2f}")

# 3. 三地圖多尺度 (1°-10°, 正規化檢查) — 完整表格
print("\n=== 三地圖多尺度完整表格 (node 57) ===")
print(f"  {'scale':>5} | {'SMICA':>8} {'NILC':>8} {'Commander':>8} | {'spread':>7}")
for fw in [1.0, 1.5, 2.0, 3.0, 4.0, 4.17, 5.0, 7.0, 10.0]:
    vals = []
    for name in ['SMICA', 'NILC', 'Commander']:
        m = load_map(name, fw)
        ns = hp.get_nside(m)
        p = hp.ang2pix(ns, gal.l.deg[57], gal.b.deg[57], lonlat=True)
        vals.append(m[p]*1e6)
    spread = max(vals) - min(vals)
    flag = "🟢" if spread < 3 else ("🟡" if spread < 8 else "🔴")
    print(f"  {fw:>5} | {vals[0]:+8.2f} {vals[1]:+8.2f} {vals[2]:+8.2f} | {spread:6.2f} {flag}")

# 4. node 57 vs node 0 溫度差 (多尺度, SMICA) — 對徑點特性
print("\n=== 對徑點特性: node0 vs node57 (SMICA) ===")
print(f"  {'scale':>5} | {'node0':>8} {'node57':>8} {'Δ(0-57)':>9}")
for fw in [1.0, 2.0, 3.0, 4.0, 4.17, 5.0, 7.0, 10.0]:
    m = load_map('SMICA', fw)
    ns = hp.get_nside(m)
    p0 = hp.ang2pix(ns, gal.l.deg[0], gal.b.deg[0], lonlat=True)
    p57 = hp.ang2pix(ns, gal.l.deg[57], gal.b.deg[57], lonlat=True)
    t0, t57 = m[p0]*1e6, m[p57]*1e6
    print(f"  {fw:>5} | {t0:+8.2f} {t57:+8.2f} {t0-t57:+9.2f}")

# 5. 對徑大尺度模式: 30° disc 嘅「對徑相關」— 直接比較
print("\n=== 對徑 30° disc 比較 (SMICA 5° 平滑) ===")
m5 = load_map('SMICA', 5.0)
ns5 = hp.get_nside(m5)
v0 = np.array([math.cos(math.radians(gal.b.deg[0]))*math.cos(math.radians(gal.l.deg[0])),
               math.cos(math.radians(gal.b.deg[0]))*math.sin(math.radians(gal.l.deg[0])),
               math.sin(math.radians(gal.b.deg[0]))])
d0 = hp.query_disc(ns5, v0, np.radians(30))
d57 = hp.query_disc(ns5, v57, np.radians(30))
t0_30, t57_30 = m5[d0]*1e6, m5[d57]*1e6
print(f"  冷斑 30°: mean={t0_30.mean():+.2f} std={t0_30.std():.2f}")
print(f"  對徑 30°: mean={t57_30.mean():+.2f} std={t57_30.std():.2f}")
print(f"  Δmean = {t0_30.mean()-t57_30.mean():+.2f} μK")
# 對徑 disc 嘅相關: 兩 disc 嘅溫度 field 有冇鏡像相關?
# 簡單做: 兩 disc mean 差 vs random

print("\n✅ 02_node57_multiscale.py 完成")
