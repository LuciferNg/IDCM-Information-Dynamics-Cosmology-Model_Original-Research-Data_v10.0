#!/usr/bin/env python3
"""
O24: 極端節點匹配不對稱分析
============================
冷端 8/10 vs 熱端 6/10 — 結構意義檢驗

問題:
- 最冷 10 節點中冷色匹配: 8/10 (期望 5/10)
- 最熱 10 節點中熱色匹配: 6/10 (期望 5/10)
- 呢個不對稱有冇結構意義?

方法:
1. Binomial 檢驗 (冷/熱端分別)
2. 剔除節點 0 (冷斑) 敏感性分析
3. 冷/熱端 mean|T| 對比
4. 隨機對照: 100,000 次隨機抽 10 節點
5. 排序位置曲線: 匹配率 vs 極端度
"""
import numpy as np
from scipy.stats import binomtest
from collections import Counter
import os

OUT = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o24_extreme_side_asym"
DATA = os.path.join(OUT, "data")
os.makedirs(DATA, exist_ok=True)

# ============ 1. 載入數據 ============
data = []
with open("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o3_node_temperatures/data/node_temps.txt") as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        parts = line.split()
        idx = int(parts[0])
        color = int(parts[1])  # 1=cold, 0=hot
        T = float(parts[2])
        l = float(parts[3])
        b = float(parts[4])
        bfs = int(parts[5])
        data.append((idx, color, T, l, b, bfs))

# Sort by temperature ascending (coldest first)
data_by_T = sorted(data, key=lambda x: x[2])
T_arr = np.array([d[2] for d in data_by_T])
color_arr = np.array([d[1] for d in data_by_T])
idx_arr = np.array([d[0] for d in data_by_T])
bfs_arr = np.array([d[5] for d in data_by_T])

print("=" * 66)
print("O24: 極端節點匹配不對稱分析")
print("=" * 66)

# ============ 2. 冷端/熱端匹配 ============
for label, n, desc in [("冷端 (最冷)", 10, "coldest"), ("熱端 (最熱)", 10, "hottest")]:
    if desc == "coldest":
        colors = color_arr[:n]
        cold_match = colors.sum()  # cold=1
        hot_match = n - cold_match
        match_str = f"冷色={cold_match}/{n}, 熱色={hot_match}/{n}"
        p = binomtest(cold_match, n, 0.5, alternative='greater').pvalue
        p_two = binomtest(cold_match, n, 0.5).pvalue
    else:
        colors = 1 - color_arr[-n:]  # Invert: we want hot=1 match
        hot_match = colors.sum()
        cold_match = n - hot_match
        match_str = f"熱色={hot_match}/{n}, 冷色={cold_match}/{n}"
        p = binomtest(hot_match, n, 0.5, alternative='greater').pvalue
        p_two = binomtest(hot_match, n, 0.5).pvalue

    print(f"\n  {label} ({desc}):")
    print(f"    匹配: {match_str}")
    print(f"    單側 Binomial p (大於期望): {p:.4f}")
    print(f"    雙側 Binomial p:            {p_two:.4f}")

# ============ 3. 剔除節點 0 (冷斑) ============
print("\n" + "=" * 66)
print("敏感性分析: 剔除節點 0 (冷斑)")
print("=" * 66)

# Find node 0 in the sorted list
idx_of_node0 = np.where(idx_arr == 0)[0][0]
print(f"  節點 0 排名: #{idx_of_node0+1} (最冷), T={data_by_T[idx_of_node0][2]:.1f} μK, color={data_by_T[idx_of_node0][1]} (冷=1)")

# Correct method: take top 10 (cold end), remove node 0 → 9 nodes
cold_10_colors = color_arr[:10]
cold_10_idx = idx_arr[:10]
mask = cold_10_idx != 0
cold_9_colors = cold_10_colors[mask]
cold_match_excl = int(cold_9_colors.sum())
n_excl = len(cold_9_colors)
print(f"\n  冷端 (剔除節點 0, 冷端 top 10 → omit idx 0 → {n_excl} 節點): 冷色={cold_match_excl}/{n_excl}")
p_excl = binomtest(cold_match_excl, n_excl, 0.5, alternative='greater').pvalue
p_excl_two = binomtest(cold_match_excl, n_excl, 0.5).pvalue
print(f"    單側 Binomial p: {p_excl:.4f}")
print(f"    雙側 Binomial p: {p_excl_two:.4f}")
print(f"    原始: 8/10 → 剔除節點 0: {cold_match_excl}/{n_excl}")

