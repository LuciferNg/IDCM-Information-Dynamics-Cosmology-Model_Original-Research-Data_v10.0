#!/usr/bin/env python3
"""
O23 一次過推完: Cross-map 驗證 + 所有延伸問題
==============================================
1. SMICA / NILC / Commander 4.17° 節點溫度
2. 各地圖 sign matching rate
3. Cross-map 一致性
4. Spearman ρ 嘅跨地圖穩定性
5. 冷/熱 mean T 差異跨地圖
6. 個 coloring 到底 predict 乜?
"""
import numpy as np
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as u
from scipy import stats
import os, json

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh'
NODES_FILE = f'{BASE}/cmb_cold_spot/data/a5_nodes.txt'
SMOOTH_CACHE = f'{BASE}/o5_catalog_compare/data/smooth_cache'
OUTDIR = f'{BASE}/o23_zeroE_sign_match/results'

os.makedirs(OUTDIR, exist_ok=True)

# === Load A₅ node positions (ICRS RA, Dec) ===
nodes_radec = np.loadtxt(NODES_FILE)
node_ra = nodes_radec[:, 0]
node_dec = nodes_radec[:, 1]

# Convert to Galactic
sc = SkyCoord(ra=node_ra * u.deg, dec=node_dec * u.deg, frame='icrs')
gal = sc.galactic
node_l = gal.l.deg
node_b = gal.b.deg

# === Load node coloring (from O3) ===
# node_temps.txt has: idx color(cold=1) T_uK l_deg b_deg bfs_hop
node_data = np.loadtxt(f'{BASE}/o3_node_temperatures/data/node_temps.txt',
                       comments='#')
node_idx = node_data[:, 0].astype(int)
node_color = node_data[:, 1].astype(int)  # 1=cold(blue), 0=hot(red)
node_T_smica = node_data[:, 2]  # SMICA temperature
node_l_orig = node_data[:, 3]
node_b_orig = node_data[:, 4]

# Verify Galactic coordinates match
print("=" * 66)
print("O23: 一次過推完 — Cross-map 驗證")
print("=" * 66)

# === Load smoothed maps ===
maps = {
    'SMICA': f'{SMOOTH_CACHE}/smica2_smooth4.17.fits',
    'NILC': f'{SMOOTH_CACHE}/nilc2_smooth4.17.fits',
    'Commander': f'{SMOOTH_CACHE}/commander_smooth4.17.fits',
}

# === Extract node temperatures from each map ===
all_T = {}  # all_T[map_name] = array of 60 temperatures
for name, fpath in maps.items():
    m = hp.read_map(fpath)
    nside = hp.get_nside(m)
    pix = hp.ang2pix(nside, node_l, node_b, lonlat=True)
    T = m[pix] * 1e6  # convert to μK
    all_T[name] = T
    print(f"  {name}: nside={nside}, T range=[{T.min():.1f}, {T.max():.1f}] μK")

# === 1. Sign matching for each map ===
print(f"\n{'='*66}")
print("1. SIGN MATCHING RATE — 3 MAPS")
print(f"{'='*66}")

# Pre-compute: does the given T match the topological color?
def sign_match(T_arr, color_arr):
    """color=1 (cold) → match if T<0; color=0 (hot) → match if T>0"""
    match = np.zeros(len(T_arr), dtype=bool)
    cold_mask = color_arr == 1
    hot_mask = color_arr == 0
    match[cold_mask] = T_arr[cold_mask] < 0
    match[hot_mask] = T_arr[hot_mask] > 0
    return match

zeroE_nodes = {10, 12, 19, 22, 23, 25, 28, 32, 37, 40, 45, 46}
is_zeroE = np.array([i in zeroE_nodes for i in node_idx])

print(f"{'Map':<12} {'Overall':<12} {'ΔE=0':<12} {'Non-ΔE':<12} {'Cold':<10} {'Hot':<10}")
print("-" * 66)

