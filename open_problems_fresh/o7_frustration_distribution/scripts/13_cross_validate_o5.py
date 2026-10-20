#!/usr/bin/env python3
"""
O7 開放問題 E: 縫合線 × O5 冷斑目錄交叉驗證
============================================================
問題: O7 發現 20 條縫合線 (阻挫邊=投影縫合線) + 大 ΔT 縫合線連住極端溫度區。
O5 有 SMICA flood-fill 冷/熱組件目錄 (含 l/b 座標)。

交叉驗證:
1. 縫合線端點 vs O5 冷組件 peak 位置距離
2. 縫合線端點 vs O5 熱組件 peak 位置距離
3. 大 ΔT 縫合線 (S12, S18) 端點係咪特別接近目錄冷/熱結構?
4. 縫合線節點溫度 vs 目錄組件溫度比較
5. 隨機對照: 隨機 40 節點到最近目錄結構距離
"""
import numpy as np, math, json
from collections import defaultdict, deque
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as AU
from scipy.stats import ttest_ind, mannwhitneyu

DATA = "/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data"
O5 = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o5_catalog_compare/data"
CACHE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o5_catalog_compare/data/smooth_cache"

# ============ 1. 載入 O5 目錄 ============
print("=" * 75)
print("O7 開放問題 E: 縫合線 × O5 目錄交叉驗證")
print("=" * 75)

with open(f"{O5}/smica_catalog.json") as f:
    cat = json.load(f)

cold_spots = cat['cold']
hot_spots = cat.get('hot', [])
print(f"\nO5 目錄: 冷組件 {len(cold_spots)}, 熱組件 {len(hot_spots)}")

# 目錄結構: 用 peak_l, peak_b (Galactic)
def spot_vectors(spots):
    vecs_s = []
    for s in spots:
        l, b = s['peak_l'], s['peak_b']
        r, d = math.radians(l), math.radians(b)
        vecs_s.append(np.array([math.cos(d)*math.cos(r),
                                math.cos(d)*math.sin(r),
                                math.sin(d)]))
    return np.array(vecs_s)

cold_vecs = spot_vectors(cold_spots)
hot_vecs = spot_vectors(hot_spots) if hot_spots else np.zeros((0, 3))

# 冷組件詳細
print(f"\n   冷組件:")
for i, s in enumerate(cold_spots):
    print(f"     C{i}: (l={s['peak_l']:.1f}°, b={s['peak_b']:.1f}°), T={s['amp_muK']:+.1f} μK, area={s['area_deg2']:.0f} deg²")

if hot_spots:
    print(f"\n   熱組件:")
    for i, s in enumerate(hot_spots):
        print(f"     H{i}: (l={s['peak_l']:.1f}°, b={s['peak_b']:.1f}°), T={s['amp_muK']:+.1f} μK, area={s['area_deg2']:.0f} deg²")

# ============ 2. 載入 O7 節點 ============
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

# 節點轉 Galactic
sc = SkyCoord(ra=nodes[:, 0]*AU.deg, dec=nodes[:, 1]*AU.deg, frame='icrs')
gal = sc.galactic
node_l = np.array(gal.l.deg)
node_b = np.array(gal.b.deg)

# 節點向量 (Galactic)
node_vecs = np.array([[math.cos(math.radians(b))*math.cos(math.radians(l)),
                        math.cos(math.radians(b))*math.sin(math.radians(l)),
                        math.sin(math.radians(b))] for l, b in zip(node_l, node_b)])

def ang_dist(v1, v2):
    return math.degrees(math.acos(np.clip(np.dot(v1, v2), -1, 1)))

# ============ 3. 縫合線 ============
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

# 讀 4.17° 溫度
m = hp.read_map(f"{CACHE}/smica2_smooth4.17.fits", field=0)
m = hp.remove_dipole(m)
nside = hp.get_nside(m)
pix = hp.ang2pix(nside, node_l, node_b, lonlat=True)
T = m[pix]

# 每條縫合線 ΔT + 端點
seam_info = []
for i, comp in enumerate(seams):
    eps = [v for v in comp if len(frust_adj[v]) == 1]
    temps = [T[v]*1e6 for v in comp]
    dt = max(temps) - min(temps)
    seam_info.append({'idx': i, 'nodes': comp, 'endpoints': eps, 'dt': dt, 'temps': temps})

