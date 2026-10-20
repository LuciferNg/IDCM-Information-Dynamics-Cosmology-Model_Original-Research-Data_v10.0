#!/usr/bin/env python3
"""
02_neighbors.py — O6: 節點 57 嘅 4 個最近鄰 (圖鄰居) 溫度
=========================================================
1. 用邊長閾值 (< 28°) 搵節點 57 嘅圖鄰居
2. 鄰居溫度: 著色交替檢查 (hop=8 冷 → 鄰居 hop=7 熱?)
3. 對徑點 vs 冷斑嘅鄰居結構對比
4. 鄰居溫度符號: 節點 57 (+8.21) 係咪孤立? 定係喺熱區?
"""
import healpy as hp
import numpy as np
import math
import os
from collections import defaultdict, deque
from astropy.coordinates import SkyCoord
import astropy.units as u

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
NODE_FILE = os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")
CACHE = "/tmp/cache_o3"
OUT = os.path.join(BASE, "o6_antipode_check/data")

# ============ 載入節點 + 座標 ============
nodes = []
with open(NODE_FILE) as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)

sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic
l_deg = gal.l.deg
b_deg = gal.b.deg

vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                  math.cos(math.radians(d))*math.sin(math.radians(r)),
                  math.sin(math.radians(d))] for r, d in nodes])

# ============ 建圖 + BFS ============
adj = defaultdict(set)
edges_list = []
for i in range(60):
    for j in range(i+1, 60):
        ang = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if ang < 28.0:
            adj[i].add(j)
            adj[j].add(i)
            edges_list.append((i, j))

# BFS 距離 (anchor 0)
hop = {0: 0}
q = deque([0])
while q:
    u = q.popleft()
    for w in adj[u]:
        if w not in hop:
            hop[w] = hop[u] + 1
            q.append(w)

# 著色 (anchor 0 冷色)
color = {}
color[0] = 1
q = deque([0])
while q:
    u = q.popleft()
    for w in adj[u]:
        if w not in color:
            color[w] = 1 - color[u]
            q.append(w)

# ============ 節點 57 鄰居 ============
print("=" * 66)
print("O6: 節點 57 對徑點鄰居分析")
print("=" * 66)
print(f"節點 57: hop={hop[57]}, 色={'冷' if color[57]==1 else '熱'}, "
      f"Gal=({l_deg[57]:.2f},{b_deg[57]:.2f})")

nbrs = sorted(adj[57])
print(f"\n=== 節點 57 圖鄰居 (degree={len(nbrs)}) ===")
for w in nbrs:
    print(f"  #{w}: hop={hop[w]}, 色={'冷' if color[w]==1 else '熱'}, "
          f"角距={math.degrees(math.acos(np.clip(np.dot(vecs[57], vecs[w]),-1,1))):.2f}°")

# ============ 節點 0 鄰居 (對比) ============
nbrs0 = sorted(adj[0])
print(f"\n=== 節點 0 圖鄰居 (degree={len(nbrs0)}) ===")
for w in nbrs0:
    print(f"  #{w}: hop={hop[w]}, 色={'冷' if color[w]==1 else '熱'}, "
          f"角距={math.degrees(math.acos(np.clip(np.dot(vecs[0], vecs[w]),-1,1))):.2f}°")

# ============ 多尺度鄰居溫度 ============
print("\n=== 節點 57 + 鄰居: 多尺度溫度 (SMICA cache) ===")
scales = [0.5, 1.0, 2.0, 3.0, 4.17, 5.0, 7.0, 10.0]
# 用 4.17 為主
m417 = hp.read_map(os.path.join(CACHE, "SMICA_4.17.fits"), field=0)
nside = hp.get_nside(m417)
pix_all = hp.ang2pix(nside, l_deg, b_deg, lonlat=True)
T417 = m417[pix_all] * 1e6

print(f"\n--- SMICA 4.17° ---")
idx_list = [57] + nbrs
for i in idx_list:
    print(f"  #{i}: T={T417[i]:+.2f} μK (色={'冷' if color[i]==1 else '熱'}, hop={hop[i]})")

