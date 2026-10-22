#!/usr/bin/env python3
"""
O23 獨立驗證腳本: 從原始數據重新計算每個數字，核對報告文件
"""
import numpy as np
from scipy import stats
from scipy.special import comb
import json

print("=" * 66)
print("O23 獨立驗證: 從原始數據重新計算")
print("=" * 66)

# === 1. VERIFY RAW DATA ===
print("\n--- 1. 原始數據驗證 ---")
data = []
with open('../o3_node_temperatures/data/node_temps.txt') as f:
    for line in f:
        if line.strip().startswith('#') or not line.strip():
            continue
        parts = line.strip().split()
        data.append({
            'idx': int(parts[0]),
            'color': int(parts[1]),
            'T': float(parts[2]),
            'l': float(parts[3]),
            'b': float(parts[4]),
            'bfs': int(parts[5])
        })

print(f"  Total nodes loaded: {len(data)}")
assert len(data) == 60, f"Expected 60 nodes, got {len(data)}"
print(f"  ✅ 60 nodes loaded correctly")

# Check ΔE=0 nodes
zeroE_nodes = {10, 12, 19, 22, 23, 25, 28, 32, 37, 40, 45, 46}
zeroE_data = [d for d in data if d['idx'] in zeroE_nodes]
print(f"  ΔE=0 nodes: {len(zeroE_data)}/12")
assert len(zeroE_data) == 12, f"Expected 12 ΔE=0 nodes, got {len(zeroE_data)}"

# Verify each ΔE=0 node exists
for idx in sorted(zeroE_nodes):
    found = any(d['idx'] == idx for d in data)
    assert found, f"ΔE=0 node {idx} not found in data!"
print(f"  ✅ All 12 ΔE=0 nodes verified in data")

# === 2. VERIFY MATCHING COUNTS ===
print("\n--- 2. 匹配計數驗證 ---")
results = []
for d in data:
    if d['color'] == 1:
        matched = d['T'] < 0
    else:
        matched = d['T'] > 0
    is_zeroE = d['idx'] in zeroE_nodes
    results.append({
        'idx': d['idx'], 'color': d['color'], 'T': d['T'],
        'matched': matched, 'is_zeroE': is_zeroE, 'absT': abs(d['T'])
    })

zeroE_match = sum(1 for r in results if r['is_zeroE'] and r['matched'])
zeroE_total = sum(1 for r in results if r['is_zeroE'])
nonE_match = sum(1 for r in results if not r['is_zeroE'] and r['matched'])
nonE_total = sum(1 for r in results if not r['is_zeroE'])
total_match = zeroE_match + nonE_match

print(f"  ΔE=0 matched: {zeroE_match}/{zeroE_total} = {zeroE_match/zeroE_total*100:.1f}%")
print(f"  Non-ΔE=0 matched: {nonE_match}/{nonE_total} = {nonE_match/nonE_total*100:.1f}%")
print(f"  Overall matched: {total_match}/60 = {total_match/60*100:.1f}%")

# Verify against reported values
assert zeroE_match == 9, f"Expected 9 ΔE=0 matches, got {zeroE_match}"
assert zeroE_total == 12, f"Expected 12 ΔE=0 total, got {zeroE_total}"
assert nonE_match == 28, f"Expected 28 non-ΔE=0 matches, got {nonE_match}"
assert nonE_total == 48, f"Expected 48 non-ΔE=0 total, got {nonE_total}"
assert total_match == 37, f"Expected 37 total matches, got {total_match}"
print(f"  ✅ All match counts verified (9/12, 28/48, 37/60)")

# === 3. VERIFY FISHER EXACT ===
print("\n--- 3. Fisher Exact Test 驗證 ---")
table = np.array([[zeroE_match, zeroE_total - zeroE_match],
                  [nonE_match, nonE_total - nonE_match]])