match_results = {}
for name, T in all_T.items():
    match = sign_match(T, node_color)
    overall = match.mean() * 100
    zeroE = match[is_zeroE].mean() * 100
    nonE = match[~is_zeroE].mean() * 100
    cold = match[node_color == 1].mean() * 100
    hot = match[node_color == 0].mean() * 100
    match_results[name] = {
        'overall': overall, 'zeroE': zeroE, 'nonE': nonE,
        'cold': cold, 'hot': hot,
        'match_arr': match.tolist(),
        'T_arr': T.tolist()
    }
    print(f"{name:<12} {overall:<12.1f} {zeroE:<12.1f} {nonE:<12.1f} {cold:<10.1f} {hot:<10.1f}")

# === 2. Binomial test for each map ===
print(f"\n{'='*66}")
print("2. BINOMIAL TEST (overall vs 50%)")
print(f"{'='*66}")
for name, T in all_T.items():
    match = sign_match(T, node_color)
    n_match = match.sum()
    p = stats.binomtest(n_match, 60, 0.5).pvalue
    print(f"  {name}: {n_match}/60 = {n_match/60*100:.1f}%, p={p:.4f}")

# === 3. Spearman correlation: predicted sign vs T ===
# predicted sign: color=1 → -1 (cold), color=0 → +1 (hot)
print(f"\n{'='*66}")
print("3. SPEARMAN ρ — predicted sign × T")
print(f"{'='*66}")
pred_sign = np.where(node_color == 1, -1, 1)
for name, T in all_T.items():
    rho, p = stats.spearmanr(pred_sign, T)
    print(f"  {name}: ρ={rho:.4f}, p={p:.4f}")

# === 4. Cold/Hot mean T difference ===
print(f"\n{'='*66}")
print("4. COLD vs HOT mean T (μK)")
print(f"{'='*66}")
print(f"{'Map':<12} {'Cold mean':<12} {'Hot mean':<12} {'ΔT':<12} {'t-test p':<12}")
print("-" * 60)
for name, T in all_T.items():
    cold_T = T[node_color == 1]
    hot_T = T[node_color == 0]
    cold_m = cold_T.mean()
    hot_m = hot_T.mean()
    t_stat, p = stats.ttest_ind(cold_T, hot_T)
    print(f"{name:<12} {cold_m:<+12.2f} {hot_m:<+12.2f} {cold_m-hot_m:<+12.2f} {p:<12.4f}")

# === 5. Cross-map node-level temperature correlation ===
print(f"\n{'='*66}")
print("5. CROSS-MAP TEMPERATURE CORRELATION")
print(f"{'='*66}")
map_names = list(all_T.keys())
for i in range(len(map_names)):
    for j in range(i+1, len(map_names)):
        n1, n2 = map_names[i], map_names[j]
        r, p = stats.pearsonr(all_T[n1], all_T[n2])
        print(f"  {n1} × {n2}: r={r:.4f}, p={p:.4e}")

# === 6. Cross-map sign matching agreement ===
print(f"\n{'='*66}")
print("6. CROSS-MAP SIGN AGREEMENT (same node, same sign?)")
print(f"{'='*66}")
for i in range(len(map_names)):
    for j in range(i+1, len(map_names)):
        n1, n2 = map_names[i], map_names[j]
        s1 = np.sign(all_T[n1])
        s2 = np.sign(all_T[n2])
        agree = (s1 == s2).mean() * 100
        print(f"  {n1} × {n2}: sign agreement = {agree:.1f}%")

# === 7. The coloring question: what does the coloring represent? ===
print(f"\n{'='*66}")
print("7. COLORING QUESTION: 個 coloring predict 乜?")
print(f"{'='*66}")

