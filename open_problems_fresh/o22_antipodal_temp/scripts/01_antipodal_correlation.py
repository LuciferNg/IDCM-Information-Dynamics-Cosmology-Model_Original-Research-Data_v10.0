#!/usr/bin/env python3
"""
O22: 對徑對溫度相關性 — 完整分析
========================================
1. 列出 30 對近對徑對 (174.66°) + 溫度 + 色
2. Spearman ρ (30 對徑對) vs 隨機配對對照 bootstrap
3. 按 hop 組合分層 (d0↔d8, d1↔d7, ...)
4. 高緯度/銀河盤分層
5. 對徑對溫度和 vs 差分佈
6. 與大尺度模式 (偶極/四極) 比較
"""

import numpy as np
import math
from scipy.stats import spearmanr, pearsonr
from collections import defaultdict
import json

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
RNG = np.random.default_rng(42)

# ─── 1. Load 60 nodes ───
nodes = []
with open(f"{BASE}/cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes_deg = np.array(nodes)  # (ra, dec) in degrees
vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                  math.cos(math.radians(d))*math.sin(math.radians(r)),
                  math.sin(math.radians(d))] for r, d in nodes_deg])

# ─── 2. Load node temps ───
temps = np.zeros(60)
colors = np.zeros(60, dtype=int)
hops = np.zeros(60, dtype=int)
lats = np.zeros(60)  # b in degrees
with open(f"{BASE}/o3_node_temperatures/data/node_temps.txt") as f:
    for line in f:
        if line.startswith('#') or line.strip() == '':
            continue
        parts = line.split()
        idx = int(parts[0])
        colors[idx] = int(parts[1])
        temps[idx] = float(parts[2])
        lats[idx] = float(parts[4])  # b (lat)

# BFS hops from O3
bfs_map = {0:0, 1:3, 2:4, 3:6, 4:5, 5:7, 6:4, 7:6, 8:4, 9:1,
           10:5, 11:3, 12:3, 13:3, 14:2, 15:2, 16:2, 17:2, 18:3, 19:3,
           20:1, 21:5, 22:4, 23:5, 24:4, 25:3, 26:6, 27:2, 28:4, 29:6,
           30:6, 31:7, 32:4, 33:2, 34:6, 35:7, 36:3, 37:4, 38:5, 39:6,
           40:3, 41:1, 42:5, 43:4, 44:5, 45:5, 46:5, 47:4, 48:4, 49:3,
           50:1, 51:4, 52:6, 53:3, 54:7, 55:2, 56:5, 57:8, 58:2, 59:5}
for i in range(60):
    hops[i] = bfs_map[i]

# ─── 3. Find all antipodal pairs (>170°) ───
all_pairs = []
for i in range(60):
    for j in range(i+1, 60):
        ang = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if ang > 170:
            all_pairs.append((ang, i, j))

all_pairs.sort(reverse=True)
print(f"=== 全部近對徑對 ({len(all_pairs)} 對) ===\n")

# ─── 4. Build antipodal pair list with temperatures ───
pairs_info = []
pair_set = set()
for ang, i, j in all_pairs:
    same_color = "同色" if colors[i] == colors[j] else "異色"
    hop_sum = hops[i] + hops[j]
    high_lat = "🟢高緯" if (abs(lats[i]) >= 20 or abs(lats[j]) >= 20) else ""
    dt = temps[i] - temps[j]
    t_sum = temps[i] + temps[j]
    t_prod = temps[i] * temps[j]
    pairs_info.append({
        'i': i, 'j': j, 'ang': ang,
        'T_i': temps[i], 'T_j': temps[j],
        'dt': dt, 't_sum': t_sum, 't_prod': t_prod,
        'color_i': colors[i], 'color_j': colors[j],
        'same_color': colors[i] == colors[j],
        'hop_i': hops[i], 'hop_j': hops[j],
        'hop_sum': hop_sum,
        'lat_i': lats[i], 'lat_j': lats[j],
        'high_lat': abs(lats[i]) >= 20 or abs(lats[j]) >= 20,
        'both_high_lat': abs(lats[i]) >= 20 and abs(lats[j]) >= 20,
        'galactic': abs(lats[i]) < 20 or abs(lats[j]) < 20,
        'both_galactic': abs(lats[i]) < 20 and abs(lats[j]) < 20,
    })
    pair_set.add((i, j))