# Hot end check
hottest_idx = idx_arr[-1]
hottest_color = color_arr[-1]
print(f"\n  最熱節點 idx={hottest_idx}, T={data_by_T[-1][2]:.1f} μK, color={hottest_color} (冷=0→熱)")
print(f"  最熱節點 53 係熱色? {'✅' if hottest_color == 0 else '❌'}")

# ============ 4. 冷/熱端 mean|T| 對比 ============
print("\n" + "=" * 66)
print("冷/熱端 mean|T| 對比")
print("=" * 66)

cold_10_T = np.abs(T_arr[:10])
hot_10_T = np.abs(T_arr[-10:])
print(f"  最冷 10 mean|T|: {cold_10_T.mean():.1f} μK")
print(f"  最熱 10 mean|T|: {hot_10_T.mean():.1f} μK")
print(f"  比率: {cold_10_T.mean()/hot_10_T.mean():.2f}x")

# Without node 0: cold end top 10 minus node 0 → 9 nodes
cold_10_abs = np.abs(T_arr[:10])
cold_10_idx = idx_arr[:10]
mask = cold_10_idx != 0
cold_9_abs = cold_10_abs[mask]
cold_9_abs_mean = cold_9_abs.mean()
print(f"  最冷 9 (冷端 top 10 剔除節點 0) mean|T|: {cold_9_abs_mean:.1f} μK")
print(f"  比率 (vs 最熱 10): {cold_9_abs_mean/hot_10_T.mean():.2f}x")

# ============ 5. 隨機對照 ============
print("\n" + "=" * 66)
print("隨機對照: 100,000 次隨機抽 10 節點")
print("=" * 66)

N_TRIALS = 100000
n_nodes = 60
all_colors = np.array([d[1] for d in data])  # original order

# For each trial, randomly pick 10 nodes, count cold matches
cold_matches = np.zeros(N_TRIALS, dtype=int)
# For hottest: pick 10, count hot matches (1-color)
hot_matches = np.zeros(N_TRIALS, dtype=int)

for i in range(N_TRIALS):
    pick = np.random.choice(n_nodes, 10, replace=False)
    cold_matches[i] = all_colors[pick].sum()
    # hot match = count of hot=0 in the pick → (10 - cold count)
    hot_matches[i] = 10 - all_colors[pick].sum()

# Distribution of cold matches
cold_counts = Counter(cold_matches)
hot_counts = Counter(hot_matches)

print(f"\n  冷色匹配數分佈 (10 節點中冷色數):")
for k in sorted(cold_counts):
    pct = cold_counts[k] / N_TRIALS * 100
    bar = "█" * int(pct / 2)
    print(f"    {k}: {cold_counts[k]:6d} ({pct:5.1f}%) {bar}")

# Probability of >=8 cold matches
p_cold_ge8 = (cold_matches >= 8).sum() / N_TRIALS
p_cold_ge7 = (cold_matches >= 7).sum() / N_TRIALS
print(f"\n  P(冷色≥8/10): {p_cold_ge8:.4f} ({p_cold_ge8*100:.1f}%)")
print(f"  P(冷色≥7/10): {p_cold_ge7:.4f} ({p_cold_ge7*100:.1f}%)")

# Hot match distribution
print(f"\n  熱色匹配數分佈 (10 節點中熱色數):")
for k in sorted(hot_counts):
    pct = hot_counts[k] / N_TRIALS * 100
    bar = "█" * int(pct / 2)
    print(f"    {k}: {hot_counts[k]:6d} ({pct:5.1f}%) {bar}")

p_hot_ge6 = (hot_matches >= 6).sum() / N_TRIALS
p_hot_ge7 = (hot_matches >= 7).sum() / N_TRIALS
print(f"\n  P(熱色≥6/10): {p_hot_ge6:.4f} ({p_hot_ge6*100:.1f}%)")
print(f"  P(熱色≥7/10): {p_hot_ge7:.4f} ({p_hot_ge7*100:.1f}%)")

# ============ 6. 排序位置曲線 ============
print("\n" + "=" * 66)
print("排序位置匹配率曲線")
print("=" * 66)

print(f"\n  {'排名':>4} {'idx':>4} {'T(μK)':>8} {'color':>5} {'冷?':>4} {'bfs':>4}")
print(f"  {'-'*35}")
for i in range(60):
    idx, color, T, l, b, bfs = data_by_T[i]
    cold_str = "✅冷" if color == 1 else "❌熱"
    print(f"  {i+1:4d} {idx:4d} {T:8.1f} {color:5d} {cold_str:>4} {bfs:4d}")