# 鄰居溫度統計
Tn = T417[nbrs]
print(f"\n節點 57 鄰居 (4.17°): mean={Tn.mean():+.2f} μK, min={Tn.min():+.2f}, max={Tn.max():+.2f}")
print(f"全部 60 節點 mean: {T417.mean():+.2f}, std: {T417.std():.1f}")
print(f"節點 57 vs 鄰居 mean 差: {T417[57]-Tn.mean():+.2f} μK")

# 符號檢查: 鄰居著色 (hop=7 熱色) 但溫度?
print("\n=== 著色交替 vs 溫度符號 (節點 57 鄰居) ===")
for i in idx_list[1:]:
    expected = "熱色" if color[i] == 0 else "冷色"
    sign = "+" if T417[i] > 0 else "-"
    match = (color[i] == 1 and T417[i] < 0) or (color[i] == 0 and T417[i] > 0)
    print(f"  #{i}: 色={expected}, T={T417[i]:+.2f} μK ({sign}), "
          f"{'✅匹配' if match else '❌唔匹配'}")

# ============ 節點 57 喺 hop=7 層嘅位置 ============
print("\n=== hop=7 層 (節點 57 鄰居層) 全部節點 ===")
hop7 = [i for i in range(60) if hop[i] == 7]
print(f"hop=7 共 {len(hop7)} 節點:")
for i in sorted(hop7, key=lambda x: T417[x]):
    print(f"  #{i}: T={T417[i]:+.2f} μK")
T7_layer = T417[hop7]
print(f"hop=7 層 mean={T7_layer.mean():+.2f} μK, std={T7_layer.std():.1f}")

# ============ 對徑對嘅鄰居結構 (30 對) ============
print("\n=== 30 對徑對: 對徑對同色驗證 + hop 和 ===")
# 搵所有 174.66° 對
pairs = []
for i in range(60):
    for j in range(i+1, 60):
        ang = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if ang > 170.0:
            pairs.append((i, j, ang))
print(f"近對徑對: {len(pairs)} 對")
same_color = sum(1 for i, j, a in pairs if color[i] == color[j])
hop8 = sum(1 for i, j, a in pairs if hop[i] + hop[j] == 8)
print(f"同色: {same_color}/{len(pairs)}, hop 和=8: {hop8}/{len(pairs)}")
for i, j, a in pairs:
    print(f"  #{i}(hop{hop[i]},{'冷' if color[i]==1 else '熱'}) ↔ #{j}(hop{hop[j]},{'冷' if color[j]==1 else '熱'}): "
          f"T_i={T417[i]:+.2f}, T_j={T417[j]:+.2f}, 角距={a:.2f}°")

# 對徑對符號相關
sign_same = sum(1 for i, j, a in pairs if (T417[i] > 0) == (T417[j] > 0))
print(f"\n對徑對同號: {sign_same}/{len(pairs)} (隨機期望 ~15)")
print(f"對徑對反號: {len(pairs)-sign_same}/{len(pairs)}")

# 儲存
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "antipode_neighbors.txt"), "w") as f:
    f.write(f"# O6 節點 57 鄰居分析 (SMICA 4.17°)\n")
    f.write(f"# node57: T={T417[57]:+.2f} uK, hop={hop[57]}, color={color[57]}, nbrs={nbrs}\n")
    f.write(f"# nbr_temps: " + " ".join(f"{T417[i]:+.2f}" for i in nbrs) + "\n")
    f.write(f"# nbr_mean={Tn.mean():+.2f}, nbr_min={Tn.min():+.2f}, nbr_max={Tn.max():+.2f}\n")
    f.write(f"# antipodal_pairs_same_color={same_color}/{len(pairs)}, hop_sum8={hop8}/{len(pairs)}\n")
    f.write(f"# antipodal_sign_same={sign_same}/{len(pairs)}\n")
    for i, j, a in pairs:
        f.write(f"pair {i} {j} {a:.2f} {T417[i]:+.2f} {T417[j]:+.2f}\n")
print(f"\n✅ 已存: {OUT}/antipode_neighbors.txt")
