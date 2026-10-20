#!/usr/bin/env python3
"""
O7 開放問題 E 最終: 縫合線跨冷熱統計 + 節點 47 銀河面檢查
============================================================
發現:
- 15/20 縫合線「一端近冷一端近熱」(跨冷熱)
- 節點 47: b=-8.6° 靠近銀河面

深入:
1. 跨冷熱比例 15/20 係咪統計顯著? (隨機對照)
2. 節點 47 嘅冷係咪銀河前景?
3. 銀河面遮罩後, 端點距離有冇變化?
"""
import numpy as np, math, json
from collections import defaultdict, deque
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as AU
from scipy.stats import ttest_ind, binomtest

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

sc = SkyCoord(ra=nodes[:, 0]*AU.deg, dec=nodes[:, 1]*AU.deg, frame='icrs')
gal = sc.galactic
node_l = np.array(gal.l.deg)
node_b = np.array(gal.b.deg)
node_vecs = np.array([[math.cos(math.radians(b))*math.cos(math.radians(l)),
                        math.cos(math.radians(b))*math.sin(math.radians(l)),
                        math.sin(math.radians(b))] for l, b in zip(node_l, node_b)])

print("=" * 75)
print("O7 開放問題 E 最終: 跨冷熱統計 + 銀河面")
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

# 目錄
with open(f"{O5}/smica_catalog.json") as f:
    cat = json.load(f)
cold_vecs = []
for s in cat['cold']:
    l, b = s['peak_l'], s['peak_b']
    r, d = math.radians(l), math.radians(b)
    cold_vecs.append(np.array([math.cos(d)*math.cos(r), math.cos(d)*math.sin(r), math.sin(d)]))
hot_vecs = []
for s in cat.get('hot', []):
    l, b = s['peak_l'], s['peak_b']
    r, d = math.radians(l), math.radians(b)
    hot_vecs.append(np.array([math.cos(d)*math.cos(r), math.cos(d)*math.sin(r), math.sin(d)]))
cold_vecs = np.array(cold_vecs)
hot_vecs = np.array(hot_vecs)

def min_dist(v, vecs_list):
    if len(vecs_list) == 0:
        return 999.0
    return min(math.degrees(math.acos(np.clip(np.dot(v, w), -1, 1))) for w in vecs_list)

def is_cross(comp):
    eps = [v for v in comp if len(frust_adj[v]) == 1]
    if len(eps) != 2:
        return False
    e1, e2 = eps
    d1c = min_dist(node_vecs[e1], cold_vecs)
    d2c = min_dist(node_vecs[e2], cold_vecs)
    d1h = min_dist(node_vecs[e1], hot_vecs)
    d2h = min_dist(node_vecs[e2], hot_vecs)
    return (d1c < d2c and d1h > d2h) or (d1c > d2c and d1h < d2h)

# 真實
real_cross = sum(1 for comp in seams if is_cross(comp))
print(f"\n真實: {real_cross}/{len(seams)} 縫合線跨冷熱")

# 隨機對照: shuffle 冷/熱目錄標籤
rng = np.random.RandomState(42)
rand_cross = []
for _ in range(10000):
    # 隨機 shuffle 冷/熱位置
    all_spots = np.concatenate([cold_vecs, hot_vecs])
    perm = rng.permutation(len(all_spots))
    r_cold = all_spots[perm[:len(cold_vecs)]]
    r_hot = all_spots[perm[len(cold_vecs):]]
    def r_is_cross(comp):
        eps = [v for v in comp if len(frust_adj[v]) == 1]
        if len(eps) != 2:
            return False
        e1, e2 = eps
        d1c = min_dist(node_vecs[e1], r_cold)
        d2c = min_dist(node_vecs[e2], r_cold)
        d1h = min_dist(node_vecs[e1], r_hot)
        d2h = min_dist(node_vecs[e2], r_hot)
        return (d1c < d2c and d1h > d2h) or (d1c > d2c and d1h < d2h)
    rand_cross.append(sum(1 for comp in seams if r_is_cross(comp)))

rand_cross = np.array(rand_cross)
pct = np.mean(rand_cross >= real_cross) * 100
print(f"隨機對照: mean={np.mean(rand_cross):.1f} ± {np.std(rand_cross):.1f}, "
      f"真實百分位={pct:.1f}% {'🟡🟡 顯著多!' if pct < 5 else '🟢 隨機水平'}")

