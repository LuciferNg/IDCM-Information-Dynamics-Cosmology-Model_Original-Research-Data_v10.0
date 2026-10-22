#!/usr/bin/env python3
"""
O23: ΔE=0 符號匹配率統計分析

Fisher exact, bootstrap, |T| stratification, logistic regression
"""
import numpy as np
from scipy import stats
from scipy.special import comb
import json

# === Load data ===
data = []
with open('../o3_node_temperatures/data/node_temps.txt') as f:
    for line in f:
        if line.strip().startswith('#') or not line.strip():
            continue
        parts = line.strip().split()
        idx = int(parts[0])
        color = int(parts[1])  # 1=cold(blue), 0=hot(red)
        T = float(parts[2])
        data.append({'idx': idx, 'color': color, 'T': T})

# ΔE=0 nodes
zeroE_nodes = {10, 12, 19, 22, 23, 25, 28, 32, 37, 40, 45, 46}

# === Compute matching ===
# cold=1 → matched if T < 0
# hot=0  → matched if T > 0
results = []
for d in data:
    if d['color'] == 1:  # predicted cold
        matched = d['T'] < 0
    else:  # predicted hot
        matched = d['T'] > 0
    is_zeroE = d['idx'] in zeroE_nodes
    results.append({
        'idx': d['idx'],
        'color': d['color'],
        'T': d['T'],
        'matched': matched,
        'is_zeroE': is_zeroE,
        'absT': abs(d['T'])
    })

# === 1. Contingency table ===
zeroE_match = sum(1 for r in results if r['is_zeroE'] and r['matched'])
zeroE_total = sum(1 for r in results if r['is_zeroE'])
nonE_match = sum(1 for r in results if not r['is_zeroE'] and r['matched'])
nonE_total = sum(1 for r in results if not r['is_zeroE'])

print("=" * 60)
print("O23: ΔE=0 符號匹配率統計分析")
print("=" * 60)

print(f"\nΔE=0 匹配: {zeroE_match}/{zeroE_total} = {zeroE_match/zeroE_total*100:.1f}%")
print(f"非 ΔE=0 匹配: {nonE_match}/{nonE_total} = {nonE_match/nonE_total*100:.1f}%")
print(f"整體匹配: {zeroE_match+nonE_match}/{zeroE_total+nonE_total} = {(zeroE_match+nonE_match)/(zeroE_total+nonE_total)*100:.1f}%")

# Contingency table: [[match, no_match], ...]
table = np.array([[zeroE_match, zeroE_total - zeroE_match],
                  [nonE_match, nonE_total - nonE_match]])
print(f"\n列聯表 (ΔE=0 × 匹配):")
print(f"  [[{table[0,0]}, {table[0,1]}],")
print(f"   [{table[1,0]}, {table[1,1]}]]")

# === Fisher exact test ===
odds_ratio, p_fisher = stats.fisher_exact(table)
print(f"\n--- Fisher Exact Test ---")
print(f"Odds ratio: {odds_ratio:.4f}")
print(f"p-value (one-sided): {p_fisher:.4f}")
print(f"Significant? {'YES' if p_fisher < 0.05 else 'NO'} (α=0.05)")

# === 2. Bootstrap permutation test ===
# Randomly sample 12 nodes from 60, measure match rate
np.random.seed(42)
n_bootstrap = 100000
all_matched = np.array([r['matched'] for r in results])
bootstrap_rates = np.zeros(n_bootstrap)

for i in range(n_bootstrap):
    sample = np.random.choice(all_matched, size=12, replace=False)
    bootstrap_rates[i] = sample.mean()

# P(rate >= 75%)
p_bootstrap = (bootstrap_rates >= 0.75).mean()
# Also the probability of >= 9 matches out of 12
# Hypergeometric: 37 matched in 60, draw 12 without replacement
M = 60  # population
K = sum(all_matched)  # successes in population
N = 12  # sample size
# P(X >= 9)
p_hyper = 0
for k in range(9, 13):
    p_hyper += comb(K, k) * comb(M-K, N-k) / comb(M, N)

print(f"\n--- Bootstrap Permutation Test (n={n_bootstrap}) ---")
print(f"隨機抽 12 節點匹配率 ≥75% 概率: {p_bootstrap:.6f}")
print(f"Hypergeometric P(X≥9): {p_hyper:.6f}")

# Expected match rate for random 12
print(f"隨機抽 12 平均匹配率: {bootstrap_rates.mean():.4f} ± {bootstrap_rates.std():.4f}")

# === 3. |T| stratification ===
print(f"\n--- |T| 分層分析 ---")

# Sort by |T| and split into 5 bins
absT = np.array([r['absT'] for r in results])
matched_arr = np.array([r['matched'] for r in results])
zeroE_arr = np.array([r['is_zeroE'] for r in results])

# Sort by absT
order = np.argsort(absT)
absT_sorted = absT[order]
matched_sorted = matched_arr[order]
zeroE_sorted = zeroE_arr[order]