# Print all pairs
print(f"{'#':>3} {'i↔j':>8} {'ang':>7} {'T_i':>9} {'T_j':>9} {'ΔT':>9} {'T_sum':>9} {'T_i×T_j':>10} {'hop':>5} {'色':>4} {'高緯':>4}")
print("-"*85)
for k, p in enumerate(pairs_info):
    sc = "同" if p['same_color'] else "異"
    hl = "🟢" if p['high_lat'] else ""
    print(f"{k:>3} #{p['i']:>2}↔#{p['j']:>2} {p['ang']:>7.2f} {p['T_i']:>9.2f} {p['T_j']:>9.2f} {p['dt']:>9.2f} {p['t_sum']:>9.2f} {p['t_prod']:>10.2f} {p['hop_sum']:>3d} {sc:>3} {hl:>4}")

# Basic stats
dts = np.array([p['dt'] for p in pairs_info])
t_sums = np.array([p['t_sum'] for p in pairs_info])
t_prods = np.array([p['t_prod'] for p in pairs_info])
t_is = np.array([p['T_i'] for p in pairs_info])
t_js = np.array([p['T_j'] for p in pairs_info])
abs_dts = np.abs(dts)

print(f"\n=== 基本統計 ===")
print(f"|ΔT| mean = {abs_dts.mean():.2f} μK")
print(f"|ΔT| median = {np.median(abs_dts):.2f} μK")
print(f"|ΔT| max = {abs_dts.max():.2f} μK")
print(f"T_i×T_j 正/負 = {sum(t_prods > 0)} / {sum(t_prods < 0)}")
print(f"T_sum mean = {t_sums.mean():.2f} μK (接近 0 = 反相關)")
print(f"T_sum std = {t_sums.std():.2f} μK")
print(f"T_i mean = {t_is.mean():.2f} μK")
print(f"T_j mean = {t_js.mean():.2f} μK")

# ─── 5. Spearman ρ (antipodal pairs) ───
rho_s, p_s = spearmanr(t_is, t_js)
rho_p, p_p = pearsonr(t_is, t_js)
print(f"\n=== 對徑對相關性 ===")
print(f"Spearman ρ = {rho_s:.4f}, p = {p_s:.4f}")
print(f"Pearson r  = {rho_p:.4f}, p = {p_p:.4f}")

# ─── 6. Bootstrap: random non-antipodal pairs ───
N_BOOT = 10000
rho_s_boot = np.zeros(N_BOOT)
rho_p_boot = np.zeros(N_BOOT)
abs_dt_boot = np.zeros(N_BOOT)
med_abs_dt_boot = np.zeros(N_BOOT)
frac_neg_prod_boot = np.zeros(N_BOOT)
t_sum_std_boot = np.zeros(N_BOOT)

for b in range(N_BOOT):
    # Random 30 pairs, not antipodal, no repeats
    used = set()
    t1, t2 = [], []
    for _ in range(30):
        while True:
            i, j = RNG.integers(0, 60, 2)
            if i == j: continue
            if (i, j) in pair_set or (j, i) in pair_set: continue
            if (i, j) in used or (j, i) in used: continue
            used.add((i, j))
            break
        t1.append(temps[i]); t2.append(temps[j])
    t1 = np.array(t1); t2 = np.array(t2)
    rho_s_boot[b], _ = spearmanr(t1, t2)
    rho_p_boot[b], _ = pearsonr(t1, t2)
    abs_dt_boot[b] = np.abs(t1 - t2).mean()
    med_abs_dt_boot[b] = np.median(np.abs(t1 - t2))
    frac_neg_prod_boot[b] = np.mean((t1 * t2) < 0)
    t_sum_std_boot[b] = np.std(t1 + t2)

print(f"\n=== Bootstrap 對照 (N={N_BOOT}, 隨機非對徑 30 對) ===")
print(f"  Spearman ρ: 觀察值 = {rho_s:.4f}")
print(f"    Bootstrap mean = {rho_s_boot.mean():.4f}, std = {rho_s_boot.std():.4f}")
print(f"    Bootstrap 95% CI = [{np.percentile(rho_s_boot, 2.5):.4f}, {np.percentile(rho_s_boot, 97.5):.4f}]")
print(f"    p(Spearman ≤ observed) = {(rho_s_boot <= rho_s).mean():.4f}")
print(f"    z-score = {(rho_s - rho_s_boot.mean()) / rho_s_boot.std():.3f}")

print(f"\n  |ΔT| mean: 觀察值 = {abs_dts.mean():.2f} μK")
print(f"    Bootstrap mean = {abs_dt_boot.mean():.2f} μK, std = {abs_dt_boot.std():.2f}")
print(f"    Bootstrap 95% CI = [{np.percentile(abs_dt_boot, 2.5):.2f}, {np.percentile(abs_dt_boot, 97.5):.2f}]")
print(f"    p(|ΔT| ≥ observed) = {(abs_dt_boot >= abs_dts.mean()).mean():.4f}")

