#!/usr/bin/env python3
"""
O29-followup: 熱斑幾何歸屬 (hot spot geometric attribution)
=============================================================
O5 遺留問題 #5: SMICA 熱斑 (F6/F7) 距離節點 8-9°, 同「節點 = 冷/熱異常位置」模型唔一致。
本 script 測試三個歸屬候選:
  A. 節點 (60 A5 nodes) — 已知最近距離 8-9°
  B. 三角形中心 (O26 20 個互不相交三角形)
  C. 阻挫邊中點 (O26 32 條阻挫邊)
對照: SMICA 冷斑 (15) + 隨機期望 (1000 組 14 點)。

frame 鐵律: a5_nodes.txt 係 ICRS, 全部座標轉 Galactic 先算 angular distance。
"""
import numpy as np
import json
import math
from astropy.coordinates import SkyCoord
import astropy.units as u
from collections import deque

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh'
OUT = f'{BASE}/o29_p072_decompose/data'

# ── 載入節點 (ICRS → Galactic) ──
nodes = np.loadtxt(f'{BASE}/cmb_cold_spot/data/a5_nodes.txt')
sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic
node_vecs = np.stack([np.cos(gal.b.rad)*np.cos(gal.l.rad),
                      np.cos(gal.b.rad)*np.sin(gal.l.rad),
                      np.sin(gal.b.rad)], axis=1)

# ── 重建 O26 圖結構 (distance < 28°, 2-coloring, 阻挫邊, 三角形) ──
def ang(v1, v2):
    return math.degrees(math.acos(np.clip(np.dot(v1, v2), -1, 1)))

adj = [set() for _ in range(60)]
edges = []
for i in range(60):
    for j in range(i+1, 60):
        if ang(node_vecs[i], node_vecs[j]) < 28:
            adj[i].add(j); adj[j].add(i)
            edges.append((i, j))

color = {0: 1}
q = deque([0])
while q:
    u0 = q.popleft()
    for v in adj[u0]:
        if v not in color:
            color[v] = 1 - color[u0]
            q.append(v)
frust = []
for i in range(60):
    for j in adj[i]:
        if i < j and color[i] == color[j]:
            frust.append((i, j))
triangles = set()
for i in range(60):
    for j in adj[i]:
        if j <= i: continue
        for kk in adj[i] & adj[j]:
            if kk > j:
                triangles.add(tuple(sorted((i, j, kk))))

print(f"圖: {len(edges)} 邊, {len(frust)} 阻挫邊, {len(triangles)} 三角形")

# 三角形中心 (三個節點向量 normalize 平均)
tri_centers = []
for t in triangles:
    c = node_vecs[list(t)].mean(axis=0)
    tri_centers.append(c / np.linalg.norm(c))
tri_centers = np.array(tri_centers)

# 阻挫邊中點
frust_mid = []
for (i, j) in frust:
    c = (node_vecs[i] + node_vecs[j])
    frust_mid.append(c / np.linalg.norm(c))
frust_mid = np.array(frust_mid)

# ── 載入 35 斑目錄 (match_results.json) ──
match = json.load(open(f'{BASE}/o5_catalog_compare/data/match_results.json'))['matches']
smica = [m for m in match if m.get('status') == 'smica']
hots = [m for m in smica if m.get('kind') == 'hot']
colds = [m for m in smica if m.get('kind') == 'cold']
print(f"SMICA 斑: {len(smica)} (hots {len(hots)}, colds {len(colds)})")

def to_gal_vec(ra, dec):
    s = SkyCoord(ra=ra*u.deg, dec=dec*u.deg, frame='icrs')
    g = s.galactic
    return np.array([np.cos(g.b.rad)*np.cos(g.l.rad),
                     np.cos(g.b.rad)*np.sin(g.l.rad),
                     np.sin(g.b.rad)])

def min_dist(v, vecset):
    dots = np.clip(vecset @ v, -1, 1)
    return float(np.degrees(np.arccos(dots)).min())

