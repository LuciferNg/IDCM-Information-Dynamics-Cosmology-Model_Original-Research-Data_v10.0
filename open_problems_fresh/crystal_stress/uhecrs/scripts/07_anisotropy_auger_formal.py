#!/usr/bin/env python3
"""
UHECR 各向異性正式檢驗 — 能量分層 + 阻挫邊大圓距離
=====================================================
數據: opendata.auger.org catalog/list/auger_catalogSD.csv (109 events, E≥46 EeV)

要點:
  1. 全樣本 (109 事件) — 係預期之中最低能量稀釋訊號
  2. 能量分層 (E>130, E>150 EeV) — 高能量事件嘅訊號應更強
  3. 阻挫邊距離用大圓垂直距離 (唔係端點距離)
"""
import math, os, json, csv
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'data')
CMB_DATA = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/cmb_cold_spot/data'

def load_pts(path):
    pts = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            p = line.split()
            pts.append((float(p[0]), float(p[1])))
    return np.array(pts)

# 60 節點
nodes = load_pts(os.path.join(CMB_DATA, 'a5_nodes.txt'))

# 阻挫邊: 32 條邊, 每條兩端點 (RA_u, Dec_u, RA_v, Dec_v)
edge_pairs = []  # list of ((ra1,dec1), (ra2,dec2))
with open(os.path.join(CMB_DATA, 'frustration_edges.txt')) as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        p = line.split()
        edge_pairs.append(((float(p[4]), float(p[5])), (float(p[6]), float(p[7]))))

# Auger 事件
ev_ra, ev_dec, ev_E, ev_id = [], [], [], []
with open(os.path.join(DATA, 'auger_catalogSD.csv')) as f:
    reader = csv.DictReader(f)
    for row in reader:
        ev_ra.append(float(row['ra']))
        ev_dec.append(float(row['dec']))
        ev_E.append(float(row['energy']))
        ev_id.append(row['id'])
ev_ra = np.array(ev_ra); ev_dec = np.array(ev_dec); ev_E = np.array(ev_E)
N_ev = len(ev_ra)

def ang_dist_mat(ra1, dec1, ra2, dec2):
    ra1, dec1 = np.radians(ra1), np.radians(dec1)
    ra2, dec2 = np.radians(ra2), np.radians(dec2)
    cosd = np.sin(dec1)[:, None]*np.sin(dec2)[None, :] + \
           np.cos(dec1)[:, None]*np.cos(dec2)[None, :]*np.cos(ra1[:, None]-ra2[None, :])
    return np.degrees(np.arccos(np.clip(cosd, -1, 1)))

# 節點距離
D_node = ang_dist_mat(ev_ra, ev_dec, nodes[:, 0], nodes[:, 1])
d_node_min = D_node.min(axis=1)

# 阻挫邊大圓垂直距離
def great_circle_dist_to_segment(ra, dec, ra1, dec1, ra2, dec2):
    """事件到邊嘅大圓垂直距離 (向量化, 支援 scalar 同 array)"""
    ra, dec = np.asarray(ra), np.asarray(dec)
    ra1, dec1 = np.asarray(ra1), np.asarray(dec1)
    ra2, dec2 = np.asarray(ra2), np.asarray(dec2)
    
    ra, dec = np.radians(ra), np.radians(dec)
    ra1, dec1 = np.radians(ra1), np.radians(dec1)
    ra2, dec2 = np.radians(ra2), np.radians(dec2)
    
    cos_c = np.sin(dec1)*np.sin(dec2) + np.cos(dec1)*np.cos(dec2)*np.cos(ra1-ra2)
    c = np.arccos(np.clip(cos_c, -1, 1))
    
    cos_a = np.sin(dec1)*np.sin(dec) + np.cos(dec1)*np.cos(dec)*np.cos(ra1-ra)
    cos_b = np.sin(dec2)*np.sin(dec) + np.cos(dec2)*np.cos(dec)*np.cos(ra2-ra)
    a = np.arccos(np.clip(cos_a, -1, 1))
    b = np.arccos(np.clip(cos_b, -1, 1))
    
    cos_A = np.clip((cos_a - cos_b*cos_c) / (np.sin(b)*np.sin(c) + 1e-15), -1, 1)
    cos_B = np.clip((cos_b - cos_a*cos_c) / (np.sin(a)*np.sin(c) + 1e-15), -1, 1)
    
    h1 = np.arcsin(np.clip(np.sin(a) * np.sqrt(1-cos_A**2), -1, 1))
    h2 = np.arcsin(np.clip(np.sin(b) * np.sqrt(1-cos_B**2), -1, 1))
    h = (h1 + h2) / 2
    
    outside = (cos_A < 0) | (cos_B < 0)
    h = np.where(outside, np.minimum(a, b), h)
    
    return np.degrees(h)

# 改: 向量化邊距離
N_edges = len(edge_pairs)
d_edge_min = np.full(N_ev, 1e10)
for i, ((r1,d1), (r2,d2)) in enumerate(edge_pairs):
    d = great_circle_dist_to_segment(ev_ra, ev_dec, r1, d1, r2, d2)
    d_edge_min = np.minimum(d_edge_min, d)

print(f"載入: {len(nodes)} 節點, {N_edges} 阻挫邊, {N_ev} Auger 事件")
print(f"最近節點距離: 中位數 {np.median(d_node_min):.2f}°, 平均 {np.mean(d_node_min):.2f}°, 最小 {d_node_min.min():.2f}°")
print(f"最近邊距離:   中位數 {np.median(d_edge_min):.2f}°, 平均 {np.mean(d_edge_min):.2f}°")