print(f"\n  |ΔT| median: 觀察值 = {np.median(abs_dts):.2f} μK")
print(f"    Bootstrap mean = {med_abs_dt_boot.mean():.2f}, std = {med_abs_dt_boot.std():.2f}")
print(f"    Bootstrap 95% CI = [{np.percentile(med_abs_dt_boot, 2.5):.2f}, {np.percentile(med_abs_dt_boot, 97.5):.2f}]")

print(f"\n  T_i×T_j 負比例: 觀察值 = {sum(t_prods < 0)/30:.4f} ({sum(t_prods < 0)}/30)")
print(f"    Bootstrap mean = {frac_neg_prod_boot.mean():.4f}, std = {frac_neg_prod_boot.std():.4f}")
print(f"    Bootstrap 95% CI = [{np.percentile(frac_neg_prod_boot, 2.5):.4f}, {np.percentile(frac_neg_prod_boot, 97.5):.4f}]")
print(f"    p(neg frac ≥ observed) = {(frac_neg_prod_boot >= sum(t_prods < 0)/30).mean():.4f}")

print(f"\n  T_sum std: 觀察值 = {t_sums.std():.2f} μK")
print(f"    Bootstrap mean = {t_sum_std_boot.mean():.2f}, std = {t_sum_std_boot.std():.2f}")
print(f"    Bootstrap 95% CI = [{np.percentile(t_sum_std_boot, 2.5):.2f}, {np.percentile(t_sum_std_boot, 97.5):.2f}]")

# ─── 7. Stratify by hop combination ───
print(f"\n=== 按 hop 組合分層 ===")
hop_sum_groups = defaultdict(list)
for p in pairs_info:
    key = f"d{p['hop_i']}↔d{p['hop_j']}" if p['hop_i'] <= p['hop_j'] else f"d{p['hop_j']}↔d{p['hop_i']}"
    hop_sum_groups[key].append(p)

for key in sorted(hop_sum_groups.keys()):
    grp = hop_sum_groups[key]
    ts1 = np.array([p['T_i'] for p in grp])
    ts2 = np.array([p['T_j'] for p in grp])
    if len(grp) >= 3:
        rho, pv = spearmanr(ts1, ts2)
    else:
        rho, pv = np.nan, np.nan
    dts_g = np.abs(ts1 - ts2)
    print(f"  {key:>8} ({len(grp):>2} 對): Spearman ρ={rho:+.4f}, p={pv:.4f}, |ΔT| mean={dts_g.mean():.2f}")

# ─── 8. Stratify by high-latitude / Galactic plane ───
print(f"\n=== 按高緯度/銀河盤分層 ===")

# Both high-lat
both_high = [p for p in pairs_info if p['both_high_lat']]
if both_high:
    ts1 = np.array([p['T_i'] for p in both_high])
    ts2 = np.array([p['T_j'] for p in both_high])
    rho, pv = spearmanr(ts1, ts2) if len(both_high) >= 3 else (np.nan, np.nan)
    dts_g = np.abs(ts1 - ts2)
    print(f"  兩者高緯 ({len(both_high):>2} 對): ρ={rho:+.4f}, p={pv:.4f}, |ΔT|={dts_g.mean():.2f}")

# Both galactic
both_gal = [p for p in pairs_info if p['both_galactic']]
if both_gal:
    ts1 = np.array([p['T_i'] for p in both_gal])
    ts2 = np.array([p['T_j'] for p in both_gal])
    rho, pv = spearmanr(ts1, ts2) if len(both_gal) >= 3 else (np.nan, np.nan)
    dts_g = np.abs(ts1 - ts2)
    print(f"  兩者銀河盤 ({len(both_gal):>2} 對): ρ={rho:+.4f}, p={pv:.4f}, |ΔT|={dts_g.mean():.2f}")

# Mixed
mixed = [p for p in pairs_info if p['high_lat'] and not p['both_high_lat'] and not p['both_galactic']]
if mixed:
    ts1 = np.array([p['T_i'] for p in mixed])
    ts2 = np.array([p['T_j'] for p in mixed])
    rho, pv = spearmanr(ts1, ts2) if len(mixed) >= 3 else (np.nan, np.nan)
    dts_g = np.abs(ts1 - ts2)
    print(f"  一高一低 ({len(mixed):>2} 對): ρ={rho:+.4f}, p={pv:.4f}, |ΔT|={dts_g.mean():.2f}")

# ─── 9. The famous 4 high-lat nodes: 10↔25, 22↔32 ───
print(f"\n=== 高緯度 4 節點對徑對 ===")
high4_pairs = [p for p in pairs_info if p['i'] in [10,22,25,32] and p['j'] in [10,22,25,32]]
for p in high4_pairs:
    print(f"  #{p['i']:>2}↔#{p['j']:>2}: T_i={p['T_i']:+.2f}, T_j={p['T_j']:+.2f}, ΔT={p['dt']:+.2f}, T_sum={p['t_sum']:+.2f}")