or_val, p_fisher = stats.fisher_exact(table)
print(f"  Contingency table: [[{zeroE_match},{zeroE_total-zeroE_match}],[{nonE_match},{nonE_total-nonE_match}]]")
from math import comb as mcomb
print(f"  Odds ratio: {or_val:.4f}")
print(f"  p-value: {p_fisher:.4f}")

# Check: the reported p=0.3404 is from scipy's fisher_exact (two-sided)
# The two-sided p-value sums all tables with probability <= observed
# Let's verify: P(a) for a=0..12
print(f"  scipy fisher_exact p (two-sided): {p_fisher:.4f}")

# Verify the one-sided sum (for completeness)
p_one_sided = 0
for a in range(9, 13):
    p_one_sided += mcomb(12, a) * mcomb(48, 37-a) / mcomb(60, 37)
print(f"  Manual one-sided (P(X≥9)): {p_one_sided:.4f}")

# The two-sided p-value should be >= one-sided
assert p_fisher >= p_one_sided, f"Two-sided p ({p_fisher}) < one-sided ({p_one_sided})!"
print(f"  ✅ Fisher p={p_fisher:.4f} (two-sided) matches scipy output")

# === 4. VERIFY BINOMIAL TEST ===
print("\n--- 4. Binomial Test 驗證 ---")
p_binom = stats.binomtest(total_match, 60, 0.5).pvalue
print(f"  Overall {total_match}/60 vs 50%: p={p_binom:.4f}")
assert abs(p_binom - 0.0925) < 0.01, f"Binomial p mismatch: {p_binom} vs 0.0925"
print(f"  ✅ Binomial p={p_binom:.4f} verified")

# === 5. VERIFY SPEARMAN CORRELATION ===
print("\n--- 5. Spearman ρ 驗證 ---")
pred_sign = np.array([-1 if d['color'] == 1 else 1 for d in data])
T_vals = np.array([d['T'] for d in data])
rho, p_rho = stats.spearmanr(pred_sign, T_vals)
print(f"  ρ = {rho:.4f}, p = {p_rho:.4f}")
assert abs(rho - 0.2406) < 0.001, f"Spearman ρ mismatch: {rho} vs 0.2406"
assert abs(p_rho - 0.0641) < 0.01, f"Spearman p mismatch: {p_rho} vs 0.0641"
print(f"  ✅ Spearman ρ={rho:.4f}, p={p_rho:.4f} verified")

# === 6. VERIFY COLD/HOT T-TEST ===
print("\n--- 6. Cold/Hot t-test 驗證 ---")
cold_T = np.array([d['T'] for d in data if d['color'] == 1])
hot_T = np.array([d['T'] for d in data if d['color'] == 0])
print(f"  Cold: {len(cold_T)} nodes, mean={cold_T.mean():.2f}, std={cold_T.std():.2f}")
print(f"  Hot: {len(hot_T)} nodes, mean={hot_T.mean():.2f}, std={hot_T.std():.2f}")
t_stat, p_ttest = stats.ttest_ind(cold_T, hot_T)
print(f"  t = {t_stat:.4f}, p = {p_ttest:.4f}")
assert abs(t_stat - (-1.9126)) < 0.01, f"t-stat mismatch: {t_stat} vs -1.9126"
assert abs(p_ttest - 0.0607) < 0.01, f"t-test p mismatch: {p_ttest} vs 0.0607"
print(f"  ✅ t-test verified")

# === 7. VERIFY BFS COLORING PATTERN ===
print("\n--- 7. BFS Parity Coloring 驗證 ---")
bfs_vals = np.array([d['bfs'] for d in data])
colors = np.array([d['color'] for d in data])

print(f"  BFS coloring pattern:")
for d in range(9):
    mask = bfs_vals == d
    if mask.sum() > 0:
        cold_pct = colors[mask].mean() * 100
        expected = 100 if d % 2 == 0 else 0
        match = "✅" if abs(cold_pct - expected) < 0.1 else "❌"
        print(f"    BFS={d}: {mask.sum():2d} nodes, cold%={cold_pct:.0f}% (expected {expected}%) {match}")
        assert abs(cold_pct - expected) < 0.1, f"BFS={d} coloring mismatch"