# Running match rate from top
running_cold = np.cumsum(color_arr)
running_rate = running_cold / np.arange(1, 61)
print(f"\n  累積冷色匹配率:")
for i in range(0, 60, 5):
    print(f"    top {i+1:2d}: {running_cold[i]:2d}/{i+1:2d} = {running_rate[i]:.3f}")

# From bottom (hottest side)
rev_color = 1 - color_arr[::-1]  # hot=1 from hottest
running_hot = np.cumsum(rev_color)
running_hot_rate = running_hot / np.arange(1, 61)
print(f"\n  累積熱色匹配率 (從最熱):")
for i in range(0, 60, 5):
    print(f"    top {i+1:2d}: {running_hot[i]:2d}/{i+1:2d} = {running_hot_rate[i]:.3f}")

# ============ 7. 冷端 vs 熱端不對稱 (Fisher exact test) ============
print("\n" + "=" * 66)
print("Fisher 精確檢驗: 冷端 8/10 vs 熱端 6/10")
print("=" * 66)

from scipy.stats import fisher_exact
# Contingency table:
#           cold-match  hot-match  total
# cold-end       8          2        10
# hot-end        4          6        10
# (hot-end cold-match = 10-6=4, hot-match=6)
table = [[8, 2], [4, 6]]
odds, p_fisher = fisher_exact(table)
print(f"  Contingency table: [[8,2],[4,6]]")
print(f"  Fisher exact p: {p_fisher:.4f}")
print(f"  Odds ratio: {odds:.2f}")

# Also with continuity correction? No, fisher_exact is exact.

# ============ 8. 寫結果文件 ============
print("\n" + "=" * 66)
print("寫入結果")
print("=" * 66)

with open(os.path.join(DATA, "o24_extreme_asymmetry_results.txt"), "w") as f:
    f.write("# O24: 極端節點匹配不對稱分析結果\n")
    f.write(f"# 生成: 2026-08-21\n")
    f.write(f"# 隨機對照: N_TRIALS={N_TRIALS}\n\n")

    f.write("=== 1. Binomial 檢驗 ===\n")
    f.write(f"冷端 8/10: p_one-sided={binomtest(8,10,0.5,alternative='greater').pvalue:.4f}, p_two-sided={binomtest(8,10,0.5).pvalue:.4f}\n")
    f.write(f"熱端 6/10: p_one-sided={binomtest(6,10,0.5,alternative='greater').pvalue:.4f}, p_two-sided={binomtest(6,10,0.5).pvalue:.4f}\n\n")

    f.write("=== 2. 剔除節點 0 (冷斑) ===\n")
    f.write(f"冷端 8/10 → 剔除節點 0 → {cold_match_excl}/{n_excl} (p_one={p_excl:.4f}, p_two={p_excl_two:.4f})\n\n")

    f.write("=== 3. 冷/熱端 mean|T| 對比 ===\n")
    f.write(f"最冷 10 mean|T|: {cold_10_T.mean():.1f} μK\n")
    f.write(f"最熱 10 mean|T|: {hot_10_T.mean():.1f} μK\n")
    f.write(f"比率: {cold_10_T.mean()/hot_10_T.mean():.2f}x\n")
    f.write(f"最冷 9 (剔除節點 0) mean|T|: {cold_9_abs_mean:.1f} μK\n")
    f.write(f"冷9/熱10 比率: {cold_9_abs_mean/hot_10_T.mean():.2f}x\n\n")

    f.write("=== 4. 隨機對照 (100,000 trials) ===\n")
    f.write(f"P(冷色≥8/10): {p_cold_ge8:.4f}\n")
    f.write(f"P(冷色≥7/10): {p_cold_ge7:.4f}\n")
    f.write(f"P(熱色≥6/10): {p_hot_ge6:.4f}\n")
    f.write(f"P(熱色≥7/10): {p_hot_ge7:.4f}\n\n")

    f.write("=== 5. Fisher exact test (冷端 vs 熱端) ===\n")
    f.write(f"Fisher p={p_fisher:.4f}, OR={odds:.2f}\n\n")

    f.write("=== 6. 完整排序列表 ===\n")
    f.write(f"{'rank':>4} {'idx':>4} {'T_uK':>8} {'color':>5} {'bfs':>4}\n")
    for i in range(60):
        idx, color, T, l, b, bfs = data_by_T[i]
        f.write(f"{i+1:4d} {idx:4d} {T:8.1f} {color:5d} {bfs:4d}\n")

print("\n✅ 分析完成")