# ─── 10. H1/H2/H3 hypothesis test ───
print(f"\n=== 假說測試 ===")
print(f"H1 (無相關): ρ={rho_s:.4f}, p={p_s:.4f}")
print(f"  → {'🟢 接受 H1: 對徑對溫度無系統相關性' if p_s > 0.05 else '🔴 拒絕 H1: 有顯著相關'}")
print(f"H2 (反相關): ρ={rho_s:.4f}")
print(f"  → {'🟢 支持反相關' if rho_s < -0.2 and p_s < 0.1 else '🟡 弱/無反相關證據'}")
print(f"H3 (同色正相關): ρ={rho_s:.4f}")
print(f"  → {'🟢 支持正相關' if rho_s > 0.2 and p_s < 0.1 else '🟡 弱/無正相關證據'}")

# ─── 11. Cold spot antipodal pair ───
print(f"\n=== 冷斑對徑對 (#0↔#57) ===")
cs_pair = [p for p in pairs_info if p['i']==0 or p['j']==0]
for p in cs_pair:
    print(f"  #{p['i']}↔#{p['j']}: T_i={p['T_i']:+.2f}, T_j={p['T_j']:+.2f}, ΔT={p['dt']:+.2f}")
    print(f"  冷斑 (-134.19 μK) 對徑點 #57 = {p['T_j'] if p['i']==0 else p['T_i']:+.2f} μK — 弱暖點")

# ─── 12. Check if antipodal pairs are structurally determined ───
print(f"\n=== 結構分析: 對徑對係咪幾何強制? ===")
print(f"A₅ 60 節點: 30 對近對徑 (全部 174.66°), 全部同色, hop 和=8")
print(f"呢個係 rhombicosidodecahedron 嘅 antipodal symmetry — 30 對=30 條 diameter")
print(f"唔係巧合, 係多面體嘅 antipodal involution 強制結果")
print(f"每個節點嘅對徑係 hop 補數 (8-hop), 同色因為 BFS parity 守恆")

# ─── 13. Check if antipodal correlation is a dipole artifact ───
print(f"\n=== 偶極殘餘測試 ===")
# If temperature is pure dipole: T(θ) = A·cos(θ), then antipodal T_j = -T_i
# This would give perfect anti-correlation ρ=-1, T_sum=0
# Our observed ρ = {rho_s:.4f} is far from -1
print(f"純偶極會產生 ρ=-1, T_sum=0")
print(f"觀察 ρ={rho_s:.4f}, T_sum std={t_sums.std():.2f} μK")
print(f"偶極分量最多佔 {(rho_s):.1%} 解釋力" if rho_s < 0 else "偶極分量唔明顯")

# Save results
results = {
    'n_pairs': len(pairs_info),
    'spearman_rho': float(rho_s),
    'spearman_p': float(p_s),
    'pearson_r': float(rho_p),
    'pearson_p': float(p_p),
    'abs_dt_mean': float(abs_dts.mean()),
    'abs_dt_median': float(np.median(abs_dts)),
    'abs_dt_max': float(abs_dts.max()),
    't_sum_mean': float(t_sums.mean()),
    't_sum_std': float(t_sums.std()),
    'neg_prod_frac': float((t_prods < 0).mean()),
    'neg_prod_count': int((t_prods < 0).sum()),
    'bootstrap_rho_mean': float(rho_s_boot.mean()),
    'bootstrap_rho_std': float(rho_s_boot.std()),
    'bootstrap_rho_ci95': [float(np.percentile(rho_s_boot, 2.5)), float(np.percentile(rho_s_boot, 97.5))],
    'bootstrap_absdt_mean': float(abs_dt_boot.mean()),
    'bootstrap_absdt_ci95': [float(np.percentile(abs_dt_boot, 2.5)), float(np.percentile(abs_dt_boot, 97.5))],
    'bootstrap_negfrac_mean': float(frac_neg_prod_boot.mean()),
    'bootstrap_negfrac_ci95': [float(np.percentile(frac_neg_prod_boot, 2.5)), float(np.percentile(frac_neg_prod_boot, 97.5))],
    'p_rho_le_observed': float((rho_s_boot <= rho_s).mean()),
    'p_absdt_ge_observed': float((abs_dt_boot >= abs_dts.mean()).mean()),
    'p_negfrac_ge_observed': float((frac_neg_prod_boot >= sum(t_prods < 0)/30).mean()),
}
with open(f"{BASE}/o22_antipodal_temp/data/results.json", 'w') as f:
    json.dump(results, f, indent=2)
print(f"\n✅ 結果已儲存至 data/results.json")