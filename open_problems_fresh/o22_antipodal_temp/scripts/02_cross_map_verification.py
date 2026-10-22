#!/usr/bin/env python3
"""
O22: 對徑對符號反轉 — 三地圖交叉驗證
==============================================
高緯 (|b|≥20°) ρ ≈ -0.27 vs 銀河盤 (|b|<20°) ρ ≈ +0.21
問題: 呢個符號反轉係 foreground 定係真實 CMB 結構?

方法: 用 SMICA / NILC / Commander 三幅地圖重做
- 如果符號反轉只喺 SMICA 出現 = foreground 污染
- 如果三幅地圖一致 = 真實 CMB 大尺度模式
"""

import numpy as np
import math
import healpy as hp
from scipy.stats import spearmanr
from collections import defaultdict
import json
import os

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
OUT = os.path.join(BASE, "o22_antipodal_temp")
RNG = np.random.default_rng(42)
FWHM_DEG = 4.17

# ─── 1. Load 60 nodes (geometry fixed) ───
nodes = []
with open(f"{BASE}/cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes_deg = np.array(nodes)
vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                  math.cos(math.radians(d))*math.sin(math.radians(r)),
                  math.sin(math.radians(d))] for r, d in nodes_deg])

# BFS + colors from existing data
temps_smica = np.zeros(60)
colors = np.zeros(60, dtype=int)
lats = np.zeros(60)
with open(f"{BASE}/o3_node_temperatures/data/node_temps.txt") as f:
    for line in f:
        if line.startswith('#') or line.strip() == '': continue
        parts = line.split()
        idx = int(parts[0])
        colors[idx] = int(parts[1])
        temps_smica[idx] = float(parts[2])
        lats[idx] = float(parts[4])

# ─── 2. Find antipodal pairs (fixed) ───
all_pairs = []
for i in range(60):
    for j in range(i+1, 60):
        ang = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if ang > 170:
            all_pairs.append((ang, i, j))
all_pairs.sort(reverse=True)

# ─── 3. Extract node temps from each map ───
from astropy.coordinates import SkyCoord
import astropy.units as u

maps = {
    'smica':    f'{BASE}/o5_catalog_compare/data/smooth_cache/smica2_smooth4.17.fits',
    'nilc':     f'{BASE}/o5_catalog_compare/data/smooth_cache/nilc2_smooth4.17.fits',
    'commander': f'{BASE}/o5_catalog_compare/data/smooth_cache/commander_smooth4.17.fits',
}

