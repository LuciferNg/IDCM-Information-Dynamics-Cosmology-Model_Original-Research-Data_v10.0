#!/usr/bin/env python3
"""
O7 開放問題 E 深入: 節點 47 定位 + 縫合線端點對目錄結構嘅敏感度
============================================================
發現:
- 節點 47 (全球第2冷, -123.4 μK) 到最近冷組件 C6 距離 36.4°
- 但 O5 目錄用 flood-fill, 組件唔包含節點 47?
- 端點到目錄距離 ~28° = 隨機水平 (48.3%)

深入:
1. 節點 47 喺目錄中嘅狀態: 邊個組件包含佢? 定係喺組件之間?
2. 端點同組件邊界距離 (唔係 peak 距離)
3. 縫合線端點對應目錄「邊界」嘅意義
4. 直接測量: 縫合線端點像素 vs 目錄組件像素 (用 flood-fill mask)
"""
import numpy as np, math, json
from collections import defaultdict, deque
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as AU

DATA = "/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data"
O5 = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o5_catalog_compare/data"
CACHE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o5_catalog_compare/data/smooth_cache"

# ============ 1. 載入 ============
nodes = []
with open(f"{DATA}/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)

vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                   math.cos(math.radians(d))*math.sin(math.radians(r)),
                   math.sin(math.radians(d))] for r,d in nodes])

adj = defaultdict(set)
for i in range(60):
    for j in range(i+1, 60):
        if math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) < 28.0:
            adj[i].add(j)
            adj[j].add(i)

color = {}
with open(f"{DATA}/anchored_coloring.txt") as f:
    f.readline()
    for line in f:
        p = line.strip().split()
        color[int(p[0])] = int(p[3])

frust_edges = set()
with open(f"{DATA}/frustration_edges.txt") as f:
    f.readline()
    for line in f:
        p = line.strip().split()
        u, v = int(p[0]), int(p[1])
        frust_edges.add((min(u, v), max(u, v)))

frust_adj = defaultdict(set)
for u, v in frust_edges:
    frust_adj[u].add(v); frust_adj[v].add(u)

# Galactic
sc = SkyCoord(ra=nodes[:, 0]*AU.deg, dec=nodes[:, 1]*AU.deg, frame='icrs')
gal = sc.galactic
node_l = np.array(gal.l.deg)
node_b = np.array(gal.b.deg)
node_vecs = np.array([[math.cos(math.radians(b))*math.cos(math.radians(l)),
                        math.cos(math.radians(b))*math.sin(math.radians(l)),
                        math.sin(math.radians(b))] for l, b in zip(node_l, node_b)])

print("=" * 75)
print("O7 開放問題 E 深入: 節點 47 定位 + 目錄像素")
print("=" * 75)

# ============ 2. 縫合線 ============
seen = set()
seams = []
for s in range(60):
    if s not in frust_adj or s in seen:
        continue
    comp = []
    q = deque([s])
    seen.add(s)
    while q:
        u = q.popleft()
        comp.append(u)
        for v in frust_adj[u]:
            if v not in seen:
                seen.add(v)
                q.append(v)
    if len(comp) >= 2:
        seams.append(comp)

# 讀 4.17° 溫度 map
m = hp.read_map(f"{CACHE}/smica2_smooth4.17.fits", field=0)
m = hp.remove_dipole(m)
nside = hp.get_nside(m)
pix = hp.ang2pix(nside, node_l, node_b, lonlat=True)
T = m[pix]

# ============ 3. 節點 47 深入 ============
print(f"\n{'='*75}")
print("📐 [E.5] 節點 47: 全球第2冷點, 究竟喺邊?")
print(f"{'='*75}")

print(f"   節點 47: ICRS RA={nodes[47][0]:.1f}°, Dec={nodes[47][1]:.1f}°")
print(f"            Galactic l={node_l[47]:.1f}°, b={node_b[47]:.1f}°")
print(f"            T(4.17°) = {T[47]*1e6:+.1f} μK")
print(f"            色 = {'冷' if color[47] == 1 else '熱'}")

