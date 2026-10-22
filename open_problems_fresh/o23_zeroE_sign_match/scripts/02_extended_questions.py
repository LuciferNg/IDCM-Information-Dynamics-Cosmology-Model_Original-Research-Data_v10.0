#!/usr/bin/env python3
"""
O23 延伸問題: 閉合後嘅開放問題檢查
"""
import numpy as np
from scipy import stats
from scipy.special import comb

# === Load data ===
data = []
with open('../o3_node_temperatures/data/node_temps.txt') as f:
    for line in f:
        if line.strip().startswith('#') or not line.strip():
            continue
        parts = line.strip().split()
        idx = int(parts[0])
        color = int(parts[1])
        T = float(parts[2])
        data.append({'idx': idx, 'color': color, 'T': T})

zeroE_nodes = {10, 12, 19, 22, 23, 25, 28, 32, 37, 40, 45, 46}

# === Compute matching ===
results = []
for d in data:
    if d['color'] == 1:
        matched = d['T'] < 0
    else:
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

print("=" * 60)
print("O23 延伸問題檢查")
print("=" * 60)

# === Q1: 整體 61.7% vs 50% random? ===
total_match = sum(1 for r in results if r['matched'])
total_n = len(results)
# Binomial test: 37/60 vs p=0.5
p_binom = stats.binomtest(total_match, total_n, 0.5).pvalue
print(f"\n--- Q1: 整體匹配率 61.7% vs 50% random? ---")
print(f"匹配: {total_match}/{total_n} = {total_match/total_n*100:.1f}%")
print(f"Binomial test p = {p_binom:.4f}")
print(f"顯著? {'YES' if p_binom < 0.05 else 'NO'}")

# === Q2: 冷色/熱色分開睇 ===
# Cold nodes (color=1): matched if T<0
cold_match = sum(1 for r in results if r['color'] == 1 and r['matched'])
cold_total = sum(1 for r in results if r['color'] == 1)
hot_match = sum(1 for r in results if r['color'] == 0 and r['matched'])
hot_total = sum(1 for r in results if r['color'] == 0)

print(f"\n--- Q2: 冷色 vs 熱色分開睇 ---")
print(f"冷色 (color=1) 匹配: {cold_match}/{cold_total} = {cold_match/cold_total*100:.1f}%")
print(f"熱色 (color=0) 匹配: {hot_match}/{hot_total} = {hot_match/hot_total*100:.1f}%")
# Fisher: cold x hot
ft = np.array([[cold_match, cold_total-cold_match],
               [hot_match, hot_total-hot_match]])
or_val, p_cold_hot = stats.fisher_exact(ft)
print(f"Fisher cold vs hot p = {p_cold_hot:.4f}")

# === Q3: 連續量相關 — predicted sign vs T ===
# Map color to predicted sign: color=1 → cold (-), color=0 → hot (+)
# predicted_sign = -1 if cold, +1 if hot
# If prediction works, T should correlate with predicted_sign
pred_sign = np.array([-1 if r['color'] == 1 else 1 for r in results])
T_vals = np.array([r['T'] for r in results])
# Point-biserial correlation: does color predict T sign?
# Actually simpler: rank correlation between predicted sign and actual T
rho, p_rho = stats.spearmanr(pred_sign, T_vals)
print(f"\n--- Q3: Predicted sign vs T (Spearman) ---")
print(f"ρ = {rho:.4f}, p = {p_rho:.4f}")
print(f"顯著? {'YES' if p_rho < 0.05 else 'NO'}")

# === Q4: |T| 越大匹配率越高? ===
# Bin by |T| and check match rate trend
absT = np.array([r['absT'] for r in results])
matched_arr = np.array([r['matched'] for r in results])
order = np.argsort(absT)
absT_sorted = absT[order]
matched_sorted = matched_arr[order]

# Cochran-Armitage trend test for binary outcome by |T| rank
# Simple: logistic regression matched ~ |T|
from scipy.optimize import minimize
X = np.column_stack([np.ones(len(results)), absT / absT.std()])
y = matched_arr.astype(float)

def ll(beta, X, y):
    z = X @ beta
    p = 1 / (1 + np.exp(-z))
    p = np.clip(p, 1e-15, 1 - 1e-15)
    return -np.sum(y * np.log(p) + (1 - y) * np.log(1 - p))