results = {}
for map_name, map_path in maps.items():
    print(f"\n{'='*60}")
    print(f"  {map_name.upper()} 地圖")
    print(f"{'='*60}")
    
    m = hp.read_map(map_path, field=0)
    nside = hp.get_nside(m)
    
    # Remove dipole if not already done
    if map_name != 'smica':  # SMICA already has dipole removed in O3
        m = hp.remove_dipole(m)
    
    # Extract node temps
    sc = SkyCoord(ra=nodes_deg[:, 0]*u.deg, dec=nodes_deg[:, 1]*u.deg, frame='icrs')
    gal = sc.galactic
    b_deg = gal.b.deg
    
    # Find matching NSIDE for pixel lookup
    pix = hp.ang2pix(nside, gal.l.deg, b_deg, lonlat=True)
    T_uK = m[pix] * 1e6
    
    # Build antipodal pair data
    Ts = []
    for ang, i, j in all_pairs:
        Ts.append({'i': i, 'j': j, 'T_i': T_uK[i], 'T_j': T_uK[j]})
    
    t_is = np.array([p['T_i'] for p in Ts])
    t_js = np.array([p['T_j'] for p in Ts])
    dts = t_is - t_js
    t_sums = t_is + t_js
    t_prods = t_is * t_js
    
    # Full correlation
    rho_s, p_s = spearmanr(t_is, t_js)
    print(f"  全部 30 對: ρ={rho_s:.4f}, p={p_s:.4f}")
    
    # High-lat vs Galactic
    high_lat_mask = np.array([abs(lats[p['i']]) >= 20 or abs(lats[p['j']]) >= 20 for p in Ts])
    gal_mask = ~high_lat_mask
    
    both_high_mask = np.array([abs(lats[p['i']]) >= 20 and abs(lats[p['j']]) >= 20 for p in Ts])
    both_gal_mask = np.array([abs(lats[p['i']]) < 20 and abs(lats[p['j']]) < 20 for p in Ts])
    mixed_mask = high_lat_mask & ~both_high_mask
    
    # By stratification
    for name, mask in [('高緯 (|b|≥20°)', both_high_mask), 
                       ('銀河盤 (|b|<20°)', both_gal_mask),
                       ('高緯-銀河盤混合', mixed_mask)]:
        n = mask.sum()
        if n >= 3:
            tr = spearmanr(t_is[mask], t_js[mask])
            print(f"    {name} ({n:>2} 對): ρ={tr[0]:+.4f}, p={tr[1]:.4f}, |ΔT|={np.abs(dts[mask]).mean():.2f}")
        else:
            print(f"    {name} ({n:>2} 對): 樣本太少")
    
    # By hop combination
    bfs_map = {0:0, 1:3, 2:4, 3:6, 4:5, 5:7, 6:4, 7:6, 8:4, 9:1,
               10:5, 11:3, 12:3, 13:3, 14:2, 15:2, 16:2, 17:2, 18:3, 19:3,
               20:1, 21:5, 22:4, 23:5, 24:4, 25:3, 26:6, 27:2, 28:4, 29:6,
               30:6, 31:7, 32:4, 33:2, 34:6, 35:7, 36:3, 37:4, 38:5, 39:6,
               40:3, 41:1, 42:5, 43:4, 44:5, 45:5, 46:5, 47:4, 48:4, 49:3,
               50:1, 51:4, 52:6, 53:3, 54:7, 55:2, 56:5, 57:8, 58:2, 59:5}
    hops = np.array([bfs_map[i] for i in range(60)])
    
    hop_groups = defaultdict(list)
    for p in Ts:
        hi, hj = hops[p['i']], hops[p['j']]
        key = f"d{min(hi,hj)}↔d{max(hi,hj)}"
        hop_groups[key].append(p)
    
    print(f"\n  按 hop 組合分層:")
    for key in sorted(hop_groups.keys()):
        grp = hop_groups[key]
        g1 = np.array([p['T_i'] for p in grp])
        g2 = np.array([p['T_j'] for p in grp])
        if len(grp) >= 3:
            r, pv = spearmanr(g1, g2)
        else:
            r, pv = np.nan, np.nan
        print(f"    {key:>8} ({len(grp):>2} 對): ρ={r:+.4f}, |ΔT|={np.abs(g1-g2).mean():.2f}")
    
    # Bootstrap for lat-stratified
    for layer_name, layer_mask, n in [('高緯層', both_high_mask, both_high_mask.sum()),
                                       ('銀河盤層', both_gal_mask, both_gal_mask.sum())]:
        if n < 3: continue
        lat_constraint = lambda i, j: (abs(lats[i]) >= 20 and abs(lats[j]) >= 20) if layer_name == '高緯層' else (abs(lats[i]) < 20 and abs(lats[j]) < 20)
        rho_boot = np.zeros(5000)
        for b in range(5000):
            used = set()
            bt1, bt2 = [], []
            attempts = 0
            while len(bt1) < n and attempts < 5000:
                i, j = RNG.integers(0, 60, 2)
                if i == j: continue
                if (i, j) in used or (j, i) in used: continue
                if not lat_constraint(i, j): 
                    attempts += 1
                    continue
                used.add((i, j))
                bt1.append(T_uK[i]); bt2.append(T_uK[j])
            if len(bt1) >= 3:
                rho_boot[b], _ = spearmanr(bt1, bt2)
        obs_rho = spearmanr(t_is[layer_mask], t_js[layer_mask])[0]
        p_val = (rho_boot <= obs_rho).mean() if obs_rho < 0 else (rho_boot >= obs_rho).mean()
        print(f"\n    {layer_name} bootstrap: obs ρ={obs_rho:.4f}, boot mean={rho_boot.mean():.4f}, p={p_val:.4f}")
    
    results[map_name] = {
        'rho_total': float(rho_s),
        'p_total': float(p_s),
        'rho_high': float(spearmanr(t_is[both_high_mask], t_js[both_high_mask])[0]) if both_high_mask.sum() >= 3 else None,
        'rho_gal': float(spearmanr(t_is[both_gal_mask], t_js[both_gal_mask])[0]) if both_gal_mask.sum() >= 3 else None,
        'abs_dt_mean': float(np.abs(dts).mean()),
        'neg_prod_frac': float((t_prods < 0).mean()),
        't_sum_std': float(t_sums.std()),
        'n_high': int(both_high_mask.sum()),
        'n_gal': int(both_gal_mask.sum()),
    }

# ─── 4. Summary comparison ───
print(f"\n{'='*60}")
print(f"  三地圖對比總結")
print(f"{'='*60}")
print(f"{'地圖':>12} {'總ρ':>8} {'p':>6} {'高緯ρ':>8} {'銀河ρ':>8} {'|ΔT|':>8} {'T×T負':>8}")
print("-"*60)
for map_name in ['smica', 'nilc', 'commander']:
    r = results[map_name]
    rho_g = f"{r['rho_gal']:.3f}" if r['rho_gal'] is not None else "N/A"
    print(f"{map_name:>12} {r['rho_total']:>+8.3f} {r['p_total']:>6.3f} {r['rho_high']:>+8.3f} {rho_g:>8} {r['abs_dt_mean']:>8.1f} {r['neg_prod_frac']:>8.3f}")

# ─── 5. Check high-lat 4 nodes specifically ───
print(f"\n=== 高緯度 4 節點對徑對 (三地圖) ===")
high4 = [10, 22, 25, 32]
for map_name in ['smica', 'nilc', 'commander']:
    map_path = maps[map_name]
    m = hp.read_map(map_path, field=0)
    nside = hp.get_nside(m)
    if map_name != 'smica':
        m = hp.remove_dipole(m)
    sc = SkyCoord(ra=nodes_deg[:, 0]*u.deg, dec=nodes_deg[:, 1]*u.deg, frame='icrs')
    gal = sc.galactic
    pix = hp.ang2pix(nside, gal.l.deg, gal.b.deg, lonlat=True)
    T_uK = m[pix] * 1e6
    print(f"\n  {map_name}:")
    for p in [{'i':10,'j':25}, {'i':22,'j':32}]:
        ti = T_uK[p['i']]; tj = T_uK[p['j']]
        print(f"    #{p['i']}↔#{p['j']}: {ti:+.2f}, {tj:+.2f}, ΔT={ti-tj:+.2f}, T_sum={ti+tj:+.2f}")

# Save
with open(os.path.join(OUT, "data/cross_map_results.json"), 'w') as f:
    json.dump(results, f, indent=2)
print(f"\n✅ 結果已存至 data/cross_map_results.json")