# 二項檢定
p_binom = binomtest(real_cross, len(seams), 0.5).pvalue
print(f"二項檢定 (p=0.5): p={p_binom:.4f} {'🟡 顯著' if p_binom < 0.05 else '🟢 隨機'}")

# ============ 3. 節點 47 銀河面 ============
print(f"\n{'='*75}")
print("📐 [E.8] 節點 47 銀河面檢查")
print(f"{'='*75}")

print(f"   節點 47: b={node_b[47]:.1f}°")
print(f"   銀河面定義 |b| < 20° → {'⚠️ 喺銀河面內!' if abs(node_b[47]) < 20 else '✅ 喺銀河面外'}")

# 銀河面內節點一覽
print(f"\n   銀河面內節點 (|b|<20°):")
gal_nodes = []
for v in range(60):
    if abs(node_b[v]) < 20:
        gal_nodes.append(v)
        print(f"     #{v}: l={node_l[v]:.1f}°, b={node_b[v]:.1f}°")
print(f"   共 {len(gal_nodes)} 個")

# 銀河面內節點嘅溫度
m = hp.read_map(f"{CACHE}/smica2_smooth4.17.fits", field=0)
m = hp.remove_dipole(m)
nside = hp.get_nside(m)
pix = hp.ang2pix(nside, node_l, node_b, lonlat=True)
T = m[pix]

print(f"\n   銀河面內節點溫度:")
for v in gal_nodes:
    print(f"     #{v}: T={T[v]*1e6:+.1f} μK")

# 節點 47 係咪銀河面內最冷?
gal_T = [T[v]*1e6 for v in gal_nodes]
print(f"\n   銀河面內節點平均 T: {np.mean(gal_T):+.1f} ± {np.std(gal_T):.1f} μK")
print(f"   節點 47: {T[47]*1e6:+.1f} μK")
print(f"   節點 47 喺銀河面內排名: 最冷? {'⚠️ 係!' if T[47]*1e6 == min(gal_T) else '唔係'}")

# ============ 4. 剔除銀河面後重做跨冷熱 ============
print(f"\n{'='*75}")
print("📐 [E.9] 剔除銀河面節點後嘅縫合線")
print(f"{'='*75}")

# 縫合線完整喺銀河面外?
clean_seams = []
masked_seams = []
for comp in seams:
    if all(abs(node_b[v]) >= 20 for v in comp):
        clean_seams.append(comp)
    else:
        masked_seams.append(comp)

print(f"   完整喺銀河面外: {len(clean_seams)} 條")
print(f"   涉及銀河面節點: {len(masked_seams)} 條")
for comp in masked_seams:
    in_gal = [v for v in comp if abs(node_b[v]) < 20]
    print(f"     {comp} 銀河面節點: {in_gal}")

# 乾淨縫合線嘅跨冷熱
clean_cross = sum(1 for comp in clean_seams if is_cross(comp))
if clean_seams:
    print(f"\n   乾淨縫合線跨冷熱: {clean_cross}/{len(clean_seams)}")
    p_binom2 = binomtest(clean_cross, len(clean_seams), 0.5).pvalue
    print(f"   二項檢定: p={p_binom2:.4f} {'🟡 顯著' if p_binom2 < 0.05 else '🟢 隨機'}")

# ============ 5. 總結 ============
print(f"\n{'='*75}")
print("📋 總結")
print(f"{'='*75}")
print(f"""
   縫合線 × O5 目錄最終結論:

   1. 跨冷熱比例: {real_cross}/{len(seams)}
      隨機對照: {np.mean(rand_cross):.1f} ± {np.std(rand_cross):.1f}
      百分位: {pct:.1f}%
      {'🟡 縫合線顯著傾向一端近冷一端近熱!' if pct < 5 else '🟢 隨機水平'}

   2. 節點 47 (全球第2冷):
      b={node_b[47]:.1f}° → {'喺銀河面內 ⚠️' if abs(node_b[47]) < 20 else '喺銀河面外 ✅'}
      → 冷信號可能含銀河前景污染!

   3. 剔除銀河面後: {len(clean_seams)} 條乾淨縫合線
      → 跨冷熱: {clean_cross}/{len(clean_seams)} (需檢定)

   4. 結論: 縫合線同目錄結構嘅關係...
""")