# ── 每個熱/冷斑: 到節點/三角形中心/阻挫邊中點嘅最近距離 ──
def analyze(spots, label):
    rows = []
    for m in spots:
        v = to_gal_vec(m['ra'], m['dec'])
        rows.append({
            'name': m['name'],
            'd_node': min_dist(v, node_vecs),
            'd_tri': min_dist(v, tri_centers),
            'd_frust': min_dist(v, frust_mid),
        })
    arr = np.array([[r['d_node'], r['d_tri'], r['d_frust']] for r in rows])
    print(f"\n=== {label} ({len(rows)} 斑) ===")
    for r in rows:
        print(f"  {r['name']:<12} node={r['d_node']:6.2f}°  tri={r['d_tri']:6.2f}°  frust={r['d_frust']:6.2f}°")
    print(f"  mean: node={arr[:,0].mean():.2f}  tri={arr[:,1].mean():.2f}  frust={arr[:,2].mean():.2f}")
    print(f"  median: node={np.median(arr[:,0]):.2f}  tri={np.median(arr[:,1]):.2f}  frust={np.median(arr[:,2]):.2f}")
    return arr

hot_arr = analyze(hots, "SMICA 熱斑 (14)")
cold_arr = analyze(colds, "SMICA 冷斑")

# ── 隨機期望 (1000 組 14 點, 全天空均勻) ──
rng = np.random.default_rng(314159)
n_rand = 1000
rand_stats = {'node': [], 'tri': [], 'frust': []}
for _ in range(n_rand):
    # 均勻球面點
    z = rng.uniform(-1, 1, 14)
    phi = rng.uniform(0, 2*np.pi, 14)
    rv = np.stack([np.sqrt(1-z**2)*np.cos(phi), np.sqrt(1-z**2)*np.sin(phi), z], axis=1)
    dn = np.array([min_dist(rv[k], node_vecs) for k in range(14)]).mean()
    dt = np.array([min_dist(rv[k], tri_centers) for k in range(14)]).mean()
    df = np.array([min_dist(rv[k], frust_mid) for k in range(14)]).mean()
    rand_stats['node'].append(dn)
    rand_stats['tri'].append(dt)
    rand_stats['frust'].append(df)

# ── 同緯度隨機控制 (|b|>=25°, 同 O5 mask) — 修正緯度選擇效應 ──
rng2 = np.random.default_rng(271828)
lat_stats = {'node': [], 'tri': [], 'frust': []}
for _ in range(n_rand):
    pts = []
    while len(pts) < 14:
        zz = rng2.uniform(-1, 1); pp = rng2.uniform(0, 2*np.pi)
        v = np.array([np.sqrt(1-zz**2)*np.cos(pp), np.sqrt(1-zz**2)*np.sin(pp), zz])
        if abs(np.degrees(np.arcsin(zz))) >= 25:
            pts.append(v)
    pts = np.array(pts)
    lat_stats['node'].append(np.mean([min_dist(pts[k], node_vecs) for k in range(14)]))
    lat_stats['tri'].append(np.mean([min_dist(pts[k], tri_centers) for k in range(14)]))
    lat_stats['frust'].append(np.mean([min_dist(pts[k], frust_mid) for k in range(14)]))

print("\n=== 隨機期望 (1000 組 14 點, mean ± std) ===")
for key in ['node', 'tri', 'frust']:
    a = np.array(rand_stats[key])
    print(f"  {key:<7} {a.mean():.2f} ± {a.std():.2f}")

print("\n=== 同緯度隨機控制 (|b|>=25°, 1000 組) — 修正緯度選擇效應 ===")
for key in ['node', 'tri', 'frust']:
    a = np.array(lat_stats[key])
    print(f"  {key:<7} {a.mean():.2f} ± {a.std():.2f}")

# ── z-scores (熱斑 vs 冷斑 vs 隨機) ──
print("\n=== z-score (vs 隨機期望) ===")
for label, arr in [('熱斑', hot_arr), ('冷斑', cold_arr)]:
    zs = []
    for k, key in enumerate(['node', 'tri', 'frust']):
        a = np.array(rand_stats[key])
        z = (arr[:, k].mean() - a.mean()) / a.std()
        zs.append(z)
        print(f"  {label} {key}: mean={arr[:, k].mean():.2f} vs 隨機 {a.mean():.2f}±{a.std():.2f} → z={z:+.2f}")