res = minimize(ll, x0=[0, 0], args=(X, y), method='Nelder-Mead')
beta = res.x

# Bootstrap CI
n_boot = 5000
beta_boot = []
for i in range(n_boot):
    idx = np.random.choice(len(results), size=len(results), replace=True)
    Xb = X[idx]; yb = y[idx]
    try:
        r = minimize(ll, x0=beta, args=(Xb, yb), method='Nelder-Mead')
        beta_boot.append(r.x[1])
    except:
        pass
beta_boot = np.array(beta_boot)
ci = np.percentile(beta_boot, [2.5, 97.5])

print(f"\n--- Q4: 匹配率 ~ |T| 趨勢 ---")
print(f"β₁ (|T|, std) = {beta[1]:.4f} [{ci[0]:.4f}, {ci[1]:.4f}]")
print(f"趨勢顯著? {'YES' if np.sign(ci[0]) == np.sign(ci[1]) else 'NO'}")

# === Q5: 熱色預測冷斑/熱色預測熱斑 嘅 bias ===
# Check if color=0 (hot nodes) tend to have negative T (mismatch bias)
# This would mean the coloring is systematically wrong
cold_T = np.array([r['T'] for r in results if r['color'] == 1])
hot_T = np.array([r['T'] for r in results if r['color'] == 0])
print(f"\n--- Q5: 冷/熱節點溫度分佈 ---")
print(f"冷色節點 mean T = {cold_T.mean():.2f} ± {cold_T.std():.2f}")
print(f"熱色節點 mean T = {hot_T.mean():.2f} ± {hot_T.std():.2f}")
t_stat, p_ttest = stats.ttest_ind(cold_T, hot_T)
print(f"t-test p = {p_ttest:.4f}")

# === Q6: 如果 match 定義反轉 (cold=hot, hot=cold) 會點? ===
# Is the coloring actually anti-correlated with temperature?
anti_match = sum(1 for r in results if not r['matched'])
print(f"\n--- Q6: Anti-matching (反轉定義) ---")
print(f"Anti-match: {anti_match}/{total_n} = {anti_match/total_n*100:.1f}%")
p_anti = stats.binomtest(anti_match, total_n, 0.5).pvalue
print(f"Binomial vs 50% p = {p_anti:.4f}")

# === Q7: Power analysis — effect size needed for significance ===
# Given n=60, what effect size can we detect at 80% power?
# For Fisher exact test, two proportions p1, p2
# Using normal approximation
from scipy.stats import norm
p_avg = 0.617  # overall
n1, n2 = 12, 48
# For a range of p2 values (non-zeroE match rate), what p1 would be significant?
print(f"\n--- Q7: Power analysis ---")
print(f"n_ΔE=0={n1}, n_non={n2}, baseline match rate={p_avg:.1%}")
print(f"At 80% power (α=0.05), detectable ΔE=0 match rate: >{p_avg+0.30:.0%} (estimated)")
print(f"Current ΔE=0 rate: 75% — need ~92%+ for significance with n=12")

# What sample size needed for 75% vs 58% at 80% power?
# Using normal approximation for two proportions
import math
p1, p2 = 0.75, 0.583
p_bar = (p1 + p2) / 2
z_alpha = 1.96
z_beta = 0.84
n_needed = ((z_alpha * math.sqrt(2 * p_bar * (1-p_bar)) + 
             z_beta * math.sqrt(p1*(1-p1) + p2*(1-p2))) / (p1 - p2))**2
print(f"Sample size needed (per group) for 80% power: ~{n_needed:.0f}")
print(f"Total nodes needed: ~{n_needed*2:.0f}")
print(f"Available: 60 (12 ΔE=0 + 48 non)")

print(f"\n{'='*60}")
print("SUMMARY: 開放問題判斷")
print(f"{'='*60}")
print("Q1: 整體 61.7% vs 50% → 要睇")
print("Q2: 冷色 vs 熱色匹配率差異 → 要睇")
print("Q3: Predicted sign vs T correlation → 要睇")
print("Q4: 匹配率 ~ |T| 趨勢 → 要睇")
print("Q5: 冷/熱節點溫度分佈差異 → 要睇")
print("Q6: Anti-matching 率 → 要睇")
print("Q7: Power analysis → 資訊性")