print(f"  ✅ BFS parity coloring 100% verified")

# === 8. VERIFY HIGH-LATITUDE NODES ===
print("\n--- 8. 高緯度 4 節點驗證 ---")
high_lat = [0, 4, 7, 31]
hl_data = [d for d in data if d['idx'] in high_lat]
print(f"  High-lat nodes: {[(d['idx'], d['color'], d['T'], d['b']) for d in hl_data]}")
hl_match_count = sum(1 for r in results if r['idx'] in high_lat and r['matched'])
hl_zeroE_count = sum(1 for r in results if r['idx'] in high_lat and r['is_zeroE'])
print(f"  Match: {hl_match_count}/{len(high_lat)} = {hl_match_count/len(high_lat)*100:.0f}%")
print(f"  ΔE=0 count: {hl_zeroE_count}")
assert hl_match_count == 3, f"Expected 3 high-lat matches, got {hl_match_count}"
assert hl_zeroE_count == 0, f"Expected 0 high-lat ΔE=0, got {hl_zeroE_count}"
print(f"  ✅ High-lat 4 verified (3/4, 0 ΔE=0)")

# === 9. VERIFY COLD/HOT NODE COUNTS ===
print("\n--- 9. Cold/Hot Node Counts 驗證 ---")
cold_count = sum(1 for d in data if d['color'] == 1)
hot_count = sum(1 for d in data if d['color'] == 0)
print(f"  Cold nodes: {cold_count}, Hot nodes: {hot_count}")
assert cold_count == 30, f"Expected 30 cold nodes, got {cold_count}"
assert hot_count == 30, f"Expected 30 hot nodes, got {hot_count}"
print(f"  ✅ 30/30 split verified")

# === 10. VERIFY ΔE=0 NODE COLORS AND TEMPS ===
print("\n--- 10. ΔE=0 節點詳情驗證 ---")
print(f"  {'Idx':<6} {'Color':<8} {'T_uK':<10} {'Match?':<8} {'BFS':<6}")
for r in results:
    if r['is_zeroE']:
        color_str = '冷' if r['color'] == 1 else '熱'
        match_str = '✅' if r['matched'] else '❌'
        bfs = next(d['bfs'] for d in data if d['idx'] == r['idx'])
        print(f"  {r['idx']:<6} {color_str:<8} {r['T']:<10.3f} {match_str:<8} {bfs:<6}")

# Verify the 3 mismatches
zeroE_mismatches = [r for r in results if r['is_zeroE'] and not r['matched']]
print(f"\n  ΔE=0 mismatches: {[r['idx'] for r in zeroE_mismatches]}")
assert [r['idx'] for r in zeroE_mismatches] == [10, 28, 46], f"Wrong mismatches: {[r['idx'] for r in zeroE_mismatches]}"
print(f"  ✅ ΔE=0 mismatches verified (indices 10, 28, 46)")

# === 11. VERIFY POWER ANALYSIS ===
print("\n--- 11. Power Analysis 驗證 ---")
import math
p1, p2 = 0.75, 0.583
p_bar = (p1 + p2) / 2
z_alpha = 1.96
z_beta = 0.84
n_needed = ((z_alpha * math.sqrt(2 * p_bar * (1-p_bar)) + 
             z_beta * math.sqrt(p1*(1-p1) + p2*(1-p2))) / (p1 - p2))**2
print(f"  Sample size needed per group: ~{n_needed:.0f}")
print(f"  Total nodes needed: ~{n_needed*2:.0f}")
assert abs(n_needed - 124) < 5, f"Power analysis mismatch: {n_needed} vs ~124"
print(f"  ✅ Power analysis verified (~124 per group)")

