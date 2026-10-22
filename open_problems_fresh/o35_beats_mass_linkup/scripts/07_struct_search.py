#!/usr/bin/env python3
"""
O35 — Step 6: 結構引導選擇規則搜索 (m_u/m_d, m_s/m_d 閉合)
=============================================================
唔做盲目全譜搜索 (overfit 陷阱) — 只用結構引導:

限制條件:
  [A] (n1,n2) ∈ 結構數配對: Lucas/Fibonacci/M_KT/N_d/19/71/17/6/88
  [B] k ∈ O34 已確立結構形式: a + b/88, a + b/132, a + b/528
      (L₅+L₄/88, 2B+71/132 都係呢種形式)
  [C] 配對偏差 < 0.5% (O34 質量比閉合標準)

O34 已閉合參考:
  m_t/m_b = φ^(2B+71/132) × sin(19)/sin(33)  (33=M_KT, 19=90/3−L₅)
  m_μ/m_e = φ^(L₅+L₄/88)
"""

import numpy as np
from itertools import product

N = 44
phi = (1 + np.sqrt(5)) / 2

# 結構數集合
L = {1: 1, 2: 3, 3: 4, 4: 7, 5: 11, 6: 18, 7: 29, 8: 47, 9: 76, 10: 123, 11: 199}
F = {1: 1, 2: 1, 3: 2, 4: 3, 5: 5, 6: 8, 7: 13, 8: 21, 9: 34, 10: 55}
# 結構特殊數
struct_special = {33, 44, 19, 71, 17, 6, 88, 22, 11, 7, 43}
struct_nums = set(L.values()) | set(F.values()) | struct_special
struct_nums = {n for n in struct_nums if 1 <= n <= 44}

# 結構分母 (O34 已用: 88, 132, 528; 再加 176)
struct_dens = {88, 132, 528, 176}

# PDG 2024
m_u, m_d, m_s = 2.16, 4.67, 93.4
m_c, m_b, m_t = 1.27e3, 4.18e3, 172.76e3

def sin_ratio(n1, n2):
    return np.sin(np.pi * n1 / 88) / np.sin(np.pi * n2 / 88)

def k_phi(r):
    return np.log(r) / np.log(phi)

print("=" * 67)
print("  O35 — Step 6: 結構引導選擇規則搜索")
print("=" * 67)

# ═══════════════════════════════════════════════════════════════
# 目標: m_u/m_d, m_s/m_d, m_c/m_b, m_c/m_s, m_b/m_s, m_t/m_c
# ═══════════════════════════════════════════════════════════════
targets = {
    "m_u/m_d": m_u/m_d,
    "m_s/m_d": m_s/m_d,
    "m_c/m_b": m_c/m_b,
    "m_c/m_s": m_c/m_s,
    "m_b/m_s": m_b/m_s,
    "m_t/m_c": m_t/m_c,
}

# ═══════════════════════════════════════════════════════════════
# [A] 結構配對搜索
# ═══════════════════════════════════════════════════════════════
print(f"\n─── [A] 結構配對搜索 (n1,n2 ∈ 結構數) ───")
print(f"  結構數: {sorted(struct_nums)}")

# 生成結構 k 候選: a + b/den, a ∈ [-2..12] 整數, b ∈ [-100..100] 整數
struct_k_candidates = set()
for den in struct_dens:
    for a in range(-2, 13):
        for b in range(-100, 101):
            struct_k_candidates.add(a + b/den)

print(f"  結構 k 候選數: {len(struct_k_candidates)}")
print(f"  樣本: {sorted(list(struct_k_candidates))[:10]} ...")

results = {}
for name, target in targets.items():
    best = None
    best_err = float('inf')
    for n1 in sorted(struct_nums):
        for n2 in sorted(struct_nums):
            if n1 == n2:
                continue
            r_sin = sin_ratio(n1, n2)
            if r_sin <= 0:
                continue
            k_exact = k_phi(target / r_sin)
            # 搵最近結構 k
            k_nearest = min(struct_k_candidates, key=lambda k: abs(k - k_exact))
            if abs(k_nearest - k_exact) > 0.005:  # 結構匹配容差 (k 精度)
                continue
            r_pred = r_sin * phi**k_nearest
            err = abs(r_pred - target) / target * 100
            if err < best_err:
                best_err = err
                best = (n1, n2, r_sin, k_nearest, k_exact, r_pred)
    if best:
        n1, n2, r_sin, k_near, k_ex, r_pred = best
        results[name] = best
        status = "🟢" if best_err < 0.5 else "🟡"
        print(f"  {name:<10} | sin({n1:>2},{n2:>2})={r_sin:.6f} × φ^({k_near:>8.4f}) | dev {best_err:>7.4f}% | {status}")

