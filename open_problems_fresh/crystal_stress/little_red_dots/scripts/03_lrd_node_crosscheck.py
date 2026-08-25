#!/usr/bin/env python3
"""
COSMOS-Web LRD 位置 vs 60 A₅ 節點 — 直接檢驗
===============================================
假設: LRD = 拓撲缺陷節點
→ 預測: LRD 聚集喺 A₅ 節點附近 (正相關)
→ 對照: 星系團避開節點 (負相關, 已證實 3.43σ)
→ 完美對稱!

數據: COSMOS-Web Akins+2024 (2406.10341), 434 LRD, 0.54 deg²
"""
import math, os, json
import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE, '../data')
RECORDS_DIR = os.path.join(BASE, '../records')
CMB_DATA = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/cmb_cold_spot/data'

# ============ 載入 LRD (手動 ECSV parser) ============
print("載入 COSMOS-Web LRD catalog...")
with open(os.path.join(DATA_DIR, 'COSMOS-Web_LRDs.dat')) as f:
    lines = f.readlines()

# 搵數據開始行
data_start = 0
for i, line in enumerate(lines):
    if not line.startswith('#'):
        data_start = i
        break

# 搵 column names (ECSV header)
col_names = None
for line in lines[:data_start]:
    if 'name:' in line and 'datatype' in line:
        # 例如: # - {name: ra, unit: deg, datatype: float64, ...}
        m = line.split('name:')[1].split(',')[0].strip()
        if col_names is None:
            col_names = [m]
        else:
            col_names.append(m)

print(f"  Columns: {len(col_names)} ({col_names[0]}, {col_names[1]}, {col_names[2]}, ...)")
print(f"  Data rows: {len(lines) - data_start}")

# Parse data (skip header line, start from data_start+1)
lr_ra, lr_dec, lr_z = [], [], []
for i in range(data_start + 1, len(lines)):
    p = lines[i].strip().split()
    if len(p) < 3: continue
    lr_ra.append(float(p[1]))
    lr_dec.append(float(p[2]))
    # redshift: z_qso_med 係 col 50 (0-indexed)
    if len(p) > 50 and p[50] != '-99.0':
        lr_z.append(float(p[50]))
    else:
        lr_z.append(-1)

lr_ra = np.array(lr_ra)
lr_dec = np.array(lr_dec)
lr_z = np.array(lr_z)
N_lrd = len(lr_ra)
print(f"LRD: {N_lrd} objects, RA={lr_ra.min():.2f}-{lr_ra.max():.2f}, Dec={lr_dec.min():.2f}-{lr_dec.max():.2f}")

# ============ 載入 60 節點 ============
nodes = []
with open(os.path.join(CMB_DATA, 'a5_nodes.txt')) as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'): continue
        p = line.split()
        nodes.append((float(p[0]), float(p[1])))
nodes = np.array(nodes)
print(f"60 節點: RA={nodes[:,0].min():.1f}-{nodes[:,0].max():.1f}, Dec={nodes[:,1].min():.1f}-{nodes[:,1].max():.1f}")

# ============ 載入 32 阻挫邊 ============
edges = []
with open(os.path.join(CMB_DATA, 'frustration_edges.txt')) as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'): continue
        p = line.split()
        edges.append((float(p[0]), float(p[1]), float(p[2]), float(p[3])))
edges = np.array(edges)
print(f"32 阻挫邊")

# ============ 角距離 ============
def ang_dist(ra1, dec1, ra2, dec2):
    ra1, dec1 = np.radians(ra1), np.radians(dec1)
    ra2, dec2 = np.radians(ra2), np.radians(dec2)
    cosd = np.sin(dec1)*np.sin(dec2) + np.cos(dec1)*np.cos(dec2)*np.cos(ra1-ra2)
    return np.degrees(np.arccos(np.clip(cosd, -1, 1)))

# 每 LRD 到最近節點
d_min_node = np.array([min(ang_dist(lr_ra[i], lr_dec[i], n[0], n[1]) for n in nodes) for i in range(N_lrd)])
print(f"\nLRD 到最近節點: median={np.median(d_min_node):.2f}°, mean={d_min_node.mean():.2f}°")

# ============ MC 隨機 ============
rng = np.random.default_rng(42)
N_MC = 3000
N_lrd_local = N_lrd

