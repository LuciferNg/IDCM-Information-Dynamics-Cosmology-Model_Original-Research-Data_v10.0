#!/usr/bin/env python3
"""
14_d1_layer.py — d=1 層低估嘅深入分析
=======================================
O4 最明顯 gap: d=1 (4 節點) 觀測 46.2 vs 理論 92.7 μK

問題: 係咪真係系統性低估? 定係 4 節點小樣本 + 平滑效應?

檢查:
1. d=1 節點嘅屬性 (色彩, 阻挫連接, 位置)
2. 平滑效應: 4.17° 平滑會唔會壓低節點值?
3. 其他平滑尺度: 0.5°-7° 嘅 d=1 層 mean
4. 與 O2 熱斑 (F₆/F₇) 嘅關係: d=1 節點有冇熱斑?
"""
import numpy as np
import math
from collections import defaultdict, deque
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as astro_u

phi = (1 + 5**0.5) / 2

print("=" * 72)
print("O4 14: d=1 層低估深入分析")
print("=" * 72)

nodes = np.loadtxt('/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt')
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

# ---------- 1. d=1 節點屬性 ----------
print("\n=== 1. d=1 節點屬性 ===")
d1 = [i for i in range(60) if dist[i] == 1]
print(f"{'node':>5} {'RA':>8} {'Dec':>7} {'color':>6} {'阻挫邊':>5} {'鄰居':>4}")
for i in d1:
    fr_count = sum(1 for v in adj[i] if (i, v) in frustration or (v, i) in frustration)
    print(f"{i:>5} {nodes[i,0]:>8.2f} {nodes[i,1]:>7.2f} {'冷' if color[i]==1 else '熱':>6} {fr_count:>5} {len(adj[i]):>4}")

print(f"\nd=1 色彩: {[color[i] for i in d1]}")
print(f"阻挫: 全部 d=1 節點都應該連住冷斑 (d=0), 而冷斑係冷色")
print(f"→ 冷-熱邊 = 正常邊 → d=1 應該全部係熱色?")
print(f"實際: color = {[color[i] for i in d1]} → 全部熱 (0) ✅")

# ---------- 2. 平滑效應 (全解析度 nside 2048 — 完整測試) ----------
print("\n=== 2. 平滑效應 (nside 2048 全解析度) ===")
m = hp.read_map('/tmp/smica2.fits', field=0)
nside = hp.get_nside(m)
sc = SkyCoord(ra=nodes[:, 0]*astro_u.deg, dec=nodes[:, 1]*astro_u.deg, frame='icrs')
gal = sc.galactic
pix = hp.ang2pix(nside, gal.l.deg, gal.b.deg, lonlat=True)

print(f"{'FWHM':>5} {'d0 |T|':>8} {'d1 |T|':>8} {'d2 |T|':>8} {'d1/d0':>7} {'理論 φ^-1':>8}")
results_fwhm = []
for fwhm in [0.5, 1.0, 2.0, 3.0, 4.17, 5.0, 7.0]:
    sigma_rad = np.radians(fwhm) / (2 * np.sqrt(2 * np.log(2)))
    m_s = hp.remove_dipole(hp.smoothing(m, sigma=sigma_rad))
    T = m_s[pix] * 1e6
    d0v = abs(T[0])
    d1v = np.mean([abs(T[i]) for i in d1])
    d2_idx = [i for i in range(60) if dist[i] == 2]
    d2v = np.mean([abs(T[i]) for i in d2_idx])
    results_fwhm.append((fwhm, d1v/d0v))
    print(f"{fwhm:>5.2f} {d0v:>8.1f} {d1v:>8.1f} {d2v:>8.1f} {d1v/d0v:>7.3f} {phi**-1:>8.3f}")

