#!/usr/bin/env python3
"""
O53: Σ(3c)² = 36 係咪湊數?
================================
9 個粒子 c_f: t=+1/3, b=+1, c=+2/3, τ=-2/3, s=-2/3, μ=-1/3, d=-2/3, u=0, e=+1
3c_f: t=1, b=3, c=2, τ=-2, s=-2, μ=-1, d=-2, u=0, e=3

Σ(3c)² = 1+9+4+4+4+1+4+0+9 = 36

測試: 呢個 36 係咪排列不變? (係! 平方和唔受排列影響)
→ 真正問題: 集合 {0,±1,±2,3} 嘅 9 個值, 邊啲子集有 Σ²=36?

所有 9 選 9 排列都係 36 — 但組合 (multiset) 固定先有 36
→ 檢查: {0,1,1,2,2,3,3,4,4} 或者 {0,1,2,3,4,4,4,4,4} 都係 36?

重點: 值集 {0, ±1, ±2, 3} 有冇「最小性」?
"""
import os, json, math, sys
import numpy as np
from itertools import combinations_with_replacement

print("=" * 70)
print("O53: Σ²=36 湊數測試")
print("=" * 70)

# 實際值
vals = [1, 3, 2, -2, -2, -1, -2, 0, 3]
print(f"[1] 實際 3c_f: {vals}")
print(f"  Σ² = {sum(v*v for v in vals)}")

# 檢查: 用唔同嘅「c_f 集合」有冇 Σ²=36?
# c_f ∈ {±1, ±2/3, ±1/3, 0} → 3c_f ∈ {±3, ±2, ±1, 0}
allowed = [0, 1, 2, 3, -1, -2, -3]
print(f"\n[2] 允許值: {allowed}")

# 隨機 9 個值 (從 allowed) 嘅 Σ² 分佈
rng = np.random.default_rng(42)
counts = []
for _ in range(100000):
    sample = rng.choice(allowed, 9, replace=True)
    counts.append(sum(v*v for v in sample))
counts = np.array(counts)
print(f"  隨機 9 值 Σ² 分佈: mean={counts.mean():.1f}, std={counts.std():.1f}")
print(f"  36 出現: {(counts == 36).sum()}/100000 = {(counts==36).mean()*100:.2f}%")

# 實際值嘅 Σ²=36 有咩特別?
# 實際: {0,1,2,3,3,2,2,2,1} (絕對值) → Σ=16, Σ²=36
abs_vals = sorted(abs(v) for v in vals)
print(f"\n[3] 絕對值: {abs_vals}")
print(f"  Σ = {sum(abs_vals)}")
print(f"  Σ² = {sum(v*v for v in abs_vals)}")

# 平均
print(f"  mean |3c| = {np.mean(abs_vals):.3f}")
print(f"  mean (3c)² = {np.mean([v*v for v in vals]):.3f} = 4")
print(f"  4 = B! (K_Chain 邊界)")

# 關鍵發現: mean(3c)² = 4 = B
print(f"\n[4] mean(3c)² = 36/9 = 4 = B ✓")
print(f"  即係 Σ(3c)² = 9B = 36")
print(f"  9 = 3² = 三代²")
print(f"  36 = 9B = 3² × 4")

# 但 4 = B 係咪「被選中」?
# 如果 mean² = 5 (B+1), Σ² = 45
# 如果 mean² = 3, Σ² = 27
print(f"\n[5] 其他可能:")
for m in [3, 4, 5, 6]:
    print(f"  mean(3c)² = {m}: Σ² = {9*m}")

# 檢查: 有冇其他 9 值集合 (從 allowed) 有 Σ=16 且 Σ²=36?
print(f"\n[6] 搜尋 Σ²=36 嘅 9 值集合 (絕對值 0-3):")
solutions = []
for combo in combinations_with_replacement([0, 1, 2, 3], 9):
    if sum(v*v for v in combo) == 36:
        solutions.append(combo)
print(f"  有 {len(solutions)} 個組合")
for s in solutions[:10]:
    print(f"    {s}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)