# COSMOS field: RA ~ 149.5-150.5, Dec ~ 1.5-2.5
# 用實際 LRD 嘅 RA/Dec 邊界做 MC
ra_lo, ra_hi = lr_ra.min(), lr_ra.max()
dec_lo, dec_hi = lr_dec.min(), lr_dec.max()
area_pct = (ra_hi-ra_lo)/360 * (np.sin(np.radians(dec_hi)) - np.sin(np.radians(dec_lo))) / 2

print(f"\nCOSMOS field: RA=[{ra_lo:.1f},{ra_hi:.1f}] Dec=[{dec_lo:.1f},{dec_hi:.1f}]")
print(f"Field area: {area_pct*41253:.0f} deg² (full sky: 41253 deg²)")
print(f"MC: {N_MC} realizations, keep dec±1° field")

# 節點檢驗
mc_med = np.zeros(N_MC)
mc_frac5 = np.zeros(N_MC)
mc_frac8 = np.zeros(N_MC)
mc_frac10 = np.zeros(N_MC)

for j in range(N_MC):
    # 隨機點喺 COSMOS field 入面
    mc_ra = rng.uniform(ra_lo, ra_hi, N_lrd_local)
    mc_dec = rng.uniform(dec_lo, dec_hi, N_lrd_local)
    mc_d = np.array([min(ang_dist(mc_ra[k], mc_dec[k], n[0], n[1]) for n in nodes) for k in range(N_lrd_local)])
    mc_med[j] = np.median(mc_d)
    mc_frac5[j] = (mc_d < 5).mean() * 100
    mc_frac8[j] = (mc_d < 8).mean() * 100
    mc_frac10[j] = (mc_d < 10).mean() * 100

obs_med = np.median(d_min_node)
obs_frac5 = (d_min_node < 5).mean() * 100
obs_frac8 = (d_min_node < 8).mean() * 100
obs_frac10 = (d_min_node < 10).mean() * 100

p_med = float((mc_med <= obs_med).mean())
p_frac5 = float((mc_frac5 <= obs_frac5).mean())
p_frac8 = float((mc_frac8 <= obs_frac8).mean())
p_frac10 = float((mc_frac10 <= obs_frac10).mean())

print(f"\n{'='*70}")
print("LRD vs 60 節點 — 直接檢驗")
print(f"{'='*70}")
print(f"{'統計量':<15} {'觀測':>10} {'MC 期望':>10} {'p-value':>10}")
print(f"{'中位數距離':<15} {obs_med:>10.2f}° {mc_med.mean():>10.2f}° {p_med:>10.4f}")
print(f"{'<5° 比例':<15} {obs_frac5:>10.1f}% {mc_frac5.mean():>10.1f}% {p_frac5:>10.4f}")
print(f"{'<8° 比例':<15} {obs_frac8:>10.1f}% {mc_frac8.mean():>10.1f}% {p_frac8:>10.4f}")
print(f"{'<10° 比例':<15} {obs_frac10:>10.1f}% {mc_frac10.mean():>10.1f}% {p_frac10:>10.4f}")

# ============ 阻挫邊檢驗 ============
print(f"\n{'='*70}")
print("LRD vs 32 阻挫邊")
print(f"{'='*70}")

N_MC_EDGE = 500

def great_circle_dist_to_segment(ra, dec, ra1, dec1, ra2, dec2):
    ra, dec = np.radians(ra), np.radians(dec)
    ra1, dec1 = np.radians(ra1), np.radians(dec1)
    ra2, dec2 = np.radians(ra2), np.radians(dec2)
    v = np.array([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])
    v1 = np.array([np.cos(dec1)*np.cos(ra1), np.cos(dec1)*np.sin(ra1), np.sin(dec1)])
    v2 = np.array([np.cos(dec2)*np.cos(ra2), np.cos(dec2)*np.sin(ra2), np.sin(dec2)])
    n = np.cross(v1, v2); n /= np.linalg.norm(n)
    d = abs(np.arcsin(np.clip(np.dot(v, n), -1, 1)))
    t = np.dot(v - v1, v2 - v1) / np.dot(v2 - v1, v2 - v1)
    if t < 0 or t > 1:
        d = min(np.arccos(np.clip(np.dot(v, v1), -1, 1)),
                np.arccos(np.clip(np.dot(v, v2), -1, 1)))
    return np.degrees(d)