# ============ 能量分層各向異性 ============
print(f"\n{'='*70}")
print("能量分層各向異性檢驗")
print(f"{'='*70}")

rng = np.random.default_rng(42)
N_MC = 5000  # 每能量層

for E_cut in [46, 100, 130, 150, 160]:
    mask = ev_E >= E_cut
    N_sub = mask.sum()
    if N_sub < 3: continue
    sub_d = d_node_min[mask]
    
    for r in [8, 10]:
        obs = (sub_d < r).sum()
        # MC
        mc = np.zeros(N_MC, dtype=int)
        for i in range(N_MC):
            ra_rand = rng.uniform(0, 360, N_sub)
            D = ang_dist_mat(ra_rand, ev_dec[mask], nodes[:, 0], nodes[:, 1])
            mc[i] = (D.min(axis=1) < r).sum()
        p = (mc >= obs).mean()
        sig = "🟢" if p < 0.05 else ("🟡" if p < 0.15 else "  ")
        print(f"  E≥{E_cut:>3} EeV ({N_sub:>3} ev): 節點<{r:>2}°: {obs:>3}/{N_sub} ({obs/N_sub*100:>5.1f}%)  MC={mc.mean():.1f}±{mc.std():.1f}  p={p:.4f} {sig}")

# ============ 最高能量事件詳細 ============
print(f"\n{'='*70}")
print("最高能量事件 (E>130 EeV) vs 節點/邊詳細")
print(f"{'='*70}")
order = np.argsort(-ev_E)
for i in order:
    if ev_E[i] < 130: break
    d_e = [great_circle_dist_to_segment(ev_ra[i], ev_dec[i], e[0][0], e[0][1], e[1][0], e[1][1]) 
           for e in edge_pairs]
    d_edge_best = min(d_e)
    print(f"  {ev_id[i]:<12} E={ev_E[i]:5.0f} EeV  RA={ev_ra[i]:6.1f} Dec={ev_dec[i]:6.1f}  "
          f"Δ節點={d_node_min[i]:5.2f}°  Δ邊={d_edge_best:5.2f}°")

# ============ 詳細統計 ============
print(f"\n{'='*70}")
print("詳細統計")
print(f"{'='*70}")
d10 = np.percentile(d_node_min, 10)
d50 = np.median(d_node_min)
d90 = np.percentile(d_node_min, 90)
print(f"節點距離分佈: 10%={d10:.1f}°  50%={d50:.1f}°  90%={d90:.1f}°")
print(f"隨機期望:     10%={np.percentile([np.random.uniform(0,360)*0+0 for _ in range(10000)], 10):.1f}°  (圓盤分佈)")
# 隨機均勻分佈嘅最近節點距離中位數
rng2 = np.random.default_rng(42)
rand_dist = []
for _ in range(50000):
    ra_r = rng2.uniform(0, 360)
    dec_r = np.degrees(np.arcsin(rng2.uniform(-1, 1)))
    d = min(math.degrees(
        math.acos(max(-1, min(1, math.sin(math.radians(dec_r))*math.sin(math.radians(n[1])) + 
                math.cos(math.radians(dec_r))*math.cos(math.radians(n[1]))*math.cos(math.radians(ra_r-n[0]))))))
        for n in nodes)
    rand_dist.append(d)
print(f"天球均勻隨機: 最近節點中位數 = {np.median(rand_dist):.1f}°")

# ============ 能量分層結果收集 (用較少 MC 加速) ============
energy_layers = {}
for E_cut in [46, 100, 130, 150, 160]:
    mask = ev_E >= E_cut
    N_sub = int(mask.sum())
    if N_sub < 3: continue
    sub_d = d_node_min[mask]
    layer = {}
    for r in [8, 10]:
        obs = int((sub_d < r).sum())
        N_MC2 = 3000
        mc = np.zeros(N_MC2, dtype=int)
        for i in range(N_MC2):
            ra_rand = rng.uniform(0, 360, N_sub)
            D = ang_dist_mat(ra_rand, ev_dec[mask], nodes[:, 0], nodes[:, 1])
            mc[i] = (D.min(axis=1) < r).sum()
        p = float((mc >= obs).mean())
        layer[f"{r}deg"] = {
            "obs": obs, "n": N_sub, "obs_pct": obs/N_sub*100,
            "mc_mean": float(mc.mean()), "mc_std": float(mc.std()),
            "p_value": p
        }
    energy_layers[f"E>={E_cut}"] = layer

# ============ 保存 ============
results = {
    "n_events": N_ev,
    "energy_range_EeV": [float(ev_E.min()), float(ev_E.max())],
    "median_d_node": float(np.median(d_node_min)),
    "mean_d_node": float(np.mean(d_node_min)),
    "min_d_node": float(d_node_min.min()),
    "energy_layers": energy_layers,
    "top10": [
        {"id": ev_id[i], "E_EeV": float(ev_E[i]), "d_node": float(d_node_min[i]),
         "d_edge": float(min(great_circle_dist_to_segment(ev_ra[i], ev_dec[i], e[0][0], e[0][1], e[1][0], e[1][1]) for e in edge_pairs))}
        for i in order[:10]
    ],
    "note": "Auger Open Data catalogSD"
}
with open(os.path.join(DATA, 'anisotropy_auger_formal.json'), 'w') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\n已保存 data/anisotropy_auger_formal.json")