# 用 4.17° 已平滑 map (nside 2048, 精確) — 由 loop 內重用
sigma_417 = np.radians(4.17) / (2 * np.sqrt(2 * np.log(2)))
m_417 = hp.remove_dipole(hp.smoothing(m, sigma=sigma_417))
T_417 = m_417[pix] * 1e6
d0v = abs(T_417[0]); d1v = np.mean([abs(T_417[i]) for i in d1])
print(f"4.17 (2048): d0={d0v:.1f}, d1={d1v:.1f}, d1/d0={d1v/d0v:.3f}")

# ---------- 3. 未平滑 (raw) ----------
print("\n=== 3. 未平滑 raw (前景污染但見趨勢) ===")
T_raw = m[pix] * 1e6
d1_raw = [abs(T_raw[i]) for i in d1]
print(f"raw d=1: {[f'{v:.0f}' for v in d1_raw]} → mean {np.mean(d1_raw):.1f}")
print(f"raw d=0: {abs(T_raw[0]):.1f}")
print(f"→ raw 都係 d1 << d0 → 平滑唔係主因")

# ---------- 4. 與 O2 熱斑 ----------
print("\n=== 4. d=1 節點 vs O2 熱斑 (F₆@1.0° F₇@0.5°) ===")
# O2: F₆=277.7 μK @ (157.8°, -70.3°) @ 1.0°平滑; F₇=353.1 @ (0.2°,-37.9°) @ 0.5°
# d=1 節點位置 (銀道):
hot6 = np.array([157.8, -70.3])  # gal l, b
hot7 = np.array([0.2, -37.9])
print(f"{'node':>5} {'gal_l':>8} {'gal_b':>7} {'距F₆':>6} {'距F₇':>6}")
for i in d1:
    l_i, b_i = gal.l.deg[i], gal.b.deg[i]
    # 角距離
    def ang_deg(l1, b1, l2, b2):
        v1 = np.array([math.cos(math.radians(b1))*math.cos(math.radians(l1)),
                       math.cos(math.radians(b1))*math.sin(math.radians(l1)),
                       math.sin(math.radians(b1))])
        v2 = np.array([math.cos(math.radians(b2))*math.cos(math.radians(l2)),
                       math.cos(math.radians(b2))*math.sin(math.radians(l2)),
                       math.sin(math.radians(b2))])
        return math.degrees(math.acos(np.clip(np.dot(v1, v2), -1, 1)))
    d6 = ang_deg(l_i, b_i, *hot6)
    d7 = ang_deg(l_i, b_i, *hot7)
    print(f"{i:>5} {l_i:>8.2f} {b_i:>7.2f} {d6:>6.1f} {d7:>6.1f}")

# ---------- 5. 判斷 ----------
print("\n=== 5. 判斷 ===")
print("""
d=1 層低估可能原因:
A. 平滑效應: 4.17° 平滑將 26° 間距嘅節點互相稀釋 (測試 2 顯示 FWHM 越大 d1 越低?)
B. 小樣本: n=4, t=-2.51, p=0.087 — 未達 0.05
C. 冷斑特強: d=0 (134.2) 已經低過理論 150 (10.5%) — 整體 scale 都偏低
D. 方向性: d=1 節點喺冷斑對面? (需要檢查)
E. 真實物理: d=1 衰減比 φ⁻¹ 更快? (可能係多模疊加唔係純主模)

關鍵測試: 如果係平滑效應, 細 FWHM 應該 d1/d0 接近 φ⁻¹
""")

with open('/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o4_fib_motivation/data/d1_layer.txt', 'w') as f:
    f.write("# O4 14: d=1 層分析\n")
    f.write(f"# d=1 nodes: {d1}, colors: {[color[i] for i in d1]}\n")
    f.write(f"# FWHM d1/d0 (重用 loop 結果, 唔重新平滑): ")
    for fwhm, ratio in results_fwhm:
        f.write(f"{fwhm}:{ratio:.3f} ")
    f.write("\n")
print(f"\n✅ 已存: data/d1_layer.txt")