# The topological coloring (blue=cold, red=hot) was assigned based on
# the Rhombicosidodecahedron frustration graph. The 20 triangles are cold
# (blue), the 30 squares are hot (red), plus 12 pentagons.
# 
# Let's check: is the coloring related to the topological structure
# (frustration edges, BFS distance) rather than temperature?

# Load BFS distances from node_temps.txt (6th column, index 5)
bfs_hop = node_data[:, 5].astype(int)  # BFS hop distance from cold spot

# Check: does color correlate with BFS hop?
print(f"  Color ~ BFS hop distance:")
for d in range(int(bfs_hop.min()), int(bfs_hop.max())+1):
    mask = bfs_hop == d
    ratio = node_color[mask].mean() * 100
    print(f"    BFS={d}: {mask.sum():2d} nodes, cold%={ratio:.0f}%")

# Check: does color relate to node type (triangle/square/pentagon)?
# From the Rhombicosidodecahedron A₅:
# 20 triangles = cold (blue), 30 squares = hot (red), 
# but the coloring was assigned differently...
# Actually, let me check the actual coloring pattern.

# The nodes are indexed 0-59. Let me check if the coloring follows
# a geometric pattern (e.g., alternating on the graph)
print(f"\n  Color pattern along node index:")
print(f"  Cold nodes (color=1): {np.where(node_color == 1)[0].tolist()}")
print(f"  Hot nodes (color=0): {np.where(node_color == 0)[0].tolist()}")

# Check bipartite-like property: are adjacent nodes (by BFS=1) opposite colors?
# Find nodes with BFS distance = 1 from cold spot
adjacent_to_0 = np.where(bfs_hop == 1)[0]
print(f"\n  Nodes adjacent to cold spot (BFS=1):")
print(f"    Indices: {adjacent_to_0.tolist()}")
print(f"    Colors: {node_color[adjacent_to_0].tolist()}")
print(f"    Cold spot (node 0) color: {node_color[0]}")

# === 8. Zero-energy node analysis across maps ===
print(f"\n{'='*66}")
print("8. ΔE=0 SIGN MATCHING ACROSS MAPS")
print(f"{'='*66}")
print(f"{'Map':<12} {'ΔE=0 match':<14} {'Non-ΔE match':<16} {'Diff':<10} {'Fisher p':<10}")
print("-" * 62)
for name, T in all_T.items():
    match = sign_match(T, node_color)
    z_match = match[is_zeroE].sum()
    z_total = is_zeroE.sum()
    nz_match = match[~is_zeroE].sum()
    nz_total = (~is_zeroE).sum()
    table = np.array([[z_match, z_total - z_match],
                      [nz_match, nz_total - nz_match]])
    or_val, p = stats.fisher_exact(table)
    print(f"{name:<12} {z_match/z_total*100:<14.1f} {nz_match/nz_total*100:<16.1f} "
          f"{z_match/z_total*100 - nz_match/nz_total*100:<+10.1f} {p:<10.4f}")

