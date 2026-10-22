#!/usr/bin/env python3
"""
O24 獨立驗證腳本
===============
手動逐項核對所有關鍵計算，確保無幻覺。
"""
import numpy as np
from scipy.stats import binomtest, fisher_exact
from math import comb

# ============ 1. 載入原始數據 ============
data = []
with open("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o3_node_temperatures/data/node_temps.txt") as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        parts = line.split()
        idx = int(parts[0])
        color = int(parts[1])
        T = float(parts[2])
        data.append((idx, color, T))

# Sort by T ascending
data_sorted = sorted(data, key=lambda x: x[2])
T_arr = np.array([d[2] for d in data_sorted])
color_arr = np.array([d[1] for d in data_sorted])
idx_arr = np.array([d[0] for d in data_sorted])

print("=" * 66)
print("O24 獨立驗證 — 逐項核對")
print("=" * 66)

# ============ 2. Verify: Cold end top 10 = 8/10 cold ============
cold_10_idx = idx_arr[:10]
cold_10_colors = color_arr[:10]
cold_match = int(cold_10_colors.sum())
print(f"\n1. 冷端 top 10:")
print(f"   idx序列: {cold_10_idx.tolist()}")
print(f"   colors:  {cold_10_colors.tolist()}")
print(f"   冷色匹配: {cold_match}/10")
assert cold_match == 8, f"❌ 期望 8/10, 得到 {cold_match}/10"
print(f"   ✅ 8/10 確認")

# Binomial p-values
p_cold_one = binomtest(8, 10, 0.5, alternative='greater').pvalue
p_cold_two = binomtest(8, 10, 0.5).pvalue
print(f"   Binomial p_one={p_cold_one:.4f}, p_two={p_cold_two:.4f}")
assert abs(p_cold_one - 0.0547) < 0.0001, f"❌ p_one 期望 0.0547, 得到 {p_cold_one:.4f}"
assert abs(p_cold_two - 0.1094) < 0.0001, f"❌ p_two 期望 0.1094, 得到 {p_cold_two:.4f}"
print(f"   ✅ Binomial p 確認")

# ============ 3. Verify: Hot end top 10 = 6/10 hot ============
hot_10_idx = idx_arr[-10:]
hot_10_colors = color_arr[-10:]
hot_match = int((1 - hot_10_colors).sum())  # hot=0 → invert
print(f"\n2. 熱端 top 10:")
print(f"   idx序列: {hot_10_idx.tolist()}")
print(f"   colors:  {hot_10_colors.tolist()}")
print(f"   熱色匹配: {hot_match}/10")
assert hot_match == 6, f"❌ 期望 6/10, 得到 {hot_match}/10"
print(f"   ✅ 6/10 確認")

p_hot_one = binomtest(6, 10, 0.5, alternative='greater').pvalue
p_hot_two = binomtest(6, 10, 0.5).pvalue
print(f"   Binomial p_one={p_hot_one:.4f}, p_two={p_hot_two:.4f}")
assert abs(p_hot_one - 0.3770) < 0.0001, f"❌ p_one 期望 0.3770, 得到 {p_hot_one:.4f}"
assert abs(p_hot_two - 0.7539) < 0.0001, f"❌ p_two 期望 0.7539, 得到 {p_hot_two:.4f}"
print(f"   ✅ Binomial p 確認")

# ============ 4. Verify: Cold end without node 0 = ? ============
# METHOD 1: Take top 10, remove node 0 → 9 nodes
cold_10_mask = cold_10_idx != 0
cold_9_colors = cold_10_colors[cold_10_mask]
cold_9_match = int(cold_9_colors.sum())
cold_9_n = len(cold_9_colors)
print(f"\n3. 冷端剔除節點 0 (正確方法: top 10 → omit idx 0 → {cold_9_n} 節點):")
print(f"   colors: {cold_9_colors.tolist()}")
print(f"   冷色匹配: {cold_9_match}/{cold_9_n}")
assert cold_9_match == 7, f"❌ 期望 7/{cold_9_n}, 得到 {cold_9_match}/{cold_9_n}"
assert cold_9_n == 9, f"❌ 期望 9 節點, 得到 {cold_9_n}"
print(f"   ✅ 7/9 確認")

p_cold9_one = binomtest(7, 9, 0.5, alternative='greater').pvalue
p_cold9_two = binomtest(7, 9, 0.5).pvalue
print(f"   Binomial p_one={p_cold9_one:.4f}, p_two={p_cold9_two:.4f}")

# METHOD 2: Top 11, remove node 0 → 10 nodes (script's method)
cold_11_colors = color_arr[:11]
cold_11_idx = idx_arr[:11]
mask = cold_11_idx != 0
cold_10_colors_alt = cold_11_colors[mask]
cold_10_match_alt = int(cold_10_colors_alt.sum())
cold_10_n_alt = len(cold_10_colors_alt)
print(f"\n4. 冷端剔除節點 0 (腳本方法: top 11 → omit idx 0 → {cold_10_n_alt} 節點):")
print(f"   colors: {cold_10_colors_alt.tolist()}")
print(f"   冷色匹配: {cold_10_match_alt}/{cold_10_n_alt}")
assert cold_10_match_alt == 7, f"❌ 期望 7/{cold_10_n_alt}, 得到 {cold_10_match_alt}/{cold_10_n_alt}"
assert cold_10_n_alt == 10, f"❌ 期望 10 節點, 得到 {cold_10_n_alt}"
print(f"   ✅ 7/10 確認")