# === 12. VERIFY CROSS-MAP RESULTS FROM JSON ===
print("\n--- 12. Cross-map JSON 結果驗證 ---")
with open('results/cross_map_sign_analysis.json') as f:
    cm = json.load(f)

# Check json matches reported values
assert abs(cm['match_rates']['SMICA'] - 61.6667) < 0.01
assert abs(cm['match_rates']['NILC'] - 63.3333) < 0.01
assert abs(cm['match_rates']['Commander'] - 61.6667) < 0.01
assert abs(cm['zeroE_match']['SMICA'] - 75.0) < 0.01
assert abs(cm['zeroE_match']['NILC'] - 75.0) < 0.01
assert abs(cm['zeroE_match']['Commander'] - 75.0) < 0.01
assert abs(cm['spearman']['SMICA']['rho'] - 0.2406) < 0.001
assert abs(cm['spearman']['NILC']['rho'] - 0.2425) < 0.001
assert abs(cm['spearman']['Commander']['rho'] - 0.2406) < 0.001
assert abs(cm['cross_map_corr']['SMICA×NILC']['r'] - 0.9993) < 0.001
assert abs(cm['cross_map_corr']['SMICA×Commander']['r'] - 0.9975) < 0.001
assert abs(cm['cross_map_sign_agreement']['SMICA×NILC'] - 98.3333) < 0.01
assert abs(cm['cross_map_sign_agreement']['SMICA×Commander'] - 100.0) < 0.01
print(f"  ✅ Cross-map JSON values verified")

# === 13. VERIFY zeroE SIGN ANALYSIS JSON ===
print("\n--- 13. zeroE JSON 結果驗證 ---")
with open('results/zeroE_sign_analysis.json') as f:
    ze = json.load(f)

assert ze['zeroE_match'] == 9
assert ze['zeroE_total'] == 12
assert ze['nonE_match'] == 28
assert ze['nonE_total'] == 48
assert abs(ze['fisher_p'] - 0.3404) < 0.01
assert abs(ze['fisher_odds_ratio'] - 2.1429) < 0.01
assert abs(ze['bootstrap_p_ge75'] - 0.2358) < 0.01
assert abs(ze['hypergeometric_p_ge9'] - 0.2358) < 0.01
assert ze['significant'] == False
assert ze['high_lat_match'] == 3
assert ze['high_lat_total'] == 4
print(f"  ✅ zeroE JSON values verified")

# === FINAL SUMMARY ===
all_checks = [
    ("Raw data (60 nodes, 12 ΔE=0)", True),
    ("Match counts (9/12, 28/48, 37/60)", True),
    ("Fisher exact (p=0.34)", abs(p_fisher - 0.3404) < 0.01),
    ("Binomial test (p=0.09)", abs(p_binom - 0.0925) < 0.01),
    ("Spearman ρ (ρ=0.24, p=0.06)", abs(rho - 0.2406) < 0.001),
    ("Cold/Hot t-test (p=0.06)", abs(p_ttest - 0.0607) < 0.01),
    ("BFS parity coloring (100% pattern)", True),
    ("High-lat 4 (3/4, 0 ΔE=0)", True),
    ("Cold/Hot split (30/30)", True),
    ("ΔE=0 mismatches (10, 28, 46)", True),
    ("Power analysis (~124/group)", abs(n_needed - 124) < 5),
    ("Cross-map JSON values", True),
    ("zeroE JSON values", True),
]

print(f"\n{'='*66}")
print("VERIFICATION SUMMARY")
print(f"{'='*66}")
all_pass = True
for name, passed in all_checks:
    status = "✅" if passed else "❌"
    if not passed:
        all_pass = False
    print(f"  {status} {name}")

print(f"\n{'='*66}")
if all_pass:
    print("🎉 ALL 13 CHECKS PASSED — 所有數字正確無誤!")
else:
    print("⚠️  SOME CHECKS FAILED — 需要修正!")
print(f"{'='*66}")