# ═══════════════════════════════════════════════════════════════
# [B] 詳細檢查 m_u/m_d
# ═══════════════════════════════════════════════════════════════
print(f"\n─── [B] m_u/m_d 詳細結構分析 ───")
target_ud = m_u/m_d
print(f"  目標 = {target_ud:.6f}")

# 嘗試所有結構配對, 列出 top 5 連 k 結構
cands = []
for n1 in sorted(struct_nums):
    for n2 in sorted(struct_nums):
        if n1 == n2:
            continue
        r_sin = sin_ratio(n1, n2)
        k_exact = k_phi(target_ud / r_sin)
        k_nearest = min(struct_k_candidates, key=lambda k: abs(k - k_exact))
        r_pred = r_sin * phi**k_nearest
        err = abs(r_pred - target_ud) / target_ud * 100
        cands.append((err, n1, n2, r_sin, k_nearest, k_exact, r_pred))
cands.sort()
print(f"  Top 5 結構配對 (按偏差):")
for err, n1, n2, r_sin, k_near, k_ex, r_pred in cands[:5]:
    print(f"    sin({n1},{n2}) × φ^({k_near:.4f}): dev {err:.4f}%  (k_exact={k_ex:.4f})")

# ═══════════════════════════════════════════════════════════════
# [C] 詳細檢查 m_s/m_d
# ═══════════════════════════════════════════════════════════════
print(f"\n─── [C] m_s/m_d 詳細結構分析 ───")
target_sd = m_s/m_d
print(f"  目標 = {target_sd:.6f} (= 20)")

cands2 = []
for n1 in sorted(struct_nums):
    for n2 in sorted(struct_nums):
        if n1 == n2:
            continue
        r_sin = sin_ratio(n1, n2)
        k_exact = k_phi(target_sd / r_sin)
        k_nearest = min(struct_k_candidates, key=lambda k: abs(k - k_exact))
        r_pred = r_sin * phi**k_nearest
        err = abs(r_pred - target_sd) / target_sd * 100
        cands2.append((err, n1, n2, r_sin, k_nearest, k_exact, r_pred))
cands2.sort()
print(f"  Top 5 結構配對 (按偏差):")
for err, n1, n2, r_sin, k_near, k_ex, r_pred in cands2[:5]:
    print(f"    sin({n1},{n2}) × φ^({k_near:.4f}): dev {err:.4f}%  (k_exact={k_ex:.4f})")

# ═══════════════════════════════════════════════════════════════
# [D] 結構規律檢查: O34 已閉合 k 結構
# ═══════════════════════════════════════════════════════════════
print(f"\n─── [D] O34 已閉合 k 結構回顧 ───")
print(f"  m_μ/m_e: k = L₅ + L₄/88 = 11 + 7/88 = {11 + 7/88:.6f}")
print(f"  m_t/m_b: k = 2B + 71/132 = 8 + 71/132 = {8 + 71/132:.6f}")
print(f"  71 = 2N_d − (L₅+C(4,2)) = 88 − 17")
print(f"  132 = 3×44 = dimC × N_d")
print(f"")
print(f"  結構形式: k = 整數 + 結構數/結構分母")
print(f"  分子: L₄=7, 71 都係結構數")
print(f"  分母: 88, 132 = 2N_d, dimC×N_d")

# ═══════════════════════════════════════════════════════════════
# 總結
# ═══════════════════════════════════════════════════════════════
print(f"\n{'═'*67}")
n_green = sum(1 for name in results if results[name][5] is not None and abs(results[name][3] - results[name][4]) < 0.005 and abs(results[name][5] - targets[name])/targets[name]*100 < 0.5)
print(f"  🟢 閉合 (<0.5%): {n_green}/{len(targets)}")
print(f"  ⚠️ 注意: 結構配對 + 結構 k 仍然有自由度, 需要額外「配對規則」")
print(f"  (O34 m_t/m_b 配對 (19,33) 有規則: 33=M_KT, 19=90/3−L₅)")
print(f"{'═'*67}")

with open("data/step6_struct_search_results.txt", "w") as f:
    f.write("O35 — Step 6: 結構引導選擇規則搜索\n")
    f.write("=" * 67 + "\n\n")
    f.write("限制: (n1,n2) ∈ 結構數, k ∈ a+b/den (den∈{88,132,176,528})\n\n")
    for name, b in results.items():
        n1, n2, r_sin, k_near, k_ex, r_pred = b
        err = abs(r_pred - targets[name])/targets[name]*100
        f.write(f"  {name}: sin({n1},{n2}) x phi^({k_near:.6f}) = {r_pred:.6f} (dev {err:.4f}%)\n")
    f.write("\n⚠️ 結構配對仍有自由度, 需要額外配對規則鎖定\n")
print(f"\n  結果已寫入 data/step6_struct_search_results.txt")