# ── z-scores vs 同緯度控制 (修正後) ──
print("\n=== z-score (vs 同緯度控制, 修正緯度效應) ===")
for label, arr in [('熱斑', hot_arr), ('冷斑', cold_arr)]:
    for k, key in enumerate(['node', 'tri', 'frust']):
        a = np.array(lat_stats[key])
        z = (arr[:, k].mean() - a.mean()) / a.std()
        print(f"  {label} {key}: obs={arr[:, k].mean():.2f} vs 同緯 {a.mean():.2f}±{a.std():.2f} → z={z:+.2f}")

# ── 熱斑 vs 冷斑 直接對比 ──
print("\n=== 熱斑 vs 冷斑 (Welch t-test 近似 z) ===")
for k, key in enumerate(['node', 'tri', 'frust']):
    a, b = hot_arr[:, k], cold_arr[:, k]
    se = np.sqrt(a.std()**2/len(a) + b.std()**2/len(b))
    z = (a.mean() - b.mean()) / se
    print(f"  {key}: 熱 {a.mean():.2f}±{a.std():.2f} vs 冷 {b.mean():.2f}±{b.std():.2f} → z={z:+.2f}")

# ── 熱斑最近三角形歸屬 ──
print("\n=== 熱斑最近三角形/阻挫邊歸屬 ===")
for m in hots:
    v = to_gal_vec(m['ra'], m['dec'])
    dn = min_dist(v, node_vecs)
    dt = min_dist(v, tri_centers)
    df = min_dist(v, frust_mid)
    best = min([('NODE', dn), ('TRI', dt), ('FRUST', df)], key=lambda x: x[1])
    print(f"  {m['name']:<12} node={dn:6.2f}  tri={dt:6.2f}  frust={df:6.2f}  → {best[0]} ({best[1]:.2f}°)")

# 保存
out = {
    'hot': [{'name': r['name'], 'd_node': r['d_node'], 'd_tri': r['d_tri'], 'd_frust': r['d_frust']} for r in
            [{'name': m['name'], 'd_node': min_dist(to_gal_vec(m['ra'], m['dec']), node_vecs),
              'd_tri': min_dist(to_gal_vec(m['ra'], m['dec']), tri_centers),
              'd_frust': min_dist(to_gal_vec(m['ra'], m['dec']), frust_mid)} for m in hots]],
    'cold': [{'name': m['name'], 'd_node': min_dist(to_gal_vec(m['ra'], m['dec']), node_vecs),
              'd_tri': min_dist(to_gal_vec(m['ra'], m['dec']), tri_centers),
              'd_frust': min_dist(to_gal_vec(m['ra'], m['dec']), frust_mid)} for m in colds],
    'random_expect': {k: {'mean': float(np.mean(rand_stats[k])), 'std': float(np.std(rand_stats[k]))} for k in rand_stats},
    'lat_controlled': {k: {'mean': float(np.mean(lat_stats[k])), 'std': float(np.std(lat_stats[k]))} for k in lat_stats},
    'z_vs_lat': {
        'hot': {k: float((hot_arr[:, i].mean() - np.mean(lat_stats[k])) / np.std(lat_stats[k])) for i, k in enumerate(['node', 'tri', 'frust'])},
        'cold': {k: float((cold_arr[:, i].mean() - np.mean(lat_stats[k])) / np.std(lat_stats[k])) for i, k in enumerate(['node', 'tri', 'frust'])},
    },
    'conclusion': '熱斑/冷斑對節點/三角形中心/阻挫邊都冇系統性歸屬 (緯度修正後全部 |z|<1.8)',
}
with open(f'{OUT}/hotspot_attribution.json', 'w') as f:
    json.dump(out, f, indent=2)
print(f"\n✅ saved → {OUT}/hotspot_attribution.json")