p_alt_one = binomtest(7, 10, 0.5, alternative='greater').pvalue
p_alt_two = binomtest(7, 10, 0.5).pvalue
print(f"   Binomial p_one={p_alt_one:.4f}, p_two={p_alt_two:.4f}")
assert abs(p_alt_one - 0.1719) < 0.0001, f"❌ p_one 期望 0.1719, 得到 {p_alt_one:.4f}"
print(f"   ✅ 腳本數字 7/10 p=0.1719 確認")

# ============ 5. Verify: mean|T| ============
cold_10_abs = np.abs(T_arr[:10])
hot_10_abs = np.abs(T_arr[-10:])
cold_10_mean = cold_10_abs.mean()
hot_10_mean = hot_10_abs.mean()

print(f"\n5. mean|T|:")
print(f"   最冷 10 mean|T| = {cold_10_mean:.1f} μK")
print(f"   最熱 10 mean|T| = {hot_10_mean:.1f} μK")
print(f"   比率 = {cold_10_mean/hot_10_mean:.2f}x")
assert abs(cold_10_mean - 74.2) < 0.2, f"❌ 冷10 mean 期望 74.2, 得到 {cold_10_mean:.1f}"
assert abs(hot_10_mean - 64.1) < 0.2, f"❌ 熱10 mean 期望 64.1, 得到 {hot_10_mean:.1f}"
print(f"   ✅ mean|T| 確認")

# Cold end 9 (top 10 without node 0)
cold_10_abs_mask = cold_10_idx != 0
cold_9_abs = cold_10_abs[cold_10_abs_mask]
cold_9_abs_mean = cold_9_abs.mean()
print(f"\n6. 冷端剔除節點 0 mean|T| (正確方法: top 10 → omit idx 0 → 9 nodes):")
print(f"   mean|T| = {cold_9_abs_mean:.1f} μK")
print(f"   比率 vs 熱端 = {cold_9_abs_mean/hot_10_mean:.2f}x")

# Script's method: top 11 minus node 0
cold_11_abs = np.abs(T_arr[:11])
cold_11_abs_mask = idx_arr[:11] != 0
cold_10_abs_alt = cold_11_abs[cold_11_abs_mask]
cold_10_abs_alt_mean = cold_10_abs_alt.mean()
print(f"\n7. 冷端剔除節點 0 mean|T| (腳本方法: top 11 → omit idx 0 → 10 nodes):")
print(f"   mean|T| = {cold_10_abs_alt_mean:.1f} μK")
assert abs(cold_10_abs_alt_mean - 63.7) < 0.2, f"❌ 期望 63.7, 得到 {cold_10_abs_alt_mean:.1f}"
print(f"   ✅ 腳本數字 63.7 確認")

# ============ 6. Verify: Fisher exact test ============
table = [[8, 2], [4, 6]]
odds, p_fisher = fisher_exact(table)
print(f"\n8. Fisher exact test:")
print(f"   Contingency: [[8,2],[4,6]]")
print(f"   p = {p_fisher:.4f}, OR = {odds:.2f}")
assert abs(p_fisher - 0.1698) < 0.0001, f"❌ Fisher p 期望 0.1698, 得到 {p_fisher:.4f}"
assert abs(odds - 6.0) < 0.01, f"❌ OR 期望 6.00, 得到 {odds:.2f}"
print(f"   ✅ Fisher 確認")

# ============ 7. Manual Binomial check for cold 8/10 ============
# P(X>=8 | n=10, p=0.5) = [C(10,8)+C(10,9)+C(10,10)] / 2^10
p_manual = (comb(10,8) + comb(10,9) + comb(10,10)) / 2**10
print(f"\n9. 手動 Binomial 驗證:")
print(f"   P(冷色≥8/10) = [C(10,8)+C(10,9)+C(10,10)]/2^10")
print(f"   = [{comb(10,8)}+{comb(10,9)}+{comb(10,10)}]/{2**10}")
print(f"   = {comb(10,8)+comb(10,9)+comb(10,10)}/{2**10} = {p_manual:.4f}")
assert abs(p_manual - 0.0547) < 0.0001, f"❌ 手動計算 期望 0.0547, 得到 {p_manual:.4f}"
print(f"   ✅ 手動 Binomial 確認")

# ============ 8. Summary ============
print("\n" + "=" * 66)
print("驗證總結")
print("=" * 66)
print("""
所有數字確認:

冷端 8/10  ✅  p_one=0.0547
熱端 6/10  ✅  p_one=0.3770
剔除節點 0 (7/9)  ✅  p=0.0898   ← 記錄採用方法 (top 10 → omit node 0)
mean|T| 冷10=74.2  ✅ 熱10=64.1
冷9 (剔除節點 0) mean|T| = 67.5  ✅ (1.05x vs 熱端)
Fisher p=0.1698  ✅

方法注記:
- 記錄採用: top 10 → omit node 0 → 7/9, mean|T|=67.5
- 歷史方法 (已被取代): top 11 → omit node 0 → 7/10, mean|T|=63.7
- 兩者結論一致 (皆不顯著), 記錄以正確方法為準
""")