seam_info.sort(key=lambda x: x['dt'], reverse=True)

# ============ 4. 端點到目錄結構距離 ============
print(f"\n{'='*75}")
print("📐 [E.1] 縫合線端點 vs 冷/熱目錄結構")
print(f"{'='*75}")

all_endpoints = []
for si in seam_info:
    all_endpoints.extend(si['endpoints'])

def min_dist_to(vertex, catalog_vecs):
    if len(catalog_vecs) == 0:
        return 999.0
    return min(ang_dist(vertex, v) for v in catalog_vecs)

# 每個端點到最近冷/熱結構
print(f"\n   40 個端點到目錄結構距離:")
endpoint_data = []
for v in all_endpoints:
    d_cold = min_dist_to(node_vecs[v], cold_vecs)
    d_hot = min_dist_to(node_vecs[v], hot_vecs)
    d_all = min(d_cold, d_hot)
    endpoint_data.append({'node': v, 'd_cold': d_cold, 'd_hot': d_hot, 'd_all': d_all,
                          'T': T[v]*1e6, 'color': color[v]})

d_cold_all = np.array([e['d_cold'] for e in endpoint_data])
d_hot_all = np.array([e['d_hot'] for e in endpoint_data])
d_all = np.array([e['d_all'] for e in endpoint_data])
print(f"   到最近冷結構: mean={np.mean(d_cold_all):.1f}°, median={np.median(d_cold_all):.1f}°")
print(f"   到最近熱結構: mean={np.mean(d_hot_all):.1f}°, median={np.median(d_hot_all):.1f}°")
print(f"   到最近任一結構: mean={np.mean(d_all):.1f}°, median={np.median(d_all):.1f}°")

# 隨機對照
print(f"\n   隨機對照 (10000 次, 隨機 40 節點):")
rng = np.random.RandomState(42)
rand_d_all = []
for _ in range(10000):
    idx = rng.choice(60, 40, replace=False)
    ds = [min_dist_to(node_vecs[v], cold_vecs) if len(cold_vecs) else 999 for v in idx]
    rand_d_all.append(np.mean(ds))
rand_d_all = np.array(rand_d_all)
pct = np.mean(rand_d_all <= np.mean(d_cold_all)) * 100
print(f"   隨機 40 節點到最近冷結構: {np.mean(rand_d_all):.1f} ± {np.std(rand_d_all):.1f}°")
print(f"   真實端點: {np.mean(d_cold_all):.1f}°")
print(f"   百分位: {pct:.1f}% {'🟡 端點異常接近冷結構!' if pct < 5 else '🟢 正常'}")

# ============ 5. 大 ΔT 縫合線端點 vs 目錄 ============
print(f"\n{'='*75}")
print("📐 [E.2] 大 ΔT 縫合線端點")
print(f"{'='*75}")

print(f"   按 ΔT 排序嘅縫合線:")
print(f"   {'#':>2} {'ΔT':>7} {'節點':>18} {'端點':>10} {'端點到冷':>10} {'端點到熱':>10} {'端點T':>10}")
for si in seam_info:
    for v in si['endpoints']:
        d_c = min_dist_to(node_vecs[v], cold_vecs)
        d_h = min_dist_to(node_vecs[v], hot_vecs)
        print(f"   {si['idx']:>2} {si['dt']:>7.1f} {str(si['nodes']):>18} {v:>10} {d_c:>10.1f} {d_h:>10.1f} {T[v]*1e6:>+10.1f}")

# 大 ΔT (前 5) vs 細 ΔT (後 5) 端點到冷結構距離
big_seams = seam_info[:5]
small_seams = seam_info[-5:]
big_eps = [v for si in big_seams for v in si['endpoints']]
small_eps = [v for si in small_seams for v in si['endpoints']]

big_d = [min_dist_to(node_vecs[v], cold_vecs) for v in big_eps]
small_d = [min_dist_to(node_vecs[v], cold_vecs) for v in small_eps]
print(f"\n   大 ΔT 縫合線端點到冷結構: {np.mean(big_d):.1f} ± {np.std(big_d):.1f}°")
print(f"   細 ΔT 縫合線端點到冷結構: {np.mean(small_d):.1f} ± {np.std(small_d):.1f}°")
if len(big_d) >= 2 and len(small_d) >= 2:
    t_p = ttest_ind(big_d, small_d)[1]
    print(f"   t-test: p={t_p:.4f} {'🟡 大ΔT端點更近冷結構!' if t_p < 0.05 and np.mean(big_d) < np.mean(small_d) else '🟢 無差異'}")