# 5 bins of 12
n_bins = 5
bin_size = 12
print(f"{'Bin':<6} {'|T| range':<16} {'ΔE=0 count':<12} {'Match rate':<12} {'ΔE=0 match':<12} {'Non-ΔE0 match':<12}")
print("-" * 70)
for b in range(n_bins):
    start = b * bin_size
    end = start + bin_size
    bin_matched = matched_sorted[start:end]
    bin_zeroE = zeroE_sorted[start:end]
    t_range = f"{absT_sorted[start]:.1f}-{absT_sorted[end-1]:.1f}"
    z_count = bin_zeroE.sum()
    z_match = bin_matched[bin_zeroE].mean() if z_count > 0 else 0
    nz_match = bin_matched[~bin_zeroE].mean() if (~bin_zeroE).sum() > 0 else 0
    print(f"{b:<6} {t_range:<16} {z_count:<12} {bin_matched.mean()*100:<12.1f} {z_match*100:<12.1f} {nz_match*100:<12.1f}")

# === 4. Logistic regression: matched ~ absT + is_zeroE ===
from scipy.optimize import minimize

X = np.column_stack([
    np.ones(len(results)),
    absT / absT.std(),  # standardize
    zeroE_arr.astype(float)
])
y = matched_arr.astype(float)

def log_likelihood(beta, X, y):
    z = X @ beta
    p = 1 / (1 + np.exp(-z))
    p = np.clip(p, 1e-15, 1 - 1e-15)
    return -np.sum(y * np.log(p) + (1 - y) * np.log(1 - p))

result = minimize(log_likelihood, x0=[0, 0, 0], args=(X, y), method='Nelder-Mead')
beta = result.x

# Confidence via bootstrap of logistic
n_boot = 5000
beta_boot = np.zeros((n_boot, 3))
for i in range(n_boot):
    idx = np.random.choice(len(results), size=len(results), replace=True)
    Xb = X[idx]
    yb = y[idx]
    try:
        res = minimize(log_likelihood, x0=beta, args=(Xb, yb), method='Nelder-Mead')
        beta_boot[i] = res.x
    except:
        beta_boot[i] = np.nan

beta_boot = beta_boot[~np.isnan(beta_boot).any(axis=1)]
ci_low = np.percentile(beta_boot, 2.5, axis=0)
ci_high = np.percentile(beta_boot, 97.5, axis=0)

print(f"\n--- Logistic Regression: matched ~ |T| + is_zeroE ---")
print(f"β₀ (intercept): {beta[0]:.4f} [{ci_low[0]:.4f}, {ci_high[0]:.4f}]")
print(f"β₁ (|T|, std): {beta[1]:.4f} [{ci_low[1]:.4f}, {ci_high[1]:.4f}]")
print(f"β₂ (is_zeroE): {beta[2]:.4f} [{ci_low[2]:.4f}, {ci_high[2]:.4f}]")
print(f"zeroE effect significant? {'YES' if np.sign(ci_low[2]) == np.sign(ci_high[2]) else 'NO'} (CI excludes 0)")

# === 5. High-latitude 4 nodes ===
high_lat_nodes = [0, 4, 7, 31]  # |b| > 60
high_lat_results = [r for r in results if r['idx'] in high_lat_nodes]
hl_match = sum(1 for r in high_lat_results if r['matched'])
hl_total = len(high_lat_results)
hl_zeroE = sum(1 for r in high_lat_results if r['is_zeroE'])

print(f"\n--- 高緯度 4 節點 ({high_lat_nodes}) ---")
print(f"匹配: {hl_match}/{hl_total} = {hl_match/hl_total*100:.1f}%")
print(f"ΔE=0 節點數: {hl_zeroE}")

# === 6. Detailed listing ===
print(f"\n--- ΔE=0 節點詳情 ---")
print(f"{'Idx':<6} {'Color':<8} {'T_uK':<10} {'Match?':<8}")
for r in results:
    if r['is_zeroE']:
        color_str = '冷' if r['color'] == 1 else '熱'
        match_str = '✅' if r['matched'] else '❌'
        print(f"{r['idx']:<6} {color_str:<8} {r['T']:<10.3f} {match_str:<8}")

# === 7. Summary table ===
print(f"\n{'='*60}")
print("SUMMARY")
print(f"{'='*60}")
print(f"Fisher exact p: {p_fisher:.4f}")
print(f"Bootstrap P(≥75%): {p_bootstrap:.6f}")
print(f"Hypergeometric P(X≥9): {p_hyper:.6f}")
print(f"Logistic zeroE coefficient β₂: {beta[2]:.4f} [{ci_low[2]:.4f}, {ci_high[2]:.4f}]")
print(f"|T| stratification: ΔE=0 nodes concentrated in low-|T| bins?")
print(f"High-lat 4: {hl_match}/{hl_total}")

# Write results to file
output = {
    'zeroE_match': int(zeroE_match),
    'zeroE_total': int(zeroE_total),
    'nonE_match': int(nonE_match),
    'nonE_total': int(nonE_total),
    'fisher_p': float(p_fisher),
    'fisher_odds_ratio': float(odds_ratio),
    'bootstrap_p_ge75': float(p_bootstrap),
    'hypergeometric_p_ge9': float(p_hyper),
    'logistic_beta_zeroE': float(beta[2]),
    'logistic_ci_zeroE': [float(ci_low[2]), float(ci_high[2])],
    'high_lat_match': int(hl_match),
    'high_lat_total': int(hl_total),
    'significant': bool(p_fisher < 0.05)
}

with open('results/zeroE_sign_analysis.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to results/zeroE_sign_analysis.json")