d_min_edge = np.zeros(N_lrd_local)
for i in range(N_lrd_local):
    d_min_edge[i] = min(great_circle_dist_to_segment(lr_ra[i], lr_dec[i], e[0], e[1], e[2], e[3]) for e in edges)

mc_edge_med = np.zeros(N_MC_EDGE)
mc_edge_frac3 = np.zeros(N_MC_EDGE)
for j in range(N_MC_EDGE):
    mc_ra = rng.uniform(ra_lo, ra_hi, N_lrd_local)
    mc_dec = rng.uniform(dec_lo, dec_hi, N_lrd_local)
    mc_d = np.zeros(N_lrd_local)
    for k in range(N_lrd_local):
        mc_d[k] = min(great_circle_dist_to_segment(mc_ra[k], mc_dec[k], e[0], e[1], e[2], e[3]) for e in edges)
    mc_edge_med[j] = np.median(mc_d)
    mc_edge_frac3[j] = (mc_d < 3).mean() * 100

obs_edge_med = np.median(d_min_edge)
obs_edge_frac3 = (d_min_edge < 3).mean() * 100
p_edge_med = float((mc_edge_med <= obs_edge_med).mean())
p_edge_frac3 = float((mc_edge_frac3 <= obs_edge_frac3).mean())

print(f"{'統計量':<15} {'觀測':>10} {'MC 期望':>10} {'p-value':>10}")
print(f"{'中位數距離':<15} {obs_edge_med:>10.2f}° {mc_edge_med.mean():>10.2f}° {p_edge_med:>10.4f}")
print(f"{'<3° 比例':<15} {obs_edge_frac3:>10.1f}% {mc_edge_frac3.mean():>10.1f}% {p_edge_frac3:>10.4f}")

# ============ 紅移依賴 ============
print(f"\n{'='*70}")
print("紅移依賴性 (z_qso_med)")
z = np.array(lr_z)
# 分高/低紅移
z_med = np.median(z)
mask_lo = z < z_med
mask_hi = z >= z_med
for label, mask in [("z < median", mask_lo), ("z ≥ median", mask_hi)]:
    d = d_min_node[mask]
    obs = np.median(d)
    mc = np.zeros(N_MC)
    N_sub = mask.sum()
    for j in range(N_MC):
        mc_ra = rng.uniform(ra_lo, ra_hi, N_sub)
        mc_dec = rng.uniform(dec_lo, dec_hi, N_sub)
        mc_d = np.array([min(ang_dist(mc_ra[k], mc_dec[k], n[0], n[1]) for n in nodes) for k in range(N_sub)])
        mc[j] = np.median(mc_d)
    p = float((mc <= obs).mean())
    print(f"  {label:20s} N={N_sub:4d}  median d={obs:.2f}° vs MC={mc.mean():.2f}°  p={p:.4f}")

# ============ 保存 ============
results = {
    "n_lrd": int(N_lrd),
    "field_deg2": float(area_pct*41253),
    "node_test": {
        "obs_median": float(obs_med), "mc_median": float(mc_med.mean()), "p_median": float(p_med),
        "obs_frac5": float(obs_frac5), "mc_frac5": float(mc_frac5.mean()), "p_frac5": float(p_frac5),
        "obs_frac8": float(obs_frac8), "mc_frac8": float(mc_frac8.mean()), "p_frac8": float(p_frac8),
        "obs_frac10": float(obs_frac10), "mc_frac10": float(mc_frac10.mean()), "p_frac10": float(p_frac10)
    },
    "edge_test": {
        "obs_median": float(obs_edge_med), "mc_median": float(mc_edge_med.mean()), "p_median": float(p_edge_med),
        "obs_frac3": float(obs_edge_frac3), "mc_frac3": float(mc_edge_frac3.mean()), "p_frac3": float(p_edge_frac3)
    }
}
os.makedirs(DATA_DIR, exist_ok=True)
with open(os.path.join(DATA_DIR, 'lrd_node_crosscheck.json'), 'w') as f:
    json.dump(results, f, indent=2)
print(f"\n已保存 data/lrd_node_crosscheck.json")