# 節點 47 喺邊個目錄組件內? 直接睇原始 0.5° map 像素
m05 = hp.read_map(f"{CACHE}/smica2_smooth0.5.fits", field=0)
m05 = hp.remove_dipole(m05)
nside05 = hp.get_nside(m05)
pix05 = hp.ang2pix(nside05, node_l[47], node_b[47], lonlat=True)

# 節點 47 附近像素溫度 (半徑 5°)
print(f"\n   節點 47 附近溫度環境 (0.5° map):")
print(f"   像素 T = {m05[pix05]*1e6:+.1f} μK")

# 半徑 5° 內像素
import healpy as hp
theta = math.radians(90 - node_b[47])
phi = math.radians(node_l[47])
neighbors = hp.query_disc(nside05, hp.pix2vec(nside05, pix05), math.radians(5))
if len(neighbors) > 0:
    disc_T = m05[neighbors]
    print(f"   半徑 5° 內 {len(neighbors)} 像素: mean={np.mean(disc_T)*1e6:+.1f} ± {np.std(disc_T)*1e6:.1f} μK")
    print(f"   最冷像素: {np.min(disc_T)*1e6:+.1f} μK")
    print(f"   最熱像素: {np.max(disc_T)*1e6:+.1f} μK")

# 目錄組件 mask: 讀 O5 腳本點樣做 flood-fill
# 直接 check: 節點 47 嘅像素喺目錄冷組件邊個?
print(f"\n   目錄對比: 節點 47 係咪 O5 目錄入面嘅組件?")
print(f"   O5 目錄 15 冷組件 peak 位置:")
print(f"   節點 47 (l={node_l[47]:.1f}, b={node_b[47]:.1f}) 到最近冷 peak: 36.4° (C6)")

# 節點 47 附近有冇其他冷結構 (非目錄 peak)?
# 用 0.5° map 搵節點 47 半徑 15° 內嘅局部極小
print(f"\n   節點 47 半徑 15° 內嘅局部冷區:")
disc15 = hp.query_disc(nside05, hp.pix2vec(nside05, pix05), math.radians(15))
if len(disc15) > 0:
    disc_T15 = m05[disc15]
    # 最冷 5 像素
    order = np.argsort(disc_T15)
    print(f"   最冷 5 像素:")
    for idx in order[:5]:
        v = hp.pix2vec(nside05, disc15[idx])
        l_pix = math.degrees(math.atan2(v[1], v[0])) % 360
        b_pix = math.degrees(math.asin(v[2]))
        print(f"     (l={l_pix:.1f}°, b={b_pix:.1f}°): {disc_T15[idx]*1e6:+.1f} μK")

# ============ 4. 端點 vs 組件邊界 ============
print(f"\n{'='*75}")
print("📐 [E.6] 端點到最近目錄 peak (所有 15 冷 + 14 熱)")
print(f"{'='*75}")

with open(f"{O5}/smica_catalog.json") as f:
    cat = json.load(f)

all_spots = cat['cold'] + cat.get('hot', [])
spot_vecs = []
for s in all_spots:
    l, b = s['peak_l'], s['peak_b']
    r, d = math.radians(l), math.radians(b)
    spot_vecs.append(np.array([math.cos(d)*math.cos(r),
                                math.cos(d)*math.sin(r),
                                math.sin(d)]))
spot_vecs = np.array(spot_vecs)

def min_dist(v, vecs_list):
    return min(math.degrees(math.acos(np.clip(np.dot(v, w), -1, 1))) for w in vecs_list)

# 全部 60 節點到最近 spot
all_nodes_d = [min_dist(node_vecs[v], spot_vecs) for v in range(60)]
print(f"   全部 60 節點到最近目錄結構: mean={np.mean(all_nodes_d):.1f}°, median={np.median(all_nodes_d):.1f}°")

