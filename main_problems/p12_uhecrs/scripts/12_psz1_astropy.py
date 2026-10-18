#!/usr/bin/env python3
"""
PSZ1 星系團 — A₅ 節點對齊檢驗 (astropy 正確解析)
====================================================
數據: HEASARC TAP plancksz (1227 星系團, 全天)
檢驗 H2: 星系團 (物質凝聚) 應該對齊 60 個 A₅ 節點?

注意: 用天球均勻隨機做 null (全天樣本), 唔係打散 RA
"""
import math, os, json
import numpy as np
from astropy.io import votable

# ============ 1. 正確解析 ============
v = votable.parse('/tmp/psz_all.xml')
t = v.get_first_table().to_table()
cl_ra = np.array(t['ra'], dtype=float)
cl_dec = np.array(t['dec'], dtype=float)
cl_z = np.array([np.nan if np.isnan(x) else x for x in t['redshift']])
print(f"星系團: {len(cl_ra)} 個 (全天)")

# ============ 2. 60 節點 ============
CMB_DATA = '/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data'
nodes = []
with open(os.path.join(CMB_DATA, 'a5_nodes.txt')) as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'): continue
        p = line.split()
        nodes.append((float(p[0]), float(p[1])))
nodes = np.array(nodes)

def ang_dist_mat(ra1, dec1, ra2, dec2):
    ra1, dec1 = np.radians(ra1), np.radians(dec1)
    ra2, dec2 = np.radians(ra2), np.radians(dec2)
    cosd = np.sin(dec1)[:, None]*np.sin(dec2)[None, :] + \
           np.cos(dec1)[:, None]*np.cos(dec2)[None, :]*np.cos(ra1[:, None]-ra2[None, :])
    return np.degrees(np.arccos(np.clip(cosd, -1, 1)))

D = ang_dist_mat(cl_ra, cl_dec, nodes[:, 0], nodes[:, 1])
d_min = D.min(axis=1)
print(f"最近節點距離: 中位數 {np.median(d_min):.2f}°, 平均 {np.mean(d_min):.2f}°")
print(f"分佈: 10%={np.percentile(d_min,10):.1f}° 50%={np.median(d_min):.1f}° 90%={np.percentile(d_min,90):.1f}°")

# ============ 3. MC: 天球均勻 (正確 null) ============
rng = np.random.default_rng(42)
N_MC = 5000
print(f"\n{'='*70}")
print("MC: 天球均勻隨機 (正確 for 全天)")
print(f"{'='*70}")
for r in [5, 8, 10, 15]:
    obs = int((d_min < r).sum())
    mc = np.zeros(N_MC, dtype=int)
    for i in range(N_MC):
        ra_r = rng.uniform(0, 360, len(cl_ra))
        dec_r = np.degrees(np.arcsin(rng.uniform(-1, 1, len(cl_ra))))
        D_r = ang_dist_mat(ra_r, dec_r, nodes[:, 0], nodes[:, 1])
        mc[i] = (D_r.min(axis=1) < r).sum()
    p_hi = float((mc >= obs).mean())
    p_lo = float((mc <= obs).mean())
    sig_hi = "🟢 過量!" if p_hi < 0.05 else ""
    sig_lo = "🟢 不足!" if p_lo < 0.05 else ""
    print(f"  節點<{r:>2}°: 觀測 {obs:>4} ({obs/len(cl_ra)*100:5.1f}%)  MC={mc.mean():.1f}±{mc.std():.1f} ({mc.mean()/len(cl_ra)*100:5.1f}%)  P(≥)={p_hi:.4f} {sig_hi}  P(≤)={p_lo:.4f} {sig_lo}")

# ============ 4. 阻挫邊檢驗 (向量化大圓距離) ============
print(f"\n{'='*70}")
print("星系團 vs 32 阻挫邊 (應力集中線)")
print(f"{'='*70}")
edges = []
with open(os.path.join(CMB_DATA, 'frustration_edges.txt')) as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'): continue
        p = line.split()
        edges.append(((float(p[4]), float(p[5])), (float(p[6]), float(p[7]))))

def vec_to_cart(ra, dec):
    ra, dec = np.radians(ra), np.radians(dec)
    return np.stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)], axis=-1)

# 邊法向量 (32 × 3)
edge_normals = []
for e in edges:
    A = vec_to_cart(np.array([e[0][0]]), np.array([e[0][1]]))[0]
    B = vec_to_cart(np.array([e[1][0]]), np.array([e[1][1]]))[0]
    n = np.cross(A, B)
    n = n / (np.linalg.norm(n) + 1e-15)
    edge_normals.append(n)
edge_normals = np.array(edge_normals)  # (32, 3)

# 星系團 3D 向量 (1228 × 3)
P_cl = vec_to_cart(cl_ra, cl_dec)  # (1228, 3)

# 大圓距離: sin(d) = |P·n| → d = arcsin(|P·n|)
D_edge = np.abs(P_cl @ edge_normals.T)  # (1228, 32)
D_edge = np.clip(D_edge, 0, 1)
d_edge = np.degrees(np.arcsin(D_edge)).min(axis=1)
print(f"最近阻挫邊距離: 中位數 {np.median(d_edge):.2f}°, 平均 {np.mean(d_edge):.2f}°")

# 邊 MC (向量化)
for r in [3, 5, 8]:
    obs = int((d_edge < r).sum())
    mc = np.zeros(3000, dtype=int)
    for i in range(3000):
        ra_r = rng.uniform(0, 360, len(cl_ra))
        dec_r = np.degrees(np.arcsin(rng.uniform(-1, 1, len(cl_ra))))
        P_r = vec_to_cart(ra_r, dec_r)
        D_r = np.abs(P_r @ edge_normals.T)
        D_r = np.clip(D_r, 0, 1)
        d_r = np.degrees(np.arcsin(D_r)).min(axis=1)
        mc[i] = (d_r < r).sum()
    p_hi = float((mc >= obs).mean())
    p_lo = float((mc <= obs).mean())
    sig_hi = "🟢 過量!" if p_hi < 0.05 else ""
    sig_lo = "🟢 不足!" if p_lo < 0.05 else ""
    print(f"  邊<{r:>2}°: 觀測 {obs:>4} ({obs/len(cl_ra)*100:5.1f}%)  MC={mc.mean():.1f}±{mc.std():.1f} ({mc.mean()/len(cl_ra)*100:5.1f}%)  P(≥)={p_hi:.4f} {sig_hi}  P(≤)={p_lo:.4f} {sig_lo}")

# ============ 5. 保存 ============
os.makedirs('data', exist_ok=True)
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/psz1_alignment_astropy.json'), 'w') as f:
    json.dump({
        "n_clusters": int(len(cl_ra)),
        "median_d_node": float(np.median(d_min)),
        "median_d_edge": float(np.median(d_edge)),
        "status": "full-sky uniform MC null",
        "note": "PSZ1 v2.1 via HEASARC TAP"
    }, f, indent=2)
print(f"\n已保存 data/psz1_alignment_astropy.json")