# === 9. Summary table ===
print(f"\n{'='*66}")
print("FINAL SUMMARY")
print(f"{'='*66}")
print(f"\n{'Metric':<35} {'SMICA':<12} {'NILC':<12} {'Commander':<12}")
print("-" * 71)
for name in map_names:
    T = all_T[name]
    match = sign_match(T, node_color)
    rho, p_rho = stats.spearmanr(pred_sign, T)
    cold_T = T[node_color == 1]
    hot_T = T[node_color == 0]
    _, p_ttest = stats.ttest_ind(cold_T, hot_T)
    
    # Only print once per metric
    if name == 'SMICA':
        print(f"{'Overall match rate (%)':<35} {match.mean()*100:<12.1f}", end='')
    elif name == 'NILC':
        print(f" {match.mean()*100:<12.1f}", end='')
    else:
        print(f" {match.mean()*100:<12.1f}")

    if name == 'SMICA':
        print(f"{'Spearman ρ (sign × T)':<35} {rho:<12.4f}", end='')
    elif name == 'NILC':
        print(f" {rho:<12.4f}", end='')
    else:
        print(f" {rho:<12.4f}")

    if name == 'SMICA':
        print(f"{'Spearman p-value':<35} {p_rho:<12.4f}", end='')
    elif name == 'NILC':
        print(f" {p_rho:<12.4f}", end='')
    else:
        print(f" {p_rho:<12.4f}")

    if name == 'SMICA':
        print(f"{'Cold-Hot ΔT (μK)':<35} {cold_T.mean()-hot_T.mean():<+12.2f}", end='')
    elif name == 'NILC':
        print(f" {cold_T.mean()-hot_T.mean():<+12.2f}", end='')
    else:
        print(f" {cold_T.mean()-hot_T.mean():<+12.2f}")

    if name == 'SMICA':
        print(f"{'t-test p (cold vs hot)':<35} {p_ttest:<12.4f}", end='')
    elif name == 'NILC':
        print(f" {p_ttest:<12.4f}", end='')
    else:
        print(f" {p_ttest:<12.4f}")

    if name == 'SMICA':
        print(f"{'Binom p (overall vs 50%)':<35} {stats.binomtest(match.sum(), 60, 0.5).pvalue:<12.4f}", end='')
    elif name == 'NILC':
        print(f" {stats.binomtest(match.sum(), 60, 0.5).pvalue:<12.4f}", end='')
    else:
        print(f" {stats.binomtest(match.sum(), 60, 0.5).pvalue:<12.4f}")

print(f"\n  Cross-map T correlation: SMICA×NILC r={stats.pearsonr(all_T['SMICA'], all_T['NILC'])[0]:.4f}, "
      f"SMICA×Commander r={stats.pearsonr(all_T['SMICA'], all_T['Commander'])[0]:.4f}")
print(f"  Cross-map sign agreement: SMICA×NILC {(np.sign(all_T['SMICA'])==np.sign(all_T['NILC'])).mean()*100:.1f}%, "
      f"SMICA×Commander {(np.sign(all_T['SMICA'])==np.sign(all_T['Commander'])).mean()*100:.1f}%")

# === Save results ===
output = {
    'match_rates': {name: match_results[name]['overall'] for name in map_names},
    'zeroE_match': {name: match_results[name]['zeroE'] for name in map_names},
    'spearman': {},
    'cross_map_corr': {},
    'cross_map_sign_agreement': {},
    'cold_hot_ttest': {},
    'coloring_pattern': {
        'cold_nodes': np.where(node_color == 1)[0].tolist(),
        'hot_nodes': np.where(node_color == 0)[0].tolist(),
        'bfs_by_color': {int(d): float(node_color[bfs_hop == d].mean() * 100)
                         for d in range(int(bfs_hop.min()), int(bfs_hop.max())+1)}
    }
}
for name, T in all_T.items():
    rho, p = stats.spearmanr(pred_sign, T)
    output['spearman'][name] = {'rho': float(rho), 'p': float(p)}
    cold_T = T[node_color == 1]
    hot_T = T[node_color == 0]
    t_stat, p_t = stats.ttest_ind(cold_T, hot_T)
    output['cold_hot_ttest'][name] = {'t': float(t_stat), 'p': float(p_t)}

for i in range(len(map_names)):
    for j in range(i+1, len(map_names)):
        n1, n2 = map_names[i], map_names[j]
        r, p = stats.pearsonr(all_T[n1], all_T[n2])
        output['cross_map_corr'][f'{n1}×{n2}'] = {'r': float(r), 'p': float(p)}
        agree = (np.sign(all_T[n1]) == np.sign(all_T[n2])).mean() * 100
        output['cross_map_sign_agreement'][f'{n1}×{n2}'] = float(agree)

with open(f'{OUTDIR}/cross_map_sign_analysis.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\n  Results saved to {OUTDIR}/cross_map_sign_analysis.json")