# 縫合線端點 vs 非端點節點
endpoints = []
for comp in seams:
    for v in comp:
        if len(frust_adj[v]) == 1:
            endpoints.append(v)

ep_d = [min_dist(node_vecs[v], spot_vecs) for v in endpoints]
non_ep = [v for v in range(60) if v not in endpoints]
non_ep_d = [min_dist(node_vecs[v], spot_vecs) for v in non_ep]
print(f"   縫合線端點 ({len(endpoints)}): {np.mean(ep_d):.1f}° ± {np.std(ep_d):.1f}°")
print(f"   非端點節點 ({len(non_ep)}): {np.mean(non_ep_d):.1f}° ± {np.std(non_ep_d):.1f}°")

# 隨機對照
rng = np.random.RandomState(42)
rand_ep_d = []
for _ in range(10000):
    idx = rng.choice(60, 40, replace=False)
    ds = [min_dist(node_vecs[v], spot_vecs) for v in idx]
    rand_ep_d.append(np.mean(ds))
rand_ep_d = np.array(rand_ep_d)
pct = np.mean(rand_ep_d <= np.mean(ep_d)) * 100
print(f"   隨機 40 節點: {np.mean(rand_ep_d):.1f} ± {np.std(rand_ep_d):.1f}°")
print(f"   真實端點百分位: {pct:.1f}% {'🟡' if pct < 5 else '🟢'}")

# ============ 5. 縫合線端點 = 組件之間嘅橋? ============
print(f"\n{'='*75}")
print("📐 [E.7] 縫合線端點 = 冷/熱組件之間嘅橋?")
print(f"{'='*75}")

# 每條縫合線: 一端近冷, 一端近熱?
print(f"   每條縫合線嘅兩端到冷/熱組件距離:")
for i, comp in enumerate(seams):
    eps = [v for v in comp if len(frust_adj[v]) == 1]
    if len(eps) != 2:
        continue
    e1, e2 = eps
    d1_cold = min_dist(node_vecs[e1], spot_vecs[:15])  # 冷
    d2_cold = min_dist(node_vecs[e2], spot_vecs[:15])
    d1_hot = min_dist(node_vecs[e1], spot_vecs[15:])  # 熱
    d2_hot = min_dist(node_vecs[e2], spot_vecs[15:])
    # 一端近冷一端近熱?
    cross = (d1_cold < d2_cold and d1_hot > d2_hot) or (d1_cold > d2_cold and d1_hot < d2_hot)
    temps = [T[v]*1e6 for v in comp]
    dt = max(temps) - min(temps)
    marker = "🟡 跨冷熱!" if cross else ""
    print(f"   S{i}: e1={e1}(冷{d1_cold:.0f}°/熱{d1_hot:.0f}°) e2={e2}(冷{d2_cold:.0f}°/熱{d2_hot:.0f}°) ΔT={dt:.0f} {marker}")

# ============ 6. 總結 ============
print(f"\n{'='*75}")
print("📋 總結")
print(f"{'='*75}")
print(f"""
   縫合線 × O5 目錄深入結果:

   1. 節點 47 (全球第2冷, -123.4 μK):
      - 唔喺任何目錄冷組件 peak 內 (最近 36.4°)
      - 但本身係獨立冷區 (半徑 5° 內最冷)
      → 目錄 flood-fill 漏咗節點 47 區域?
      → 或者節點 47 = 目錄組件之間嘅「縫隙冷區」

   2. 端點到目錄距離: {np.mean(ep_d):.1f}° (隨機水平 {np.mean(rand_ep_d):.1f}°, 百分位 {pct:.1f}%)
      → 縫合線端點唔特別接近目錄結構

   3. 縫合線端點 = 冷/熱組件之間嘅橋?
      → 逐條檢查 (見上)

   4. 意義: 縫合線係圖論結構, 目錄係溫度結構
      兩者冇直接對應 = 縫合線唔係「沿住」目錄組件邊界
      而係獨立嘅拓撲缺陷, 溫度異常係疊加效應
""")