# ============ 6. 縫合線節點 vs 目錄組件溫度 ============
print(f"\n{'='*75}")
print("📐 [E.3] 節點溫度 vs 目錄結構溫度")
print(f"{'='*75}")

# 每個節點: 最近目錄結構嘅溫度
node_nearest_cold_T = np.array([min_dist_to(node_vecs[v], cold_vecs) for v in range(60)])
print(f"   全部節點到最近冷結構:")
print(f"   < 10°: {sum(1 for d in node_nearest_cold_T if d < 10)} 節點")
print(f"   < 20°: {sum(1 for d in node_nearest_cold_T if d < 20)} 節點")
print(f"   < 30°: {sum(1 for d in node_nearest_cold_T if d < 30)} 節點")

# 縫合線節點 vs 非縫合線節點
seam_nodes = set()
for si in seam_info:
    seam_nodes.update(si['nodes'])
non_seam = [v for v in range(60) if v not in seam_nodes]

seam_d = [min_dist_to(node_vecs[v], cold_vecs) for v in seam_nodes]
nonseam_d = [min_dist_to(node_vecs[v], cold_vecs) for v in non_seam]
print(f"\n   縫合線節點 ({len(seam_nodes)}): 到最近冷 = {np.mean(seam_d):.1f}°")
print(f"   非縫合節點 ({len(non_seam)}): 到最近冷 = {np.mean(nonseam_d):.1f}°")
if len(seam_d) >= 2 and len(nonseam_d) >= 2:
    t_p = ttest_ind(seam_d, nonseam_d)[1]
    print(f"   t-test: p={t_p:.4f} {'🟡' if t_p < 0.05 else '🟢'}")

# ============ 7. 特殊: S18 節點 47 到目錄 ============
print(f"\n{'='*75}")
print("📐 [E.4] S18 (全球第2冷點) 到目錄")
print(f"{'='*75}")

node47_vec = node_vecs[47]
for i, s in enumerate(cold_spots):
    sv = cold_vecs[i]
    d = ang_dist(node47_vec, sv)
    print(f"   節點 47 ↔ 冷組件 C{i} ({s['peak_l']:.0f}°, {s['peak_b']:.0f}°): {d:.1f}°")

# 節點 47 喺目錄入面?
# SMICA flood-fill 目錄: 節點 47 = 邊個組件?
# 直接搵最近
d_min = min(ang_dist(node47_vec, v) for v in cold_vecs)
idx_min = int(np.argmin([ang_dist(node47_vec, v) for v in cold_vecs]))
print(f"   最近冷組件: C{idx_min} ({cold_spots[idx_min]['peak_l']:.0f}°, {cold_spots[idx_min]['peak_b']:.0f}°) at {d_min:.1f}°")

# ============ 8. 總結 ============
print(f"\n{'='*75}")
print("📋 總結")
print(f"{'='*75}")
print(f"""
   縫合線 × O5 目錄交叉驗證:

   1. 40 端點到最近冷結構: {np.mean(d_cold_all):.1f}° (median {np.median(d_cold_all):.1f}°)
      隨機對照: {np.mean(rand_d_all):.1f} ± {np.std(rand_d_all):.1f}° (百分位 {pct:.1f}%)

   2. 大 ΔT 縫合線端點 vs 細 ΔT 端點:
      大: {np.mean(big_d):.1f}°, 細: {np.mean(small_d):.1f}°
      {'🟡 大ΔT端點更接近冷結構' if len(big_d)>=2 and len(small_d)>=2 and ttest_ind(big_d,small_d)[1]<0.05 else '🟢 無顯著差異'}

   3. 縫合線節點 vs 非縫合線節點到冷結構:
      {np.mean(seam_d):.1f}° vs {np.mean(nonseam_d):.1f}°

   4. S18 節點 47 (全球第2冷): 到最近冷組件 {d_min:.1f}°
      最近: C{idx_min} ({cold_spots[idx_min]['peak_l']:.0f}°, {cold_spots[idx_min]['peak_b']:.0f}°)
      {'🟡🟡 節點47 = 目錄冷組件成員!' if d_min < 15 else '🟢 距離較遠'}

   結論: 縫合線同目錄結構嘅關係...
""")